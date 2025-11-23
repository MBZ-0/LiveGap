"use client";

import { useState } from "react";

type Goal = "sign_up" | "book_demo" | "add_to_cart" | "extract_pricing";

type SiteResult = {
  site_id: string;
  site_name: string;
  url: string;
  success: boolean;
  reason: string;
  video_url?: string | null;
};

type RunResponse = {
  goal: Goal;
  mode: "heuristic" | "llm";
  overall_success_rate: number;
  total_sites: number;
  successful_sites: number;
  failed_sites: number;
  results: SiteResult[];
};

// Resolve API base from env; add fallback + debug exposure.
let API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "").replace(/\/$/, "");
if (!API_BASE) {
  API_BASE = "http://localhost:8000"; // fallback if env missing
}
// eslint-disable-next-line no-console
console.log("[LiveGap Mini] API_BASE=", API_BASE);

export default function HomePage() {
  const [goal, setGoal] = useState<Goal>("extract_pricing");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"heuristic" | "llm">("heuristic");
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RunResponse | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  function openVideo(url?: string | null) {
    if (url) setVideoUrl(url);
  }
  function closeVideo() {
    setVideoUrl(null);
  }

  async function runRealityCheck() {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/run-reality-check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal, mode }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      const json = (await res.json()) as RunResponse;
      setData(json);
    } catch (e: any) {
      setError(e.message || "Failed to run reality check");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <div className="mx-auto max-w-4xl px-6 py-10">
        {/* Header */}
        <header className="mb-8">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">
            LiveGap Mini
          </p>
          <h1 className="mt-2 text-3xl font-semibold">
            See how badly your agent would fail on real sites.
          </h1>
          <p className="mt-2 text-sm text-slate-400 max-w-xl">
            We run a reference browser agent against a fixed set of painful
            real-world sites and estimate how easy it would be for an AI
            assistant to achieve a simple goal like “find pricing” or “book a
            demo”.
          </p>
        </header>
        {/* Debug: show API base in dev */}
        <div className="mb-4 rounded-xl border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-400">
          <span className="font-semibold text-slate-300">API Base:</span> {API_BASE}
        </div>

        {/* Control panel */}
        <section className="mb-8 rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div className="flex-1 space-y-2">
              <label className="text-xs font-medium uppercase text-slate-400">
                Goal
              </label>
              <select
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-slate-400"
                value={goal}
                onChange={(e) => setGoal(e.target.value as Goal)}
              >
                <option value="extract_pricing">Extract pricing info</option>
                <option value="sign_up">Sign up / create an account</option>
                <option value="book_demo">Book a demo / talk to sales</option>
                <option value="add_to_cart">Add a product to cart</option>
              </select>
              <p className="text-xs text-slate-500">
                We use a fixed internal agent as a benchmark and score each site
                on whether it exposes clear cues for this goal.
              </p>
            </div>
            <div className="flex-1 space-y-2">
              <label className="text-xs font-medium uppercase text-slate-400">Mode</label>
              <select
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-slate-400"
                value={mode}
                onChange={(e) => setMode(e.target.value as "heuristic" | "llm")}
              >
                <option value="heuristic">Heuristic (fast)</option>
                <option value="llm">LLM (iterative)</option>
              </select>
              <p className="text-xs text-slate-500">
                LLM mode runs multi-step planner loop (stubbed) per site.
              </p>
            </div>

            <button
              onClick={runRealityCheck}
              disabled={loading}
              className="mt-2 inline-flex items-center justify-center rounded-xl bg-red-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-red-500/25 transition hover:bg-red-600 disabled:cursor-not-allowed disabled:bg-slate-700"
            >
              {loading ? "Running on 10 sites…" : "Run Reality Check"}
            </button>
          </div>
          {error && (
            <p className="mt-3 rounded-xl bg-red-900/40 px-3 py-2 text-xs text-red-200">
              {error}
            </p>
          )}
        </section>

        {/* Results */}
        {data && (
          <section className="space-y-6">
            {/* Scorecard */}
            <div className="flex flex-col gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-slate-400">
                  Reality score
                </p>
                <p className="mt-2 text-4xl font-semibold">
                  {data.overall_success_rate.toFixed(0)}
                  <span className="text-lg text-slate-400"> / 100</span>
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  {data.successful_sites} / {data.total_sites} sites where a
                  reference agent could reasonably achieve the goal.
                </p>
              </div>
              <div className="text-xs text-slate-400">
                <p>
                  Goal:{" "}
                  <span className="font-semibold text-slate-200">
                    {goal.replace("_", " ")}
                  </span>
                </p>
                <p>
                  Mode:{" "}
                  <span className="font-semibold text-slate-200">{mode}</span>
                </p>
                <p>
                  Successes:{" "}
                  <span className="text-emerald-400">
                    {data.successful_sites}
                  </span>
                </p>
                <p>
                  Failures:{" "}
                  <span className="text-red-400">{data.failed_sites}</span>
                </p>
              </div>
            </div>

            {/* Table of sites */}
            <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-900/80 text-xs uppercase tracking-wide text-slate-400">
                  <tr>
                    <th className="px-4 py-3 text-left">Site</th>
                    <th className="px-4 py-3 text-left">URL</th>
                    <th className="px-4 py-3 text-left">Result</th>
                    <th className="px-4 py-3 text-left">Reason</th>
                    <th className="px-4 py-3 text-left">Video</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {data.results.map((r) => (
                    <tr key={r.site_id} className="hover:bg-slate-900/80">
                      <td className="px-4 py-3 font-medium text-slate-100">
                        {r.site_name}
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-400">
                        <a
                          href={r.url}
                          target="_blank"
                          rel="noreferrer"
                          className="underline decoration-dotted underline-offset-2"
                        >
                          {r.url}
                        </a>
                      </td>
                      <td className="px-4 py-3">
                        {r.success ? (
                          <span className="rounded-full bg-emerald-500/15 px-2.5 py-1 text-xs font-medium text-emerald-300">
                            success
                          </span>
                        ) : (
                          <span className="rounded-full bg-red-500/15 px-2.5 py-1 text-xs font-medium text-red-300">
                            failed
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-300">
                        {r.reason}
                      </td>
                      <td className="px-4 py-3 text-xs">
                        {r.video_url ? (
                          <button
                            type="button"
                            onClick={() => openVideo(r.video_url)}
                            className="underline decoration-dotted underline-offset-2 text-slate-400 hover:text-slate-200"
                          >
                            video
                          </button>
                        ) : (
                          <span className="text-slate-600">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Raw JSON (dev view) */}
            <details className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-xs text-slate-300">
              <summary className="cursor-pointer text-slate-200">
                Developer view (raw JSON)
              </summary>
              <pre className="mt-3 max-h-80 overflow-auto text-[11px] leading-relaxed">
                {JSON.stringify(data, null, 2)}
              </pre>
            </details>
          </section>
        )}
      </div>
      {videoUrl && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" role="dialog" aria-modal="true">
          <div className="w-full max-w-3xl rounded-2xl border border-slate-700 bg-slate-900 p-4 shadow-xl">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-medium text-slate-200">Recorded Session</h2>
              <button
                onClick={closeVideo}
                className="rounded-md bg-slate-800 px-2 py-1 text-xs text-slate-300 hover:bg-slate-700"
              >
                Close
              </button>
            </div>
            <video
              key={videoUrl}
              className="w-full rounded-md bg-black"
              controls
              autoPlay
              src={`${API_BASE}${videoUrl}`}
            >
              Your browser does not support HTML5 video.
            </video>
          </div>
        </div>
      )}
    </div>
  );
}
