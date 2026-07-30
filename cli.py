"""
Video Pipeline CLI
Command-line interface for the entire video production pipeline.

Usage:
  python cli.py run --topic "Sabrina Carpenter almost quit" --channel taylor_sabrina
  python cli.py script --topic "Apple almost died" --channel one_decision
  python cli.py setup-transcripts --video-ids abc123 def456
  python cli.py batch --topics-file topics.txt --channel how_they_went_broke
  python cli.py list-channels
  python cli.py list-voices
"""

import sys
import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import CHANNELS, API_KEYS, OUTPUT_DIR

console = Console()


@click.group()
def cli():
    """🎬 Video Pipeline — AI-Powered YouTube Shorts Production"""
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# FULL PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.option("--topic", "-t", required=True, help="Video topic")
@click.option("--channel", "-c", required=True, type=click.Choice(list(CHANNELS.keys())), help="Channel type")
@click.option("--output-name", "-o", default=None, help="Custom output folder name")
@click.option("--no-research", is_flag=True, help="Skip research step")
@click.option("--no-voice", is_flag=True, help="Skip voiceover generation")
@click.option("--no-captions", is_flag=True, help="Skip caption generation")
@click.option("--no-thumbnail", is_flag=True, help="Skip thumbnail generation")
@click.option("--no-download", is_flag=True, help="Don't download clips (dry run)")
@click.option("--no-transcript-search", is_flag=True, help="Skip transcript database search")
@click.option("--no-stock", is_flag=True, help="Don't use stock footage")
def run(topic, channel, output_name, no_research, no_voice, no_captions,
        no_thumbnail, no_download, no_transcript_search, no_stock):
    """Run the complete video production pipeline."""
    from pipeline import MasterPipeline

    pipeline = MasterPipeline()
    result = pipeline.run(
        topic=topic,
        channel_key=channel,
        output_name=output_name,
        research=not no_research,
        use_transcript_search=not no_transcript_search,
        use_stock=not no_stock,
        generate_voice=not no_voice,
        generate_captions=not no_captions,
        generate_thumbnail=not no_thumbnail,
        download_clips=not no_download,
    )

    if result.status == "complete":
        console.print(f"\n[bold green]🎉 Video complete: {result.final_video_path}[/]")
    else:
        console.print(f"\n[yellow]⚠ Pipeline finished with status: {result.status}[/]")


# ═══════════════════════════════════════════════════════════════════════════════
# BATCH PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.option("--topics-file", "-f", required=True, type=click.Path(exists=True), help="Text file with one topic per line")
@click.option("--channel", "-c", required=True, type=click.Choice(list(CHANNELS.keys())), help="Channel type")
@click.option("--no-research", is_flag=True, help="Skip research step")
@click.option("--no-voice", is_flag=True, help="Skip voiceover generation")
@click.option("--no-download", is_flag=True, help="Don't download clips")
def batch(topics_file, channel, no_research, no_voice, no_download):
    """Run pipeline for multiple topics from a file."""
    from pipeline import MasterPipeline

    with open(topics_file) as f:
        topics = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    console.print(f"[bold]Loaded {len(topics)} topics from {topics_file}[/]")

    pipeline = MasterPipeline()
    results = pipeline.run_batch(
        topics=topics,
        channel_key=channel,
        research=not no_research,
        generate_voice=not no_voice,
        download_clips=not no_download,
    )

    complete = sum(1 for r in results if r.status == "complete")
    console.print(f"\n[bold green]Batch complete: {complete}/{len(results)} videos produced[/]")


# ═══════════════════════════════════════════════════════════════════════════════
# INDIVIDUAL STEPS
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.option("--topic", "-t", required=True, help="Video topic")
@click.option("--channel", "-c", required=True, type=click.Choice(list(CHANNELS.keys())), help="Channel type")
@click.option("--research/--no-research", default=True, help="Include research step")
@click.option("--save", "-s", default=None, help="Save script to file")
def script(topic, channel, research, save):
    """Generate a script only (no video production)."""
    from script_generator import ScriptGenerator, ResearchAgent

    research_text = ""
    if research:
        researcher = ResearchAgent()
        research_text = researcher.research_topic(topic, channel)

    gen = ScriptGenerator(channel)
    result = gen.generate(topic, additional_context=research_text)

    console.print(Panel(result, title=f"Script: {topic}", border_style="green"))

    if save:
        Path(save).write_text(result)
        console.print(f"[green]Saved to {save}[/]")


@cli.command()
@click.option("--topic", "-t", required=True, help="Video topic")
@click.option("--channel", "-c", required=True, type=click.Choice(list(CHANNELS.keys())), help="Channel type")
def research(topic, channel):
    """Research a topic only."""
    from script_generator import ResearchAgent

    researcher = ResearchAgent()
    result = researcher.research_topic(topic, channel)
    console.print(Panel(result, title=f"Research: {topic}", border_style="cyan"))


@cli.command()
@click.option("--text", "-t", required=True, help="Text to convert to speech")
@click.option("--output", "-o", default="voiceover.mp3", help="Output file path")
@click.option("--channel", "-c", default=None, type=click.Choice(list(CHANNELS.keys())), help="Use channel voice settings")
def voiceover(text, output, channel):
    """Generate a voiceover from text."""
    from voice_generator import VoiceGenerator

    vg = VoiceGenerator()
    output_path = Path(output)

    if channel:
        result = vg.generate_for_channel(text, channel, output_path)
    else:
        result = vg.generate(text, output_path)

    if result:
        console.print(f"[green]✓ Voiceover saved: {result}[/]")
    else:
        console.print("[red]✗ Voiceover generation failed[/]")


@cli.command()
@click.option("--title", "-t", required=True, help="Thumbnail title text")
@click.option("--channel", "-c", required=True, type=click.Choice(list(CHANNELS.keys())), help="Channel style")
@click.option("--subtitle", "-s", default="", help="Optional subtitle")
@click.option("--background", "-b", default=None, help="Background image path")
def thumbnail(title, channel, subtitle, background):
    """Generate a thumbnail image."""
    from thumbnail_generator import ThumbnailGenerator

    tg = ThumbnailGenerator()
    bg = Path(background) if background else None
    result = tg.generate(title, channel, subtitle=subtitle, background_image=bg)

    if result:
        console.print(f"[green]✓ Thumbnail: {result}[/]")


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSCRIPT DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command("setup-transcripts")
@click.option("--video-ids", "-v", multiple=True, help="YouTube video IDs to index")
@click.option("--channel-url", "-u", default=None, help="YouTube channel URL to scrape")
@click.option("--max-videos", default=50, help="Max videos from channel")
@click.option("--index-only", is_flag=True, help="Skip download, only index existing transcripts")
def setup_transcripts(video_ids, channel_url, max_videos, index_only):
    """Download YouTube transcripts and build search index."""
    from pipeline import MasterPipeline

    pipeline = MasterPipeline()

    if index_only:
        idx = pipeline._get_transcript_idx()
        idx.index_all_transcripts()
    else:
        pipeline.setup_transcript_database(
            video_ids=list(video_ids) if video_ids else None,
            channel_url=channel_url,
            max_videos=max_videos,
        )


@cli.command("search-transcripts")
@click.option("--query", "-q", required=True, help="Search query")
@click.option("--results", "-n", default=5, help="Number of results")
def search_transcripts(query, results):
    """Search indexed transcripts for matching clips."""
    from transcript_manager import TranscriptIndex

    idx = TranscriptIndex()
    matches = idx.search(query, n_results=results)

    if not matches:
        console.print("[yellow]No matches found. Run setup-transcripts first.[/]")
        return

    table = Table(title=f"Transcript Search: '{query}'")
    table.add_column("Video ID")
    table.add_column("Time")
    table.add_column("Similarity")
    table.add_column("Text", max_width=60)

    for m in matches:
        table.add_row(
            m["video_id"],
            f"{m['start_time']:.1f}s - {m['end_time']:.1f}s",
            f"{m['similarity']:.3f}",
            m["text"][:60],
        )

    console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# STOCK FOOTAGE
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command("search-stock")
@click.option("--query", "-q", required=True, help="Search keywords")
@click.option("--orientation", default="portrait", type=click.Choice(["portrait", "landscape"]))
@click.option("--count", "-n", default=5, help="Number of results")
def search_stock(query, orientation, count):
    """Search Pexels for stock footage."""
    from clip_finder import StockFootageFinder

    finder = StockFootageFinder()
    results = finder.find_footage(query, video_count=count, orientation=orientation)

    if results["videos"]:
        table = Table(title=f"Stock Videos: '{query}'")
        table.add_column("ID")
        table.add_column("Size")
        table.add_column("Duration")
        table.add_column("Photographer")

        for v in results["videos"]:
            table.add_row(
                str(v["id"]),
                f"{v.get('width', '?')}x{v.get('height', '?')}",
                f"{v.get('duration', '?')}s",
                v.get("photographer", "?"),
            )
        console.print(table)
    else:
        console.print("[yellow]No stock videos found.[/]")


# ═══════════════════════════════════════════════════════════════════════════════
# INFO COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command("list-channels")
def list_channels():
    """List all available channel configurations."""
    table = Table(title="Available Channels", border_style="blue")
    table.add_column("Key", style="bold")
    table.add_column("Name")
    table.add_column("Tone", max_width=50)
    table.add_column("Duration")

    for key, ch in CHANNELS.items():
        table.add_row(key, ch.name, ch.tone[:50], f"{ch.target_duration_seconds}s")

    console.print(table)


@cli.command("list-voices")
def list_voices():
    """List available ElevenLabs voices."""
    from voice_generator import VoiceGenerator
    vg = VoiceGenerator()
    vg.list_voices()


@cli.command("check-setup")
def check_setup():
    """Check which API keys and tools are configured."""
    import shutil

    console.print(Panel("[bold]Pipeline Setup Check[/]", border_style="blue"))

    # API Keys
    console.print("\n[bold]API Keys:[/]")
    keys = {
        "OpenAI (GPT-4)": bool(API_KEYS.openai),
        "ElevenLabs (Voice)": bool(API_KEYS.elevenlabs),
        "Pexels (Stock)": bool(API_KEYS.pexels),
        "Reddit (Images)": bool(API_KEYS.reddit_client_id),
        "Twelve Labs (Visual Search)": bool(API_KEYS.twelve_labs),
        "YouTube Data API": bool(API_KEYS.youtube),
    }

    for name, configured in keys.items():
        icon = "✅" if configured else "❌"
        console.print(f"  {icon} {name}")

    # CLI Tools
    console.print("\n[bold]CLI Tools:[/]")
    tools = {
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
        "yt-dlp": shutil.which("yt-dlp"),
        "whisper": shutil.which("whisper"),
    }

    for name, path in tools.items():
        icon = "✅" if path else "❌"
        console.print(f"  {icon} {name}: {path or 'NOT FOUND'}")

    # Python packages
    console.print("\n[bold]Python Packages:[/]")
    packages = [
        "openai", "chromadb", "sentence_transformers",
        "youtube_transcript_api", "moviepy", "PIL",
        "praw", "requests", "click", "rich",
    ]

    for pkg in packages:
        try:
            __import__(pkg)
            console.print(f"  ✅ {pkg}")
        except ImportError:
            console.print(f"  ❌ {pkg}")

    # Transcript database
    console.print("\n[bold]Transcript Database:[/]")
    from config.settings import TRANSCRIPTS_DIR
    count = len(list(TRANSCRIPTS_DIR.glob("*.json")))
    console.print(f"  Downloaded transcripts: {count}")


@cli.command("status")
def status():
    """Show output directory status and recent runs."""
    if not OUTPUT_DIR.exists():
        console.print("[yellow]No output directory found.[/]")
        return

    table = Table(title="Pipeline Outputs", border_style="blue")
    table.add_column("Video")
    table.add_column("Status")
    table.add_column("Channel")
    table.add_column("Files")

    for folder in sorted(OUTPUT_DIR.iterdir()):
        if not folder.is_dir():
            continue

        meta_path = folder / "pipeline_metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
            table.add_row(
                folder.name[:40],
                meta.get("status", "?"),
                meta.get("channel", "?"),
                str(len(list(folder.iterdir()))),
            )
        else:
            table.add_row(folder.name[:40], "—", "—", str(len(list(folder.iterdir()))))

    console.print(table)


if __name__ == "__main__":
    cli()

