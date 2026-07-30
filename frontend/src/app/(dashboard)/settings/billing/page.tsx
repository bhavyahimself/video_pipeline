/**
 * ClipEngine — Billing Page
 */
"use client";

const PLANS = [
  {
    name: "Free",
    price: 0,
    current: true,
    features: ["3 videos/month", "3 channels", "720p", "Watermark"],
  },
  {
    name: "Creator",
    price: 29,
    current: false,
    popular: true,
    features: ["30 videos/month", "All 11 channels", "1080p", "No watermark", "YouTube upload", "Custom voice"],
  },
  {
    name: "Studio",
    price: 99,
    current: false,
    features: ["Unlimited videos", "Custom channels", "Team (5)", "API access", "Batch gen", "Priority queue"],
  },
  {
    name: "Enterprise",
    price: 299,
    current: false,
    features: ["Everything in Studio", "Unlimited team", "White-label", "Dedicated workers", "Custom SLA"],
  },
];

export default function BillingPage() {
  return (
    <div className="max-w-4xl animate-fade-in">
      <h1 className="text-2xl font-bold mb-2">Billing & Plan</h1>
      <p className="text-gray-400 text-sm mb-8">Manage your subscription and usage.</p>

      {/* Current Usage */}
      <div className="bg-surface-raised border border-white/5 rounded-xl p-6 mb-8">
        <h3 className="font-semibold mb-4">Current Usage</h3>
        <div className="grid grid-cols-3 gap-6">
          <div>
            <div className="text-sm text-gray-500">Plan</div>
            <div className="text-lg font-bold mt-1">Free</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Videos Used</div>
            <div className="text-lg font-bold mt-1">1 / 3</div>
            <div className="w-full bg-white/5 rounded-full h-2 mt-2">
              <div className="bg-brand-500 h-2 rounded-full" style={{ width: "33%" }} />
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Resets</div>
            <div className="text-lg font-bold mt-1">In 27 days</div>
          </div>
        </div>
      </div>

      {/* Plans */}
      <h3 className="font-semibold mb-4">Available Plans</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {PLANS.map((plan) => (
          <div
            key={plan.name}
            className={`p-5 rounded-xl border ${
              plan.popular
                ? "bg-brand-600/10 border-brand-600/30 ring-1 ring-brand-600/20"
                : "bg-surface-raised border-white/5"
            }`}
          >
            {plan.popular && (
              <div className="text-xs font-medium text-brand-400 mb-2">MOST POPULAR</div>
            )}
            <h4 className="font-semibold">{plan.name}</h4>
            <div className="mt-1 mb-4">
              <span className="text-2xl font-bold">${plan.price}</span>
              {plan.price > 0 && <span className="text-gray-400 text-sm">/mo</span>}
            </div>
            <ul className="space-y-2 mb-6">
              {plan.features.map((f) => (
                <li key={f} className="text-xs text-gray-300 flex gap-2">
                  <span className="text-brand-400">✓</span> {f}
                </li>
              ))}
            </ul>
            <button
              className={`w-full py-2 rounded-lg text-sm font-medium transition ${
                plan.current
                  ? "bg-white/5 border border-white/10 text-gray-400 cursor-not-allowed"
                  : plan.popular
                  ? "bg-brand-600 hover:bg-brand-700"
                  : "bg-white/5 border border-white/10 hover:bg-white/10"
              }`}
              disabled={plan.current}
            >
              {plan.current ? "Current Plan" : "Upgrade"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

