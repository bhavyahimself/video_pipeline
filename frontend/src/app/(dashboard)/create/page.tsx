/**
 * ClipEngine — Video Creator Wizard
 * 4-step flow: Topic → Channel → Customize → Review & Generate
 */
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

const CHANNELS = [
  { key: "taylor_sabrina", name: "Taylor & Sabrina", emoji: "🎵", desc: "Pop culture & celebrity stories" },
  { key: "how_they_went_broke", name: "How They Went Broke", emoji: "💸", desc: "Celebrity financial disasters" },
  { key: "salary_transparent", name: "Salary Transparent", emoji: "💰", desc: "Real salary breakdowns by job & city" },
  { key: "one_decision", name: "One Decision", emoji: "🎯", desc: "Pivotal moments that changed everything" },
  { key: "designed_to_trick_you", name: "Designed to Trick You", emoji: "🧠", desc: "Dark patterns & manipulation tactics" },
  { key: "rank_the_room", name: "Rank the Room", emoji: "🏠", desc: "Interior design ratings & advice" },
  { key: "what_your_x_says", name: "What Your X Says", emoji: "🔮", desc: "Personality-based content" },
  { key: "body_language_decoded", name: "Body Language Decoded", emoji: "👀", desc: "Non-verbal communication analysis" },
  { key: "exposed_by_algorithm", name: "Exposed by Algorithm", emoji: "🔓", desc: "Online scams uncovered" },
  { key: "last_24_hours", name: "The Last 24 Hours", emoji: "⏰", desc: "Dramatic final moments in history" },
  { key: "why_this_place_failed", name: "Why This Place Failed", emoji: "🏚️", desc: "Business post-mortems" },
];

const STEPS = ["Topic", "Channel", "Customize", "Review"];

export default function CreateVideoPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [topic, setTopic] = useState("");
  const [channel, setChannel] = useState("");
  const [skipResearch, setSkipResearch] = useState(false);
  const [skipVoice, setSkipVoice] = useState(false);
  const [skipCaptions, setSkipCaptions] = useState(false);
  const [skipThumbnail, setSkipThumbnail] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const canProceed = () => {
    if (step === 0) return topic.length >= 3;
    if (step === 1) return channel !== "";
    return true;
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    try {
      const video = await api.createVideo({
        topic,
        channel_type: channel,
        skip_research: skipResearch,
        skip_voice: skipVoice,
      });
      router.push(`/library/${video.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create video");
      setLoading(false);
    }
  };

  const selectedChannel = CHANNELS.find((c) => c.key === channel);

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      <h1 className="text-2xl font-bold mb-2">Create New Video</h1>
      <p className="text-gray-400 text-sm mb-8">Generate a publish-ready YouTube Short in minutes.</p>

      {/* Step Indicator */}
      <div className="flex items-center gap-2 mb-10">
        {STEPS.map((s, i) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                i <= step
                  ? "bg-brand-600 text-white"
                  : "bg-white/5 text-gray-500 border border-white/10"
              }`}
            >
              {i < step ? "✓" : i + 1}
            </div>
            <span className={`text-sm ${i <= step ? "text-white" : "text-gray-500"}`}>{s}</span>
            {i < STEPS.length - 1 && <div className="w-8 h-px bg-white/10" />}
          </div>
        ))}
      </div>

      {error && (
        <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Step 1: Topic */}
      {step === 0 && (
        <div className="animate-slide-up">
          <h2 className="text-lg font-semibold mb-4">What's your video about?</h2>
          <textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., How Mike Tyson blew $300 million, $100K salary in San Francisco vs Texas, Why Blockbuster failed..."
            className="w-full h-32 px-4 py-3 bg-surface-raised border border-white/10 rounded-xl focus:outline-none focus:border-brand-500 transition text-white resize-none"
          />
          <div className="mt-4">
            <p className="text-xs text-gray-500 mb-3">💡 Trending topics</p>
            <div className="flex flex-wrap gap-2">
              {[
                "Sabrina Carpenter's rise to fame",
                "$200K household income in 2026",
                "Why Circuit City failed",
                "The IKEA store layout trick",
                "Taylor Swift's wedding privacy",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setTopic(suggestion)}
                  className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-gray-300 hover:border-brand-500/30 transition"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Channel */}
      {step === 1 && (
        <div className="animate-slide-up">
          <h2 className="text-lg font-semibold mb-4">Choose a channel type</h2>
          <div className="grid grid-cols-2 gap-3">
            {CHANNELS.map((ch) => (
              <button
                key={ch.key}
                onClick={() => setChannel(ch.key)}
                className={`p-4 text-left rounded-xl border transition ${
                  channel === ch.key
                    ? "bg-brand-600/10 border-brand-600/30 ring-1 ring-brand-600/20"
                    : "bg-surface-raised border-white/5 hover:border-white/20"
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{ch.emoji}</span>
                  <div>
                    <div className="font-medium text-sm">{ch.name}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{ch.desc}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 3: Customize */}
      {step === 2 && (
        <div className="animate-slide-up space-y-6">
          <h2 className="text-lg font-semibold mb-4">Customize your video</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-surface-raised border border-white/5 rounded-xl">
              <div>
                <div className="font-medium text-sm">AI Research</div>
                <div className="text-xs text-gray-500">Research the topic before scripting</div>
              </div>
              <button
                onClick={() => setSkipResearch(!skipResearch)}
                className={`w-11 h-6 rounded-full transition ${
                  !skipResearch ? "bg-brand-600" : "bg-white/10"
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-white shadow transition transform ${
                    !skipResearch ? "translate-x-5" : "translate-x-0.5"
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-surface-raised border border-white/5 rounded-xl">
              <div>
                <div className="font-medium text-sm">AI Voiceover</div>
                <div className="text-xs text-gray-500">Use a fresh VEED voice export</div>
              </div>
              <button
                onClick={() => setSkipVoice(!skipVoice)}
                className={`w-11 h-6 rounded-full transition ${
                  !skipVoice ? "bg-brand-600" : "bg-white/10"
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-white shadow transition transform ${
                    !skipVoice ? "translate-x-5" : "translate-x-0.5"
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-surface-raised border border-white/5 rounded-xl">
              <div>
                <div className="font-medium text-sm">Auto Captions</div>
                <div className="text-xs text-gray-500">Generate word-level subtitles</div>
              </div>
              <button
                onClick={() => setSkipCaptions(!skipCaptions)}
                className={`w-11 h-6 rounded-full transition ${
                  !skipCaptions ? "bg-brand-600" : "bg-white/10"
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-white shadow transition transform ${
                    !skipCaptions ? "translate-x-5" : "translate-x-0.5"
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-surface-raised border border-white/5 rounded-xl">
              <div>
                <div className="font-medium text-sm">Thumbnail</div>
                <div className="text-xs text-gray-500">Auto-generate a click-worthy thumbnail</div>
              </div>
              <button
                onClick={() => setSkipThumbnail(!skipThumbnail)}
                className={`w-11 h-6 rounded-full transition ${
                  !skipThumbnail ? "bg-brand-600" : "bg-white/10"
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-white shadow transition transform ${
                    !skipThumbnail ? "translate-x-5" : "translate-x-0.5"
                  }`}
                />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Step 4: Review */}
      {step === 3 && (
        <div className="animate-slide-up">
          <h2 className="text-lg font-semibold mb-4">Review & Generate</h2>
          <div className="bg-surface-raised border border-white/5 rounded-xl p-6 space-y-4">
            <div>
              <span className="text-xs text-gray-500">Topic</span>
              <p className="text-sm mt-1">{topic}</p>
            </div>
            <div>
              <span className="text-xs text-gray-500">Channel</span>
              <p className="text-sm mt-1">
                {selectedChannel?.emoji} {selectedChannel?.name}
              </p>
            </div>
            <div>
              <span className="text-xs text-gray-500">Options</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {!skipResearch && (
                  <span className="px-2 py-1 bg-white/5 rounded text-xs">✓ Research</span>
                )}
                {!skipVoice && (
                  <span className="px-2 py-1 bg-white/5 rounded text-xs">✓ Voiceover</span>
                )}
                {!skipCaptions && (
                  <span className="px-2 py-1 bg-white/5 rounded text-xs">✓ Captions</span>
                )}
                {!skipThumbnail && (
                  <span className="px-2 py-1 bg-white/5 rounded text-xs">✓ Thumbnail</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between mt-8">
        <button
          onClick={() => setStep(Math.max(0, step - 1))}
          disabled={step === 0}
          className="px-6 py-2.5 bg-white/5 border border-white/10 rounded-lg font-medium text-sm disabled:opacity-30 hover:bg-white/10 transition"
        >
          ← Back
        </button>

        {step < 3 ? (
          <button
            onClick={() => setStep(step + 1)}
            disabled={!canProceed()}
            className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 rounded-lg font-medium text-sm disabled:opacity-30 transition"
          >
            Next →
          </button>
        ) : (
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="px-8 py-2.5 bg-brand-600 hover:bg-brand-700 rounded-lg font-medium text-sm disabled:opacity-50 transition shadow-lg shadow-brand-600/25"
          >
            {loading ? "🔄 Generating..." : "⚡ Generate Video"}
          </button>
        )}
      </div>
    </div>
  );
}
