# Reusable Audio Asset Library

Use this directory for reusable, licensed audio assets used by the video pipeline.

Read first:

- `../docs/audio_retention_and_sonic_identity_system.md`
- `../docs/audio_retention_event_ledger_template.json`

Recommended storage:

- `original/` — synthesis and recordings created for the project
- `youtube_audio_library/` — assets downloaded from the official YouTube Audio Library
- `cc0_public_domain/` — verified CC0 or public-domain recordings
- `licensed/` — other commercial-use assets with saved license evidence
- `receipts/` — license pages, attribution text, and download receipts

Filename convention:

`source_category_meaning_variant_license.ext`

Examples:

- `original_ui_lock_soft_v01_owned.wav`
- `youtube_library_ocean_surf_01_ytal.mp3`
- `cc0_radio_static_short_02_cc0.wav`

Never save ripped YouTube, movie, television, news, game, commercial-song, meme, brand-alert, or competitor audio here.

For each used file, record:

- source page
- direct download URL
- creator
- license and version
- attribution
- download date
- checksum
- videos and timestamps where used

Do not assume that an asset is safe because its filename includes “royalty free” or “no copyright.”

## Core assembler usage

`VideoAssembler.assemble_from_clips` now accepts:

- `background_audio_path` — a licensed bed that loops and fades to narration length
- `sound_events` — timestamped events containing `path`, `start_seconds`, and `gain_db`

Example:

```python
assembler.assemble_from_clips(
    clip_paths=clips,
    voiceover_path=narration,
    output_name="nature_tsunami",
    background_audio_path=Path("audio/original/ocean_pressure_bed.wav"),
    sound_events=[
        {
            "path": Path("audio/original/pressure_crack_v01.wav"),
            "start_seconds": 0.0,
            "gain_db": -10.0,
        },
        {
            "path": Path("audio/original/data_ping_v02.wav"),
            "start_seconds": 4.2,
            "gain_db": -13.0,
        },
    ],
)
```

The mixer keeps narration first, loops and fades the bed, delays events to their timeline positions, normalizes the final audio near `-16 LUFS`, and limits true peak to `-1.5 dBTP`.
