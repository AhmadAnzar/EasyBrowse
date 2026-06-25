import sys
import asyncio

# This will run automatically on startup for ANY python process spawned in this environment
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("Sitecustomize: Successfully configured WindowsProactorEventLoopPolicy")
    except Exception as e:
        print(f"Sitecustomize: Failed to set loop policy: {e}")
