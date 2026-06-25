import time
import asyncio
import logging
from app.models.session import AgentSession
from app.browser.extraction import extract_interactive_elements
from app.browser.tools.extract_text import extract_text
from app.browser.tools.navigate import navigate
from app.browser.tools.click import click
from app.browser.tools.type_text import type_text
from app.browser.tools.scroll import scroll
from app.browser.tools.screenshot import screenshot
from app.browser.tools.click_on_screen import click_on_screen
from app.browser.tools.double_click import double_click
from app.llm.planner import plan_next_action
from app.llm.summarizer import summarize_extracted_text

logger = logging.getLogger(__name__)

async def run_agent(
    session: AgentSession,
    send_update
) -> str:
    """
    Runs the agent loop:
    observe -> extract DOM/text -> plan -> execute -> verify -> screenshot
    """
    session.status = "running"
    session.start_time = time.time()
    
    max_steps = int(session.history[0].get("max_steps", 20) if session.history else 20)
    max_duration = 300.0  # 5 minutes
    
    # Store accumulated visible texts
    accumulated_texts = []
    current_visible_text = ""
    
    # Start browser lifecycle (ensure page is opened)
    if not session.page:
        session.status = "error"
        session.current_action = "Browser not initialized."
        await send_update(session)
        return "Error: Browser not initialized."
        
    try:
        while session.current_step < max_steps:
            # Check if stopped by user
            if session.status == "stopped":
                return "Stopped: Session aborted by user."

            # 1. Check time limits
            elapsed_time = time.time() - session.start_time
            if elapsed_time > max_duration:
                session.status = "error"
                session.current_action = "Session timeout exceeded."
                await send_update(session)
                return "Error: Session duration limit exceeded."
                
            session.current_step += 1
            session.current_action = "Observing and extracting DOM..."
            await send_update(session)
            
            # 2. Observe & Extract DOM / Text
            session.current_url = session.page.url
            interactive_elements = await extract_interactive_elements(session.page)
            
            # 3. Plan via Groq
            session.current_action = "Asking Groq Planner for next step..."
            await send_update(session)
            
            plan = await plan_next_action(
                goal=session.goal,
                current_url=session.current_url,
                interactive_elements=interactive_elements,
                visible_text=current_visible_text,
                history=session.history
            )
            
            tool = plan.get("tool", "finish_task")
            element_id = plan.get("element_id")
            arguments = plan.get("arguments", {})
            reasoning = plan.get("reasoning", "")
            confidence = plan.get("confidence", 1.0)
            done = plan.get("done", False)
            
            session.current_action = f"Reasoning: {reasoning}"
            await send_update(session)
            
            # 4. Handle confidence threshold
            if confidence < 0.5:
                session.status = "waiting_for_input"
                session.current_action = f"Planner is uncertain: {reasoning}. Awaiting guidance..."
                
                # Take screenshot before pausing
                scr_res = await screenshot(session.page, session.session_id, session.current_step)
                screenshot_url = scr_res.get("data", {}).get("screenshot_url")
                await send_update(session, screenshot_url)
                
                # Wait for user input via Event
                session.resume_event = asyncio.Event()
                await session.resume_event.wait()
                
                if session.status == "stopped":
                    return "Stopped: Session aborted by user."
                
                # Append user guidance to session history
                session.history.append({
                    "step": session.current_step,
                    "tool": "user_guidance",
                    "reasoning": f"User provided guidance: {session.user_input}",
                    "success": True,
                    "message": f"Guidance: {session.user_input}"
                })
                
                # Reset status and retry planning
                session.status = "running"
                session.user_input = ""
                session.current_action = "Retrying planning with user guidance..."
                await send_update(session)
                continue
                
            # 5. Handle Done / Finish task
            if done or tool == "finish_task":
                session.current_action = "Synthesizing final summary..."
                await send_update(session)
                
                final_result = arguments.get("result", "Goal completed.")
                if accumulated_texts:
                    # Summarize accumulated text content
                    all_text = "\n\n=== SOURCE CONTENT ===\n\n".join(accumulated_texts)
                    final_result = await summarize_extracted_text(session.goal, all_text)
                    
                session.status = "completed"
                session.current_action = "Task Finished successfully."
                
                scr_res = await screenshot(session.page, session.session_id, session.current_step)
                screenshot_url = scr_res.get("data", {}).get("screenshot_url")
                await send_update(session, screenshot_url)
                
                session.history.append({
                    "step": session.current_step,
                    "tool": "finish_task",
                    "reasoning": reasoning,
                    "success": True,
                    "result": final_result
                })
                return final_result
                
            # 6. Execute action
            exec_message = f"Executing tool: {tool}"
            exec_success = False
            prev_url = session.page.url
            
            # Resolve element_id to selector if needed
            selector = None
            if element_id is not None:
                matched = next((el for el in interactive_elements if el["id"] == element_id), None)
                if matched:
                    selector = matched["selector"]
                else:
                    exec_message = f"Error: element_id {element_id} not found in DOM."
            
            # Support assignment-specific tool arguments if passed dynamically
            if tool == "navigate_to_url" or tool == "navigate":
                url = arguments.get("url")
                if url:
                    exec_res = await navigate(session.page, url)
                    exec_success = exec_res["success"]
                    exec_message = exec_res["message"]
                    
            elif tool == "click":
                if selector:
                    exec_res = await click(session.page, selector)
                    exec_success = exec_res["success"]
                    exec_message = exec_res["message"]
                    
            elif tool == "click_on_screen":
                x = arguments.get("x")
                y = arguments.get("y")
                if x is not None and y is not None:
                    exec_res = await click_on_screen(session.page, float(x), float(y))
                    exec_success = exec_res["success"]
                    exec_message = exec_res["message"]
                else:
                    exec_message = "Error: Coordinates 'x' and 'y' must be specified for click_on_screen."
                    
            elif tool == "send_keys" or tool == "type_text":
                text = arguments.get("text")
                if selector and text is not None:
                    exec_res = await type_text(session.page, selector, text)
                    exec_success = exec_res["success"]
                    exec_message = exec_res["message"]
                else:
                    exec_message = "Error: Element selector and text must be specified for typing."
                    
            elif tool == "scroll":
                direction = arguments.get("direction", "down")
                exec_res = await scroll(session.page, direction)
                exec_success = exec_res["success"]
                exec_message = exec_res["message"]
                
            elif tool == "double_click":
                # Double click can either be on element or on screen coordinates
                target_selector = selector or arguments.get("selector")
                x = arguments.get("x")
                y = arguments.get("y")
                
                exec_res = await double_click(
                    session.page, 
                    selector=target_selector, 
                    x=float(x) if x is not None else None, 
                    y=float(y) if y is not None else None
                )
                exec_success = exec_res["success"]
                exec_message = exec_res["message"]
                
            elif tool == "take_screenshot" or tool == "screenshot":
                exec_res = await screenshot(session.page, session.session_id, session.current_step)
                exec_success = exec_res["success"]
                exec_message = exec_res["message"]
                
            elif tool == "extract_text":
                sel = arguments.get("selector", "body")
                exec_res = await extract_text(session.page, sel)
                exec_success = exec_res["success"]
                exec_message = exec_res["message"]
                if exec_success:
                    extracted_val = exec_res["data"].get("text", "")
                    current_visible_text = extracted_val
                    accumulated_texts.append(f"Url: {session.page.url}\nSelector: {sel}\nContent: {extracted_val}")
                    
            else:
                exec_message = f"Unknown tool: {tool}"
                
            # 7. Verification step
            verification_status = "Not verified"
            if exec_success:
                verification_status = "Verified successfully"
                # Do light post-verification checks
                if tool in ["navigate", "navigate_to_url"]:
                    if session.page.url == prev_url and prev_url != "about:blank":
                        verification_status = "Verify alert: URL did not change."
                elif tool in ["type_text", "send_keys"] and selector:
                    try:
                        val = await session.page.locator(selector).first.input_value()
                        if val != arguments.get("text"):
                            verification_status = f"Verify alert: Field value mismatch (Expected: {arguments.get('text')}, Got: {val})"
                    except Exception:
                        pass
            
            session.history.append({
                "step": session.current_step,
                "tool": tool,
                "element_id": element_id,
                "arguments": arguments,
                "reasoning": reasoning,
                "message": exec_message,
                "success": exec_success,
                "verification": verification_status
            })
            
            # Update action message
            session.current_action = f"Action: {tool}. Status: {exec_message}. Verification: {verification_status}."
            
            # 8. Capture post-action screenshot for visual timeline
            scr_res = await screenshot(session.page, session.session_id, session.current_step)
            screenshot_url = scr_res.get("data", {}).get("screenshot_url")
            await send_update(session, screenshot_url)
            
            # Small cooldown between actions
            await asyncio.sleep(1.5)
            
        session.status = "completed"
        session.current_action = "Reached maximum step limit."
        await send_update(session)
        return "Task stopped: Max step limit reached."
        
    except Exception as e:
        logger.exception("Error in agent execution loop:")
        session.status = "error"
        session.current_action = f"Exception: {str(e)}"
        await send_update(session)
        return f"Error: {str(e)}"
