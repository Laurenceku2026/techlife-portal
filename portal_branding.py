"""TechLife portal branding assets and mobile home-screen (PWA) hooks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import streamlit as st
import streamlit.components.v1 as components

APP_DISPLAY_NAME = "DFSS"

BRAND_DIR = Path(__file__).resolve().parent / "assets" / "brand"
LOCAL_ICON_48 = BRAND_DIR / "icon-48.png"
LOCAL_ICON_512 = BRAND_DIR / "icon-512.png"

DEFAULT_GITHUB_REPO = "Laurenceku2026/techlife-portal"
DEFAULT_GITHUB_REF = "main"


def local_page_icon() -> str:
    """Path for st.set_page_config(page_icon=...)."""
    if LOCAL_ICON_48.is_file():
        return str(LOCAL_ICON_48)
    return "🔧"


def brand_cdn_base(*, repo: str = DEFAULT_GITHUB_REPO, ref: str = DEFAULT_GITHUB_REF) -> str:
    return f"https://cdn.jsdelivr.net/gh/{repo}@{ref}/assets/brand"


def _pwa_manifest_json(*, icon_base: str, start_url: str, scope: str) -> str:
    manifest = {
        "name": APP_DISPLAY_NAME,
        "short_name": APP_DISPLAY_NAME,
        "description": "AI-powered DFSS tools: VOC feasibility, DQA, tolerance simulation, and failure analysis.",
        "start_url": start_url,
        "scope": scope,
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
    return json.dumps(manifest, ensure_ascii=False)


def inject_mobile_home_screen_meta(*, repo: str = DEFAULT_GITHUB_REPO, ref: str = DEFAULT_GITHUB_REF) -> None:
    """Inject manifest + icons into the Streamlit page head (parent document) for PWA install."""
    cdn_base = brand_cdn_base(repo=repo, ref=ref)
    manifest_json = _pwa_manifest_json(
        icon_base=cdn_base,
        start_url="/",
        scope="/",
    )
    app_name = APP_DISPLAY_NAME

    components.html(
        f"""
        <script>
        (function () {{
            let doc;
            try {{
                doc = window.parent.document;
            }} catch (err) {{
                doc = document;
            }}
            const head = doc.head;
            if (!head) return;

            const loc = window.parent.location;
            const path = (loc.pathname || "/").replace(/\\/$/, "");
            const staticBase = loc.origin + (path || "") + "/app/static/brand";
            const cdnBase = {json.dumps(cdn_base)};
            const appName = {json.dumps(app_name)};

            head.querySelectorAll(
                'link[rel="icon"], link[rel="shortcut icon"], link[rel="apple-touch-icon"], link[rel="manifest"]'
            ).forEach(function (node) {{ node.remove(); }});

            const title = doc.querySelector("title");
            if (title) title.textContent = appName;

            function addTag(spec) {{
                const el = doc.createElement(spec.tag);
                Object.keys(spec).forEach(function (key) {{
                    if (key !== "tag") el.setAttribute(key, spec[key]);
                }});
                head.appendChild(el);
                return el;
            }}

            const iconCandidates = [
                staticBase + "/icon-192.png",
                cdnBase + "/icon-192.png",
            ];
            const appleCandidates = [
                staticBase + "/apple-touch-icon.png",
                cdnBase + "/apple-touch-icon.png",
            ];
            const faviconCandidates = [
                staticBase + "/favicon-32.png",
                cdnBase + "/favicon-32.png",
            ];

            addTag({{ tag: "link", rel: "icon", type: "image/png", sizes: "192x192", href: iconCandidates[0] }});
            addTag({{ tag: "link", rel: "icon", type: "image/png", sizes: "32x32", href: faviconCandidates[0] }});
            addTag({{ tag: "link", rel: "apple-touch-icon", sizes: "180x180", href: appleCandidates[0] }});

            const manifest = {manifest_json};
            manifest.start_url = loc.href;
            manifest.scope = loc.origin + (path || "") + "/";
            manifest.icons = [
                {{ src: staticBase + "/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" }},
                {{ src: cdnBase + "/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" }},
                {{ src: staticBase + "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" }},
                {{ src: cdnBase + "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" }},
                {{ src: cdnBase + "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" }},
            ];

            const blob = new Blob([JSON.stringify(manifest)], {{ type: "application/manifest+json" }});
            const manifestUrl = URL.createObjectURL(blob);
            addTag({{ tag: "link", rel: "manifest", href: manifestUrl }});

            [
                {{ tag: "meta", name: "theme-color", content: "#1B3A5F" }},
                {{ tag: "meta", name: "apple-mobile-web-app-capable", content: "yes" }},
                {{ tag: "meta", name: "apple-mobile-web-app-status-bar-style", content: "black-translucent" }},
                {{ tag: "meta", name: "apple-mobile-web-app-title", content: appName }},
                {{ tag: "meta", name: "application-name", content: appName }},
                {{ tag: "meta", name: "mobile-web-app-capable", content: "yes" }},
                {{ tag: "meta", name: "msapplication-TileColor", content: "#1B3A5F" }},
                {{ tag: "meta", name: "msapplication-TileImage", content: staticBase + "/icon-512.png" }},
            ].forEach(addTag);
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
