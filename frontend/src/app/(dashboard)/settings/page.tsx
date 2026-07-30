/**
 * ClipEngine — Settings Page
 */
"use client";

import Link from "next/link";

export default function SettingsPage() {
  return (
    <div className="max-w-2xl animate-fade-in">
      <h1 className="text-2xl font-bold mb-8">Settings</h1>

      {/* Profile */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Profile</h2>
        <div className="bg-surface-raised border border-white/5 rounded-xl p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Name</label>
            <input
              type="text"
              defaultValue="Demo User"
              className="w-full px-4 py-2.5 bg-surface border border-white/10 rounded-lg focus:outline-none focus:border-brand-500 transition text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Email</label>
            <input
              type="email"
              defaultValue="demo@clipengine.io"
              className="w-full px-4 py-2.5 bg-surface border border-white/10 rounded-lg focus:outline-none focus:border-brand-500 transition text-white"
              disabled
            />
          </div>
          <button className="px-4 py-2 bg-brand-600 hover:bg-brand-700 rounded-lg text-sm font-medium transition">
            Save Changes
          </button>
        </div>
      </section>

      {/* API Keys */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">API Keys</h2>
        <p className="text-sm text-gray-400 mb-4">
          Provide your own API keys for higher limits and custom configurations.
        </p>
        <div className="bg-surface-raised border border-white/5 rounded-xl p-6 space-y-4">
          {[
            { label: "OpenAI API Key", placeholder: "sk-..." },
            { label: "ElevenLabs API Key", placeholder: "Your ElevenLabs key" },
            { label: "Pexels API Key", placeholder: "Your Pexels key" },
          ].map((key) => (
            <div key={key.label}>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">{key.label}</label>
              <input
                type="password"
                placeholder={key.placeholder}
                className="w-full px-4 py-2.5 bg-surface border border-white/10 rounded-lg focus:outline-none focus:border-brand-500 transition text-white"
              />
            </div>
          ))}
          <button className="px-4 py-2 bg-brand-600 hover:bg-brand-700 rounded-lg text-sm font-medium transition">
            Save API Keys
          </button>
        </div>
      </section>

      {/* Integrations */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Integrations</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-surface-raised border border-white/5 rounded-xl">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📺</span>
              <div>
                <div className="font-medium text-sm">YouTube</div>
                <div className="text-xs text-gray-500">Connect to upload videos directly</div>
              </div>
            </div>
            <button className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm hover:bg-white/10 transition">
              Connect
            </button>
          </div>
        </div>
      </section>

      {/* Navigation to sub-pages */}
      <div className="grid grid-cols-2 gap-4">
        <Link
          href="/settings/billing"
          className="p-4 bg-surface-raised border border-white/5 rounded-xl hover:border-brand-600/20 transition"
        >
          <span className="text-xl">💳</span>
          <div className="font-medium text-sm mt-2">Billing & Plan</div>
          <div className="text-xs text-gray-500 mt-1">Manage your subscription</div>
        </Link>
        <Link
          href="/settings/team"
          className="p-4 bg-surface-raised border border-white/5 rounded-xl hover:border-brand-600/20 transition"
        >
          <span className="text-xl">👥</span>
          <div className="font-medium text-sm mt-2">Team</div>
          <div className="text-xs text-gray-500 mt-1">Manage team members</div>
        </Link>
      </div>
    </div>
  );
}

