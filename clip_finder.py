"""
Clip Finder Module
Finds and downloads video clips from multiple sources:
  - YouTube (via transcript matching + yt-dlp)
  - Pexels (stock footage)
  - Pixabay (stock footage)
  - Internet Archive (archival footage)
  - Reddit (images for "Rank the Room" channel)
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console
from tqdm import tqdm

from config.settings import CLIPS_DIR, API_KEYS, CHANNELS

console = Console()


class YouTubeClipDownloader:
    """Downloads specific segments from YouTube videos using yt-dlp."""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or CLIPS_DIR
        self._check_ytdlp()

    def _check_ytdlp(self):
        """Verify yt-dlp is installed."""
        if not shutil.which("yt-dlp"):
            console.print("[red]✗ yt-dlp not found. Install with: pip install yt-dlp[/]")
            raise RuntimeError("yt-dlp not installed")

    def download_segment(
        self,
        video_id: str,
        start_time: float,
        end_time: float,
        output_name: str = None,
        max_height: int = 1080,
    ) -> Optional[Path]:
        """Download a specific time segment from a YouTube video.

        Args:
            video_id: YouTube video ID
            start_time: Start time in seconds
            end_time: End time in seconds
            output_name: Custom output filename (without extension)
            max_height: Maximum video height

        Returns:
            Path to downloaded clip, or None on failure
        """
        if output_name is None:
            output_name = f"{video_id}_{start_time:.0f}_{end_time:.0f}"

        output_path = self.output_dir / f"{output_name}.mp4"

        if output_path.exists():
            console.print(f"[yellow]⚠ Clip already exists: {output_path.name}[/]")
            return output_path

        url = f"https://www.youtube.com/watch?v={video_id}"
        section = f"*{start_time}-{end_time}"

        console.print(f"[blue]Downloading clip: {video_id} [{start_time:.1f}s - {end_time:.1f}s][/]")

        try:
            result = subprocess.run(
                [
                    "yt-dlp",
                    "--download-sections", section,
                    "-f", f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]",
                    "--merge-output-format", "mp4",
                    "-o", str(output_path),
                    "--no-playlist",
                    "--quiet",
                    url,
                ],
                capture_output=True, text=True, timeout=120,
            )

            if output_path.exists():
                console.print(f"[green]✓ Downloaded: {output_path.name}[/]")
                return output_path
            else:
                console.print(f"[red]✗ Download failed: {result.stderr[:200]}[/]")
                return None

        except subprocess.TimeoutExpired:
            console.print(f"[red]✗ Download timed out for {video_id}[/]")
            return None
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/]")
            return None

    def download_full_video(self, video_id: str, max_height: int = 1080) -> Optional[Path]:
        """Download a full YouTube video."""
        output_path = self.output_dir / f"{video_id}_full.mp4"
        if output_path.exists():
            return output_path

        url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            subprocess.run(
                [
                    "yt-dlp",
                    "-f", f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]",
                    "--merge-output-format", "mp4",
                    "-o", str(output_path),
                    "--no-playlist",
                    "--quiet",
                    url,
                ],
                capture_output=True, text=True, timeout=600,
            )

            if output_path.exists():
                console.print(f"[green]✓ Downloaded full video: {output_path.name}[/]")
                return output_path
            return None

        except Exception as e:
            console.print(f"[red]✗ Error downloading full video: {e}[/]")
            return None

    def download_clips_from_matches(self, clip_map: list[dict]) -> list[dict]:
        """Download clips for each script line based on transcript match results.

        Args:
            clip_map: Output from TranscriptIndex.find_clips_for_script()

        Returns:
            Updated clip_map with 'clip_path' added to each best match
        """
        for item in clip_map:
            match = item.get("best_match")
            if not match:
                continue

            clip_path = self.download_segment(
                video_id=match["video_id"],
                start_time=match["start_time"],
                end_time=match["end_time"],
            )
            item["clip_path"] = str(clip_path) if clip_path else None

        return clip_map


class PexelsClient:
    """Search and download stock footage from Pexels."""

    BASE_URL = "https://api.pexels.com"

    def __init__(self):
        if not API_KEYS.pexels:
            console.print("[yellow]⚠ Pexels API key not set. Stock footage search unavailable.[/]")
        self.headers = {"Authorization": API_KEYS.pexels}

    def search_videos(self, query: str, per_page: int = 5, orientation: str = "portrait") -> list[dict]:
        """Search for stock videos on Pexels.

        Args:
            query: Search keywords
            per_page: Number of results
            orientation: 'portrait' for Shorts, 'landscape' for long-form

        Returns:
            List of video results with download URLs
        """
        if not API_KEYS.pexels:
            return []

        try:
            response = requests.get(
                f"{self.BASE_URL}/videos/search",
                headers=self.headers,
                params={
                    "query": query,
                    "per_page": per_page,
                    "orientation": orientation,
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for video in data.get("videos", []):
                # Find the best quality file
                video_files = sorted(
                    video.get("video_files", []),
                    key=lambda x: x.get("height", 0),
                    reverse=True,
                )
                if video_files:
                    best = video_files[0]
                    results.append({
                        "id": video["id"],
                        "url": video["url"],
                        "download_url": best["link"],
                        "width": best.get("width"),
                        "height": best.get("height"),
                        "duration": video.get("duration"),
                        "photographer": video.get("user", {}).get("name", "Unknown"),
                    })

            console.print(f"[green]✓ Pexels: Found {len(results)} videos for '{query}'[/]")
            return results

        except Exception as e:
            console.print(f"[red]✗ Pexels search error: {e}[/]")
            return []

    def search_photos(self, query: str, per_page: int = 5) -> list[dict]:
        """Search for stock photos on Pexels (for channels using still images)."""
        if not API_KEYS.pexels:
            return []

        try:
            response = requests.get(
                f"{self.BASE_URL}/v1/search",
                headers=self.headers,
                params={"query": query, "per_page": per_page},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for photo in data.get("photos", []):
                results.append({
                    "id": photo["id"],
                    "url": photo["url"],
                    "download_url": photo["src"]["original"],
                    "large_url": photo["src"]["large2x"],
                    "width": photo["width"],
                    "height": photo["height"],
                    "photographer": photo.get("photographer", "Unknown"),
                })

            console.print(f"[green]✓ Pexels: Found {len(results)} photos for '{query}'[/]")
            return results

        except Exception as e:
            console.print(f"[red]✗ Pexels photo search error: {e}[/]")
            return []

    def download_video(self, download_url: str, filename: str) -> Optional[Path]:
        """Download a stock video file."""
        output_path = CLIPS_DIR / filename
        if output_path.exists():
            return output_path

        try:
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            console.print(f"[green]✓ Downloaded stock clip: {filename}[/]")
            return output_path

        except Exception as e:
            console.print(f"[red]✗ Download error: {e}[/]")
            return None

    def download_photo(self, download_url: str, filename: str) -> Optional[Path]:
        """Download a stock photo."""
        output_path = CLIPS_DIR / filename
        if output_path.exists():
            return output_path

        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            console.print(f"[green]✓ Downloaded stock photo: {filename}[/]")
            return output_path

        except Exception as e:
            console.print(f"[red]✗ Photo download error: {e}[/]")
            return None


class StockFootageFinder:
    """Unified stock footage finder — tries multiple sources."""

    def __init__(self):
        self.pexels = PexelsClient()

    def find_footage(
        self,
        query: str,
        video_count: int = 3,
        photo_count: int = 3,
        orientation: str = "portrait",
    ) -> dict:
        """Search for footage across all available stock sources.

        Returns dict with 'videos' and 'photos' lists.
        """
        console.print(f"[blue]Searching stock footage: '{query}'[/]")

        results = {
            "query": query,
            "videos": self.pexels.search_videos(query, per_page=video_count, orientation=orientation),
            "photos": self.pexels.search_photos(query, per_page=photo_count),
        }

        return results

    def find_footage_for_script(
        self,
        visual_cues: list[dict],
        download: bool = False,
    ) -> list[dict]:
        """Find stock footage for each visual cue from a script.

        Args:
            visual_cues: Output from ScriptGenerator.extract_visual_cues()
            download: Whether to download the best match immediately

        Returns:
            List of footage results per script line
        """
        footage_map = []

        for cue in visual_cues:
            keywords = cue.get("search_keywords", [])
            query = " ".join(keywords) if isinstance(keywords, list) else str(keywords)

            results = self.find_footage(query, video_count=2, photo_count=2)

            entry = {
                "script_line": cue.get("line", ""),
                "visual_description": cue.get("visual_description", ""),
                "search_query": query,
                "footage": results,
                "downloaded_path": None,
            }

            if download and results["videos"]:
                best = results["videos"][0]
                ext = "mp4"
                filename = f"stock_{best['id']}.{ext}"
                path = self.pexels.download_video(best["download_url"], filename)
                entry["downloaded_path"] = str(path) if path else None

            footage_map.append(entry)

        return footage_map


class RedditImageScraper:
    """Scrapes room images from Reddit for 'Rank the Room' channel."""

    def __init__(self):
        self._reddit = None

    @property
    def reddit(self):
        if self._reddit is None:
            import praw
            self._reddit = praw.Reddit(
                client_id=API_KEYS.reddit_client_id,
                client_secret=API_KEYS.reddit_client_secret,
                user_agent=API_KEYS.reddit_user_agent,
            )
        return self._reddit

    def fetch_room_images(
        self,
        subreddits: list[str] = None,
        sort: str = "top",
        time_filter: str = "week",
        limit: int = 20,
    ) -> list[dict]:
        """Fetch room images from interior design subreddits.

        Args:
            subreddits: List of subreddit names
            sort: 'top', 'hot', 'new'
            time_filter: 'day', 'week', 'month', 'year', 'all'
            limit: Max posts per subreddit
        """
        if subreddits is None:
            subreddits = [
                "malelivingspace",
                "femalelivingspace",
                "RoomPorn",
                "AmateurRoomPorn",
                "CozyPlaces",
            ]

        results = []
        for sub_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(sub_name)
                if sort == "top":
                    posts = subreddit.top(time_filter=time_filter, limit=limit)
                elif sort == "hot":
                    posts = subreddit.hot(limit=limit)
                else:
                    posts = subreddit.new(limit=limit)

                for post in posts:
                    if post.url and any(post.url.endswith(ext) for ext in [".jpg", ".png", ".jpeg", ".webp"]):
                        results.append({
                            "title": post.title,
                            "url": post.url,
                            "subreddit": sub_name,
                            "score": post.score,
                            "permalink": f"https://reddit.com{post.permalink}",
                            "author": str(post.author),
                        })

                console.print(f"[green]✓ r/{sub_name}: Found {len([r for r in results if r['subreddit'] == sub_name])} images[/]")

            except Exception as e:
                console.print(f"[red]✗ r/{sub_name} error: {e}[/]")

        console.print(f"[bold green]Total room images found: {len(results)}[/]")
        return results

    def download_image(self, url: str, filename: str) -> Optional[Path]:
        """Download a single image."""
        output_path = CLIPS_DIR / filename
        if output_path.exists():
            return output_path

        try:
            response = requests.get(url, timeout=15, headers={"User-Agent": "video_pipeline/1.0"})
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

            return output_path

        except Exception as e:
            console.print(f"[red]✗ Image download error: {e}[/]")
            return None


class InternetArchiveClient:
    """Search Internet Archive for archival footage and old commercials."""

    BASE_URL = "https://archive.org"

    def search(self, query: str, media_type: str = "movies", rows: int = 10) -> list[dict]:
        """Search Internet Archive.

        Args:
            query: Search keywords
            media_type: 'movies', 'image', 'audio'
            rows: Number of results
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/advancedsearch.php",
                params={
                    "q": query,
                    "mediatype": media_type,
                    "rows": rows,
                    "output": "json",
                    "fl[]": ["identifier", "title", "description", "mediatype"],
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for doc in data.get("response", {}).get("docs", []):
                results.append({
                    "identifier": doc.get("identifier"),
                    "title": doc.get("title"),
                    "description": doc.get("description", ""),
                    "url": f"{self.BASE_URL}/details/{doc.get('identifier')}",
                    "download_base": f"{self.BASE_URL}/download/{doc.get('identifier')}",
                })

            console.print(f"[green]✓ Internet Archive: Found {len(results)} results for '{query}'[/]")
            return results

        except Exception as e:
            console.print(f"[red]✗ Internet Archive search error: {e}[/]")
            return []

    def get_wayback_snapshot(self, url: str, timestamp: str = "") -> Optional[str]:
        """Get a Wayback Machine snapshot URL for a website.

        Args:
            url: The original URL
            timestamp: Optional timestamp in YYYYMMDD format
        """
        try:
            params = {"url": url}
            if timestamp:
                params["timestamp"] = timestamp

            response = requests.get(
                f"{self.BASE_URL}/wayback/available",
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            snapshot = data.get("archived_snapshots", {}).get("closest", {})
            if snapshot and snapshot.get("available"):
                return snapshot["url"]
            return None

        except Exception as e:
            console.print(f"[red]✗ Wayback error: {e}[/]")
            return None

