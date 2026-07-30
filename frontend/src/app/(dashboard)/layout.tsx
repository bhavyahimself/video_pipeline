/**
 * ClipEngine — Dashboard Layout
 * Sidebar + top bar for authenticated pages.
 */
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "📊" },
  { href: "/create", label: "Create Video", icon: "✨" },
  { href: "/library", label: "Video Library", icon: "📁" },
  { href: "/channels", label: "Channels", icon: "📺" },
  { href: "/templates", label: "Templates", icon: "🧩" },
  { href: "/analytics", label: "Analytics", icon: "📈" },
];

const BOTTOM_NAV = [
  { href: "/settings", label: "Settings", icon: "⚙️" },
  { href: "/settings/billing", label: "Billing", icon: "💳" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-surface border-r border-white/5 flex flex-col">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-white/5">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">🎬</span>
            <span className="text-lg font-bold bg-gradient-to-r from-brand-400 to-brand-600 bg-clip-text text-transparent">
              ClipEngine
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition ${
                  isActive
                    ? "bg-brand-600/10 text-brand-400 border border-brand-600/20"
                    : "text-gray-400 hover:text-white hover:bg-white/5"
                }`}
              >
                <span className="text-base">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Bottom nav */}
        <div className="px-3 py-4 border-t border-white/5 space-y-1">
          {BOTTOM_NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-white/5 transition"
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </div>

        {/* Usage meter */}
        <div className="px-4 py-4 border-t border-white/5">
          <div className="text-xs text-gray-500 mb-2">Videos This Month</div>
          <div className="w-full bg-white/5 rounded-full h-2 mb-1">
            <div className="bg-brand-500 h-2 rounded-full" style={{ width: "33%" }} />
          </div>
          <div className="text-xs text-gray-400">1 / 3 used</div>
          <Link
            href="/settings/billing"
            className="block mt-3 text-xs text-brand-400 hover:text-brand-300"
          >
            Upgrade for more →
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {/* Top bar */}
        <header className="sticky top-0 z-40 h-16 bg-surface/80 backdrop-blur-xl border-b border-white/5 flex items-center justify-between px-8">
          <div>
            <input
              type="text"
              placeholder="Search videos, scripts, channels..."
              className="w-80 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm focus:outline-none focus:border-brand-500 transition"
            />
          </div>
          <div className="flex items-center gap-4">
            <button className="w-9 h-9 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 transition">
              🔔
            </button>
            <div className="w-9 h-9 rounded-full bg-brand-600 flex items-center justify-center text-sm font-medium">
              U
            </div>
          </div>
        </header>

        {/* Page content */}
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}

