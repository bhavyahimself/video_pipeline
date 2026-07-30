"""
Video Pipeline Configuration
Centralized settings for all pipeline modules.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
TRANSCRIPTS_DIR = BASE_DIR / os.getenv("TRANSCRIPTS_DIR", "transcripts")
CLIPS_DIR = BASE_DIR / os.getenv("CLIPS_DIR", "clips")
CAPTIONS_DIR = BASE_DIR / "captions"
OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "output")
THUMBNAILS_DIR = BASE_DIR / "thumbnails"
RECORDINGS_DIR = BASE_DIR / "recordings"

# Ensure directories exist
for d in [TRANSCRIPTS_DIR, CLIPS_DIR, CAPTIONS_DIR, OUTPUT_DIR, THUMBNAILS_DIR, RECORDINGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class ChannelConfig:
    """Configuration for a specific channel type."""
    name: str
    voice_id: str = ""
    voice_stability: float = 0.5
    voice_similarity: float = 0.75
    tone: str = "confident, conversational"
    target_duration_seconds: int = 55
    format_guide: str = ""
    clip_sources: list = field(default_factory=list)
    stock_keywords: list = field(default_factory=list)


# ── Channel Configurations ──────────────────────────────────────────────────

CHANNELS = {
    "taylor_sabrina": ChannelConfig(
        name="Taylor Swift & Sabrina Carpenter",
        tone="Confident, slightly conspiratorial. Like telling a friend something you just figured out.",
        target_duration_seconds=55,
        format_guide=(
            "Line 1: Hook\n"
            "Line 2: Supporting hook (if needed)\n"
            "Line 3-4: Setting the scene\n"
            "Line 5-6: Setting the stakes\n"
            "Line 7: Payoff\n"
            "Line 8: CTA (subtle) + loop 'So—'\n"
            "Reading level: 5th-8th grade max. No filler. Every line earns the next.\n"
            "Tease the viewer. Intro should always payoff. Psychological frenzy.\n"
            "Don't insult audience intelligence. Deliver payoff fast at end."
        ),
        clip_sources=["interviews", "concerts", "music_videos", "red_carpet", "podcasts"],
        stock_keywords=["concert stage", "recording studio", "crowd cheering", "music performance"],
    ),
    "how_they_went_broke": ChannelConfig(
        name="How They Went Broke",
        tone="Calm, authoritative, slightly incredulous at the waste.",
        target_duration_seconds=55,
        format_guide=(
            "Hook: Shocking money number\n"
            "Scene: How they got rich\n"
            "Stakes: The spending spiral\n"
            "Payoff: How it all collapsed\n"
            "Loop: 'So—'"
        ),
        clip_sources=["news_clips", "lifestyle_videos", "court_footage"],
        stock_keywords=["luxury mansion", "sports car", "money cash", "empty wallet", "courtroom"],
    ),
    "why_this_place_failed": ChannelConfig(
        name="Why This Place Failed",
        tone="Nostalgic, slightly melancholic, matter-of-fact.",
        target_duration_seconds=55,
        format_guide=(
            "Hook: What the place was\n"
            "Scene: The glory days\n"
            "Stakes: What went wrong\n"
            "Payoff: The final nail\n"
            "Loop: 'So—'"
        ),
        clip_sources=["google_earth", "internet_archive", "old_commercials"],
        stock_keywords=["abandoned building", "empty mall", "closed store", "old commercial"],
    ),
    "one_decision": ChannelConfig(
        name="One Decision",
        tone="Thoughtful, building intensity, dramatic pause on payoff.",
        target_duration_seconds=55,
        format_guide=(
            "Hook: The decision (one line)\n"
            "Scene: The context / what was at stake\n"
            "Stakes: What could have gone wrong\n"
            "Payoff: What actually happened\n"
            "Loop: 'So—'"
        ),
        clip_sources=["archival_footage", "wikimedia", "stock"],
        stock_keywords=["boardroom", "crossroads", "decision", "turning point"],
    ),
    "exposed_by_algorithm": ChannelConfig(
        name="Exposed by the Algorithm",
        tone="Slightly intense, investigative, building urgency.",
        target_duration_seconds=55,
        format_guide=(
            "Hook: The scam in one line\n"
            "Scene: How it worked\n"
            "Stakes: How many people got hurt\n"
            "Payoff: How they got caught\n"
            "Loop: 'So—'"
        ),
        clip_sources=["court_docs", "social_media", "news_clips"],
        stock_keywords=["handcuffs", "computer hacking", "money fraud", "courtroom gavel"],
    ),
    "rank_the_room": ChannelConfig(
        name="Rank the Room",
        tone="Warm, opinionated, casual, slightly snarky.",
        target_duration_seconds=50,
        format_guide=(
            "Open: Show the room\n"
            "Rate: Give a score\n"
            "Explain: What's wrong / right\n"
            "Fix: The one change that would help\n"
            "Loop: 'So—'"
        ),
        clip_sources=["reddit_images"],
        stock_keywords=["interior design", "modern room", "cozy bedroom", "living room"],
    ),
    "body_language_decoded": ChannelConfig(
        name="Body Language Decoded",
        tone="Analytical, observant, 'watch this' energy.",
        target_duration_seconds=55,
        format_guide=(
            "Hook: Point out the moment\n"
            "Scene: Context of the situation\n"
            "Stakes: What it reveals\n"
            "Payoff: The hidden meaning\n"
            "Loop: 'So—'"
        ),
        clip_sources=["press_conferences", "interviews", "trials"],
        stock_keywords=["interview closeup", "handshake", "facial expression", "body language"],
    ),
    "what_your_x_says": ChannelConfig(
        name="What Your X Says About You",
        tone="Energetic, playful, 'I know something about you' vibe.",
        target_duration_seconds=45,
        format_guide=(
            "Hook: 'What your [X] says about you'\n"
            "Walk through 3-5 options\n"
            "Each option = personality trait\n"
            "End: 'Which one were you?'\n"
            "Loop: 'So—'"
        ),
        clip_sources=["ai_generated", "stock_photos"],
        stock_keywords=["personality", "choices", "psychology", "colorful options"],
    ),
    "salary_transparent": ChannelConfig(
        name="Salary Transparent",
        tone="Calm, authoritative, data-driven, slightly surprising.",
        target_duration_seconds=55,
        format_guide=(
            "Hook: Shocking salary number\n"
            "Scene: The job / city\n"
            "Breakdown: Taxes, rent, expenses\n"
            "Payoff: What's actually left\n"
            "Loop: 'So—'"
        ),
        clip_sources=["data_visualizations", "city_footage"],
        stock_keywords=["office work", "city skyline", "paycheck", "calculator money"],
    ),
    "last_24_hours": ChannelConfig(
        name="The Last 24 Hours",
        tone="Somber, cinematic, building urgency like a countdown.",
        target_duration_seconds=60,
        format_guide=(
            "Hook: 'The last 24 hours of [X]'\n"
            "Timeline: Walk through hour by hour\n"
            "Stakes: The point of no return\n"
            "Payoff: What happened at the end\n"
            "Loop: 'So—'"
        ),
        clip_sources=["archival", "internet_archive", "wikimedia"],
        stock_keywords=["clock ticking", "old photographs", "abandoned", "historical"],
    ),
    "designed_to_trick_you": ChannelConfig(
        name="Designed to Trick You",
        tone="Eye-opening, 'let me show you' energy, slightly conspiratorial.",
        target_duration_seconds=55,
        format_guide=(
            "Hook: 'This is designed to trick you'\n"
            "Scene: Show the design/layout\n"
            "Explain: The psychology behind it\n"
            "Payoff: How to not fall for it\n"
            "Loop: 'So—'"
        ),
        clip_sources=["screen_recordings", "store_layouts"],
        stock_keywords=["shopping cart", "app interface", "grocery store", "website design"],
    ),
}


# ── API Keys ────────────────────────────────────────────────────────────────

@dataclass
class APIKeys:
    openai: str = os.getenv("OPENAI_API_KEY", "")
    pexels: str = os.getenv("PEXELS_API_KEY", "")
    reddit_client_id: str = os.getenv("REDDIT_CLIENT_ID", "")
    reddit_client_secret: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_user_agent: str = os.getenv("REDDIT_USER_AGENT", "video_pipeline/1.0")
    twelve_labs: str = os.getenv("TWELVE_LABS_API_KEY", "")
    youtube: str = os.getenv("YOUTUBE_API_KEY", "")
    anthropic: str = os.getenv("ANTHROPIC_API_KEY", "")

    def validate(self, required: list[str]) -> list[str]:
        """Check which required keys are missing."""
        missing = []
        for key in required:
            if not getattr(self, key, ""):
                missing.append(key)
        return missing


API_KEYS = APIKeys()
