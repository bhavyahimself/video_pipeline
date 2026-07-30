/**
 * ClipEngine — Landing Page
 */

import Link from "next/link";

const FEATURES = [
  {
    icon: "🎯",
    title: "AI Script Generation",
    desc: "GPT-4 writes viral scripts tailored to your channel's voice and format.",
  },
  {
    icon: "🔍",
    title: "Smart Clip Finding",
    desc: "Automatically finds relevant footage from YouTube, Pexels, and more.",
  },
  {
    icon: "🎙️",
    title: "AI Voiceover",
    desc: "ElevenLabs voices with channel-specific tone and modulation.",
  },
  {
    icon: "✂️",
    title: "Auto Assembly",
    desc: "FFmpeg stitches clips, voice, and captions into a publish-ready video.",
  },
  {
    icon: "📝",
    title: "Smart Captions",
    desc: "Whisper-powered word-level captions, auto-styled per channel.",
  },
  {
    icon: "🖼️",
    title: "Thumbnail Gen",
    desc: "Eye-catching thumbnails generated to maximize click-through rate.",
  },
];

const CHANNELS = [
  { name: "Taylor & Sabrina", emoji: "🎵", desc: "Pop culture & celebrity" },
  { name: "How They Went Broke", emoji: "💸", desc: "Celebrity finance disasters" },
  { name: "Salary Transparent", emoji: "💰", desc: "Real salary breakdowns" },
  { name: "One Decision", emoji: "🎯", desc: "Pivotal decisions that changed everything" },
  { name: "Designed to Trick You", emoji: "🧠", desc: "Dark patterns & manipulation" },
  { name: "Rank the Room", emoji: "🏠", desc: "Interior design ratings" },
  { name: "What Your X Says", emoji: "🔮", desc: "Personality-based content" },
  { name: "Body Language Decoded", emoji: "👀", desc: "Non-verbal analysis" },
  { name: "Exposed by Algorithm", emoji: "🔓", desc: "Online scams uncovered" },
  { name: "The Last 24 Hours", emoji: "⏰", desc: "Dramatic final moments" },
  { name: "Why This Place Failed", emoji: "🏚️", desc: "Business post-mortems" },
];

const PRICING = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    features: ["3 videos/month", "3 channel templates", "720p output", "ClipEngine watermark"],
    cta: "Get Started",
    highlight: false,
  },
  {
    name: "Creator",
    price: "$29",
    period: "/month",
    features: [
      "30 videos/month",
      "All 11 channels",
      "Custom voice selection",
      "1080p, no watermark",
      "YouTube direct upload",
      "Script version history",
    ],
    cta: "Start Free Trial",
    highlight: true,
  },
  {
    name: "Studio",
    price: "$99",
    period: "/month",
    features: [
      "Unlimited videos",
      "Custom channel creation",
      "Team collaboration (5)",
      "API access",
      "Batch generation",
      "Priority rendering",
      "A/B thumbnail testing",
    ],
    cta: "Start Free Trial",
    highlight: false,
  },
  {
    name: "Enterprise",
    price: "$299",
    period: "/month",
    features: [
      "Everything in Studio",
      "Unlimited team",
      "White-label output",
      "Dedicated workers",
      "Custom integrations",
      "99.9% SLA",
    ],
    cta: "Contact Sales",
    highlight: false,
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-surface/80 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🎬</span>
            <span className="text-xl font-bold bg-gradient-to-r from-brand-400 to-brand-600 bg-clip-text text-transparent">
              ClipEngine
            </span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-gray-400">
            <a href="#features" className="hover:text-white transition">Features</a>
            <a href="#channels" className="hover:text-white transition">Channels</a>
            <a href="#pricing" className="hover:text-white transition">Pricing</a>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm text-gray-400 hover:text-white transition">
              Sign In
            </Link>
            <Link
              href="/register"
              className="text-sm px-4 py-2 bg-brand-600 hover:bg-brand-700 rounded-lg font-medium transition"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-24 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-block px-4 py-1.5 bg-brand-600/10 border border-brand-600/20 rounded-full text-brand-400 text-sm mb-8">
            🚀 AI-Powered YouTube Shorts Production
          </div>
          <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-6">
            One topic.
            <br />
            <span className="bg-gradient-to-r from-brand-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              One click.
            </span>
            <br />
            One video.
          </h1>
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            ClipEngine automates your entire YouTube Shorts production pipeline.
            From research to publish-ready video in minutes, not hours.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link
              href="/register"
              className="px-8 py-3.5 bg-brand-600 hover:bg-brand-700 rounded-xl font-semibold text-lg transition shadow-lg shadow-brand-600/25"
            >
              Start Creating Free →
            </Link>
            <a
              href="#features"
              className="px-8 py-3.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl font-semibold text-lg transition"
            >
              See How It Works
            </a>
          </div>

          {/* Pipeline visualization */}
          <div className="mt-20 flex items-center justify-center gap-3 flex-wrap text-sm">
            {["Topic", "→", "Research", "→", "Script", "→", "Clips", "→", "Voice", "→", "Assembly", "→", "Video"].map(
              (step, i) =>
                step === "→" ? (
                  <span key={i} className="text-gray-600">→</span>
                ) : (
                  <span
                    key={i}
                    className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-gray-300"
                  >
                    {step}
                  </span>
                )
            )}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">
            Every step, automated
          </h2>
          <p className="text-gray-400 text-center mb-16 max-w-2xl mx-auto">
            Our 7-step pipeline handles everything from topic research to final video render.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f) => (
              <div
                key={f.title}
                className="p-6 bg-surface-raised border border-white/5 rounded-2xl hover:border-brand-600/30 transition"
              >
                <div className="text-3xl mb-4">{f.icon}</div>
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-gray-400">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Channels */}
      <section id="channels" className="py-20 px-6 bg-surface-raised/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">
            11 channel types, ready to go
          </h2>
          <p className="text-gray-400 text-center mb-16 max-w-2xl mx-auto">
            Pre-configured voice, tone, format, and clip sources for each niche.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {CHANNELS.map((ch) => (
              <div
                key={ch.name}
                className="p-4 bg-surface border border-white/5 rounded-xl hover:border-brand-600/30 transition text-center"
              >
                <div className="text-2xl mb-2">{ch.emoji}</div>
                <div className="font-medium text-sm">{ch.name}</div>
                <div className="text-xs text-gray-500 mt-1">{ch.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">
            Simple, transparent pricing
          </h2>
          <p className="text-gray-400 text-center mb-16">
            Start free. Scale when you're ready.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {PRICING.map((plan) => (
              <div
                key={plan.name}
                className={`p-6 rounded-2xl border ${
                  plan.highlight
                    ? "bg-brand-600/10 border-brand-600/30 ring-1 ring-brand-600/20"
                    : "bg-surface-raised border-white/5"
                }`}
              >
                {plan.highlight && (
                  <div className="text-xs font-medium text-brand-400 mb-3">MOST POPULAR</div>
                )}
                <h3 className="text-lg font-semibold">{plan.name}</h3>
                <div className="mt-2 mb-6">
                  <span className="text-3xl font-bold">{plan.price}</span>
                  <span className="text-gray-400 text-sm">{plan.period}</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f) => (
                    <li key={f} className="text-sm text-gray-300 flex items-start gap-2">
                      <span className="text-brand-400 mt-0.5">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/register"
                  className={`block w-full text-center py-2.5 rounded-lg font-medium text-sm transition ${
                    plan.highlight
                      ? "bg-brand-600 hover:bg-brand-700 text-white"
                      : "bg-white/5 hover:bg-white/10 border border-white/10"
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 px-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">🎬</span>
            <span className="font-bold text-gray-400">ClipEngine</span>
          </div>
          <p className="text-sm text-gray-600">© 2026 ClipEngine. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

