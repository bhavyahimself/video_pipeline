"""
ClipEngine — Video Service
Orchestrates the video pipeline engine for the SaaS layer.
"""

import asyncio
from typing import Optional


async def regenerate_script_content(topic: str, channel_type: str) -> str:
    """Regenerate a script using the engine's ScriptGenerator."""
    import sys
    from pathlib import Path

    # Add engine to path
    engine_path = Path(__file__).parent.parent.parent / "engine"
    sys.path.insert(0, str(engine_path))

    from script_generator import ScriptGenerator

    gen = ScriptGenerator(channel_type)
    # Run in thread pool since it uses sync OpenAI client
    loop = asyncio.get_event_loop()
    script = await loop.run_in_executor(None, gen.generate, topic)
    return script

