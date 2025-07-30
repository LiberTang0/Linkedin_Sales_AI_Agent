from __future__ import annotations

import time
from typing import List

from playwright.sync_api import Page, sync_playwright


class LinkedInBrowser:
    """Lightweight Playwright wrapper for LinkedIn actions."""

    def __init__(self, email: str, password: str, *, headless: bool = True):
        self.email = email
        self.password = password
        self.headless = headless

        self._playwright = None
        self._browser = None
        self.page: Page | None = None

    # ---------------------------------------------------------------------
    # Context-manager helpers
    # ---------------------------------------------------------------------
    def __enter__(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        # Create context with a realistic desktop Chrome UA
        context = self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        self.page = context.new_page()
        self._context = context  # Save for cleanup
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def login(self) -> None:
        """Sign into LinkedIn."""
        assert self.page, "Browser not initialised"

        self.page.goto("https://www.linkedin.com/login")
        # Slow typing to appear human
        self.page.type("input#username", self.email, delay=50)
        self.page.type("input#password", self.password, delay=50)
        self.page.click("button[type='submit']")
        # Wait until redirected to the feed or we time-out after 10 seconds
        self.page.wait_for_load_state("networkidle")
        if "feed" not in self.page.url:
            raise RuntimeError("LinkedIn login failed – check credentials or 2FA settings.")

    # ------------------------------------------------------------------
    # Search helpers
    # ------------------------------------------------------------------
    def search_profiles(self, query: str, max_results: int = 10) -> List[str]:
        """Return a list of profile URLs for the given keyword search."""
        assert self.page
        self.page.goto(
            f"https://www.linkedin.com/search/results/people/?keywords={query}&origin=GLOBAL_SEARCH_HEADER"
        )
        self.page.wait_for_selector("div.search-results-container")

        # Collect anchors that contain profile links
        anchors = self.page.eval_on_selector_all(
            "a.app-aware-link[href*='linkedin.com/in/']",
            "els => els.map(e => e.href)",
        )
        deduped: List[str] = []
        for url in anchors:
            if url not in deduped:
                deduped.append(url)
            if len(deduped) >= max_results:
                break
        return deduped

    # ------------------------------------------------------------------
    # Outreach helpers
    # ------------------------------------------------------------------
    def connect_with_profile(self, profile_url: str, message: str = "") -> bool:
        """Send a connection request (with an optional personalised note)."""
        assert self.page
        self.page.goto(profile_url)
        try:
            self.page.wait_for_selector("button:has-text('Connect')", timeout=8000)
            self.page.click("button:has-text('Connect')")
        except Exception:
            # Already connected or button missing
            return False

        # Optionally add a note if popup appears
        time.sleep(1)  # Small delay for dialog
        try:
            self.page.click("button:has-text('Add a note')", timeout=3000)
            if message:
                self.page.fill("textarea[name='message']", message)
            self.page.click("button:has-text('Send')")
        except Exception:
            # No dialog – LinkedIn might have sent request directly
            pass
        return True

    def send_message(self, profile_url: str, message: str) -> bool:
        """Send an inbox message to an already-connected profile."""
        assert self.page
        self.page.goto(profile_url)
        try:
            self.page.click("button.message-anywhere-button")
            self.page.wait_for_selector("div.msg-form__contenteditable")
            self.page.fill("div.msg-form__contenteditable", message)
            self.page.click("button.msg-form__send-button")
        except Exception:
            return False
        return True 