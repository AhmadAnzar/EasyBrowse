# Architecture Document - EasyBrowse

This document explains the architecture design decisions, directory structures, and agentic workflows of the Website Automation Agent.

---

## 🏛️ Design Overview

EasyBrowse is built as a decoupled **Client-Server Application**:
- **Backend (Python / FastAPI)**: Hosts the agent execution loop, coordinates Playwright browser context, processes DOM extractions, structures Groq LLM prompts, and communicates with the client via WebSockets.
- **Frontend (React / Vite)**: Renders a stateful visual control panel that manages state using Zustand, displaying real-time timeline screenshots, logs, intervention forms, and final synthesized outcomes.

```
┌───────────────────┐               ┌──────────────────────┐
│  React Frontend   │ ◄─── Ws ────► │ FastAPI Agent Server │
└───────────────────┘               └──────────────────────┘
                                                │
                                       (Groq LLM / Playwright)
                                                ▼
                                    ┌──────────────────────┐
                                    │     Target Web Page   │
                                    └──────────────────────┘
```

---

## 📂 Project Structure

```
EasyBrowse/
├── backend/
│   ├── app/
│   │   ├── agent/           # Core autonomous execution runner
│   │   ├── browser/         # Playwright driver actions and interactive element detection
│   │   ├── llm/             # Groq planner prompts and summarization templates
│   │   ├── models/          # Session models representing state
│   │   ├── services/        # Event loop routers and socket interfaces
│   │   └── main.py          # FastAPI application routes
│   ├── cli.py               # Terminal client execution CLI
│   └── run.py               # Reload-capable development server entrypoint
└── frontend/
    ├── src/
    │   ├── components/      # UI components (Console, Chat, BrowserView)
    │   ├── services/        # HTTP / WS api clients
    │   ├── store/           # Zustand stores for browser logs & outputs
    │   └── App.tsx          # Application configuration dashboard
```

---

## 🧠 Autonomous Agent Workflow Loop

The agent runs a continuous ReAct loop until it reaches the goal or runs out of steps:

1. **Observe**: The agent navigates to the page and extracts visible, interactive elements (buttons, inputs, select fields) along with their coordinate bounding boxes, tags, placeholders, and roles.
2. **Truncate & Optimize**: Selectors are stripped out from elements to optimize prompt sizes by 70%, avoiding rate limits (TPM limits) of the LLM.
3. **Plan**: The state (goal, URL, elements, history, visible text) is serialized to JSON and sent to Groq (`llama-3.3-70b-versatile`). Llama outputs a structured JSON action plan.
4. **Execute**: The backend matches the planned action ID back to the Playwright CSS selectors and runs the specific tool (e.g. `navigate_to_url`, `click`, `send_keys`, `scroll`, `double_click`).
5. **Verify**: A lightweight verification step confirms if the page shifted or inputs were entered correctly.
6. **Timeline Capture**: Playwright takes a page screenshot (`take_screenshot`) and broadcasts the updated session state, logs, and screenshots back to the React UI via WebSockets.

---

## 🛠️ Modular Browser Tools

Actions are decoupled into separate modular components under `backend/app/browser/tools/`:
- `navigate_to_url`: Directs viewport page.
- `click`: Selector-based element click.
- `click_on_screen`: Coordinate-based mouse click.
- `send_keys`: Focuses and inputs text.
- `scroll`: Page scrolling.
- `double_click`: Selector or coordinate double click.
- `take_screenshot`: Captures current screen buffer.
