import pytest

from gemini_media_pass_mcp import runner


@pytest.fixture(autouse=True)
def fresh_agy_ping():
    """Every test starts with no cached agy ping."""
    runner._last_ping_ok = 0.0
    yield
    runner._last_ping_ok = 0.0
