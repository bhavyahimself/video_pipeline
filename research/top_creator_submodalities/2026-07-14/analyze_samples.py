from __future__ import annotations

import json
import math
import re
import shlex
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
FRAMES = ROOT / "frames"
OUT = ROOT / "analysis.json"

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

FRAMES.mkdir(exist_ok=True)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def ffprobe_json(video: Path) -> dict:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(video),
        ]
    )
    return json.loads(result.stdout)


def volumedetect(video: Path) -> tuple[float | None, float | None]:
    result = subprocess.run(
        ["ffmpeg", "-i", str(video), "-af", "volumedetect", "-f", "null", "-"],
        text=True,
        capture_output=True,
        check=False,
    )
    stderr = result.stderr
    mean_match = re.search(r"mean_volume:\s*(-?\d+(\.\d+)?) dB", stderr)
    max_match = re.search(r"max_volume:\s*(-?\d+(\.\d+)?) dB", stderr)
    mean = float(mean_match.group(1)) if mean_match else None
    peak = float(max_match.group(1)) if max_match else None
    return mean, peak


def yavg_samples(video: Path) -> list[tuple[float, float]]:
    result = subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(video),
            "-vf",
            "signalstats,metadata=print:file=-",
            "-an",
            "-f",
            "null",
            "-",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    samples: list[tuple[float, float]] = []
    current_time: float | None = None
    for line in result.stdout.splitlines():
        line = line.strip()
        if "pts_time:" in line:
            try:
                current_time = float(line.split("pts_time:")[1])
            except ValueError:
                current_time = None
        elif "lavfi.signalstats.YAVG=" in line and current_time is not None:
            try:
                value = float(line.split("=")[-1])
                samples.append((current_time, value))
            except ValueError:
                pass
    return samples


def scene_cut_count(video: Path, threshold: float = 0.27) -> int:
    result = subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(video),
            "-vf",
            f"select=gt(scene\\,{threshold}),showinfo",
            "-an",
            "-f",
            "null",
            "-",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    return sum(1 for line in result.stderr.splitlines() if "showinfo" in line and "pts_time:" in line)


def extract_frame(video: Path, timestamp: float, output: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            f"{timestamp:.2f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            str(output),
            "-y",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def make_contact_sheet(images: list[Path], output: Path, label: str) -> None:
    thumbs = [Image.open(image).convert("RGB").resize((240, 426)) for image in images]
    canvas = Image.new("RGB", (240 * 3, 426 * 2 + 88), (12, 12, 14))
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(FONT_BOLD, 30)
    meta_font = ImageFont.truetype(FONT, 18)
    draw.text((24, 22), label, fill=(255, 255, 255), font=title_font)
    draw.text((24, 58), "Frames sampled across the timeline", fill=(180, 185, 192), font=meta_font)
    for index, thumb in enumerate(thumbs):
        x = (index % 3) * 240
        y = 88 + (index // 3) * 426
        canvas.paste(thumb, (x, y))
    canvas.save(output, quality=92)


def safe_mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def summarize(video: Path) -> dict:
    info = ffprobe_json(video)
    video_stream = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    duration = float(info["format"]["duration"])
    mean_db, peak_db = volumedetect(video)
    samples = yavg_samples(video)
    first_3_values = [value for time, value in samples if time <= 3.0]
    all_values = [value for _, value in samples]
    cuts = scene_cut_count(video)
    cuts_per_30 = round(cuts / duration * 30, 2) if duration else None

    timestamps = sorted(
        {
            0.35,
            max(0.35, duration * 0.2),
            max(0.35, duration * 0.4),
            max(0.35, duration * 0.6),
            max(0.35, duration * 0.8),
            max(0.35, duration - 0.65),
        }
    )
    frame_paths: list[Path] = []
    base = video.stem.replace(" ", "_")
    for index, timestamp in enumerate(timestamps):
        frame_path = FRAMES / f"{base}_{index+1:02d}.jpg"
        extract_frame(video, timestamp, frame_path)
        frame_paths.append(frame_path)
    make_contact_sheet(frame_paths, FRAMES / f"{base}_contact.jpg", video.stem)

    return {
        "file": video.name,
        "channel": video.stem.split("_")[0],
        "duration_seconds": round(duration, 2),
        "resolution": f"{video_stream['width']}x{video_stream['height']}",
        "avg_luma_first_3s": safe_mean(first_3_values),
        "avg_luma_full": safe_mean(all_values),
        "scene_cut_count": cuts,
        "scene_cuts_per_30s": cuts_per_30,
        "mean_volume_db": mean_db,
        "peak_volume_db": peak_db,
        "contact_sheet": str((FRAMES / f"{base}_contact.jpg").name),
        "sample_timestamps": [round(value, 2) for value in timestamps],
    }


def main() -> None:
    summaries = [summarize(video) for video in sorted(RAW.glob("*")) if video.is_file()]
    OUT.write_text(json.dumps(summaries, indent=2))
    print(OUT)


if __name__ == "__main__":
    main()
