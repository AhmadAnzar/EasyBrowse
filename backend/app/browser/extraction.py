from playwright.async_api import Page
from typing import List, Dict, Any

async def extract_interactive_elements(page: Page) -> List[Dict[str, Any]]:
    """
    Executes a JavaScript script in the page context to find all visible,
    enabled, and interactive elements. Assigns each a unique ID.
    """
    js_script = """
    () => {
        const interactiveSelectors = [
            'input:not([type="hidden"])',
            'textarea',
            'button',
            'select',
            'a[href]',
            '[role="button"]',
            '[role="link"]',
            '[role="checkbox"]',
            '[role="radio"]'
        ];
        
        const elements = document.querySelectorAll(interactiveSelectors.join(','));
        const extracted = [];
        
        function getUniqueSelector(el) {
            if (el.id) {
                return `#${CSS.escape(el.id)}`;
            }
            
            // Try name attribute
            if (el.name) {
                const nameSelector = `${el.tagName.toLowerCase()}[name="${CSS.escape(el.name)}"]`;
                if (document.querySelectorAll(nameSelector).length === 1) {
                    return nameSelector;
                }
            }
            
            // Generate path-based selector
            const path = [];
            let current = el;
            while (current && current.nodeType === Node.ELEMENT_NODE) {
                let selector = current.tagName.toLowerCase();
                
                // If it has classes, append them (excluding very dynamic looking classes)
                if (current.className && typeof current.className === 'string') {
                    const classes = current.className.split(/\\s+/).filter(c => c && !c.includes(':') && c.length < 25);
                    if (classes.length > 0) {
                        selector += '.' + classes.join('.');
                    }
                }
                
                // Find sibling index
                let sibling = current;
                let sibIndex = 1;
                while (sibling = sibling.previousElementSibling) {
                    if (sibling.tagName === current.tagName) {
                        sibIndex++;
                    }
                }
                
                // Only add nth-of-type if there are siblings of the same tag
                let hasSameTagSiblings = false;
                let next = current.nextElementSibling;
                while (next) {
                    if (next.tagName === current.tagName) {
                        hasSameTagSiblings = true;
                        break;
                    }
                    next = next.nextElementSibling;
                }
                if (sibIndex > 1 || hasSameTagSiblings) {
                    selector += `:nth-of-type(${sibIndex})`;
                }
                
                path.unshift(selector);
                
                // Stop at body or form if they have unique specifiers
                if (current.tagName === 'BODY' || (current.tagName === 'FORM' && current.id)) {
                    break;
                }
                
                current = current.parentNode;
            }
            return path.join(' > ');
        }
        
        function getLabel(el) {
            // 1. Check for associated <label>
            if (el.id) {
                const label = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
                if (label && label.innerText) return label.innerText.trim();
            }
            
            // 2. Check parent <label>
            let parent = el.parentElement;
            while (parent) {
                if (parent.tagName === 'LABEL') {
                    return parent.innerText.trim();
                }
                parent = parent.parentElement;
            }
            
            // 3. Check aria attributes
            if (el.getAttribute('aria-label')) {
                return el.getAttribute('aria-label').trim();
            }
            const labelledBy = el.getAttribute('aria-labelledby');
            if (labelledBy) {
                const labelEl = document.getElementById(labelledBy);
                if (labelEl && labelEl.innerText) return labelEl.innerText.trim();
            }
            
            // 4. Text content or attributes
            const textContent = el.innerText || el.textContent;
            if (textContent && textContent.trim()) {
                return textContent.trim();
            }
            
            if (el.tagName === 'INPUT' && (el.type === 'submit' || el.type === 'button')) {
                return el.value || '';
            }
            
            return '';
        }
        
        function isVisible(el) {
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0) {
                return false;
            }
            
            const rect = el.getBoundingClientRect();
            // Allow offscreen elements that are within reasonable range, but prioritize viewport
            const inViewport = (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
            
            // Element must have some width and height
            return rect.width > 0 && rect.height > 0;
        }
        
        elements.forEach(el => {
            if (isVisible(el) && !el.disabled) {
                extracted.push({
                    tag: el.tagName.toLowerCase(),
                    selector: getUniqueSelector(el),
                    label: getLabel(el).substring(0, 80), // Limit label size
                    placeholder: el.placeholder || el.getAttribute('placeholder') || '',
                    role: el.getAttribute('role') || el.type || el.tagName.toLowerCase()
                });
            }
        });
        
        return extracted;
    }
    """
    
    try:
        raw_elements = await page.evaluate(js_script)
        # Assign numeric IDs sequential starting at 1
        elements_with_ids = []
        for index, item in enumerate(raw_elements, start=1):
            item["id"] = index
            elements_with_ids.append(item)
        return elements_with_ids
    except Exception as e:
        print(f"Error in DOM extraction JS: {e}")
        return []
