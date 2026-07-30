"""
Video Assembler Module
Assembles final videos from clips, voiceover, and captions.
Handles clip cutting, concatenation, audio mixing, caption burning, and Ken Burns effects.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional

from rich.console import Console

from config.settings import OUTPUT_DIR, CLIPS_DIR, CAPTIONS_DIR

console = Console()


class FFmpegProcessor:
    """Low-level FFmpeg operations for video processing."""

    def __init__(self):
        if not shutil.which("ffmpeg"):
            console.print("[red]✗ FFmpeg not found. Install from https://ffmpeg.org/[/]")
            raise RuntimeError("FFmpeg not installed")

    def cut_clip(
        self,
        input_path: Path,
        output_path: Path,
        start_seconds: float,
        end_seconds: float,
    ) -> Optional[Path]:
        """Cut a segment from a video file."""
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(input_path),
                    "-ss", str(start_seconds),
                    "-to", str(end_seconds),
                    "-c", "copy",
                    "-avoid_negative_ts", "make_zero",
                    str(output_path),
                ],
                capture_output=True, text=True, timeout=60,
            )
            if output_path.exists():
                return output_path
            return None
        except Exception as e:
            console.print(f"[red]✗ FFmpeg cut error: {e}[/]")
            return None

    def get_duration(self, file_path: Path) -> float:
        """Get duration of a video/audio file in seconds."""
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(file_path),
                ],
                capture_output=True, text=True, timeout=15,
            )
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    def get_resolution(self, file_path: Path) -> tuple:
        """Get video resolution (width, height)."""
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "csv=p=0",
                    str(file_path),
                ],
                capture_output=True, text=True, timeout=15,
            )
            parts = result.stdout.strip().split(",")
            return int(parts[0]), int(parts[1])
        except Exception:
            return 0, 0

    def scale_to_shorts(
        self,
        input_path: Path,
        output_path: Path,
        width: int = 1080,
        height: int = 1920,
    ) -> Optional[Path]:
        """Scale/crop a video to vertical Shorts format (9:16)."""
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(input_path),
                    "-vf", (
                        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                        f"crop={width}:{height}"
                    ),
                    "-c:a", "copy",
                    str(output_path),
                ],
                capture_output=True, text=True, timeout=120,
            )
            if output_path.exists():
                return output_path
            return None
        except Exception as e:
            console.print(f"[red]✗ Scale error: {e}[/]")
            return None

    def image_to_video(
        self,
        image_path: Path,
        output_path: Path,
        duration: float = 5.0,
        ken_burns: bool = True,
        width: int = 1080,
        height: int = 1920,
    ) -> Optional[Path]:
        """Convert a still image to a video clip with optional Ken Burns zoom effect."""
        try:
            if ken_burns:
                # Slow zoom in effect
                vf = (
                    f"scale=8000:-1,"
                    f"zoompan=z='min(zoom+0.001,1.5)':d={int(duration * 30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30"
                )
            else:
                vf = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"

            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-loop", "1",
                    "-i", str(image_path),
                    "-vf", vf,
                    "-t", str(duration),
                    "-pix_fmt", "yuv420p",
                    "-c:v", "libx264",
                    "-r", "30",
                    str(output_path),
                ],
                capture_output=True, text=True, timeout=120,
            )
            if output_path.exists():
                return output_path
            return None
        except Exception as e:
            console.print(f"[red]✗ Image to video error: {e}[/]")
            return None

    def add_audio_to_video(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
    ) -> Optional[Path]:
        """Replace/add audio track to a video."""
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-shortest",
                    str(output_path),
                ],
                capture_output=True, text=True, timeout=120,
            )
            if output_path.exists():
                return output_path
            return None
        except Exception as e:
            console.print(f"[red]✗ Audio merge error: {e}[/]")
            return None

    def mix_retention_audio(
        self,
        video_path: Path,
        narration_path: Path,
        output_path: Path,
        background_audio_path: Path = None,
        sound_events: list[dict] = None,
        background_gain_db: float = -21.0,
        target_lufs: float = -16.0,
        true_peak_dbtp: float = -1.5,
    ) -> Optional[Path]:
        """Mix narration, an optional looping bed, and timestamped sound events.

        ``sound_events`` accepts dictionaries with:

        - ``path``: audio asset path
        - ``start_seconds``: timeline start
        - ``gain_db``: event gain relative to its source, default ``-12``

        Narration stays first in the ``amix`` input order so the final mix ends
        with the narration rather than an endlessly looped background bed.
        """
        events = sound_events or []
        duration = self.get_duration(narration_path)
        if duration <= 0:
            console.print("[red]✗ Retention mix requires valid narration audio[/]")
            return None

        inputs = ["-i", str(video_path), "-i", str(narration_path)]
        filter_parts = [
            "[1:a]aresample=48000,"
            "aformat=sample_fmts=fltp:channel_layouts=stereo[voice]"
        ]
        mix_labels = ["[voice]"]
        next_input = 2

        if background_audio_path:
            background_audio_path = Path(background_audio_path)
            if not background_audio_path.exists():
                console.print(f"[red]✗ Background audio not found: {background_audio_path}[/]")
                return None
            inputs.extend(["-stream_loop", "-1", "-i", str(background_audio_path)])
            fade_out_start = max(0.0, duration - 0.4)
            filter_parts.append(
                f"[{next_input}:a]aresample=48000,"
                "aformat=sample_fmts=fltp:channel_layouts=stereo,"
                f"volume={background_gain_db}dB,atrim=0:{duration:.3f},"
                "afade=t=in:st=0:d=0.25,"
                f"afade=t=out:st={fade_out_start:.3f}:d=0.4[bed]"
            )
            mix_labels.append("[bed]")
            next_input += 1

        for index, event in enumerate(events):
            event_asset = event.get("path")
            if not event_asset:
                console.print(f"[red]✗ Sound event {index} is missing a path[/]")
                return None
            event_path = Path(event_asset)
            if not event_path.exists():
                console.print(f"[red]✗ Sound event not found: {event_path}[/]")
                return None
            start_seconds = max(0.0, float(event.get("start_seconds", 0.0)))
            gain_db = float(event.get("gain_db", -12.0))
            delay_ms = round(start_seconds * 1000)
            label = f"sfx{index}"
            inputs.extend(["-i", str(event_path)])
            filter_parts.append(
                f"[{next_input}:a]aresample=48000,"
                "aformat=sample_fmts=fltp:channel_layouts=stereo,"
                f"volume={gain_db}dB,adelay={delay_ms}|{delay_ms}[{label}]"
            )
            mix_labels.append(f"[{label}]")
            next_input += 1

        filter_parts.append(
            "".join(mix_labels)
            + f"amix=inputs={len(mix_labels)}:duration=first:dropout_transition=0,"
            f"loudnorm=I={target_lufs}:TP={true_peak_dbtp}:LRA=7[mix]"
        )

        try:
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    *inputs,
                    "-filter_complex", ";".join(filter_parts),
                    "-map", "0:v:0",
                    "-map", "[mix]",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "256k",
                    "-ar", "48000",
                    "-shortest",
                    "-movflags", "+faststart",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                timeout=max(180, int(duration * 5)),
                check=True,
            )
            if output_path.exists():
                return output_path
            return None
        except Exception as e:
            console.print(f"[red]✗ Retention audio mix error: {e}[/]")
            return None

    def burn_captions(
        self,
        video_path: Path,
        srt_path: Path,
        output_path: Path,
        font_name: str = "Arial",
        font_size: int = 22,
        font_color: str = "&HFFFFFF",
        outline_color: str = "&H000000",
        outline_width: int = 2,
        position: str = "center",
    ) -> Optional[Path]:
        """Burn SRT captions into video.

        Args:
            position: 'center', 'bottom', 'top'
        """
        margin_v = {"center": 0, "bottom": 40, "top": 40}.get(position, 0)
        alignment = {"center": 10, "bottom": 2, "top": 6}.get(position, 10)

        style = (
            f"FontName={font_name},"
            f"FontSize={font_size},"
            f"PrimaryColour={font_color},"
            f"OutlineColour={outline_color},"
            f"Outline={outline_width},"
            f"MarginV={margin_v},"
            f"Alignment={alignment}"
        )

        try:
            # Escape path for FFmpeg filter
            srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")

            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(video_path),
                    "-vf", f"subtitles={srt_escaped}:force_style='{style}'",
                    "-c:a", "copy",
                    str(output_path),
                ],
                capture_output=True, text=True, timeout=180,
            )
            if output_path.exists():
                console.print(f"[green]✓ Captions burned: {output_path.name}[/]")
                return output_path
            return None
        except Exception as e:
            console.print(f"[red]✗ Caption burn error: {e}[/]")
            return None

    def concatenate_clips(
        self,
        clip_paths: list[Path],
        output_path: Path,
        normalize_resolution: bool = True,
        width: int = 1080,
        height: int = 1920,
    ) -> Optional[Path]:
        """Concatenate multiple clips into one video.

        If normalize_resolution is True, all clips are scaled to the same resolution first.
        """
        if not clip_paths:
            console.print("[red]✗ No clips to concatenate[/]")
            return None

        working_dir = output_path.parent / "temp_concat"
        working_dir.mkdir(exist_ok=True)

        try:
            processed_clips = []

            if normalize_resolution:
                console.print(f"[blue]Normalizing {len(clip_paths)} clips to {width}x{height}...[/]")
                for i, clip in enumerate(clip_paths):
                    normalized = working_dir / f"norm_{i:03d}.mp4"
                    result = self.scale_to_shorts(clip, normalized, width, height)
                    if result:
                        processed_clips.append(result)
                    else:
                        console.print(f"[yellow]⚠ Skipping clip {clip.name} (normalization failed)[/]")
            else:
                processed_clips = clip_paths

            if not processed_clips:
                console.print("[red]✗ No valid clips after processing[/]")
                return None

            # Create file list for FFmpeg concat
            list_file = working_dir / "concat_list.txt"
            with open(list_file, "w") as f:
                for clip in processed_clips:
                    f.write(f"file '{clip}'\n")

            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", str(list_file),
                    "-c", "copy",
                    str(output_path),
                ],
                capture_output=True, text=True, timeout=300,
            )

            # Cleanup
            shutil.rmtree(working_dir, ignore_errors=True)

            if output_path.exists():
                duration = self.get_duration(output_path)
                console.print(f"[green]✓ Concatenated {len(processed_clips)} clips → {output_path.name} ({duration:.1f}s)[/]")
                return output_path
            return None

        except Exception as e:
            shutil.rmtree(working_dir, ignore_errors=True)
            console.print(f"[red]✗ Concatenation error: {e}[/]")
            return None


class VideoAssembler:
    """High-level video assembly — puts together the final video from components."""

    def __init__(self):
        self.ffmpeg = FFmpegProcessor()

    def assemble_from_clips(
        self,
        clip_paths: list[Path],
        voiceover_path: Path,
        output_name: str,
        srt_path: Path = None,
        shorts_format: bool = True,
        background_audio_path: Path = None,
        sound_events: list[dict] = None,
    ) -> Optional[Path]:
        """Assemble video from clips, narration, optional retention audio, and captions.

        Pipeline:
          1. Concatenate all clips
          2. Add voiceover and optional licensed sound bed/events
          3. Burn captions (if SRT provided)
          4. Output final video
        """
        console.print(f"\n[bold blue]═══ Assembling Video: {output_name} ═══[/]")

        output_dir = OUTPUT_DIR / output_name
        output_dir.mkdir(parents=True, exist_ok=True)

        width, height = (1080, 1920) if shorts_format else (1920, 1080)

        # Step 1: Concatenate clips
        console.print("[bold]Step 1/3: Concatenating clips...[/]")
        concat_path = output_dir / "concatenated.mp4"
        result = self.ffmpeg.concatenate_clips(clip_paths, concat_path, width=width, height=height)
        if not result:
            console.print("[red]✗ Assembly failed at concatenation[/]")
            return None

        # Step 2: Add voiceover and optional retention audio
        console.print("[bold]Step 2/3: Adding narration and retention audio...[/]")
        with_audio_path = output_dir / "with_audio.mp4"
        if background_audio_path or sound_events:
            result = self.ffmpeg.mix_retention_audio(
                concat_path,
                voiceover_path,
                with_audio_path,
                background_audio_path=background_audio_path,
                sound_events=sound_events,
            )
        else:
            result = self.ffmpeg.add_audio_to_video(concat_path, voiceover_path, with_audio_path)
        if not result:
            console.print("[red]✗ Assembly failed at audio merge[/]")
            return None

        # Step 3: Burn captions
        if srt_path and srt_path.exists():
            console.print("[bold]Step 3/3: Burning captions...[/]")
            final_path = output_dir / f"{output_name}_final.mp4"
            result = self.ffmpeg.burn_captions(with_audio_path, srt_path, final_path)
            if not result:
                console.print("[yellow]⚠ Caption burn failed, using video without captions[/]")
                final_path = with_audio_path
        else:
            console.print("[dim]Step 3/3: No captions to burn, skipping[/]")
            final_path = with_audio_path

        console.print(f"\n[bold green]✓ Video assembled: {final_path}[/]")
        console.print(f"[dim]Duration: {self.ffmpeg.get_duration(final_path):.1f}s[/]")

        return final_path

    def assemble_from_images(
        self,
        image_paths: list[Path],
        durations: list[float],
        voiceover_path: Path,
        output_name: str,
        ken_burns: bool = True,
        srt_path: Path = None,
        shorts_format: bool = True,
        background_audio_path: Path = None,
        sound_events: list[dict] = None,
    ) -> Optional[Path]:
        """Assemble images with narration, optional retention audio, and captions.

        Converts each image to a video clip with Ken Burns effect, then assembles.
        """
        console.print(f"\n[bold blue]═══ Assembling from Images: {output_name} ═══[/]")

        output_dir = OUTPUT_DIR / output_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Convert images to video clips
        clip_paths = []
        for i, (img, dur) in enumerate(zip(image_paths, durations)):
            clip_path = output_dir / f"img_clip_{i:03d}.mp4"
            result = self.ffmpeg.image_to_video(
                img, clip_path, duration=dur, ken_burns=ken_burns,
            )
            if result:
                clip_paths.append(result)
            else:
                console.print(f"[yellow]⚠ Skipping image {img.name}[/]")

        if not clip_paths:
            console.print("[red]✗ No image clips generated[/]")
            return None

        return self.assemble_from_clips(
            clip_paths=clip_paths,
            voiceover_path=voiceover_path,
            output_name=output_name,
            srt_path=srt_path,
            shorts_format=shorts_format,
            background_audio_path=background_audio_path,
            sound_events=sound_events,
        )

    def assemble_mixed(
        self,
        media_items: list[dict],
        voiceover_path: Path,
        output_name: str,
        srt_path: Path = None,
        shorts_format: bool = True,
        background_audio_path: Path = None,
        sound_events: list[dict] = None,
    ) -> Optional[Path]:
        """Assemble mixed media with optional retention audio and captions.

        Args:
            media_items: List of dicts with keys:
                'path': Path to file
                'type': 'video' or 'image'
                'duration': Duration in seconds (for images)
        """
        console.print(f"\n[bold blue]═══ Assembling Mixed Media: {output_name} ═══[/]")

        output_dir = OUTPUT_DIR / output_name
        output_dir.mkdir(parents=True, exist_ok=True)

        clip_paths = []
        for i, item in enumerate(media_items):
            path = Path(item["path"])
            media_type = item.get("type", "video")

            if media_type == "image":
                clip_path = output_dir / f"mixed_clip_{i:03d}.mp4"
                result = self.ffmpeg.image_to_video(
                    path, clip_path,
                    duration=item.get("duration", 5.0),
                    ken_burns=True,
                )
                if result:
                    clip_paths.append(result)
            elif media_type == "video":
                clip_paths.append(path)

        if not clip_paths:
            console.print("[red]✗ No valid media items[/]")
            return None

        return self.assemble_from_clips(
            clip_paths=clip_paths,
            voiceover_path=voiceover_path,
            output_name=output_name,
            srt_path=srt_path,
            shorts_format=shorts_format,
            background_audio_path=background_audio_path,
            sound_events=sound_events,
        )
