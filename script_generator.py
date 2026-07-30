"""
Script Generator Module
Generates viral YouTube Shorts scripts using OpenAI GPT-4 / Claude.
Customized per channel with tone, format, and style guides.
"""

import json
from pathlib import Path
from typing import Optional

from rich.console import Console

from config.settings import CHANNELS, API_KEYS, ChannelConfig

console = Console()


class ScriptGenerator:
    """Generates scripts for any channel type using LLM APIs."""

    def __init__(self, channel_key: str):
        if channel_key not in CHANNELS:
            raise ValueError(f"Unknown channel: {channel_key}. Available: {list(CHANNELS.keys())}")
        self.channel = CHANNELS[channel_key]
        self.channel_key = channel_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            missing = API_KEYS.validate(["openai"])
            if missing:
                raise RuntimeError(f"Missing API keys: {missing}. Set them in .env")
            from openai import OpenAI
            self._client = OpenAI(api_key=API_KEYS.openai)
        return self._client

    def _build_system_prompt(self) -> str:
        return (
            f"You are an expert viral YouTube Shorts scriptwriter for a channel called "
            f"'{self.channel.name}'.\n\n"
            f"VOICE & TONE:\n{self.channel.tone}\n\n"
            f"SCRIPT FORMAT (follow exactly):\n{self.channel.format_guide}\n\n"
            f"RULES:\n"
            f"- Target spoken duration: {self.channel.target_duration_seconds} seconds\n"
            f"- Reading level: 5th-8th grade max. Short sentences. No jargon.\n"
            f"- No filler. Every single line must earn the next line.\n"
            f"- Hook must create a curiosity gap that ONLY the payoff closes.\n"
            f"- Tease the viewer psychologically — they think they know, but they're wrong.\n"
            f"- Don't insult audience intelligence by over-explaining.\n"
            f"- End with 'So—' for a loop effect.\n"
            f"- Subtle CTA only — relate to the viewer, don't beg for subscribes.\n"
            f"  Example: 'If you already knew that… you're paying closer attention than most. So—'\n"
            f"- Script must be YouTube monetization-friendly (no hate, violence, or policy violations).\n"
            f"- Make it better and longer than competition. Analyze what others do and beat them.\n"
            f"- Scripting and storyline is 80% of the video. Focus on it.\n"
            f"- Output ONLY the script text. No headers, no labels, no formatting instructions."
        )

    def generate(self, topic: str, additional_context: str = "") -> str:
        """Generate a single script for a given topic."""
        console.print(f"[bold blue]Generating script:[/] {topic}")

        user_prompt = f"Write a viral YouTube Short script about: {topic}"
        if additional_context:
            user_prompt += f"\n\nAdditional context/research:\n{additional_context}"

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,
            max_tokens=800,
        )

        script = response.choices[0].message.content.strip()
        console.print(f"[green]✓ Script generated ({len(script.split())} words)[/]")
        return script

    def generate_batch(self, topics: list[str]) -> list[dict]:
        """Generate scripts for multiple topics."""
        results = []
        for i, topic in enumerate(topics, 1):
            console.print(f"\n[bold]Script {i}/{len(topics)}[/]")
            try:
                script = self.generate(topic)
                results.append({
                    "topic": topic,
                    "script": script,
                    "channel": self.channel_key,
                    "status": "success",
                })
            except Exception as e:
                console.print(f"[red]✗ Failed: {e}[/]")
                results.append({
                    "topic": topic,
                    "script": "",
                    "channel": self.channel_key,
                    "status": f"error: {e}",
                })
        return results

    def split_script_lines(self, script: str) -> list[str]:
        """Split a script into individual lines for clip matching."""
        lines = [line.strip() for line in script.split("\n") if line.strip()]
        # Filter out any formatting artifacts
        lines = [l for l in lines if not l.startswith(("Hook:", "CTA", "Setting", "Stakes:", "Payoff:", "Supporting"))]
        return lines

    def extract_visual_cues(self, script: str) -> list[dict]:
        """Use AI to extract visual/clip suggestions for each script line."""
        console.print("[blue]Extracting visual cues from script...[/]")

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a video editor's assistant. Given a voiceover script, "
                        "extract what visuals should be shown for each line. "
                        "Output JSON array where each item has:\n"
                        '  "line": the script line,\n'
                        '  "visual_description": what should be shown on screen,\n'
                        '  "search_keywords": 3-5 keywords to search for stock footage or clips,\n'
                        '  "duration_seconds": estimated spoken duration of this line\n'
                        "Output ONLY valid JSON. No markdown."
                    ),
                },
                {"role": "user", "content": f"Extract visuals for this script:\n\n{script}"},
            ],
            temperature=0.3,
            max_tokens=1500,
        )

        try:
            cues = json.loads(response.choices[0].message.content)
            console.print(f"[green]✓ Extracted {len(cues)} visual cues[/]")
            return cues
        except json.JSONDecodeError:
            console.print("[yellow]⚠ Could not parse visual cues as JSON, returning raw[/]")
            return [{"line": script, "visual_description": "general b-roll", "search_keywords": self.channel.stock_keywords, "duration_seconds": self.channel.target_duration_seconds}]


class ResearchAgent:
    """Gathers research material for script topics using web sources."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=API_KEYS.openai)
        return self._client

    def research_topic(self, topic: str, channel_key: str) -> str:
        """Use GPT-4 to research and compile facts about a topic."""
        console.print(f"[blue]Researching: {topic}[/]")

        channel = CHANNELS.get(channel_key)
        context = f"Channel type: {channel.name}" if channel else ""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a research assistant for a YouTube content creator. "
                        "Given a topic, compile the most interesting, verified, and "
                        "specific facts that would make a compelling short video. "
                        "Include: key dates, numbers, surprising twists, direct quotes "
                        "if available. Be concise. Bullet points only. "
                        "Cite sources where possible."
                    ),
                },
                {"role": "user", "content": f"{context}\n\nResearch this topic: {topic}"},
            ],
            temperature=0.4,
            max_tokens=1000,
        )

        research = response.choices[0].message.content.strip()
        console.print(f"[green]✓ Research compiled ({len(research.split())} words)[/]")
        return research

