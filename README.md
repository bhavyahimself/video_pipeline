# Video Pipeline

An extensible, retention-first production system for review-ready YouTube videos.
It combines research, story design, rights tracking, VEED narration requirements,
caption-safe layouts, media QA, and upload metadata into one reusable workflow.

## Start Here

Read these in order before extending the pipeline:

1. [Creative Standard](CREATIVE_STANDARD.md)
2. [Rolling Lessons Log](docs/rolling_lessons_log.md)
3. [Audio Retention and Sonic Identity System](docs/audio_retention_and_sonic_identity_system.md)
4. [Top-Creator Submodality Playbook](docs/top_creator_submodality_playbook.md)
5. [Repository Scope](REPOSITORY_SCOPE.md)

## Local Development

```bash
cp .env.example .env
python3 verify_setup.py
```

The optional service stack is available through Docker:

```bash
docker-compose up -d
```

## Pipeline Principles

- Treat scripting and story structure as the primary retention lever.
- Use footage that directly proves each spoken beat; do not use generic filler.
- Use VEED for final narration and sound design when a production requires it.
- Preserve source URLs, licenses, and attribution in a rights ledger.
- Run technical and human quality gates before review or upload.
- Keep generated media and channel credentials outside this source repository.

## Research

- [Roblox creator benchmark, 2026-07-30](research/roblox_creator_benchmark_2026-07-30.md)
- [Top-creator visual analysis](research/top_creator_submodalities/2026-07-14/analysis.json)
- [3D animation channel plan](docs/3d_animation_channel_plan.md)

## Project Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Product Requirements](docs/PRODUCT_REQUIREMENTS.md)
- [Sprint Plan](docs/SPRINT_PLAN.md)
- [Audio Event Ledger Template](docs/audio_retention_event_ledger_template.json)
