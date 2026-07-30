/**
 * ClipEngine — Login Page
 */
"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.login(email, password);
      router.push("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="text-4xl">🎬</span>
          <h1 className="text-2xl font-bold mt-4">Welcome back</h1>
          <p className="text-gray-400 mt-2">Sign in to your ClipEngine account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 bg-surface-raised border border-white/10 rounded-lg focus:outline-none focus:border-brand-500 transition text-white"
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 bg-surface-raised border border-white/10 rounded-lg focus:outline-none focus:border-brand-500 transition text-white"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-brand-600 hover:bg-brand-700 rounded-lg font-medium transition disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-400">
            Don't have an account?{" "}
            <Link href="/register" className="text-brand-400 hover:text-brand-300">
              Sign up free
            </Link>
          </p>
        </div>

        <div className="mt-8">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-surface text-gray-500">Or continue with</span>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <button className="flex items-center justify-center gap-2 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition text-sm">
              <span>🔵</span> Google
            </button>
            <button className="flex items-center justify-center gap-2 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition text-sm">
              <span>⚫</span> GitHub
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

