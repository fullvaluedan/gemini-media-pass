import os
import shutil
import platform
from typing import Optional

def load_dotenv():
    """Lightweight zero-dependency .env file loader."""
    candidates = [
        ".env",
        os.path.join(os.getcwd(), ".env"),
        os.path.expanduser("~/.gemini_media_pass.env")
    ]
    for env_path in candidates:
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip().strip('"').strip("'")
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass

load_dotenv()

def get_bridge_url() -> str:
    """The local bridge URL, or "" when BRIDGE_URL is not set. Off by default: any process listening on that
    port would receive every prompt. Example: BRIDGE_URL=http://127.0.0.1:8000/v1/chat/completions"""
    return os.environ.get("BRIDGE_URL", "").strip()

def get_default_tier() -> str:
    """The default model tier ('flash' or 'pro'). Defaults to 'flash' for 97% cost savings."""
    tier = os.environ.get("GMP_DEFAULT_TIER", "flash").strip().lower()
    return "pro" if tier == "pro" else "flash"

def get_video_tier() -> str:
    """The model tier for video analysis. Defaults to GMP_VIDEO_TIER, or falls back to GMP_DEFAULT_TIER ('flash')."""
    tier = os.environ.get("GMP_VIDEO_TIER", "").strip().lower()
    return "pro" if tier == "pro" else ("flash" if tier == "flash" else get_default_tier())

def resolve_model_name(tier: Optional[str] = None, default_to_video: bool = False) -> str:
    """
    Resolves the internal model identifier string ('gemini-3.8-flash-high' or 'gemini-3.1-pro-high')
    based on the requested tier ('flash' or 'pro') or environment settings.
    """
    t = (tier.strip().lower() if tier else None)
    if not t:
        t = get_video_tier() if default_to_video else get_default_tier()

    if t == "pro":
        return "gemini-3.1-pro-high"
    return "gemini-3.8-flash-high"

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
