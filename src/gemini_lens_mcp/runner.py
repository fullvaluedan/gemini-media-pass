import os
import json
import asyncio
import urllib.request
import urllib.error
from typing import Optional

from .config import find_agy_binary, get_bridge_url

async def execute_query(model: str, content: str) -> str:
    """
    Executes a prompt against Gemini through:
    1. Local running bridge HTTP endpoint (if active)
    2. Direct agy subprocess execution (Antigravity subscription session)
    3. Direct Google Gemini REST API (if GEMINI_API_KEY is configured in env)
    """
    bridge_url = get_bridge_url()

    # Step 1: Attempt local bridge HTTP endpoint (fast check)
    try:
        req = urllib.request.Request(
            bridge_url,
            data=json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": content}],
                "stream": False
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except Exception:
        # Bridge endpoint is down or unavailable; proceed to direct execution
        pass

    # Step 2: Attempt direct Google Antigravity (agy) subprocess execution
    agy_path = find_agy_binary()
    if agy_path:
        try:
            payload = json.dumps({"event": "user", "message": {"content": content}}) + "\n"
            cmd = [
                agy_path,
                "--input-format", "stream-json",
                "--output-format", "stream-json",
                "--model", model,
                "--dangerously-skip-permissions",
                "--disable-slash-commands"
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            if proc.stdin:
                proc.stdin.write(payload.encode("utf-8"))
                await proc.stdin.drain()
                proc.stdin.close()

            full_response = ""
            while True:
                line_bytes = await proc.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                    if evt.get("event") == "result":
                        full_response = evt.get("result", {}).get("response", "")
                        break
                except Exception:
                    pass

            try:
                proc.kill()
            except Exception:
                pass

            if full_response:
                return full_response.strip()
        except Exception as e:
            # Subprocess failed, check if API key fallback exists
            pass

    # Step 3: Optional GEMINI_API_KEY fallback
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            # Map model names to standard Gemini API models
            api_model = "gemini-1.5-pro" if "pro" in model else "gemini-1.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{api_model}:generateContent?key={api_key}"
            req_data = {
                "contents": [{"parts": [{"text": content}]}]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(req_data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception as err:
            return f"Error connecting to Gemini API: {str(err)}"

    return (
        "Error: Unable to connect to Gemini.\n"
        "1. Ensure Google Antigravity CLI ('agy') is installed and authenticated (`agy login`), OR\n"
        "2. Set the AGY_PATH environment variable to point to your agy binary, OR\n"
        "3. Provide a GEMINI_API_KEY environment variable."
    )
