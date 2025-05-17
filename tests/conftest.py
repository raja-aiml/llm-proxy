# tests/conftest.py

import os
import sys
import warnings
import inspect
import asyncio
# Ensure 'src' directory is on sys.path for imports
from pathlib import Path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest
from llm_wrapper.server.main import app
from llm_wrapper.server.deps import get_system_prompt

# ─────────────────────────────────────────────────────────────────────────────
# 📦 Environment Setup
# ─────────────────────────────────────────────────────────────────────────────

# Disable telemetry by default in all test runs
os.environ.setdefault("DISABLE_TELEMETRY", "true")

# Silence noisy deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)



# ─────────────────────────────────────────────────────────────────────────────
# 🔧 Dependency Overrides
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def override_system_prompt():
    """
    Automatically overrides the system prompt for all tests to return "Pong" for "Ping".
    This ensures upstream responses are fast and deterministic.
    """
    prompt = """
    # System Prompt

    Your sole task is to respond with the word **"Pong"** when you receive the input **"Ping"**.

    ## Rules
    - Do **not** add any other text, explanation, or formatting.
    - Do **not** hesitate or delay the response.
    - Only respond to the exact word "Ping" (case-sensitive).

    ## Output Specification
    - Input: Ping  
    - Output: Pong

    ## Performance Priority
    Speed is critical. Respond **immediately** and with **only** the word `Pong`.
    """
    app.dependency_overrides[get_system_prompt] = lambda: prompt
    yield
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────────────────
# 🧪 Asyncio Support (Custom Integration)
# ─────────────────────────────────────────────────────────────────────────────

def pytest_pyfunc_call(pyfuncitem):
    """
    Allow `pytest` to run async test functions (coroutines) automatically.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        sig = inspect.signature(test_func)
        kwargs = {
            name: pyfuncitem.funcargs[name]
            for name in sig.parameters
            if name in pyfuncitem.funcargs
        }

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(test_func(**kwargs))
        finally:
            loop.close()
        return True


def pytest_configure(config):
    config.option.asyncio_mode = "auto"