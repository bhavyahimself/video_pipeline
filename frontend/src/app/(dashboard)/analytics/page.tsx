/**
 * ClipEngine — Analytics Dashboard
 */
"use client";

export default function AnalyticsPage() {
  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold mb-2">Analytics</h1>
      <p className="text-gray-400 text-sm mb-8">Track your video production metrics.</p>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Videos", value: "12", icon: "🎬" },
          { label: "This Month", value: "5", icon: "📅" },
          { label: "Total Duration", value: "14.5 min", icon: "⏱️" },
          { label: "Avg Gen Time", value: "3.2 min", icon: "⚡" },
        ].map((stat) => (
          <div key={stat.label} className="p-5 bg-surface-raised border border-white/5 rounded-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">{stat.label}</span>
              <span>{stat.icon}</span>
            </div>
            <div className="text-2xl font-bold">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Channel Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-surface-raised border border-white/5 rounded-xl p-6">
          <h3 className="font-semibold mb-4">Videos by Channel</h3>
          <div className="space-y-3">
            {[
              { name: "Salary Transparent", count: 5, pct: 42 },
              { name: "Taylor & Sabrina", count: 3, pct: 25 },
              { name: "How They Went Broke", count: 2, pct: 17 },
              { name: "Designed to Trick You", count: 1, pct: 8 },
              { name: "One Decision", count: 1, pct: 8 },
            ].map((ch) => (
              <div key={ch.name} className="flex items-center gap-3">
                <div className="w-32 text-sm text-gray-300 truncate">{ch.name}</div>
                <div className="flex-1 bg-white/5 rounded-full h-2">
                  <div
                    className="bg-brand-500 h-2 rounded-full"
                    style={{ width: `${ch.pct}%` }}
                  />
                </div>
                <div className="text-sm text-gray-400 w-8 text-right">{ch.count}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-surface-raised border border-white/5 rounded-xl p-6">
          <h3 className="font-semibold mb-4">Generation Time Trend</h3>
          <div className="flex items-end gap-2 h-40">
            {[3.1, 2.8, 4.2, 3.5, 2.9, 3.0, 3.2].map((time, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div
                  className="w-full bg-brand-500/50 rounded-t"
                  style={{ height: `${(time / 5) * 100}%` }}
                />
                <span className="text-xs text-gray-500">{time}m</span>
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-600">
            <span>Mon</span>
            <span>Sun</span>
          </div>
        </div>
      </div>
    </div>
  );
}

