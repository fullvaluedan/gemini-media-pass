"""
Runs gflow without reading "Chrome Safe Storage" from the macOS Keychain.

gflow's fast session check calls `security find-generic-password` for Chrome's key, and macOS answers with a
Keychain prompt on every call. This launcher makes that fast path report failure, so gflow takes its built-in
Playwright fallback, which reads the same saved session without the Keychain.

Run it with gflow's own Python (flow._find_gflow does this): python -I gflow_nokeychain.py <gflow args>
"""

import sys

from gflow_cli.auth import cookies


def _skip_keychain(*_args, **_kwargs):
    raise PermissionError("Keychain read skipped by gemini-media-pass")


cookies._get_chrome_cookies3 = _skip_keychain

from gflow_cli.cli import main  # noqa: E402  (after the patch on purpose)

sys.exit(main())
