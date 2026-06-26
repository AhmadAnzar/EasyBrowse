# EasyBrowse - Website Automation Agent (Assignment 04)

EasyBrowse is an intelligent, autonomous website automation agent powered by Playwright and Llama 3.3. It takes natural language goals, plans its browser actions dynamically, and executes them step-by-step, providing real-time feedback through an interactive dashboard UI or terminal CLI.

##  Features

- **Autonomous Agent Loop**: Observe -> Extract interactive DOM -> Plan -> Execute -> Verify -> Capture Screenshot.
- **Core Browser Actions**: Supports `navigate_to_url`, `click`, `click_on_screen`, `send_keys`, `scroll`, `double_click`, and `take_screenshot`.
- **Interactive Dashboard**: A React frontend featuring real-time WebSocket state streaming, timeline screenshots, live console logs, and preset mission templates.
- **User Intervention Chat**: Seamless agent pause and recovery mechanism to ask users for guidance when plan confidence is low.
- **Python CLI Runner**: Execute web automation goals directly from your terminal.

---

##  Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup
1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Playwright browser engines:
   ```bash
   playwright install chromium
   ```
5. Configure environment variables. Create a `.env` file inside `backend/` and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   PLAYWRIGHT_HEADLESS=false
   ```
6. Run the backend development server:
   ```bash
   python run.py
   ```

### 2. Frontend Setup
1. Open another terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run the frontend development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173`.

---

##  Usage

### Interactive Web Dashboard
1. Select one of the **Quick Presets** (e.g., "Shadcn Form Submission" to auto-fill the Name and Description fields) or enter your own custom goal.
2. Click **LAUNCH AGENT** to start the mission.
3. Observe the live browser screen timeline, logs, and success outcomes directly in the UI.

### Python CLI Runner
To run the agent directly from the command line, run the following command from the `backend/` directory:
```bash
# Windows
.\.venv\Scripts\python cli.py --goal "Identify Name and Description input fields, type values, and submit." --url "https://ui.shadcn.com/docs/forms/react-hook-form"
```
