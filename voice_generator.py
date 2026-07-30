"""
Voice Generator Module
Generates AI voiceovers using ElevenLabs API.
Supports per-channel voice configuration and batch generation.
"""

import json
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console

from config.settings import API_KEYS, CHANNELS, OUTPUT_DIR

console = Console()


class VoiceGenerator:
    """Generate voiceovers using ElevenLabs Text-to-Speech API."""

    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, voice_id: str = None):
        self.voice_id = voice_id or API_KEYS.elevenlabs_voice_id
        if not API_KEYS.elevenlabs:
            console.print("[yellow]⚠ ElevenLabs API key not set. Voice generation unavailable.[/]")

    @property
    def headers(self):
        return {
            "xi-api-key": API_KEYS.elevenlabs,
            "Content-Type": "application/json",
        }

    def list_voices(self) -> list[dict]:
        """List all available voices."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/voices",
                headers=self.headers,
                timeout=15,
            )
            response.raise_for_status()
            voices = response.json().get("voices", [])

            console.print(f"\n[bold]Available Voices ({len(voices)}):[/]")
            for v in voices:
                labels = v.get("labels", {})
                accent = labels.get("accent", "")
                gender = labels.get("gender", "")
                console.print(f"  {v['voice_id']}: {v['name']} ({gender}, {accent})")

            return voices

        except Exception as e:
            console.print(f"[red]✗ Failed to list voices: {e}[/]")
            return []

    def generate(
        self,
        text: str,
        output_path: Path = None,
        voice_id: str = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        model_id: str = "eleven_monolingual_v1",
    ) -> Optional[Path]:
        """Generate voiceover audio from text.

        Args:
            text: The script text to convert to speech
            output_path: Where to save the audio file
            voice_id: Override default voice ID
            stability: Voice stability (0-1). Lower = more expressive
            similarity_boost: Voice clarity (0-1). Higher = clearer
            style: Style exaggeration (0-1). Higher = more stylized
            model_id: ElevenLabs model to use

        Returns:
            Path to generated audio file
        """
        if not API_KEYS.elevenlabs:
            console.print("[red]✗ ElevenLabs API key required[/]")
            return None

        vid = voice_id or self.voice_id
        if not vid:
            console.print("[red]✗ No voice_id specified. Run list_voices() to find one.[/]")
            return None

        if output_path is None:
            output_path = OUTPUT_DIR / "voiceover.mp3"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        console.print(f"[blue]Generating voiceover ({len(text.split())} words)...[/]")

        try:
            response = requests.post(
                f"{self.BASE_URL}/text-to-speech/{vid}",
                headers=self.headers,
                json={
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": {
                        "stability": stability,
                        "similarity_boost": similarity_boost,
                        "style": style,
                    },
                },
                timeout=60,
            )
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

            console.print(f"[green]✓ Voiceover saved: {output_path.name}[/]")
            return output_path

        except requests.exceptions.HTTPError as e:
            error_body = e.response.text if e.response else ""
            console.print(f"[red]✗ ElevenLabs API error: {e}\n{error_body}[/]")
            return None
        except Exception as e:
            console.print(f"[red]✗ Voice generation error: {e}[/]")
            return None

    def generate_for_channel(
        self,
        text: str,
        channel_key: str,
        output_path: Path = None,
    ) -> Optional[Path]:
        """Generate voiceover with channel-specific voice settings."""
        channel = CHANNELS.get(channel_key)
        if not channel:
            console.print(f"[red]✗ Unknown channel: {channel_key}[/]")
            return None

        vid = channel.voice_id or self.voice_id

        return self.generate(
            text=text,
            output_path=output_path,
            voice_id=vid,
            stability=channel.voice_stability,
            similarity_boost=channel.voice_similarity,
        )

    def get_usage(self) -> Optional[dict]:
        """Check API usage and remaining characters."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/user/subscription",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            used = data.get("character_count", 0)
            limit = data.get("character_limit", 0)
            remaining = limit - used

            console.print(f"\n[bold]ElevenLabs Usage:[/]")
            console.print(f"  Characters used: {used:,}")
            console.print(f"  Character limit: {limit:,}")
            console.print(f"  Remaining: {remaining:,}")
            console.print(f"  Tier: {data.get('tier', 'unknown')}")

            return data

        except Exception as e:
            console.print(f"[red]✗ Failed to get usage: {e}[/]")
            return None


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
        from config.settings import CAPTIONS_DIR
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

