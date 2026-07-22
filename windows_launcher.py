from __future__ import annotations
import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

def bundled_path(name: str) -> str:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return str(root / name)

def configure_tools() -> None:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    os.environ["PATH"] = str(root) + os.pathsep + os.environ.get("PATH", "")

def open_browser() -> None:
    time.sleep(3)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    configure_tools()
    print("=" * 52)
    print("StreamScout draait op http://127.0.0.1:8000")
    print("Laat dit venster open tijdens het analyseren.")
    print("=" * 52)
    threading.Thread(target=open_browser, daemon=True).start()
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info")
