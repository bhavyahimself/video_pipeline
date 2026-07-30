"""
Screen Recorder Module
Automated screen recording of websites/apps for "Designed to Trick You" channel.
Uses Playwright to navigate websites and record dark patterns.
"""

import asyncio
from pathlib import Path
from typing import Optional

from rich.console import Console

from config.settings import RECORDINGS_DIR

console = Console()


class WebScreenRecorder:
    """Record screen captures of websites showing dark patterns, UX tricks, etc."""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or RECORDINGS_DIR

    async def record_website(
        self,
        url: str,
        output_name: str,
        actions: list[dict] = None,
        viewport_width: int = 1080,
        viewport_height: int = 1920,
        timeout_ms: int = 30000,
    ) -> Optional[Path]:
        """Record a website interaction.

        Args:
            url: Website URL to record
            output_name: Output filename (without extension)
            actions: List of actions to perform. Each action is a dict:
                {'type': 'click', 'selector': '#button'}
                {'type': 'scroll', 'pixels': 500}
                {'type': 'wait', 'seconds': 2}
                {'type': 'hover', 'selector': '.menu'}
                {'type': 'screenshot', 'name': 'step_1'}
                {'type': 'type', 'selector': '#input', 'text': 'hello'}
            viewport_width: Browser viewport width
            viewport_height: Browser viewport height
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            console.print("[red]✗ Playwright not installed. Run: pip install playwright && playwright install[/]")
            return None

        video_path = self.output_dir / f"{output_name}.webm"
        screenshots_dir = self.output_dir / f"{output_name}_screenshots"
        screenshots_dir.mkdir(exist_ok=True)

        console.print(f"[blue]Recording: {url}[/]")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height},
                record_video_dir=str(self.output_dir),
                record_video_size={"width": viewport_width, "height": viewport_height},
            )

            page = await context.new_page()

            try:
                await page.goto(url, timeout=timeout_ms)
                await page.wait_for_load_state("networkidle", timeout=10000)

                # Initial screenshot
                await page.screenshot(path=str(screenshots_dir / "initial.png"))

                # Execute actions
                if actions:
                    for i, action in enumerate(actions):
                        await self._execute_action(page, action, screenshots_dir, i)

                # Final screenshot
                await page.screenshot(path=str(screenshots_dir / "final.png"))

            except Exception as e:
                console.print(f"[red]✗ Recording error: {e}[/]")

            await context.close()
            await browser.close()

        # Find the recorded video
        videos = list(self.output_dir.glob("*.webm"))
        if videos:
            latest = max(videos, key=lambda p: p.stat().st_mtime)
            target = self.output_dir / f"{output_name}.webm"
            if latest != target:
                latest.rename(target)
            console.print(f"[green]✓ Recorded: {target.name}[/]")
            return target

        console.print("[yellow]⚠ No video file found[/]")
        return None

    async def _execute_action(self, page, action: dict, screenshots_dir: Path, index: int):
        """Execute a single page action."""
        action_type = action.get("type", "")

        if action_type == "click":
            selector = action.get("selector", "")
            await page.click(selector, timeout=5000)
            await asyncio.sleep(0.5)

        elif action_type == "scroll":
            pixels = action.get("pixels", 500)
            await page.evaluate(f"window.scrollBy(0, {pixels})")
            await asyncio.sleep(0.5)

        elif action_type == "wait":
            seconds = action.get("seconds", 1)
            await asyncio.sleep(seconds)

        elif action_type == "hover":
            selector = action.get("selector", "")
            await page.hover(selector, timeout=5000)
            await asyncio.sleep(0.5)

        elif action_type == "screenshot":
            name = action.get("name", f"step_{index}")
            await page.screenshot(path=str(screenshots_dir / f"{name}.png"))

        elif action_type == "type":
            selector = action.get("selector", "")
            text = action.get("text", "")
            await page.fill(selector, text)
            await asyncio.sleep(0.3)

    def record_sync(self, url: str, output_name: str, actions: list[dict] = None, **kwargs) -> Optional[Path]:
        """Synchronous wrapper for record_website."""
        return asyncio.run(self.record_website(url, output_name, actions, **kwargs))

    def capture_dark_pattern(
        self,
        url: str,
        pattern_name: str,
        steps: list[str] = None,
    ) -> dict:
        """Convenience method to capture a specific dark pattern with before/after screenshots.

        Args:
            url: Website URL
            pattern_name: Name of the dark pattern (e.g., "hidden_unsubscribe")
            steps: Human-readable description of what to look for

        Returns:
            Dict with paths to screenshots and video
        """
        screenshots_dir = self.output_dir / f"pattern_{pattern_name}"
        screenshots_dir.mkdir(exist_ok=True)

        result = {
            "pattern_name": pattern_name,
            "url": url,
            "steps": steps or [],
            "video_path": None,
            "screenshots": [],
        }

        video_path = self.record_sync(
            url=url,
            output_name=f"pattern_{pattern_name}",
            actions=[
                {"type": "screenshot", "name": "before"},
                {"type": "scroll", "pixels": 300},
                {"type": "wait", "seconds": 1},
                {"type": "screenshot", "name": "during"},
                {"type": "scroll", "pixels": 500},
                {"type": "wait", "seconds": 1},
                {"type": "screenshot", "name": "after"},
            ],
        )

        result["video_path"] = str(video_path) if video_path else None
        result["screenshots"] = [str(p) for p in screenshots_dir.glob("*.png")]

        return result

