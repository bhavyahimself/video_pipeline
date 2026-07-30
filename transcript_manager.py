"""
Transcript Manager Module
Downloads, stores, and indexes YouTube video transcripts.
Provides semantic search to find clips matching script lines.
"""

import json
import hashlib
from pathlib import Path
from typing import Optional

from rich.console import Console
from tqdm import tqdm

from config.settings import TRANSCRIPTS_DIR, API_KEYS

console = Console()


class TranscriptDownloader:
    """Downloads transcripts from YouTube videos."""

    def __init__(self):
        self.output_dir = TRANSCRIPTS_DIR

    def download_single(self, video_id: str, languages: list[str] = None) -> Optional[list[dict]]:
        """Download transcript for a single YouTube video."""
        if languages is None:
            languages = ["en"]

        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)

            # Save to file
            output_path = self.output_dir / f"{video_id}.json"
            with open(output_path, "w") as f:
                json.dump({
                    "video_id": video_id,
                    "segments": transcript,
                    "total_segments": len(transcript),
                }, f, indent=2)

            console.print(f"[green]✓ Downloaded transcript: {video_id} ({len(transcript)} segments)[/]")
            return transcript

        except Exception as e:
            console.print(f"[red]✗ Failed to download {video_id}: {e}[/]")
            return None

    def download_batch(self, video_ids: list[str]) -> dict:
        """Download transcripts for multiple videos."""
        results = {"success": [], "failed": []}
        for vid in tqdm(video_ids, desc="Downloading transcripts"):
            transcript = self.download_single(vid)
            if transcript:
                results["success"].append(vid)
            else:
                results["failed"].append(vid)

        console.print(f"\n[bold]Results: {len(results['success'])} success, {len(results['failed'])} failed[/]")
        return results

    def download_from_channel(self, channel_url: str, max_videos: int = 50) -> list[str]:
        """Download transcripts from all videos on a YouTube channel."""
        console.print(f"[blue]Fetching video IDs from channel...[/]")

        import subprocess
        try:
            result = subprocess.run(
                [
                    "yt-dlp", "--flat-playlist", "--print", "id",
                    "--playlist-end", str(max_videos),
                    channel_url,
                ],
                capture_output=True, text=True, timeout=120,
            )
            video_ids = [vid.strip() for vid in result.stdout.strip().split("\n") if vid.strip()]
            console.print(f"[green]Found {len(video_ids)} videos[/]")

            self.download_batch(video_ids)
            return video_ids

        except Exception as e:
            console.print(f"[red]✗ Failed to fetch channel videos: {e}[/]")
            return []

    def load_transcript(self, video_id: str) -> Optional[list[dict]]:
        """Load a previously downloaded transcript from disk."""
        path = self.output_dir / f"{video_id}.json"
        if not path.exists():
            return None
        with open(path) as f:
            data = json.load(f)
        return data.get("segments", [])

    def list_available(self) -> list[str]:
        """List all downloaded transcript video IDs."""
        return [p.stem for p in self.output_dir.glob("*.json")]


class TranscriptIndex:
    """Semantic search index over transcripts using ChromaDB + sentence-transformers."""

    def __init__(self, collection_name: str = "video_clips"):
        self.collection_name = collection_name
        self._collection = None
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            console.print("[blue]Loading embedding model...[/]")
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            console.print("[green]✓ Model loaded[/]")
        return self._model

    @property
    def collection(self):
        if self._collection is None:
            import chromadb
            client = chromadb.Client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def index_transcript(self, video_id: str, segments: list[dict], chunk_size: int = 3):
        """Index transcript segments into the vector database.

        Args:
            video_id: YouTube video ID
            segments: List of transcript segments with 'text', 'start', 'duration'
            chunk_size: Number of consecutive segments to merge for better context
        """
        console.print(f"[blue]Indexing {video_id} ({len(segments)} segments)...[/]")

        documents = []
        embeddings = []
        metadatas = []
        ids = []

        # Create overlapping chunks for better context
        for i in range(0, len(segments), max(1, chunk_size - 1)):
            chunk_segments = segments[i:i + chunk_size]
            if not chunk_segments:
                continue

            text = " ".join(seg["text"] for seg in chunk_segments)
            start_time = chunk_segments[0]["start"]
            end_time = chunk_segments[-1]["start"] + chunk_segments[-1].get("duration", 3)

            # Generate embedding
            embedding = self.model.encode(text).tolist()

            # Create unique ID
            doc_id = hashlib.md5(f"{video_id}_{start_time}".encode()).hexdigest()

            documents.append(text)
            embeddings.append(embedding)
            metadatas.append({
                "video_id": video_id,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
            })
            ids.append(doc_id)

        # Add to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            self.collection.add(
                documents=documents[i:i + batch_size],
                embeddings=embeddings[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
                ids=ids[i:i + batch_size],
            )

        console.print(f"[green]✓ Indexed {len(documents)} chunks from {video_id}[/]")

    def index_all_transcripts(self, transcript_dir: Path = None):
        """Index all downloaded transcripts."""
        if transcript_dir is None:
            transcript_dir = TRANSCRIPTS_DIR

        files = list(transcript_dir.glob("*.json"))
        console.print(f"[blue]Indexing {len(files)} transcript files...[/]")

        for f in tqdm(files, desc="Indexing"):
            with open(f) as fp:
                data = json.load(fp)
            segments = data.get("segments", [])
            if segments:
                self.index_transcript(f.stem, segments)

        console.print(f"[green]✓ All transcripts indexed. Collection size: {self.collection.count()}[/]")

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        """Search for clips matching a query string.

        Returns list of matches with video_id, start_time, end_time, text, score.
        """
        embedding = self.model.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        matches = []
        for i in range(len(results["ids"][0])):
            matches.append({
                "text": results["documents"][0][i],
                "video_id": results["metadatas"][0][i]["video_id"],
                "start_time": results["metadatas"][0][i]["start_time"],
                "end_time": results["metadatas"][0][i]["end_time"],
                "duration": results["metadatas"][0][i]["duration"],
                "similarity": 1 - results["distances"][0][i],  # Convert distance to similarity
            })

        return matches

    def find_clips_for_script(self, script_lines: list[str], clips_per_line: int = 3) -> list[dict]:
        """Find matching clips for each line of a script.

        Returns a list of dicts, one per script line, each with matching clips.
        """
        console.print(f"[blue]Finding clips for {len(script_lines)} script lines...[/]")

        clip_map = []
        for line in script_lines:
            matches = self.search(line, n_results=clips_per_line)
            clip_map.append({
                "script_line": line,
                "matches": matches,
                "best_match": matches[0] if matches else None,
            })
            if matches:
                best = matches[0]
                console.print(
                    f"  [dim]{line[:50]}...[/] → "
                    f"[green]{best['video_id']}[/] @ {best['start_time']:.1f}s "
                    f"(similarity: {best['similarity']:.2f})"
                )
            else:
                console.print(f"  [dim]{line[:50]}...[/] → [yellow]No match found[/]")

        return clip_map

