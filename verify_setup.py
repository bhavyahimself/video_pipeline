"""Quick setup verification script."""
import shutil
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

results = []

# Check config imports
try:
    from config.settings import API_KEYS, CHANNELS, TRANSCRIPTS_DIR
    results.append("OK: config.settings imported")
    results.append(f"   Channels defined: {len(CHANNELS)}")
except Exception as e:
    results.append(f"FAIL: config.settings -> {e}")

# Check API keys
results.append("")
results.append("=== API Keys ===")
try:
    for name, val in [
        ("OpenAI", API_KEYS.openai),
        ("ElevenLabs", API_KEYS.elevenlabs),
        ("Pexels", API_KEYS.pexels),
        ("Reddit", API_KEYS.reddit_client_id),
    ]:
        status = "SET" if val else "NOT SET"
        results.append(f"   {name}: {status}")
except Exception as e:
    results.append(f"   Error: {e}")

# Check CLI tools
results.append("")
results.append("=== CLI Tools ===")
for tool in ["ffmpeg", "ffprobe", "yt-dlp", "whisper"]:
    path = shutil.which(tool)
    results.append(f"   {tool}: {'FOUND at ' + path if path else 'NOT FOUND'}")

# Check Python packages
results.append("")
results.append("=== Python Packages ===")
packages = [
    "openai", "chromadb", "youtube_transcript_api",
    "PIL", "requests", "click", "rich", "matplotlib",
    "tqdm", "pydantic",
]
for pkg in packages:
    try:
        __import__(pkg)
        results.append(f"   {pkg}: OK")
    except Exception as e:
        results.append(f"   {pkg}: FAIL ({str(e)[:60]})")

# Optional packages
results.append("")
results.append("=== Optional Packages ===")
optional = ["sentence_transformers", "praw", "moviepy", "playwright"]
for pkg in optional:
    try:
        __import__(pkg)
        results.append(f"   {pkg}: OK")
    except Exception as e:
        results.append(f"   {pkg}: NOT INSTALLED ({str(e)[:50]})")

# Check module imports
results.append("")
results.append("=== Pipeline Modules ===")
modules = [
    "script_generator",
    "transcript_manager",
    "clip_finder",
    "voice_generator",
    "video_assembler",
    "thumbnail_generator",
    "data_visualizer",
    "screen_recorder",
    "pipeline",
    "channel_pipelines",
]
for mod in modules:
    try:
        __import__(mod)
        results.append(f"   {mod}: OK")
    except Exception as e:
        results.append(f"   {mod}: FAIL ({str(e)[:60]})")

# Write results to file
output = "\n".join(results)
print(output)

with open("_setup_check.txt", "w") as f:
    f.write(output)

