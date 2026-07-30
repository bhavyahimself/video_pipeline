"""
Master Pipeline
Orchestrates the full video creation flow:
  Script → Visual Cues → Clip Finding → Voiceover → Assembly → Captions → Thumbnail

One command = one finished video.
"""

import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import CHANNELS, OUTPUT_DIR, CLIPS_DIR
from script_generator import ScriptGenerator, ResearchAgent
from transcript_manager import TranscriptDownloader, TranscriptIndex
from clip_finder import (
    YouTubeClipDownloader,
    StockFootageFinder,
    RedditImageScraper,
    InternetArchiveClient,
)
from voice_generator import VoiceGenerator, WhisperCaptionGenerator
from video_assembler import VideoAssembler
from thumbnail_generator import ThumbnailGenerator

console = Console()


@dataclass
class PipelineResult:
    """Result of a pipeline run."""
    video_name: str
    channel: str
    status: str = "pending"
    script: str = ""
    voiceover_path: Optional[Path] = None
    caption_path: Optional[Path] = None
    thumbnail_path: Optional[Path] = None
    final_video_path: Optional[Path] = None
    clip_paths: list = field(default_factory=list)
    visual_cues: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    duration_seconds: float = 0.0
    processing_time_seconds: float = 0.0


class MasterPipeline:
    """Full automation pipeline for video production."""

    def __init__(self):
        self.script_gen = None
        self.researcher = ResearchAgent()
        self.transcript_dl = TranscriptDownloader()
        self.transcript_idx = None
        self.clip_dl = YouTubeClipDownloader()
        self.stock_finder = StockFootageFinder()
        self.voice_gen = VoiceGenerator()
        self.caption_gen = WhisperCaptionGenerator()
        self.assembler = VideoAssembler()
        self.thumb_gen = ThumbnailGenerator()

    def _get_script_gen(self, channel_key: str) -> ScriptGenerator:
        """Get or create script generator for a channel."""
        if self.script_gen is None or self.script_gen.channel_key != channel_key:
            self.script_gen = ScriptGenerator(channel_key)
        return self.script_gen

    def _get_transcript_idx(self, collection: str = "video_clips") -> TranscriptIndex:
        """Get or create transcript index."""
        if self.transcript_idx is None:
            self.transcript_idx = TranscriptIndex(collection)
        return self.transcript_idx

    # ═══════════════════════════════════════════════════════════════════════
    # INDIVIDUAL STEPS (can be run standalone)
    # ═══════════════════════════════════════════════════════════════════════

    def step_research(self, topic: str, channel_key: str) -> str:
        """Step 1: Research a topic."""
        return self.researcher.research_topic(topic, channel_key)

    def step_generate_script(
        self,
        topic: str,
        channel_key: str,
        research: str = "",
    ) -> str:
        """Step 2: Generate a script."""
        gen = self._get_script_gen(channel_key)
        return gen.generate(topic, additional_context=research)

    def step_extract_visuals(self, script: str, channel_key: str) -> list[dict]:
        """Step 3: Extract visual cues from script."""
        gen = self._get_script_gen(channel_key)
        return gen.extract_visual_cues(script)

    def step_find_clips(
        self,
        visual_cues: list[dict],
        channel_key: str,
        use_transcript_search: bool = True,
        use_stock: bool = True,
        download: bool = True,
    ) -> list[dict]:
        """Step 4: Find clips for each visual cue."""
        clip_results = []

        for cue in visual_cues:
            entry = {
                "line": cue.get("line", ""),
                "visual": cue.get("visual_description", ""),
                "transcript_match": None,
                "stock_footage": None,
                "downloaded_path": None,
            }

            # Try transcript search first (for channels with indexed transcripts)
            if use_transcript_search:
                idx = self._get_transcript_idx()
                if idx.collection.count() > 0:
                    matches = idx.search(cue.get("line", ""), n_results=3)
                    if matches and matches[0]["similarity"] > 0.4:
                        entry["transcript_match"] = matches[0]
                        if download:
                            path = self.clip_dl.download_segment(
                                video_id=matches[0]["video_id"],
                                start_time=matches[0]["start_time"],
                                end_time=matches[0]["end_time"],
                            )
                            if path:
                                entry["downloaded_path"] = str(path)

            # Fall back to stock footage
            if use_stock and not entry["downloaded_path"]:
                keywords = cue.get("search_keywords", [])
                query = " ".join(keywords) if isinstance(keywords, list) else str(keywords)
                if query:
                    results = self.stock_finder.find_footage(query, video_count=2)
                    if results["videos"]:
                        entry["stock_footage"] = results["videos"][0]
                        if download:
                            best = results["videos"][0]
                            filename = f"stock_{best['id']}.mp4"
                            path = self.stock_finder.pexels.download_video(
                                best["download_url"], filename,
                            )
                            if path:
                                entry["downloaded_path"] = str(path)

            clip_results.append(entry)

        return clip_results

    def step_generate_voiceover(
        self,
        script: str,
        channel_key: str,
        output_name: str,
    ) -> Optional[Path]:
        """Step 5: Generate voiceover."""
        output_path = OUTPUT_DIR / output_name / "voiceover.mp3"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return self.voice_gen.generate_for_channel(script, channel_key, output_path)

    def step_generate_captions(self, audio_path: Path) -> Optional[Path]:
        """Step 6: Generate SRT captions from voiceover."""
        return self.caption_gen.generate_srt(audio_path)

    def step_assemble(
        self,
        clip_paths: list[Path],
        voiceover_path: Path,
        output_name: str,
        srt_path: Path = None,
        background_audio_path: Path = None,
        sound_events: list[dict] = None,
    ) -> Optional[Path]:
        """Step 7: Assemble final video."""
        return self.assembler.assemble_from_clips(
            clip_paths=clip_paths,
            voiceover_path=voiceover_path,
            output_name=output_name,
            srt_path=srt_path,
            background_audio_path=background_audio_path,
            sound_events=sound_events,
        )

    def step_generate_thumbnail(
        self,
        title: str,
        channel_key: str,
        output_name: str,
    ) -> Optional[Path]:
        """Step 8: Generate thumbnail."""
        return self.thumb_gen.generate(title, channel_key)

    # ═══════════════════════════════════════════════════════════════════════
    # FULL PIPELINE
    # ═══════════════════════════════════════════════════════════════════════

    def run(
        self,
        topic: str,
        channel_key: str,
        output_name: str = None,
        research: bool = True,
        use_transcript_search: bool = True,
        use_stock: bool = True,
        generate_voice: bool = True,
        generate_captions: bool = True,
        generate_thumbnail: bool = True,
        download_clips: bool = True,
        background_audio_path: Path = None,
        sound_events: list[dict] = None,
    ) -> PipelineResult:
        """Run the complete video production pipeline.

        Args:
            topic: Video topic
            channel_key: Channel type (from CHANNELS dict)
            output_name: Custom output folder name
            research: Whether to research the topic first
            use_transcript_search: Search indexed transcripts for clips
            use_stock: Use stock footage as fallback
            generate_voice: Generate AI voiceover
            generate_captions: Generate and burn captions
            generate_thumbnail: Generate thumbnail image
            download_clips: Actually download clips (False = dry run)
            background_audio_path: Optional licensed music or ambience bed
            sound_events: Optional timestamped licensed sound cues
        """
        start_time = time.time()

        if output_name is None:
            safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:40])
            output_name = f"{channel_key}_{safe_topic}_{int(time.time())}"

        result = PipelineResult(video_name=output_name, channel=channel_key)

        console.print(Panel(
            f"[bold]Topic:[/] {topic}\n[bold]Channel:[/] {CHANNELS[channel_key].name}\n[bold]Output:[/] {output_name}",
            title="[bold blue]═══ MASTER PIPELINE ═══[/]",
            border_style="blue",
        ))

        try:
            # ── Step 1: Research ──
            research_text = ""
            if research:
                console.print("\n[bold cyan]▶ STEP 1: Research[/]")
                research_text = self.step_research(topic, channel_key)

            # ── Step 2: Script ──
            console.print("\n[bold cyan]▶ STEP 2: Generate Script[/]")
            script = self.step_generate_script(topic, channel_key, research_text)
            result.script = script
            console.print(Panel(script, title="Generated Script", border_style="green"))

            # ── Step 3: Visual Cues ──
            console.print("\n[bold cyan]▶ STEP 3: Extract Visual Cues[/]")
            visual_cues = self.step_extract_visuals(script, channel_key)
            result.visual_cues = visual_cues

            # ── Step 4: Find Clips ──
            console.print("\n[bold cyan]▶ STEP 4: Find Clips[/]")
            clip_results = self.step_find_clips(
                visual_cues, channel_key,
                use_transcript_search=use_transcript_search,
                use_stock=use_stock,
                download=download_clips,
            )

            clip_paths = []
            for cr in clip_results:
                if cr.get("downloaded_path"):
                    clip_paths.append(Path(cr["downloaded_path"]))

            result.clip_paths = [str(p) for p in clip_paths]

            if not clip_paths:
                console.print("[yellow]⚠ No clips found. Video assembly requires manual clip selection.[/]")
                result.status = "partial_no_clips"

            # ── Step 5: Voiceover ──
            if generate_voice:
                console.print("\n[bold cyan]▶ STEP 5: Generate Voiceover[/]")
                voice_path = self.step_generate_voiceover(script, channel_key, output_name)
                result.voiceover_path = voice_path

                # ── Step 6: Captions ──
                if generate_captions and voice_path:
                    console.print("\n[bold cyan]▶ STEP 6: Generate Captions[/]")
                    srt_path = self.step_generate_captions(voice_path)
                    result.caption_path = srt_path

            # ── Step 7: Assemble ──
            if clip_paths and result.voiceover_path:
                console.print("\n[bold cyan]▶ STEP 7: Assemble Video[/]")
                final = self.step_assemble(
                    clip_paths=clip_paths,
                    voiceover_path=result.voiceover_path,
                    output_name=output_name,
                    srt_path=result.caption_path,
                    background_audio_path=background_audio_path,
                    sound_events=sound_events,
                )
                result.final_video_path = final
                if final:
                    from video_assembler import FFmpegProcessor
                    result.duration_seconds = FFmpegProcessor().get_duration(final)
            else:
                console.print("[yellow]⚠ Skipping assembly (missing clips or voiceover)[/]")

            # ── Step 8: Thumbnail ──
            if generate_thumbnail:
                console.print("\n[bold cyan]▶ STEP 8: Generate Thumbnail[/]")
                thumb = self.step_generate_thumbnail(topic, channel_key, output_name)
                result.thumbnail_path = thumb

            # ── Done ──
            result.processing_time_seconds = time.time() - start_time
            result.status = "complete" if result.final_video_path else "partial"

        except Exception as e:
            result.status = f"error: {e}"
            result.errors.append(str(e))
            result.processing_time_seconds = time.time() - start_time
            console.print(f"[red]✗ Pipeline error: {e}[/]")

        # Print summary
        self._print_summary(result)

        # Save result metadata
        self._save_result(result, output_name)

        return result

    def run_batch(
        self,
        topics: list[str],
        channel_key: str,
        **kwargs,
    ) -> list[PipelineResult]:
        """Run pipeline for multiple topics."""
        results = []
        for i, topic in enumerate(topics, 1):
            console.print(f"\n\n{'═' * 60}")
            console.print(f"[bold]Video {i}/{len(topics)}[/]")
            console.print(f"{'═' * 60}")
            result = self.run(topic, channel_key, **kwargs)
            results.append(result)

        # Print batch summary
        self._print_batch_summary(results)
        return results

    # ═══════════════════════════════════════════════════════════════════════
    # SETUP HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    def setup_transcript_database(
        self,
        video_ids: list[str] = None,
        channel_url: str = None,
        max_videos: int = 50,
    ):
        """One-time setup: download transcripts and build search index.

        Provide either video_ids or channel_url.
        """
        console.print(Panel("Setting up transcript database...", title="[bold]Setup[/]"))

        # Download transcripts
        if channel_url:
            video_ids = self.transcript_dl.download_from_channel(channel_url, max_videos)
        elif video_ids:
            self.transcript_dl.download_batch(video_ids)
        else:
            console.print("[yellow]No video IDs or channel URL provided. Using existing transcripts.[/]")

        # Build index
        idx = self._get_transcript_idx()
        idx.index_all_transcripts()

        console.print(f"[bold green]✓ Database ready. {idx.collection.count()} chunks indexed.[/]")

    # ═══════════════════════════════════════════════════════════════════════
    # REPORTING
    # ═══════════════════════════════════════════════════════════════════════

    def _print_summary(self, result: PipelineResult):
        """Print a summary table for a pipeline run."""
        table = Table(title=f"Pipeline Result: {result.video_name}", border_style="blue")
        table.add_column("Component", style="bold")
        table.add_column("Status")
        table.add_column("Path")

        status_icon = {"complete": "✅", "partial": "⚠️", "partial_no_clips": "⚠️"}.get(
            result.status, "❌"
        )

        table.add_row("Script", "✅" if result.script else "❌", f"{len(result.script)} chars")
        table.add_row("Clips", f"{'✅' if result.clip_paths else '❌'}", f"{len(result.clip_paths)} clips")
        table.add_row("Voiceover", "✅" if result.voiceover_path else "❌", str(result.voiceover_path or "—"))
        table.add_row("Captions", "✅" if result.caption_path else "❌", str(result.caption_path or "—"))
        table.add_row("Thumbnail", "✅" if result.thumbnail_path else "❌", str(result.thumbnail_path or "—"))
        table.add_row("Final Video", status_icon, str(result.final_video_path or "—"))
        table.add_row("Duration", "", f"{result.duration_seconds:.1f}s")
        table.add_row("Processing Time", "", f"{result.processing_time_seconds:.1f}s")

        console.print(table)

    def _print_batch_summary(self, results: list[PipelineResult]):
        """Print summary for a batch run."""
        table = Table(title="Batch Pipeline Summary", border_style="blue")
        table.add_column("#", style="bold")
        table.add_column("Video")
        table.add_column("Status")
        table.add_column("Duration")

        for i, r in enumerate(results, 1):
            icon = "✅" if r.status == "complete" else "⚠️" if "partial" in r.status else "❌"
            table.add_row(str(i), r.video_name[:40], icon, f"{r.duration_seconds:.1f}s")

        complete = sum(1 for r in results if r.status == "complete")
        table.add_row("", f"[bold]Total: {complete}/{len(results)} complete[/]", "", "")

        console.print(table)

    def _save_result(self, result: PipelineResult, output_name: str):
        """Save pipeline result metadata to JSON."""
        output_dir = OUTPUT_DIR / output_name
        output_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "video_name": result.video_name,
            "channel": result.channel,
            "status": result.status,
            "script": result.script,
            "voiceover_path": str(result.voiceover_path) if result.voiceover_path else None,
            "caption_path": str(result.caption_path) if result.caption_path else None,
            "thumbnail_path": str(result.thumbnail_path) if result.thumbnail_path else None,
            "final_video_path": str(result.final_video_path) if result.final_video_path else None,
            "clip_paths": result.clip_paths,
            "visual_cues": result.visual_cues,
            "errors": result.errors,
            "duration_seconds": result.duration_seconds,
            "processing_time_seconds": result.processing_time_seconds,
        }

        meta_path = output_dir / "pipeline_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        console.print(f"[dim]Metadata saved: {meta_path}[/]")
