"""
app.py - Hugging Face Spaces entry point
HF Spaces looks for app.py at the repo root.
This shim sets up paths and delegates to export-agent/app.py.
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AGENT_DIR = ROOT / "export-agent"

sys.path.insert(0, str(AGENT_DIR))
sys.path.insert(0, str(AGENT_DIR / "src"))

os.chdir(AGENT_DIR)

exec(open(AGENT_DIR / "app.py").read())
