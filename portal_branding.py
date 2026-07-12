"""TechLife portal branding assets and mobile home-screen (PWA) hooks."""

from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

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


def inject_mobile_home_screen_meta(*, repo: str = DEFAULT_GITHUB_REPO, ref: str = DEFAULT_GITHUB_REF) -> None:
    """Inject manifest + Apple/Android icons so users can add the app to their home screen."""
    base = brand_cdn_base(repo=repo, ref=ref)
    manifest_url = f"{base}/manifest.webmanifest"
    apple_icon = f"{base}/apple-touch-icon.png"
    favicon = f"{base}/favicon-32.png"
    icon_192 = f"{base}/icon-192.png"

    components.html(
        f"""
        <script>
        (function () {{
            const head = document.head;
            const tags = [
                {{ tag: 'link', rel: 'manifest', href: '{manifest_url}' }},
                {{ tag: 'link', rel: 'apple-touch-icon', sizes: '180x180', href: '{apple_icon}' }},
                {{ tag: 'link', rel: 'icon', type: 'image/png', sizes: '32x32', href: '{favicon}' }},
                {{ tag: 'link', rel: 'icon', type: 'image/png', sizes: '192x192', href: '{icon_192}' }},
                {{ tag: 'meta', name: 'theme-color', content: '#1B3A5F' }},
                {{ tag: 'meta', name: 'apple-mobile-web-app-capable', content: 'yes' }},
                {{ tag: 'meta', name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' }},
                {{ tag: 'meta', name: 'apple-mobile-web-app-title', content: 'TechLife' }},
                {{ tag: 'meta', name: 'application-name', content: 'TechLife DFSS' }},
                {{ tag: 'meta', name: 'mobile-web-app-capable', content: 'yes' }},
            ];
            tags.forEach(function (spec) {{
                const key = spec.rel ? 'rel' : 'name';
                const val = spec.rel || spec.name;
                if (head.querySelector(key + '="' + val + '"')) return;
                const el = document.createElement(spec.tag);
                Object.keys(spec).forEach(function (k) {{
                    if (k !== 'tag') el.setAttribute(k, spec[k]);
                }});
                head.appendChild(el);
            }});
        }})();
        </script>
        """,
        height=0,
        width=0,
    )
