"""
Video Pipeline — AI-Powered YouTube Shorts Production System

Modules:
  - script_generator: GPT-4 powered script writing per channel
  - transcript_manager: YouTube transcript download, indexing, semantic search
  - clip_finder: Multi-source clip finding (YouTube, Pexels, Reddit, Internet Archive)
  - voice_generator: ElevenLabs voiceover + Whisper captions
  - video_assembler: FFmpeg-based video assembly (concat, audio, captions)
  - thumbnail_generator: Pillow-based thumbnail generation
  - data_visualizer: Charts and number graphics (matplotlib)
  - screen_recorder: Playwright-based website recording
  - pipeline: Master orchestration pipeline
  - channel_pipelines: Pre-configured shortcuts per channel
  - cli: Command-line interface

Usage:
  # CLI
  python cli.py run --topic "Sabrina Carpenter almost quit" --channel taylor_sabrina
  python cli.py script --topic "Apple almost died" --channel one_decision
  python cli.py check-setup

  # Python API
  from pipeline import MasterPipeline
  p = MasterPipeline()
  result = p.run("Sabrina Carpenter almost quit", "taylor_sabrina")
"""

__version__ = "1.0.0"

