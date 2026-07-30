"""
Thumbnail Generator Module
Auto-generates thumbnails for YouTube Shorts using Pillow.
Template-based system with per-channel styling.
"""

from pathlib import Path
from typing import Optional

from rich.console import Console

from config.settings import THUMBNAILS_DIR, CHANNELS

console = Console()


# ── Color Palettes per Channel ──────────────────────────────────────────────

CHANNEL_STYLES = {
    "taylor_sabrina": {
        "bg_color": (20, 20, 30),
        "text_color": (255, 255, 255),
        "accent_color": (200, 50, 100),
        "font_size_title": 80,
        "font_size_subtitle": 45,
    },
    "how_they_went_broke": {
        "bg_color": (10, 10, 10),
        "text_color": (255, 255, 255),
        "accent_color": (220, 50, 50),
        "font_size_title": 85,
        "font_size_subtitle": 40,
    },
    "why_this_place_failed": {
        "bg_color": (30, 25, 20),
        "text_color": (255, 250, 240),
        "accent_color": (180, 140, 80),
        "font_size_title": 80,
        "font_size_subtitle": 42,
    },
    "one_decision": {
        "bg_color": (15, 15, 25),
        "text_color": (255, 255, 255),
        "accent_color": (80, 150, 255),
        "font_size_title": 90,
        "font_size_subtitle": 40,
    },
    "exposed_by_algorithm": {
        "bg_color": (10, 10, 10),
        "text_color": (255, 255, 255),
        "accent_color": (255, 70, 70),
        "font_size_title": 80,
        "font_size_subtitle": 42,
    },
    "rank_the_room": {
        "bg_color": (240, 235, 225),
        "text_color": (30, 30, 30),
        "accent_color": (80, 160, 120),
        "font_size_title": 85,
        "font_size_subtitle": 42,
    },
    "body_language_decoded": {
        "bg_color": (15, 15, 20),
        "text_color": (255, 255, 255),
        "accent_color": (255, 180, 50),
        "font_size_title": 80,
        "font_size_subtitle": 42,
    },
    "what_your_x_says": {
        "bg_color": (250, 240, 250),
        "text_color": (40, 20, 60),
        "accent_color": (160, 80, 220),
        "font_size_title": 80,
        "font_size_subtitle": 42,
    },
    "salary_transparent": {
        "bg_color": (10, 30, 10),
        "text_color": (255, 255, 255),
        "accent_color": (80, 220, 80),
        "font_size_title": 85,
        "font_size_subtitle": 42,
    },
    "last_24_hours": {
        "bg_color": (10, 10, 15),
        "text_color": (255, 255, 255),
        "accent_color": (200, 200, 200),
        "font_size_title": 85,
        "font_size_subtitle": 40,
    },
    "designed_to_trick_you": {
        "bg_color": (15, 15, 15),
        "text_color": (255, 255, 255),
        "accent_color": (255, 200, 50),
        "font_size_title": 80,
        "font_size_subtitle": 42,
    },
}


class ThumbnailGenerator:
    """Generates YouTube Shorts thumbnails using Pillow."""

    def __init__(self, width: int = 1080, height: int = 1920):
        self.width = width
        self.height = height

    def generate(
        self,
        title: str,
        channel_key: str,
        output_path: Path = None,
        subtitle: str = "",
        background_image: Path = None,
    ) -> Optional[Path]:
        """Generate a thumbnail image.

        Args:
            title: Main text (2-4 words max for impact)
            channel_key: Channel type for styling
            output_path: Where to save
            subtitle: Optional smaller text
            background_image: Optional background image
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            console.print("[red]✗ Pillow not installed. Run: pip install Pillow[/]")
            return None

        style = CHANNEL_STYLES.get(channel_key, CHANNEL_STYLES["taylor_sabrina"])

        if output_path is None:
            safe_name = "".join(c if c.isalnum() else "_" for c in title[:30])
            output_path = THUMBNAILS_DIR / f"thumb_{safe_name}.png"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create base image
        if background_image and Path(background_image).exists():
            img = Image.open(background_image).convert("RGB")
            img = img.resize((self.width, self.height), Image.LANCZOS)
            # Add dark overlay for text readability
            overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 150))
            img = Image.composite(
                Image.new("RGB", (self.width, self.height), (0, 0, 0)),
                img,
                overlay.split()[3],
            )
        else:
            img = Image.new("RGB", (self.width, self.height), style["bg_color"])

        draw = ImageDraw.Draw(img)

        # Try to load fonts (fall back to default)
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", style["font_size_title"])
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", style["font_size_subtitle"])
        except (OSError, IOError):
            try:
                title_font = ImageFont.truetype("arial.ttf", style["font_size_title"])
                subtitle_font = ImageFont.truetype("arial.ttf", style["font_size_subtitle"])
            except (OSError, IOError):
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()

        # Draw accent line
        accent_y = self.height // 2 - 100
        draw.rectangle(
            [(self.width // 2 - 200, accent_y), (self.width // 2 + 200, accent_y + 6)],
            fill=style["accent_color"],
        )

        # Draw title text (centered, word-wrapped)
        self._draw_centered_text(
            draw, title.upper(), title_font,
            y_position=self.height // 2 - 60,
            color=style["text_color"],
            max_width=self.width - 100,
        )

        # Draw subtitle
        if subtitle:
            self._draw_centered_text(
                draw, subtitle, subtitle_font,
                y_position=self.height // 2 + 120,
                color=style["accent_color"],
                max_width=self.width - 120,
            )

        # Draw bottom accent line
        draw.rectangle(
            [(self.width // 2 - 200, self.height // 2 + 200),
             (self.width // 2 + 200, self.height // 2 + 206)],
            fill=style["accent_color"],
        )

        img.save(output_path, "PNG", quality=95)
        console.print(f"[green]✓ Thumbnail saved: {output_path.name}[/]")
        return output_path

    def _draw_centered_text(
        self,
        draw,
        text: str,
        font,
        y_position: int,
        color: tuple,
        max_width: int,
    ):
        """Draw text centered on the image, with word wrapping."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Draw each line centered
        total_height = len(lines) * (font.size + 10) if hasattr(font, 'size') else len(lines) * 30
        start_y = y_position - total_height // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = start_y + i * (font.size + 10 if hasattr(font, 'size') else 30)

            # Draw shadow
            draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0))
            # Draw text
            draw.text((x, y), line, font=font, fill=color)

    def generate_batch(
        self,
        titles: list[str],
        channel_key: str,
        subtitles: list[str] = None,
    ) -> list[Path]:
        """Generate thumbnails for multiple videos."""
        results = []
        if subtitles is None:
            subtitles = [""] * len(titles)

        for i, (title, subtitle) in enumerate(zip(titles, subtitles)):
            path = self.generate(title, channel_key, subtitle=subtitle)
            if path:
                results.append(path)

        console.print(f"[bold green]Generated {len(results)}/{len(titles)} thumbnails[/]")
        return results

