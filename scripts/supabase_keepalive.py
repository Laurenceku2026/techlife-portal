"""
Ping one or more Supabase free-tier projects so they are not auto-paused for inactivity.

Configure via env (GitHub Actions secrets):

  # Techlife-suite (hmvwgqcbwbdsfppycxkt)
  SUPABASE_SUITE_URL=https://hmvwgqcbwbdsfppycxkt.supabase.co
  SUPABASE_SUITE_ANON_KEY=sb_publishable_...

  # Techlife-stock-quant (wglfpwlqesjrxonfaaeb)
  SUPABASE_STOCK_URL=https://wglfpwlqesjrxonfaaeb.supabase.co
  SUPABASE_STOCK_ANON_KEY=sb_publishable_...

Any project missing URL or key is skipped. Exit code 1 if a configured project fails.
"""
from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request


TARGETS = (
    ("Techlife-suite", "SUPABASE_SUITE_URL", "SUPABASE_SUITE_ANON_KEY"),
    ("Techlife-stock-quant", "SUPABASE_STOCK_URL", "SUPABASE_STOCK_ANON_KEY"),
)


def _ping(name: str, url: str, anon_key: str) -> None:
    base = url.rstrip("/")
    # Auth health is a lightweight authenticated-ish request that counts as project activity.
    endpoint = f"{base}/auth/v1/health"
    req = urllib.request.Request(
        endpoint,
        headers={
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}",
            "User-Agent": "techlife-supabase-keepalive/1.0",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        status = resp.getcode()
        body = resp.read(200).decode("utf-8", errors="replace")
    if status >= 400:
        raise RuntimeError(f"{name}: HTTP {status} body={body[:120]!r}")
    print(f"OK  {name}: {endpoint} -> {status}")


def main() -> int:
    failures = 0
    configured = 0
    for name, url_key, anon_key_name in TARGETS:
        url = (os.getenv(url_key) or "").strip()
        anon = (os.getenv(anon_key_name) or "").strip()
        if not url and not anon:
            print(f"SKIP {name}: secrets {url_key}/{anon_key_name} not set")
            continue
        if not url or not anon:
            print(f"FAIL {name}: incomplete secrets ({url_key} / {anon_key_name})")
            failures += 1
            continue
        configured += 1
        try:
            _ping(name, url, anon)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, RuntimeError) as exc:
            print(f"FAIL {name}: {exc}")
            failures += 1

    if configured == 0:
        print("FAIL: no Supabase targets configured")
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
