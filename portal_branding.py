"""TechLife portal branding assets and mobile home-screen (PWA) hooks."""

from __future__ import annotations

import json
import os
import shutil
import urllib.parse
from pathlib import Path
from typing import Callable

import streamlit as st
import streamlit.components.v1 as components

APP_DISPLAY_NAME = "DFSS"
DEFAULT_APP_BASE_URL = "https://techlife-app.streamlit.app"
PATCH_MARKER = "<!-- dfss-brand-head -->"

BRAND_DIR = Path(__file__).resolve().parent / "assets" / "brand"
STATIC_BRAND_DIR = Path(__file__).resolve().parent / "static" / "brand"
LOCAL_ICON_48 = BRAND_DIR / "icon-48.png"
LOCAL_ICON_192 = BRAND_DIR / "icon-192.png"
LOCAL_ICON_512 = BRAND_DIR / "icon-512.png"
LOCAL_APPLE_ICON = BRAND_DIR / "apple-touch-icon.png"
LOCAL_FAVICON_32 = BRAND_DIR / "favicon-32.png"

DEFAULT_GITHUB_REPO = "Laurenceku2026/techlife-portal"
DEFAULT_GITHUB_REF = "main"


def local_page_icon() -> str:
    """Path for st.set_page_config(page_icon=...)."""
    if LOCAL_ICON_48.is_file():
        return str(LOCAL_ICON_48)
    return "🔧"


def brand_cdn_base(*, repo: str = DEFAULT_GITHUB_REPO, ref: str = DEFAULT_GITHUB_REF) -> str:
    return f"https://cdn.jsdelivr.net/gh/{repo}@{ref}/assets/brand"


def _read_app_base_url() -> str:
    env_url = os.environ.get("APP_BASE_URL", "").strip()
    if env_url:
        return env_url.rstrip("/")

    secrets_path = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"
    if secrets_path.is_file():
        try:
            text = secrets_path.read_text(encoding="utf-8")
        except OSError:
            text = ""
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            if key.strip() == "APP_BASE_URL":
                parsed = value.strip().strip('"').strip("'")
                if parsed:
                    return parsed.rstrip("/")
    return DEFAULT_APP_BASE_URL


def _build_pwa_manifest(*, icon_base: str, app_base_url: str) -> dict:
    start_url = f"{app_base_url.rstrip('/')}/"
    return {
        "name": APP_DISPLAY_NAME,
        "short_name": APP_DISPLAY_NAME,
        "description": "AI-powered DFSS tools: VOC feasibility, DQA, tolerance simulation, and failure analysis.",
        "start_url": start_url,
        "scope": start_url,
        "display": "standalone",
        "orientation": "portrait-primary",
        "background_color": "#1B3A5F",
        "theme_color": "#1B3A5F",
        "lang": "zh-CN",
        "icons": [
            {
                "src": f"{icon_base}/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": f"{icon_base}/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": f"{icon_base}/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable",
            },
        ],
    }


def _manifest_data_uri(manifest: dict) -> str:
    payload = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    return "data:application/manifest+json;charset=utf-8," + urllib.parse.quote(payload)


def _write_static_manifest(manifest: dict) -> None:
    STATIC_BRAND_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = STATIC_BRAND_DIR / "manifest.webmanifest"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def apply_streamlit_head_patch(*, repo: str = DEFAULT_GITHUB_REPO, ref: str = DEFAULT_GITHUB_REF) -> None:
    """Patch Streamlit index.html and favicon so Chrome install uses DFSS branding."""
    if os.environ.get("DFSS_HEAD_PATCHED") == "1":
        return

    try:
        import streamlit

        static_dir = Path(streamlit.__file__).resolve().parent / "static"
        index_path = static_dir / "index.html"
        favicon_path = static_dir / "favicon.png"
        if not index_path.is_file():
            return

        icon_base = brand_cdn_base(repo=repo, ref=ref)
        app_base_url = _read_app_base_url()
        manifest = _build_pwa_manifest(icon_base=icon_base, app_base_url=app_base_url)
        _write_static_manifest(manifest)
        manifest_href = _manifest_data_uri(manifest)

        html = index_path.read_text(encoding="utf-8")
        if PATCH_MARKER not in html:
            head_block = f"""
    {PATCH_MARKER}
    <link rel="manifest" href="{manifest_href}" />
    <link rel="icon" type="image/png" sizes="192x192" href="{icon_base}/icon-192.png" />
    <link rel="icon" type="image/png" sizes="32x32" href="{icon_base}/favicon-32.png" />
    <link rel="apple-touch-icon" sizes="180x180" href="{icon_base}/apple-touch-icon.png" />
    <meta name="theme-color" content="#1B3A5F" />
    <meta name="application-name" content="{APP_DISPLAY_NAME}" />
    <meta name="apple-mobile-web-app-title" content="{APP_DISPLAY_NAME}" />
    <meta name="mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
"""
            html = html.replace(
                '<link rel="shortcut icon" href="./favicon.png" />',
                f'{head_block}\n    <link rel="shortcut icon" href="{icon_base}/favicon-32.png" />',
            )
            html = html.replace("<title>Streamlit</title>", f"<title>{APP_DISPLAY_NAME}</title>")
            index_path.write_text(html, encoding="utf-8")

        icon_source = LOCAL_ICON_192 if LOCAL_ICON_192.is_file() else LOCAL_ICON_512
        if icon_source.is_file():
            shutil.copy2(icon_source, favicon_path)

        os.environ["DFSS_HEAD_PATCHED"] = "1"
    except Exception:
        return


def inject_mobile_home_screen_meta(*, repo: str = DEFAULT_GITHUB_REPO, ref: str = DEFAULT_GITHUB_REF) -> None:
    """Keep a lightweight runtime refresh for browsers that read head tags after reruns."""
    apply_streamlit_head_patch(repo=repo, ref=ref)
    icon_base = brand_cdn_base(repo=repo, ref=ref)
    app_name = APP_DISPLAY_NAME
    manifest = _build_pwa_manifest(icon_base=icon_base, app_base_url=_read_app_base_url())
    manifest_href = _manifest_data_uri(manifest)

    components.html(
        f"""
        <script>
        (function () {{
            let doc;
            try {{ doc = window.parent.document; }} catch (err) {{ doc = document; }}
            const head = doc.head;
            if (!head) return;
            head.querySelectorAll(
                'link[rel="icon"], link[rel="shortcut icon"], link[rel="apple-touch-icon"], link[rel="manifest"]'
            ).forEach(function (node) {{ node.remove(); }});
            const title = doc.querySelector("title");
            if (title) title.textContent = {json.dumps(app_name)};
            function addTag(spec) {{
                const el = doc.createElement(spec.tag);
                Object.keys(spec).forEach(function (key) {{
                    if (key !== "tag") el.setAttribute(key, spec[key]);
                }});
                head.appendChild(el);
            }}
            addTag({{ tag: "link", rel: "manifest", href: {json.dumps(manifest_href)} }});
            addTag({{ tag: "link", rel: "icon", type: "image/png", sizes: "192x192", href: {json.dumps(icon_base + "/icon-192.png")} }});
            addTag({{ tag: "link", rel: "icon", type: "image/png", sizes: "32x32", href: {json.dumps(icon_base + "/favicon-32.png")} }});
            addTag({{ tag: "link", rel: "apple-touch-icon", sizes: "180x180", href: {json.dumps(icon_base + "/apple-touch-icon.png")} }});
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def render_add_to_home_screen_help(*, translate: Callable[[], dict]):
    """Sidebar help for adding DFSS to the phone home screen across major mobile browsers."""
    text = translate()
    with st.expander(text["add_home_title"], expanded=False):
        st.markdown(text["add_home_intro"])
        st.markdown(text["add_home_ios"])
        st.markdown(text["add_home_android_chrome"])
        st.markdown(text["add_home_edge"])
        st.markdown(text["add_home_xiaomi"])
        st.markdown(text["add_home_huawei"])
        st.markdown(text["add_home_vivo"])
        st.markdown(text["add_home_samsung"])
