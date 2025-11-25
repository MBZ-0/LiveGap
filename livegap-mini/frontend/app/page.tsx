"use client";

import { useState, useEffect } from "react";

type Goal =
  | "I’m trying to talk to sales — can you help me reach the sales team?"
  | "Can you show me the pricing or plans for this company?"
  | "How do I create an account or get started?"
  | "Where can I find documentation or help resources?"
  | "Can you show me what customers say about this product?";

type SiteResult = {
  site_id: string;
  site_name: string;
  url: string;
  success: boolean;
  reason: string;
  video_url?: string | null;
  steps?: Step[] | null;
  report?: string | null;
};

type RunResponse = {
  goal: Goal;
  overall_success_rate: number;
  total_sites: number;
  successful_sites: number;
  failed_sites: number;
  results: SiteResult[];
};

type Step = {
  index: number;
  action: string;
  target?: string | null;
  observation?: string | null;
  reasoning?: string | null;
  succeeded?: boolean | null;
  done: boolean;
};

// Resolve API base from env; add fallback + debug exposure.
let API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "").replace(/\/$/, "");
if (!API_BASE) {
  API_BASE = "http://localhost:8000"; // fallback if env missing
}
// eslint-disable-next-line no-console
console.log("[another.ai Mini] API_BASE=", API_BASE);

type TestRun = {
  id: string;
  name: string;
  goal: Goal;
  createdAt: string; // ISO timestamp
  overallSuccessRate: number;
  results: SiteResult[];
};

const GOAL_SHORT: Record<Goal, string> = {
  "I’m trying to talk to sales — can you help me reach the sales team?": "Talk to Sales",
  "Can you show me the pricing or plans for this company?": "Pricing",
  "How do I create an account or get started?": "Sign Up",
  "Where can I find documentation or help resources?": "Help",
  "Can you show me what customers say about this product?": "Customers",
};

export default function HomePage() {
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newTestName, setNewTestName] = useState("");
  const [newTestGoal, setNewTestGoal] = useState<Goal>("Can you show me the pricing or plans for this company?");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [reportText, setReportText] = useState<string | null>(null);
  const [reportSiteName, setReportSiteName] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  // Load persisted runs from localStorage on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem("lg_runs");
      if (raw) {
        const parsed: TestRun[] = JSON.parse(raw);
        setTestRuns(parsed);
        if (parsed.length) setActiveRunId(parsed[0].id);
      }
    } catch (_) {}
  }, []);

  // Persist runs whenever they change
  useEffect(() => {
    try {
      localStorage.setItem("lg_runs", JSON.stringify(testRuns));
    } catch (_) {}
  }, [testRuns]);

  // Auto-select newest run if none selected
  useEffect(() => {
    if (!activeRunId && testRuns.length) setActiveRunId(testRuns[0].id);
  }, [activeRunId, testRuns]);

  const activeRun = activeRunId ? testRuns.find(r => r.id === activeRunId) || null : null;

  const filteredRuns = testRuns.filter(r => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return r.name.toLowerCase().includes(q) || GOAL_SHORT[r.goal].toLowerCase().includes(q);
  });
  function openVideo(url?: string | null) {
    if (url) setVideoUrl(url);
  }
  function closeVideo() {
    setVideoUrl(null);
  }

  function openReport(r: SiteResult) {
    if (r.report) {
      setReportText(r.report);
      setReportSiteName(r.site_name);
    }
  }
  function closeReport() {
    setReportText(null);
    setReportSiteName(null);
  }

  async function createAndRunTest() {
    if (!newTestName.trim()) {
      setError("Test name required");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/run-reality-check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal: newTestGoal }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      const json = (await res.json()) as RunResponse;
      const newRun: TestRun = {
        id: crypto.randomUUID(),
        name: newTestName.trim(),
        goal: newTestGoal,
        createdAt: new Date().toISOString(),
        overallSuccessRate: json.overall_success_rate,
        results: json.results,
      };
      setTestRuns(prev => [newRun, ...prev]);
      setActiveRunId(newRun.id);
      setCreateModalOpen(false);
      setNewTestName("");
    } catch (e: any) {
      setError(e.message || "Failed to run test");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
      {/* Global Header */}
      <header className="h-14 flex items-center justify-between border-b border-slate-800 bg-slate-900/70 px-6">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded bg-red-500/90 flex items-center justify-center text-xs font-bold tracking-wide">A</div>
          <span className="text-sm font-semibold tracking-wide">another.ai</span>
        </div>
        <div className="hidden md:flex items-center gap-4 text-[11px] text-slate-400">
          <span>API Base:</span>
          <code className="text-[11px] text-slate-300">{API_BASE}</code>
        </div>
      </header>
      {/* Body layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-72 flex flex-col border-r border-slate-800 bg-slate-900/40">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h2 className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Test Runs</h2>
            <button
              onClick={() => setCreateModalOpen(true)}
              disabled={loading}
              className="rounded-md bg-red-500 px-3 py-1.5 text-[11px] font-semibold text-white shadow shadow-red-500/30 hover:bg-red-600 disabled:bg-slate-700 disabled:cursor-not-allowed"
            >
              {loading ? "Running…" : "New"}
            </button>
          </div>
          <div className="p-3">
            <input
              placeholder="Search runs…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-xs outline-none focus:border-slate-500"
            />
          </div>
          <div className="flex-1 overflow-auto px-3 pb-4 space-y-2">
            {filteredRuns.length === 0 && (
              <p className="text-[11px] text-slate-500 mt-2">No test runs yet.</p>
            )}
            {filteredRuns.map(run => {
              const selected = activeRunId === run.id;
              const created = new Date(run.createdAt).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
              return (
                <button
                  key={run.id}
                  onClick={() => setActiveRunId(run.id)}
                  className={`group w-full rounded-lg border px-3 py-2 text-left transition ${selected ? 'border-red-500/60 bg-red-500/10' : 'border-slate-800 bg-slate-950/40 hover:border-slate-700 hover:bg-slate-900/60'}`}
                >
                  <div className="flex items-start justify-between">
                    <span className={`text-xs font-medium ${selected ? 'text-slate-100' : 'text-slate-200'}`}>{run.name}</span>
                  </div>
                  <div className="mt-1 flex items-center justify-between">
                    <span className="text-[10px] uppercase tracking-wide text-slate-400">{GOAL_SHORT[run.goal]}</span>
                    <span className="text-[10px] text-slate-500">{created}</span>
                  </div>
                  <div className="mt-1 text-[10px] text-slate-500">Success: {run.overallSuccessRate.toFixed(0)}%</div>
                </button>
              );
            })}
          </div>
        </aside>
        {/* Main Content */}
        <main className="flex-1 overflow-auto p-8">
          {error && (
            <div className="mb-4 rounded-md border border-red-800 bg-red-900/30 px-3 py-2 text-[11px] text-red-200">{error}</div>
          )}
          {!activeRun && testRuns.length === 0 && (
            <div className="max-w-xl mx-auto mt-16 text-center">
              <h1 className="text-2xl font-semibold text-slate-100">Run your first agent test</h1>
              <p className="mt-3 text-sm text-slate-400">Gauge how your reference browser agent performs across common SaaS sites.</p>
              <ul className="mt-6 space-y-2 text-left text-sm text-slate-300">
                <li className="flex gap-2"><span className="mt-1 h-2 w-2 rounded-full bg-red-500" />We run your reference agent against 10 SaaS websites.</li>
                <li className="flex gap-2"><span className="mt-1 h-2 w-2 rounded-full bg-red-500" />We evaluate how often it can complete the chosen goal.</li>
                <li className="flex gap-2"><span className="mt-1 h-2 w-2 rounded-full bg-red-500" />We record video and a step-by-step report for each site.</li>
              </ul>
              <button
                onClick={() => setCreateModalOpen(true)}
                className="mt-8 inline-flex items-center rounded-md bg-red-500 px-5 py-2.5 text-sm font-semibold text-white shadow shadow-red-500/30 hover:bg-red-600"
              >
                Create your first test
              </button>
            </div>
          )}
          {activeRun && (
            <div className="space-y-8">
              {/* Run header */}
              <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
                <div className="space-y-2">
                  <h1 className="text-2xl font-semibold text-slate-100">{activeRun.name}</h1>
                  <p className="text-sm text-slate-300">{activeRun.goal}</p>
                  <p className="text-xs text-slate-500">Created {new Date(activeRun.createdAt).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</p>
                </div>
                <div className="flex items-center gap-4">
                  {(() => {
                    const pct = Math.round(activeRun.overallSuccessRate);
                    const color = pct >= 70 ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40' : pct >= 40 ? 'bg-yellow-500/15 text-yellow-300 border-yellow-500/40' : 'bg-red-500/15 text-red-300 border-red-500/40';
                    return (
                      <div className={`rounded-xl border px-6 py-4 text-center ${color}`}>
                        <p className="text-4xl font-semibold leading-none">{pct}<span className="text-lg align-top">%</span></p>
                        <p className="mt-1 text-[11px] uppercase tracking-wide">Overall Success</p>
                      </div>
                    );
                  })()}
                </div>
              </div>
              {/* Sites evaluated */}
              <div className="rounded-xl border border-slate-800 bg-slate-900/50">
                <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
                  <h2 className="text-sm font-semibold text-slate-200">Sites Evaluated</h2>
                  <span className="text-[11px] text-slate-500">Total: {activeRun.results.length}</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-xs">
                    <thead>
                      <tr className="bg-slate-900/70 text-[11px] uppercase tracking-wide text-slate-400">
                        <th className="px-4 py-2 text-left">Site</th>
                        <th className="px-4 py-2 text-left">URL</th>
                        <th className="px-4 py-2 text-left">Status</th>
                        <th className="px-4 py-2 text-left">Reason</th>
                        <th className="px-4 py-2 text-left">Artifacts</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {activeRun.results.map(r => {
                        const shortUrl = r.url.length > 55 ? r.url.slice(0, 55) + '…' : r.url;
                        const shortReason = r.reason.length > 140 ? r.reason.slice(0, 140) + '…' : r.reason;
                        return (
                          <tr key={r.site_id} className="hover:bg-slate-900/60">
                            <td className="px-4 py-3 font-medium text-slate-200">{r.site_name}</td>
                            <td className="px-4 py-3 text-[11px] text-slate-400">
                              <a href={r.url} target="_blank" rel="noreferrer" className="underline decoration-dotted underline-offset-2">{shortUrl}</a>
                            </td>
                            <td className="px-4 py-3">
                              {r.success ? (
                                <span className="rounded-full bg-emerald-500/15 px-2.5 py-1 text-[11px] font-medium text-emerald-300">Success</span>
                              ) : (
                                <span className="rounded-full bg-red-500/15 px-2.5 py-1 text-[11px] font-medium text-red-300">Failed</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-[11px] text-slate-300 leading-relaxed w-[28rem] max-w-[28rem]">{shortReason}</td>
                            <td className="px-4 py-3 text-[11px] text-slate-400">
                              <div className="flex gap-2">
                                {r.video_url && (
                                  <button
                                    type="button"
                                    onClick={() => openVideo(r.video_url)}
                                    className="rounded-md border border-slate-700 px-2 py-1 hover:border-slate-500 hover:bg-slate-800/60"
                                  >Video</button>
                                )}
                                {r.report && (
                                  <button
                                    type="button"
                                    onClick={() => openReport(r)}
                                    className="rounded-md border border-slate-700 px-2 py-1 hover:border-slate-500 hover:bg-slate-800/60"
                                  >Report</button>
                                )}
                                {!r.video_url && !r.report && <span className="text-slate-600">—</span>}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
        {/* Create Test Modal */}
        {createModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" role="dialog" aria-modal="true">
            <div className="w-full max-w-md rounded-2xl border border-slate-700 bg-slate-900 p-5 shadow-xl">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-sm font-medium text-slate-200">New Agent Test</h2>
                <button onClick={() => setCreateModalOpen(false)} className="rounded-md bg-slate-800 px-2 py-1 text-xs text-slate-300 hover:bg-slate-700">Close</button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-medium uppercase text-slate-400">Test Name</label>
                  <input
                    value={newTestName}
                    onChange={(e) => setNewTestName(e.target.value)}
                    className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-slate-400"
                    placeholder="Slack onboarding – talk to sales"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium uppercase text-slate-400">Goal</label>
                  <select
                    value={newTestGoal}
                    onChange={(e) => setNewTestGoal(e.target.value as Goal)}
                    className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-slate-400"
                  >
                    {Object.keys(GOAL_SHORT).map(g => (
                      <option key={g} value={g}>{g}</option>
                    ))}
                  </select>
                </div>
                <button
                  onClick={createAndRunTest}
                  disabled={loading}
                  className="w-full rounded-xl bg-red-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-red-500/25 transition hover:bg-red-600 disabled:cursor-not-allowed disabled:bg-slate-700"
                >
                  {loading ? "Running test…" : "Run test on 10 SaaS sites"}
                </button>
              </div>
            </div>
          </div>
        )}
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
      {/* Steps modal removed: reports supersede granular step table */}
      {reportText && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" role="dialog" aria-modal="true">
          <div className="w-full max-w-4xl rounded-2xl border border-slate-700 bg-slate-900 p-5 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-sm font-medium text-slate-200">Report – {reportSiteName}</h2>
              <button
                onClick={closeReport}
                className="rounded-md bg-slate-800 px-2 py-1 text-xs text-slate-300 hover:bg-slate-700"
              >
                Close
              </button>
            </div>
            <div className="max-h-[60vh] overflow-auto rounded-lg border border-slate-800 bg-slate-950/40 p-4 text-xs leading-relaxed">
              {/* Render markdown naïvely; could integrate a parser later */}
              <pre className="whitespace-pre-wrap font-mono text-[11px] text-slate-200">{reportText}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
