"""LEVEL 4/5 — rendered browser fallback (Playwright).

Opens the URL, lets JavaScript execute, inspects the rendered DOM.
HARD STOP (never bypassed): CAPTCHA, access-denied pages, login walls,
anti-bot challenges, rate-limit pages. On any of these the render is
abandoned and the caller falls through to graceful failure.

No stealth plugins, no proxy rotation, no cookie reuse.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

RENDER_TIMEOUT_MS = 30000

# Any of these in title/body/URL means: stop, do not attempt to defeat it.
_BLOCK_MARKERS = (
    "captcha",
    "robot check",
    "are you a robot",
    "access denied",
    "accessdenied",
    "request blocked",
    "verify you are human",
    "unusual traffic",
    "perimeterx",
    "datadome",
    "cloudflare challenge",
    "attention required",
)


def available() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def _is_blocked(page) -> str | None:
    """Return a reason if the page shows an access barrier, else None."""
    try:
        url = (page.url or "").lower()
        if any(seg in url for seg in ("/login", "/signin", "/auth/", "/captcha")):
            if page.query_selector('input[type="password"]'):
                return "login required"
        title = (page.title() or "").lower()
        body_text = ""
        try:
            body_text = (page.inner_text("body") or "").lower()[:4000]
        except Exception:
            pass
        haystack = f"{title}\n{body_text}"
        for marker in _BLOCK_MARKERS:
            if marker in haystack:
                return f"anti-bot barrier detected ({marker})"
    except Exception as e:
        logger.debug("Block check failed: %s", str(e)[:80])
    return None


def render(url: str, wait_selector: str | None = None,
           timeout_ms: int = RENDER_TIMEOUT_MS) -> dict:
    """Render a page and return {html, blocked, reason}.

    blocked=True means extraction must STOP for this source.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"html": None, "blocked": True,
                "reason": "Browser automation not installed."}

    browser = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                )
            )
            try:
                response = page.goto(url, wait_until="domcontentloaded",
                                     timeout=timeout_ms)
            except Exception as e:
                return {"html": None, "blocked": False,
                        "reason": f"Page load failed: {str(e)[:120]}"}
            if response is not None and response.status in (403, 404, 429):
                return {"html": None, "blocked": True,
                        "reason": f"HTTP {response.status} on rendered page."}

            blocked_reason = _is_blocked(page)
            if blocked_reason:
                return {"html": None, "blocked": True, "reason": blocked_reason}

            if wait_selector:
                try:
                    page.wait_for_selector(wait_selector, timeout=12000)
                except Exception:
                    pass
            else:
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass

            blocked_reason = _is_blocked(page)
            if blocked_reason:
                return {"html": None, "blocked": True, "reason": blocked_reason}
            return {"html": page.content(), "blocked": False, "reason": ""}
    except Exception as e:
        return {"html": None, "blocked": False,
                "reason": f"Browser failed: {str(e)[:150]}"}
    finally:
        try:
            if browser:
                browser.close()
        except Exception:
            pass
