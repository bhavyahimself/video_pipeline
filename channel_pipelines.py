"""
Channel-Specific Pipelines
Pre-configured pipeline shortcuts for each of the 11 channels.
Each function handles the unique content sourcing strategy for its channel.
"""

from pathlib import Path
from typing import Optional

from rich.console import Console

from config.settings import CHANNELS, OUTPUT_DIR
from pipeline import MasterPipeline, PipelineResult
from clip_finder import RedditImageScraper, InternetArchiveClient, StockFootageFinder
from data_visualizer import ChartGenerator, SalaryDataFetcher
from screen_recorder import WebScreenRecorder
from thumbnail_generator import ThumbnailGenerator

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# TAYLOR/SABRINA — Pop Culture Commentary
# ═══════════════════════════════════════════════════════════════════════════════

def run_taylor_sabrina(
    topic: str,
    source_video_ids: list[str] = None,
    **kwargs,
) -> PipelineResult:
    """Run pipeline for Taylor Swift / Sabrina Carpenter channel.

    This channel relies on:
      - Transcript-based clip finding from interviews/concerts
      - Stock footage as B-roll
      - Conversational, conspiratorial tone
    """
    pipeline = MasterPipeline()

    # If source videos provided, ensure they're indexed
    if source_video_ids:
        pipeline.setup_transcript_database(video_ids=source_video_ids)

    return pipeline.run(
        topic=topic,
        channel_key="taylor_sabrina",
        use_transcript_search=True,
        use_stock=True,
        **kwargs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# RANK THE ROOM — Interior Design Rating (MOST AUTOMATABLE)
# ═══════════════════════════════════════════════════════════════════════════════

def run_rank_the_room(
    subreddits: list[str] = None,
    sort: str = "top",
    time_filter: str = "week",
    max_rooms: int = 5,
    **kwargs,
) -> list[PipelineResult]:
    """Run pipeline for Rank the Room channel.

    This channel relies on:
      - Reddit images from interior design subreddits
      - GPT-4 Vision for room analysis and script generation
      - Image-to-video conversion with Ken Burns effect
    """
    pipeline = MasterPipeline()

    # Fetch room images from Reddit
    scraper = RedditImageScraper()
    rooms = scraper.fetch_room_images(
        subreddits=subreddits,
        sort=sort,
        time_filter=time_filter,
        limit=max_rooms,
    )

    results = []
    for room in rooms[:max_rooms]:
        # Download image
        ext = room["url"].split(".")[-1][:4]
        filename = f"room_{room['subreddit']}_{room['score']}.{ext}"
        img_path = scraper.download_image(room["url"], filename)

        if not img_path:
            continue

        topic = f"Rate this room from r/{room['subreddit']}: {room['title'][:50]}"
        result = pipeline.run(
            topic=topic,
            channel_key="rank_the_room",
            use_transcript_search=False,
            use_stock=True,
            **kwargs,
        )
        results.append(result)

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# SALARY TRANSPARENT — Data-Driven Salary Content
# ═══════════════════════════════════════════════════════════════════════════════

def run_salary_transparent(
    job_title: str,
    city: str = "",
    gross_salary: float = None,
    deductions: dict = None,
    **kwargs,
) -> PipelineResult:
    """Run pipeline for Salary Transparent channel.

    This channel relies on:
      - BLS / salary data APIs
      - Auto-generated charts and number visuals
      - City stock footage
    """
    pipeline = MasterPipeline()
    charts = ChartGenerator()

    topic = f"What a {job_title} in {city} actually takes home" if city else f"What a {job_title} actually earns"

    # Generate salary breakdown chart if data provided
    if gross_salary and deductions:
        chart_path = charts.salary_breakdown_chart(
            gross_salary=gross_salary,
            deductions=deductions,
            title=f"{job_title} in {city}" if city else job_title,
        )

    return pipeline.run(
        topic=topic,
        channel_key="salary_transparent",
        use_transcript_search=False,
        use_stock=True,
        **kwargs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# HOW THEY WENT BROKE — Celebrity Financial Downfalls
# ═══════════════════════════════════════════════════════════════════════════════

def run_how_they_went_broke(
    celebrity_name: str,
    peak_net_worth: float = None,
    timeline: dict = None,
    **kwargs,
) -> PipelineResult:
    """Run pipeline for How They Went Broke channel.

    This channel relies on:
      - Research from news/Wikipedia
      - Net worth timeline charts
      - Stock footage of luxury items
    """
    pipeline = MasterPipeline()
    charts = ChartGenerator()

    topic = f"How {celebrity_name} went broke"

    # Generate timeline chart if data provided
    if timeline:
        years = list(timeline.keys())
        values = list(timeline.values())
        charts.net_worth_timeline(years, values, celebrity_name)

    return pipeline.run(
        topic=topic,
        channel_key="how_they_went_broke",
        use_transcript_search=False,
        use_stock=True,
        **kwargs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# WHY THIS PLACE FAILED — Dead Malls / Failed Businesses
# ═══════════════════════════════════════════════════════════════════════════════

def run_why_this_place_failed(
    place_name: str,
    website_url: str = None,
    **kwargs,
) -> PipelineResult:
    """Run pipeline for Why This Place Failed channel.

    This channel relies on:
      - Internet Archive for old website snapshots
      - Google Earth imagery (manual step)
      - Archival footage from Internet Archive
      - Stock footage of abandoned places
    """
    pipeline = MasterPipeline()
    archive = InternetArchiveClient()

    topic = f"Why {place_name} failed"

    # Search Internet Archive for related footage
    archive_results = archive.search(place_name, media_type="movies", rows=5)

    # Get Wayback Machine snapshot if website provided
    if website_url:
        snapshot = archive.get_wayback_snapshot(website_url)
        if snapshot:
            console.print(f"[green]Found archived website: {snapshot}[/]")

    return pipeline.run(
        topic=topic,
        channel_key="why_this_place_failed",
        use_transcript_search=False,
        use_stock=True,
        **kwargs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DESIGNED TO TRICK YOU — Dark Patterns / UX Manipulation
# ═══════════════════════════════════════════════════════════════════════════════

def run_designed_to_trick_you(
    topic: str,
    website_url: str = None,
    record_actions: list[dict] = None,
    **kwargs,
) -> PipelineResult:
    """Run pipeline for Designed to Trick You channel.

    This channel relies on:
      - Screen recordings of websites (Playwright)
      - Stock footage
      - Diagrams / annotations
    """
    pipeline = MasterPipeline()

    # Record website if URL provided
    if website_url:
        recorder = WebScreenRecorder()
        result = recorder.capture_dark_pattern(
            url=website_url,
            pattern_name=topic.replace(" ", "_")[:30],
        )
        console.print(f"[green]Captured dark pattern screenshots: {len(result.get('screenshots', []))}[/]")

    return pipeline.run(
        topic=topic,
        channel_key="designed_to_trick_you",
        use_transcript_search=False,
        use_stock=True,
        **kwargs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GENERIC CHANNELS (use standard pipeline)
# ═══════════════════════════════════════════════════════════════════════════════

def run_one_decision(topic: str, **kwargs) -> PipelineResult:
    """Run pipeline for One Decision channel."""
    pipeline = MasterPipeline()
    return pipeline.run(topic=topic, channel_key="one_decision", **kwargs)


def run_exposed_by_algorithm(topic: str, **kwargs) -> PipelineResult:
    """Run pipeline for Exposed by Algorithm channel."""
    pipeline = MasterPipeline()
    return pipeline.run(topic=topic, channel_key="exposed_by_algorithm", **kwargs)


def run_body_language_decoded(topic: str, source_video_ids: list[str] = None, **kwargs) -> PipelineResult:
    """Run pipeline for Body Language Decoded channel."""
    pipeline = MasterPipeline()
    if source_video_ids:
        pipeline.setup_transcript_database(video_ids=source_video_ids)
    return pipeline.run(topic=topic, channel_key="body_language_decoded", use_transcript_search=True, **kwargs)


def run_what_your_x_says(topic: str, **kwargs) -> PipelineResult:
    """Run pipeline for What Your X Says About You channel."""
    pipeline = MasterPipeline()
    return pipeline.run(topic=topic, channel_key="what_your_x_says", use_transcript_search=False, **kwargs)


def run_last_24_hours(topic: str, **kwargs) -> PipelineResult:
    """Run pipeline for The Last 24 Hours channel."""
    pipeline = MasterPipeline()
    return pipeline.run(topic=topic, channel_key="last_24_hours", **kwargs)

