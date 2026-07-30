"""VEED-only narration import and caption helpers.

Production text-to-speech is performed in VEED. This module deliberately does
not call an alternate TTS provider; it only validates/imports a VEED export.
"""

import shutil
from pathlib import Path
from typing import Optional

from rich.console import Console

from config.settings import CAPTIONS_DIR

console = Console()


class VeedOnlyProductionError(RuntimeError):
    """Raised when production code tries to generate speech outside VEED."""


class VoiceGenerator:
    """Fail-closed guard for the required VEED narration workflow."""

    def __init__(self, voice_id: str = None):
        self.voice_id = voice_id or "veed"

    def list_voices(self) -> list[dict]:
        """Reject provider voice discovery; select the voice in VEED."""
        raise VeedOnlyProductionError(
            "VEED is the only production TTS provider. Select and preview the voice in VEED."
        )

    @staticmethod
    def import_veed_export(
        export_path: Path,
        output_path: Path,
        project_id: str,
        voice_name: str,
    ) -> Path:
        """Import a reviewed VEED narration export into the pipeline."""
        if not project_id or not voice_name:
            raise VeedOnlyProductionError(
                "A VEED project ID and voice name are required for production narration."
            )
        source = Path(export_path)
        if not source.is_file():
            raise FileNotFoundError(f"VEED export not found: {source}")
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return destination

    def generate(self, text: str, output_path: Path = None, **_kwargs) -> Optional[Path]:
        """Reject direct TTS and require an imported VEED export."""
        raise VeedOnlyProductionError(
            "Direct TTS is disabled. Generate narration in a fresh VEED project, "
            "then call import_veed_export()."
        )

    def generate_for_channel(
        self,
        text: str,
        channel_key: str,
        output_path: Path = None,
    ) -> Optional[Path]:
        """Reject channel-level direct TTS requests."""
        raise VeedOnlyProductionError(
            "Channel narration must be exported from VEED and imported with "
            "import_veed_export()."
        )

    def get_usage(self) -> Optional[dict]:
        """Reject alternate-provider usage checks."""
        raise VeedOnlyProductionError(
            "Provider usage checks are disabled; manage production narration in VEED."
        )


class WhisperCaptionGenerator:
    """Generate captions/subtitles from audio using OpenAI Whisper."""

    def __init__(self):
        self._model = None

    def generate_srt(
        self,
        audio_path: Path,
        output_dir: Path = None,
        model_size: str = "base",
    ) -> Optional[Path]:
        """Generate SRT subtitle file from audio.

        Args:
            audio_path: Path to audio/video file
            output_dir: Where to save the SRT file
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')

        Returns:
            Path to generated SRT file
        """
        if output_dir is None:
            output_dir = CAPTIONS_DIR

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"[blue]Generating captions with Whisper ({model_size})...[/]")

        try:
            import subprocess
            result = subprocess.run(
                [
                    "whisper",
                    str(audio_path),
                    "--model", model_size,
                    "--output_format", "srt",
                    "--output_dir", str(output_dir),
                ],
                capture_output=True, text=True, timeout=300,
            )

            # Find the output SRT file
            srt_name = audio_path.stem + ".srt"
            srt_path = output_dir / srt_name

            if srt_path.exists():
                console.print(f"[green]✓ Captions generated: {srt_path.name}[/]")
                return srt_path
            else:
                console.print(f"[red]✗ SRT file not found at {srt_path}[/]")
                console.print(f"[dim]Whisper output: {result.stdout[:300]}[/]")
                return None

        except FileNotFoundError:
            console.print("[yellow]⚠ Whisper CLI not found. Trying Python API...[/]")
            return self._generate_srt_python(audio_path, output_dir, model_size)
        except Exception as e:
            console.print(f"[red]✗ Caption generation error: {e}[/]")
            return None

    def _generate_srt_python(
        self,
        audio_path: Path,
        output_dir: Path,
        model_size: str,
    ) -> Optional[Path]:
        """Fallback: use Whisper Python API directly."""
        try:
            import whisper

            if self._model is None or self._model_size != model_size:
                console.print(f"[blue]Loading Whisper model ({model_size})...[/]")
                self._model = whisper.load_model(model_size)
                self._model_size = model_size

            result = self._model.transcribe(str(audio_path))

            # Build SRT content
            srt_lines = []
            for i, seg in enumerate(result["segments"], 1):
                start = self._seconds_to_srt_time(seg["start"])
                end = self._seconds_to_srt_time(seg["end"])
                srt_lines.append(f"{i}\n{start} --> {end}\n{seg['text'].strip()}\n")

            srt_content = "\n".join(srt_lines)

            srt_path = output_dir / f"{audio_path.stem}.srt"
            with open(srt_path, "w") as f:
                f.write(srt_content)

            console.print(f"[green]✓ Captions generated: {srt_path.name}[/]")
            return srt_path

        except ImportError:
            console.print("[red]✗ Whisper not installed. Run: pip install openai-whisper[/]")
            return None
        except Exception as e:
            console.print(f"[red]✗ Whisper Python API error: {e}[/]")
            return None

    @staticmethod
    def _seconds_to_srt_time(seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
