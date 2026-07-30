/**
 * ClipEngine — Channels Page
 */
"use client";

const SYSTEM_CHANNELS = [
  { key: "taylor_sabrina", name: "Taylor & Sabrina", emoji: "🎵", tone: "Confident, conspiratorial", duration: 55, automation: "80%", sources: ["interviews", "concerts", "stock"] },
  { key: "how_they_went_broke", name: "How They Went Broke", emoji: "💸", tone: "Calm, authoritative", duration: 55, automation: "90%", sources: ["news", "stock", "charts"] },
  { key: "salary_transparent", name: "Salary Transparent", emoji: "💰", tone: "Data-driven, surprising", duration: 55, automation: "85%", sources: ["BLS data", "charts", "stock"] },
  { key: "one_decision", name: "One Decision", emoji: "🎯", tone: "Thoughtful, dramatic", duration: 55, automation: "85%", sources: ["archival", "stock"] },
  { key: "designed_to_trick_you", name: "Designed to Trick You", emoji: "🧠", tone: "Eye-opening, revelatory", duration: 55, automation: "70%", sources: ["screen recordings", "stock"] },
  { key: "rank_the_room", name: "Rank the Room", emoji: "🏠", tone: "Warm, snarky, casual", duration: 50, automation: "90%", sources: ["Reddit images", "GPT-4 Vision"] },
  { key: "what_your_x_says", name: "What Your X Says", emoji: "🔮", tone: "Energetic, playful", duration: 45, automation: "95%", sources: ["AI generated", "stock"] },
  { key: "body_language_decoded", name: "Body Language Decoded", emoji: "👀", tone: "Analytical, observant", duration: 55, automation: "60%", sources: ["press clips", "interviews"] },
  { key: "exposed_by_algorithm", name: "Exposed by Algorithm", emoji: "🔓", tone: "Intense, investigative", duration: 55, automation: "75%", sources: ["court docs", "news"] },
  { key: "last_24_hours", name: "The Last 24 Hours", emoji: "⏰", tone: "Somber, cinematic", duration: 60, automation: "65%", sources: ["archival", "Internet Archive"] },
  { key: "why_this_place_failed", name: "Why This Place Failed", emoji: "🏚️", tone: "Nostalgic, melancholic", duration: 55, automation: "85%", sources: ["Internet Archive", "stock"] },
];

export default function ChannelsPage() {
  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Channels</h1>
          <p className="text-gray-400 text-sm mt-1">Pre-configured templates for different YouTube niches.</p>
        </div>
        <button className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm hover:bg-white/10 transition">
          + Create Custom Channel
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {SYSTEM_CHANNELS.map((ch) => (
          <div
            key={ch.key}
            className="p-6 bg-surface-raised border border-white/5 rounded-xl hover:border-brand-600/20 transition"
          >
            <div className="flex items-start gap-4">
              <span className="text-3xl">{ch.emoji}</span>
              <div className="flex-1">
                <h3 className="font-semibold">{ch.name}</h3>
                <p className="text-sm text-gray-400 mt-1">"{ch.tone}"</p>

                <div className="grid grid-cols-3 gap-4 mt-4 text-xs">
                  <div>
                    <span className="text-gray-500 block">Duration</span>
                    <span className="text-gray-300">{ch.duration}s</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Automation</span>
                    <span className="text-gray-300">{ch.automation}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Sources</span>
                    <span className="text-gray-300">{ch.sources.length} types</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1.5 mt-3">
                  {ch.sources.map((s) => (
                    <span key={s} className="px-2 py-0.5 bg-white/5 rounded text-xs text-gray-500">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

