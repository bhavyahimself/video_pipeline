/**
 * ClipEngine — Video Detail / Player Page
 */
"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useJobProgress, PIPELINE_STEPS } from "@/hooks/use-job-progress";

const STEP_LABELS: Record<string, { label: string; icon: string }> = {
  researching: { label: "Researching", icon: "🔍" },
  scripting: { label: "Writing Script", icon: "✍️" },
  clipping: { label: "Finding Clips", icon: "🎞️" },
  voicing: { label: "Generating Voice", icon: "🎙️" },
  assembling: { label: "Assembling Video", icon: "✂️" },
  captioning: { label: "Adding Captions", icon: "📝" },
  thumbnailing: { label: "Creating Thumbnail", icon: "🖼️" },
  done: { label: "Complete!", icon: "✅" },
};

export default function VideoDetailPage() {
  const params = useParams();
  const videoId = params.id as string;

  // For demo, show a static video detail. In production, fetch from API and optionally connect WS.
  const isProcessing = false; // Set true to show progress view

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <Link href="/library" className="text-sm text-gray-400 hover:text-white mb-4 inline-block">
        ← Back to Library
      </Link>

      {isProcessing ? (
        /* Job Progress View */
        <div className="mt-6">
          <h1 className="text-2xl font-bold mb-2">Generating Video...</h1>
          <p className="text-gray-400 text-sm mb-8">Your video is being created. This usually takes 2-5 minutes.</p>

          <div className="space-y-3">
            {PIPELINE_STEPS.map((step, i) => {
              const info = STEP_LABELS[step];
              const isActive = step === "scripting"; // demo
              const isDone = i < 1; // demo
              return (
                <div
                  key={step}
                  className={`flex items-center gap-4 p-4 rounded-xl border transition ${
                    isActive
                      ? "bg-brand-600/10 border-brand-600/30"
                      : isDone
                      ? "bg-green-500/5 border-green-500/20"
                      : "bg-surface-raised border-white/5 opacity-50"
                  }`}
                >
                  <span className="text-xl">{info?.icon || "⏳"}</span>
                  <div className="flex-1">
                    <div className="text-sm font-medium">{info?.label || step}</div>
                    {isActive && (
                      <div className="text-xs text-brand-400 mt-1">In progress...</div>
                    )}
                  </div>
                  {isDone && <span className="text-green-400 text-sm">✓</span>}
                  {isActive && (
                    <div className="w-5 h-5 border-2 border-brand-400 border-t-transparent rounded-full animate-spin" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* Completed Video View */
        <div className="mt-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold">$100K in SF vs $100K in Texas</h1>
              <div className="flex items-center gap-3 mt-2">
                <span className="px-2 py-1 bg-white/5 rounded text-xs text-gray-400">💰 Salary Transparent</span>
                <span className="px-2 py-1 bg-green-500/10 text-green-400 rounded text-xs border border-green-500/20">Done</span>
                <span className="text-xs text-gray-500">52 seconds</span>
              </div>
            </div>
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm hover:bg-white/10 transition">
                📥 Download
              </button>
              <button className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm font-medium transition">
                📤 Upload to YouTube
              </button>
            </div>
          </div>

          {/* Video Player */}
          <div className="aspect-[9/16] max-w-sm mx-auto bg-surface-raised border border-white/5 rounded-2xl overflow-hidden flex items-center justify-center mb-8">
            <div className="text-center">
              <span className="text-6xl block mb-4">🎬</span>
              <p className="text-sm text-gray-400">Video Preview</p>
              <button className="mt-4 px-6 py-2 bg-brand-600 rounded-lg text-sm">▶ Play</button>
            </div>
          </div>

          {/* Tabs: Script, Thumbnail, Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Script */}
            <div className="bg-surface-raised border border-white/5 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Script</h3>
                <button className="text-xs text-brand-400 hover:text-brand-300">Edit →</button>
              </div>
              <div className="text-sm text-gray-300 leading-relaxed space-y-2">
                <p>$100,000 in San Francisco is actually worth $55,000 in Texas money. Here's the math.</p>
                <p>Federal tax on $100K: roughly $17,000. California state tax: about $6,000. Texas state tax: zero.</p>
                <p>After taxes, rent, and cost of living adjustments, $100K in San Francisco gives you roughly the same lifestyle as $55K in Austin.</p>
                <p>You took the six-figure job. You live a five-figure life. So—</p>
              </div>
            </div>

            {/* Details */}
            <div className="bg-surface-raised border border-white/5 rounded-xl p-6">
              <h3 className="font-semibold mb-4">Details</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Duration</span>
                  <span>52 seconds</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Resolution</span>
                  <span>1080x1920</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">File Size</span>
                  <span>12.4 MB</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Created</span>
                  <span>2 hours ago</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Voice</span>
                  <span>Default</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Watermark</span>
                  <span>No</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

