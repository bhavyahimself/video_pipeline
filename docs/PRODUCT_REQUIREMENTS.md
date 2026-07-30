# ClipEngine — Product Requirements Document

## Vision
Make professional YouTube Shorts production accessible to anyone with an idea. One topic in, one publish-ready video out.

## Target Users
1. **Solo Creators** — Running faceless YouTube channels, need volume
2. **Content Agencies** — Managing multiple client channels
3. **Social Media Managers** — Need short-form video at scale
4. **Educators/Coaches** — Repurposing knowledge into video content

## Pricing Tiers

### Free — $0/month
- 3 videos/month
- 3 basic channel types (Taylor/Sabrina, How They Went Broke, Salary Transparent)
- Default voice only
- ClipEngine watermark on output
- Community support (Discord)
- 720p output
- No API access

### Creator — $29/month
- 30 videos/month
- All 11 channel types
- Custom ElevenLabs voice selection
- No watermark
- 1080p output
- YouTube direct upload
- Email support
- Script version history
- Basic analytics

### Studio — $99/month
- Unlimited videos
- All channels + create custom channels
- Voice cloning support
- Team collaboration (up to 5 members)
- API access (1000 req/day)
- Batch generation (up to 10 at once)
- Priority render queue
- A/B thumbnail testing
- Advanced analytics + export
- Template marketplace access
- Priority email support

### Enterprise — $299/month
- Everything in Studio
- Unlimited team members
- White-label (remove all ClipEngine branding)
- Custom channel development assistance
- Dedicated rendering workers
- API access (10,000 req/day)
- Scheduled publishing
- Dedicated Slack support
- Custom integrations
- SLA guarantee (99.9% uptime)

## Feature Breakdown

### Core Features (All Plans)
- [x] Topic → Video pipeline (end-to-end)
- [x] AI script generation (GPT-4)
- [x] Visual cue extraction
- [x] Stock footage sourcing (Pexels)
- [x] AI voiceover (ElevenLabs)
- [x] Auto-captions (Whisper)
- [x] Thumbnail generation
- [x] Video preview & download
- [x] Script editor with AI assistance

### Creator Features
- [x] All 11 pre-built channel templates
- [x] Voice selection (20+ ElevenLabs voices)
- [x] YouTube direct upload
- [x] Script version history
- [x] Basic usage analytics
- [x] Custom output name & metadata

### Studio Features
- [x] Custom channel creation (tone, format, voice, clip sources)
- [x] Team workspaces with role-based access
- [x] REST API with documentation
- [x] Batch video generation
- [x] Priority rendering queue
- [x] A/B thumbnail testing
- [x] Template marketplace (browse & publish)
- [x] Advanced analytics with CSV/PDF export
- [x] Webhook notifications

### Enterprise Features
- [x] White-label output
- [x] Dedicated worker pool
- [x] Custom channel development
- [x] Scheduled publishing calendar
- [x] SSO integration
- [x] Custom API rate limits
- [x] Audit logs
- [x] Dedicated support channel

## UI/UX Specifications

### Landing Page
- Hero: "One topic. One click. One video." with animated demo
- Feature grid showing the 7-step pipeline visually
- Channel showcase carousel (show all 11 types with sample output)
- Social proof section (metrics, testimonials)
- Pricing table with feature comparison
- FAQ accordion
- Footer with links

### Dashboard
- Top bar: Search, notifications, profile dropdown
- Sidebar: Navigation (Dashboard, Create, Library, Scripts, Channels, Analytics, Settings)
- Main area:
  - Usage meter (videos used / quota)
  - Recent videos grid (thumbnails + status badges)
  - Quick stats (total videos, active jobs, this month)
  - Quick create button (prominent CTA)

### Video Creator Wizard (4 steps)
1. **Topic** — Text input + AI topic suggestions + trending topics
2. **Channel** — Visual channel type cards with preview of tone/style
3. **Customize** — Voice picker, duration slider, toggle options (research, stock, captions), advanced settings
4. **Review** — Summary card + "Generate Video" button → redirects to job progress

### Script Editor
- Left panel: Rich text editor (Tiptap/Monaco)
- Right panel: Visual cue preview cards (stock footage thumbnails per line)
- Toolbar: Regenerate, Version history dropdown, Copy, Export
- Bottom: Voice preview (play TTS of current script)

### Video Library
- Grid/List view toggle
- Filters: Channel type, date range, status
- Search by topic/title
- Bulk select for batch operations (delete, download, re-render)
- Each card: Thumbnail, title, channel badge, status, date, actions (preview, download, upload to YT, delete)

### Job Progress View
- Step-by-step animated progress bar:
  Research → Script → Clips → Voice → Assembly → Captions → Thumbnail → Done
- Current step highlighted with spinner
- ETA display
- Cancel button
- Auto-redirect to video preview on completion

### Analytics Dashboard
- Time range picker
- Charts: Videos created over time, generation time trends
- Channel breakdown pie chart
- Usage vs quota bar
- Top-performing scripts (if YouTube connected)
- Export buttons (CSV, PDF)

## Voice & Tonality System

Each channel has a defined voice profile:

| Channel | Voice Style | Modulation |
|---------|------------|------------|
| Taylor/Sabrina | Confident, conspiratorial | Build excitement, drop to whisper on reveals |
| How They Went Broke | Calm, authoritative | Even pace, slight incredulity on big numbers |
| Salary Transparent | Data-driven, clear | Punch specific numbers, pause after shockers |
| Designed to Trick You | Eye-opening, revelatory | "Let me show you" energy, controlled urgency |
| One Decision | Thoughtful, building | Slow build, dramatic pause before payoff |
| Last 24 Hours | Somber, cinematic | Countdown urgency, quiet on emotional beats |
| Rank the Room | Warm, snarky | Casual, opinionated, quick wit |
| What Your X Says | Energetic, playful | Fun, "I know you" vibe, rapid fire |
| Body Language Decoded | Analytical, observant | "Watch this" energy, precise |
| Why This Place Failed | Nostalgic, melancholic | Wistful on glory days, matter-of-fact on failure |
| Exposed by Algorithm | Intense, investigative | Building urgency, satisfaction on reveal |

## Success Metrics (KPIs)

| Metric | Target (Month 1) | Target (Month 6) |
|--------|-------------------|-------------------|
| Registered users | 500 | 10,000 |
| Paid subscribers | 50 | 1,000 |
| MRR | $2,000 | $40,000 |
| Videos generated/day | 100 | 2,000 |
| Avg generation time | < 5 min | < 3 min |
| User retention (30d) | 40% | 55% |
| NPS | 30 | 50 |

