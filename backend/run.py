import os
import sys
import asyncio

# Set PYTHONPATH so child worker processes automatically run sitecustomize.py
backend_dir = os.path.abspath(os.path.dirname(__file__))
os.environ["PYTHONPATH"] = backend_dir + os.path.pathsep + os.environ.get("PYTHONPATH", "")

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
