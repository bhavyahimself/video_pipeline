# Repository Scope

This repository is the reusable source layer for the video pipeline. It stores
creative standards, research summaries, production code, QA rules, metadata
templates, and lessons that a new model or contributor can pick up without
access to private channel credentials or local media.

## Included

- Story and retention standards
- Competitor and submodality research summaries
- Audio, caption, rights, and QA documentation
- Source code and configuration examples
- Upload metadata patterns and operational checklists

## Excluded

- API keys, cookies, OAuth tokens, or `.env` files
- Final videos, narration files, raw screen captures, and generated thumbnails
- Downloaded competitor videos, frames, or audio
- Channel analytics exports containing private account information
- Any asset without an explicit ownership or license record

Production folders remain local. Before a video is uploaded, its dated package
must contain a rights ledger, the final media QA report, metadata, and the human
review status. Public publishing always remains a manual approval step.
