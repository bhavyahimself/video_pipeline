/**
 * ClipEngine — Video Library
 */
"use client";

import { useState } from "react";
import Link from "next/link";

const STATUS_COLORS: Record<string, string> = {
  done: "bg-green-500/10 text-green-400 border-green-500/20",
  queued: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  failed: "bg-red-500/10 text-red-400 border-red-500/20",
  assembling: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  scripting: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  voicing: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
  researching: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
};

// Placeholder data — will be replaced with API calls
const MOCK_VIDEOS = [
  { id: "1", title: "$100K in SF vs $100K in Texas", channel: "salary_transparent", channelName: "Salary Transparent", status: "done", date: "2 hours ago", duration: "52s" },
  { id: "2", title: "Sabrina Carpenter Almost Quit", channel: "taylor_sabrina", channelName: "Taylor & Sabrina", status: "done", date: "Yesterday", duration: "48s" },
  { id: "3", title: "How Mike Tyson Blew $300M", channel: "how_they_went_broke", channelName: "How They Went Broke", status: "assembling", date: "Just now", duration: null },
  { id: "4", title: "The IKEA Store Layout Trap", channel: "designed_to_trick_you", channelName: "Designed to Trick You", status: "done", date: "2 days ago", duration: "55s" },
  { id: "5", title: "What a Nurse Actually Takes Home", channel: "salary_transparent", channelName: "Salary Transparent", status: "done", date: "3 days ago", duration: "58s" },
  { id: "6", title: "Why Blockbuster Failed", channel: "why_this_place_failed", channelName: "Why This Place Failed", status: "failed", date: "4 days ago", duration: null },
];

export default function LibraryPage() {
  const [view, setView] = useState<"grid" | "list">("grid");
  const [channelFilter, setChannelFilter] = useState<string>("");

  const filtered = channelFilter
    ? MOCK_VIDEOS.filter((v) => v.channel === channelFilter)
    : MOCK_VIDEOS;

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Video Library</h1>
          <p className="text-gray-400 text-sm mt-1">{MOCK_VIDEOS.length} videos</p>
        </div>
        <div className="flex items-center gap-3">
          {/* View toggle */}
          <div className="flex bg-white/5 rounded-lg p-1">
            <button
              onClick={() => setView("grid")}
              className={`px-3 py-1.5 rounded text-xs ${view === "grid" ? "bg-brand-600 text-white" : "text-gray-400"}`}
            >
              Grid
            </button>
            <button
              onClick={() => setView("list")}
              className={`px-3 py-1.5 rounded text-xs ${view === "list" ? "bg-brand-600 text-white" : "text-gray-400"}`}
            >
              List
            </button>
          </div>

          <Link
            href="/create"
            className="px-4 py-2 bg-brand-600 hover:bg-brand-700 rounded-lg text-sm font-medium transition"
          >
            + New Video
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <button
          onClick={() => setChannelFilter("")}
          className={`px-3 py-1.5 rounded-lg text-xs border transition ${
            !channelFilter ? "bg-brand-600/10 border-brand-600/30 text-brand-400" : "bg-white/5 border-white/10 text-gray-400"
          }`}
        >
          All
        </button>
        {["salary_transparent", "taylor_sabrina", "how_they_went_broke", "designed_to_trick_you"].map((ch) => (
          <button
            key={ch}
            onClick={() => setChannelFilter(ch)}
            className={`px-3 py-1.5 rounded-lg text-xs border transition ${
              channelFilter === ch ? "bg-brand-600/10 border-brand-600/30 text-brand-400" : "bg-white/5 border-white/10 text-gray-400"
            }`}
          >
            {ch.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      {/* Grid View */}
      {view === "grid" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((video) => (
            <Link
              key={video.id}
              href={`/library/${video.id}`}
              className="group bg-surface-raised border border-white/5 rounded-xl overflow-hidden hover:border-brand-600/30 transition"
            >
              <div className="aspect-video bg-white/5 flex items-center justify-center relative">
                <span className="text-4xl opacity-20">🎬</span>
                {video.duration && (
                  <span className="absolute bottom-2 right-2 px-2 py-0.5 bg-black/80 rounded text-xs">
                    {video.duration}
                  </span>
                )}
              </div>
              <div className="p-4">
                <h3 className="font-medium text-sm group-hover:text-brand-400 transition line-clamp-2">
                  {video.title}
                </h3>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-xs text-gray-500">{video.channelName}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${STATUS_COLORS[video.status] || ""}`}>
                    {video.status}
                  </span>
                </div>
                <div className="text-xs text-gray-600 mt-2">{video.date}</div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        /* List View */
        <div className="space-y-2">
          {filtered.map((video) => (
            <Link
              key={video.id}
              href={`/library/${video.id}`}
              className="flex items-center gap-4 p-4 bg-surface-raised border border-white/5 rounded-xl hover:border-brand-600/30 transition"
            >
              <div className="w-16 h-10 bg-white/5 rounded flex items-center justify-center flex-shrink-0">
                <span className="text-lg opacity-20">🎬</span>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-sm truncate">{video.title}</h3>
                <span className="text-xs text-gray-500">{video.channelName}</span>
              </div>
              <span className={`text-xs px-2 py-0.5 rounded-full border flex-shrink-0 ${STATUS_COLORS[video.status] || ""}`}>
                {video.status}
              </span>
              <span className="text-xs text-gray-500 flex-shrink-0 w-20 text-right">{video.date}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

