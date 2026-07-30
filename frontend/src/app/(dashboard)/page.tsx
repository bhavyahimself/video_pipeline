/**
 * ClipEngine — Dashboard Home
 */
"use client";

import Link from "next/link";

const STATS = [
  { label: "Videos Created", value: "12", change: "+3 this week", icon: "🎬" },
  { label: "Total Duration", value: "14.5 min", change: "+2.3 min", icon: "⏱️" },
  { label: "Active Jobs", value: "1", change: "In progress", icon: "⚡" },
  { label: "Plan", value: "Free", change: "1/3 videos used", icon: "📋" },
];

const RECENT_VIDEOS = [
  {
    id: "1",
    title: "$100K in SF vs $100K in Texas",
    channel: "Salary Transparent",
    status: "done",
    date: "2 hours ago",
    thumbnail: null,
  },
  {
    id: "2",
    title: "Sabrina Carpenter Almost Quit Music",
    channel: "Taylor & Sabrina",
    status: "done",
    date: "Yesterday",
    thumbnail: null,
  },
  {
    id: "3",
    title: "How Mike Tyson Blew $300M",
    channel: "How They Went Broke",
    status: "assembling",
    date: "Just now",
    thumbnail: null,
  },
];

const STATUS_COLORS: Record<string, string> = {
  done: "bg-green-500/10 text-green-400 border-green-500/20",
  queued: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  failed: "bg-red-500/10 text-red-400 border-red-500/20",
  assembling: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  scripting: "bg-purple-500/10 text-purple-400 border-purple-500/20",
};

export default function DashboardPage() {
  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Welcome back! Here's what's happening.</p>
        </div>
        <Link
          href="/create"
          className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 rounded-lg font-medium transition shadow-lg shadow-brand-600/25"
        >
          + Create Video
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {STATS.map((stat) => (
          <div
            key={stat.label}
            className="p-5 bg-surface-raised border border-white/5 rounded-xl"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">{stat.label}</span>
              <span className="text-lg">{stat.icon}</span>
            </div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-xs text-gray-500 mt-1">{stat.change}</div>
          </div>
        ))}
      </div>

      {/* Recent Videos */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Recent Videos</h2>
          <Link href="/library" className="text-sm text-brand-400 hover:text-brand-300">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {RECENT_VIDEOS.map((video) => (
            <Link
              key={video.id}
              href={`/library/${video.id}`}
              className="group bg-surface-raised border border-white/5 rounded-xl overflow-hidden hover:border-brand-600/30 transition"
            >
              {/* Thumbnail placeholder */}
              <div className="aspect-[9/16] max-h-48 bg-white/5 flex items-center justify-center">
                <span className="text-4xl opacity-20">🎬</span>
              </div>
              <div className="p-4">
                <h3 className="font-medium text-sm group-hover:text-brand-400 transition line-clamp-1">
                  {video.title}
                </h3>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-500">{video.channel}</span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full border ${
                      STATUS_COLORS[video.status] || STATUS_COLORS.queued
                    }`}
                  >
                    {video.status}
                  </span>
                </div>
                <div className="text-xs text-gray-600 mt-2">{video.date}</div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "New Video", icon: "✨", href: "/create" },
            { label: "Browse Channels", icon: "📺", href: "/channels" },
            { label: "View Analytics", icon: "📈", href: "/analytics" },
            { label: "Manage Plan", icon: "💳", href: "/settings/billing" },
          ].map((action) => (
            <Link
              key={action.label}
              href={action.href}
              className="p-4 bg-surface-raised border border-white/5 rounded-xl text-center hover:border-brand-600/30 transition"
            >
              <div className="text-2xl mb-2">{action.icon}</div>
              <div className="text-sm text-gray-300">{action.label}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

