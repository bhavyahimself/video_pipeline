"""
Data Visualization Module
Generates charts, graphs, and animated number visuals for data-driven channels.
Primary use: "Salary Transparent" and "How They Went Broke" channels.
"""

from pathlib import Path
from typing import Optional

from rich.console import Console

from config.settings import OUTPUT_DIR

console = Console()


class SalaryDataFetcher:
    """Fetch salary data from public APIs."""

    BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    def fetch_bls_data(self, series_ids: list[str], start_year: str = "2024", end_year: str = "2026") -> dict:
        """Fetch data from Bureau of Labor Statistics API.

        Args:
            series_ids: BLS series IDs
            start_year: Start year
            end_year: End year

        Returns:
            Raw API response data
        """
        import requests

        try:
            response = requests.post(
                self.BLS_API_URL,
                json={
                    "seriesid": series_ids,
                    "startyear": start_year,
                    "endyear": end_year,
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "REQUEST_SUCCEEDED":
                console.print(f"[green]✓ BLS data fetched: {len(series_ids)} series[/]")
                return data
            else:
                console.print(f"[yellow]⚠ BLS API message: {data.get('message', '')}[/]")
                return data

        except Exception as e:
            console.print(f"[red]✗ BLS API error: {e}[/]")
            return {}


class ChartGenerator:
    """Generate charts and data visualizations for videos."""

    def __init__(self):
        self.default_style = {
            "bg_color": "#0a0a0a",
            "text_color": "#ffffff",
            "accent_color": "#4CAF50",
            "negative_color": "#f44336",
            "font_size": 14,
        }

    def salary_breakdown_chart(
        self,
        gross_salary: float,
        deductions: dict,
        title: str = "Salary Breakdown",
        output_path: Path = None,
    ) -> Optional[Path]:
        """Generate a salary breakdown bar chart.

        Args:
            gross_salary: Gross annual salary
            deductions: Dict of deductions, e.g. {"Federal Tax": 15000, "State Tax": 5000, ...}
            title: Chart title
            output_path: Where to save
        """
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import matplotlib.ticker as mticker
        except ImportError:
            console.print("[red]✗ matplotlib not installed[/]")
            return None

        if output_path is None:
            safe_title = "".join(c if c.isalnum() else "_" for c in title[:30])
            output_path = OUTPUT_DIR / f"chart_{safe_title}.png"

        # Calculate take-home
        total_deductions = sum(deductions.values())
        take_home = gross_salary - total_deductions

        # Setup dark theme
        fig, ax = plt.subplots(figsize=(10, 18))
        fig.patch.set_facecolor(self.default_style["bg_color"])
        ax.set_facecolor(self.default_style["bg_color"])

        # Data
        categories = list(deductions.keys()) + ["Take Home"]
        values = list(deductions.values()) + [take_home]
        colors = [self.default_style["negative_color"]] * len(deductions) + [self.default_style["accent_color"]]

        # Horizontal bar chart
        bars = ax.barh(categories, values, color=colors, height=0.6)

        # Style
        ax.set_title(title, color=self.default_style["text_color"], fontsize=24, fontweight="bold", pad=20)
        ax.set_xlabel("", color=self.default_style["text_color"])
        ax.tick_params(colors=self.default_style["text_color"], labelsize=14)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("#333333")
        ax.spines["left"].set_color("#333333")

        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_width() + gross_salary * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"${val:,.0f}",
                va="center",
                color=self.default_style["text_color"],
                fontsize=13,
                fontweight="bold",
            )

        # Gross salary annotation
        ax.text(
            0.5, -0.05,
            f"Gross Salary: ${gross_salary:,.0f}/year",
            transform=ax.transAxes,
            ha="center",
            color="#888888",
            fontsize=14,
        )

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

        console.print(f"[green]✓ Chart saved: {output_path.name}[/]")
        return output_path

    def comparison_chart(
        self,
        labels: list[str],
        values: list[float],
        title: str = "Comparison",
        output_path: Path = None,
        value_format: str = "${:,.0f}",
    ) -> Optional[Path]:
        """Generate a comparison bar chart (vertical)."""
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            console.print("[red]✗ matplotlib not installed[/]")
            return None

        if output_path is None:
            safe_title = "".join(c if c.isalnum() else "_" for c in title[:30])
            output_path = OUTPUT_DIR / f"chart_{safe_title}.png"

        fig, ax = plt.subplots(figsize=(10, 18))
        fig.patch.set_facecolor(self.default_style["bg_color"])
        ax.set_facecolor(self.default_style["bg_color"])

        colors = [self.default_style["accent_color"]] * len(labels)
        max_val = max(values) if values else 1
        colors = [
            self.default_style["accent_color"] if v == max_val
            else "#666666"
            for v in values
        ]

        bars = ax.bar(labels, values, color=colors, width=0.6)

        ax.set_title(title, color=self.default_style["text_color"], fontsize=24, fontweight="bold", pad=20)
        ax.tick_params(colors=self.default_style["text_color"], labelsize=12)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("#333333")
        ax.spines["left"].set_color("#333333")

        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_val * 0.02,
                value_format.format(val),
                ha="center",
                color=self.default_style["text_color"],
                fontsize=13,
                fontweight="bold",
            )

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

        console.print(f"[green]✓ Chart saved: {output_path.name}[/]")
        return output_path

    def net_worth_timeline(
        self,
        years: list[int],
        values: list[float],
        person_name: str = "",
        output_path: Path = None,
    ) -> Optional[Path]:
        """Generate a net worth timeline chart (for 'How They Went Broke')."""
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import matplotlib.ticker as mticker
        except ImportError:
            console.print("[red]✗ matplotlib not installed[/]")
            return None

        if output_path is None:
            safe = "".join(c if c.isalnum() else "_" for c in person_name[:20])
            output_path = OUTPUT_DIR / f"timeline_{safe}.png"

        fig, ax = plt.subplots(figsize=(10, 18))
        fig.patch.set_facecolor(self.default_style["bg_color"])
        ax.set_facecolor(self.default_style["bg_color"])

        # Color segments based on whether value is increasing or decreasing
        for i in range(len(years) - 1):
            color = self.default_style["accent_color"] if values[i + 1] >= values[i] else self.default_style["negative_color"]
            ax.plot(years[i:i + 2], values[i:i + 2], color=color, linewidth=3)

        ax.fill_between(years, values, alpha=0.1, color=self.default_style["accent_color"])
        ax.scatter(years, values, color=self.default_style["text_color"], s=50, zorder=5)

        title = f"Net Worth: {person_name}" if person_name else "Net Worth Timeline"
        ax.set_title(title, color=self.default_style["text_color"], fontsize=24, fontweight="bold", pad=20)
        ax.tick_params(colors=self.default_style["text_color"], labelsize=12)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x / 1e6:.0f}M" if abs(x) >= 1e6 else f"${x:,.0f}"))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("#333333")
        ax.spines["left"].set_color("#333333")

        # Annotate peak and lowest
        peak_idx = values.index(max(values))
        low_idx = values.index(min(values))

        ax.annotate(
            f"Peak: ${values[peak_idx]:,.0f}",
            xy=(years[peak_idx], values[peak_idx]),
            xytext=(0, 20), textcoords="offset points",
            color=self.default_style["accent_color"],
            fontsize=12, fontweight="bold",
            ha="center",
        )

        if low_idx != peak_idx:
            ax.annotate(
                f"Low: ${values[low_idx]:,.0f}",
                xy=(years[low_idx], values[low_idx]),
                xytext=(0, -25), textcoords="offset points",
                color=self.default_style["negative_color"],
                fontsize=12, fontweight="bold",
                ha="center",
            )

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

        console.print(f"[green]✓ Timeline chart saved: {output_path.name}[/]")
        return output_path

    def big_number_image(
        self,
        number: str,
        label: str,
        output_path: Path = None,
        color: str = None,
        width: int = 1080,
        height: int = 1920,
    ) -> Optional[Path]:
        """Generate a large number display image (for dramatic reveals in Shorts)."""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            console.print("[red]✗ Pillow not installed[/]")
            return None

        if output_path is None:
            safe = "".join(c if c.isalnum() else "_" for c in number[:15])
            output_path = OUTPUT_DIR / f"number_{safe}.png"

        bg = tuple(int(self.default_style["bg_color"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        img = Image.new("RGB", (width, height), bg)
        draw = ImageDraw.Draw(img)

        # Try loading a bold font
        try:
            num_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 140)
            label_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        except (OSError, IOError):
            try:
                num_font = ImageFont.truetype("arial.ttf", 140)
                label_font = ImageFont.truetype("arial.ttf", 48)
            except (OSError, IOError):
                num_font = ImageFont.load_default()
                label_font = ImageFont.load_default()

        # Draw number centered
        num_color = color or self.default_style["accent_color"]
        if num_color.startswith("#"):
            num_color = tuple(int(num_color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))

        # Center the number
        bbox = draw.textbbox((0, 0), number, font=num_font)
        num_w = bbox[2] - bbox[0]
        x = (width - num_w) // 2
        y = height // 2 - 80

        draw.text((x, y), number, font=num_font, fill=num_color)

        # Label below
        bbox = draw.textbbox((0, 0), label, font=label_font)
        label_w = bbox[2] - bbox[0]
        x = (width - label_w) // 2
        y = height // 2 + 100

        draw.text((x, y), label, font=label_font, fill=(180, 180, 180))

        img.save(output_path, "PNG")
        console.print(f"[green]✓ Number image saved: {output_path.name}[/]")
        return output_path

