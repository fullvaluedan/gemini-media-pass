import os
import shutil
import platform
from typing import Optional

DEFAULT_BRIDGE_URL = "http://127.0.0.1:8000/v1/chat/completions"

def get_bridge_url() -> str:
    """Returns the bridge URL from environment variable or default."""
    return os.environ.get("BRIDGE_URL", DEFAULT_BRIDGE_URL)

def find_agy_binary() -> Optional[str]:
    """
    Locates the Google Antigravity (agy) executable across Windows, macOS, and Linux.
    Returns the resolved path or None if not found.
    """
    # 1. Check explicit environment override
    if env_path := os.environ.get("AGY_PATH"):
        if os.path.isfile(env_path):
            return env_path

    # 2. Check system PATH
    bin_name = "agy.exe" if platform.system() == "Windows" else "agy"
    if path_bin := shutil.which(bin_name) or shutil.which("agy"):
        return path_bin

    # 3. Check OS-specific default installation paths
    system = platform.system()
    candidates = []

    if system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        user_profile = os.environ.get("USERPROFILE", "")
        if local_app_data:
            candidates.append(os.path.join(local_app_data, "agy", "bin", "agy.exe"))
        if user_profile:
            candidates.append(os.path.join(user_profile, "AppData", "Local", "agy", "bin", "agy.exe"))
    elif system == "Darwin":  # macOS
        home = os.path.expanduser("~")
        candidates.extend([
            os.path.join(home, "Library", "Application Support", "agy", "bin", "agy"),
            os.path.join(home, ".local", "bin", "agy"),
            "/usr/local/bin/agy",
            "/opt/homebrew/bin/agy",
        ])
    else:  # Linux
        home = os.path.expanduser("~")
        candidates.extend([
            os.path.join(home, ".local", "bin", "agy"),
            "/usr/local/bin/agy",
            "/usr/bin/agy",
        ])

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    return None
