"use client";

import Link from "next/link";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      {/* Header */}
      <header className="h-14 flex items-center justify-between border-b border-slate-800 bg-slate-900/70 px-6 sticky top-0 z-50 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded bg-red-500/90 flex items-center justify-center text-xs font-bold tracking-wide">A</div>
          <span className="text-sm font-semibold tracking-wide">another.ai</span>
        </div>
        <Link 
          href="/"
          className="text-xs font-medium text-slate-400 hover:text-slate-200 transition"
        >
          Back to Dashboard
        </Link>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(239,68,68,0.08),transparent_50%)]" />
        <div className="relative max-w-6xl mx-auto px-6 py-20">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-1.5 text-xs font-medium text-red-300 mb-6">
              <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
              AI Agent Reality Check Platform
            </div>
            <h1 className="text-5xl font-bold tracking-tight text-slate-50 mb-6">
              Know Why Your Agent Fails
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-red-600">Before Your Users Do</span>
            </h1>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-8 leading-relaxed">
              The first platform that shows you <strong className="text-slate-100">exactly</strong> why your browser agent drops from 92% in demos to 65% in production—with full video recordings and step-by-step traces.
            </p>
            <div className="flex items-center justify-center gap-4">
              <Link 
                href="/"
                className="inline-flex items-center rounded-xl bg-red-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-red-500/25 transition hover:bg-red-600"
              >
                Try Live Demo
              </Link>
              <a 
                href="#how-it-works"
                className="inline-flex items-center rounded-xl border border-slate-700 bg-slate-800/50 px-6 py-3 text-sm font-semibold text-slate-200 transition hover:bg-slate-800"
              >
                Learn More
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="border-b border-slate-800 bg-slate-950/50 py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-50 mb-4">The Problem</h2>
            <p className="text-lg text-slate-400">Every agent team faces the same nightmare</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                emoji: "🎬",
                title: "Demo Magic",
                stat: "92%",
                desc: "Your agent works perfectly on cherry-picked test sites. Investors are impressed.",
              },
              {
                emoji: "💥",
                title: "Production Reality",
                stat: "65%",
                desc: "Live users hit infinite loops, wrong clicks, and silent failures. Support tickets flood in.",
              },
              {
                emoji: "🔍",
                title: "The Mystery",
                stat: "0%",
                desc: "You have no idea which sites fail, why they fail, or how to fix it systematically.",
              },
            ].map((item, i) => (
              <div key={i} className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 text-center">
                <div className="text-4xl mb-3">{item.emoji}</div>
                <h3 className="text-lg font-semibold text-slate-100 mb-2">{item.title}</h3>
                <div className="text-3xl font-bold text-red-400 mb-3">{item.stat}</div>
                <p className="text-sm text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="border-b border-slate-800 py-20 bg-gradient-to-b from-slate-950 to-slate-900">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-50 mb-4">How It Works</h2>
            <p className="text-lg text-slate-400">From code to insights in 3 steps</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                num: "01",
                title: "Run Your Agent",
                desc: "We execute your browser agent against real SaaS websites with common user goals—pricing lookup, demo booking, account creation.",
                icon: "🚀",
              },
              {
                num: "02",
                title: "Capture Everything",
                desc: "Full video recordings, Playwright traces, step-by-step logs, and DOM snapshots for every single interaction.",
                icon: "📹",
              },
              {
                num: "03",
                title: "AI-Powered Analysis",
                desc: "Claude judges success/failure and classifies issues: infinite loops, hallucinations, CAPTCHA blocks, tool errors.",
                icon: "🧠",
              },
            ].map((step, i) => (
              <div key={i} className="relative">
                <div className="flex flex-col items-center text-center">
                  <div className="h-16 w-16 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center text-3xl mb-4">
                    {step.icon}
                  </div>
                  <div className="text-xs font-bold text-red-400 tracking-[0.2em] mb-2">{step.num}</div>
                  <h3 className="text-xl font-semibold text-slate-100 mb-3">{step.title}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{step.desc}</p>
                </div>
                {i < 2 && (
                  <div className="hidden md:block absolute top-8 left-[calc(100%+1rem)] w-[calc(100%-2rem)] h-0.5 bg-gradient-to-r from-red-500/50 to-transparent" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* MVP vs Vision Section */}
      <section className="border-b border-slate-800 bg-slate-950 py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-50 mb-4">MVP vs. Full Vision</h2>
            <p className="text-lg text-slate-400">We're shipping fast, but the future is even bigger</p>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            {/* MVP - What's Live Now */}
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-10 w-10 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold">✓</div>
                <div>
                  <h3 className="text-xl font-bold text-emerald-300">MVP (Live Now)</h3>
                  <p className="text-xs text-emerald-400/70 uppercase tracking-wide">Production Ready</p>
                </div>
              </div>
              <ul className="space-y-3 text-sm text-slate-300">
                <li className="flex gap-3">
                  <span className="text-emerald-400 mt-0.5">✓</span>
                  <span><strong className="text-slate-100">Built-in reference agent</strong> — Our pre-configured Playwright agent with Claude AI (no GitHub URL needed)</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-400 mt-0.5">✓</span>
                  <span><strong className="text-slate-100">10 curated SaaS sites</strong> — Hardcoded test suite covering common agent scenarios</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-400 mt-0.5">✓</span>
                  <span><strong className="text-slate-100">5 predefined goals</strong> — Talk to sales, pricing lookup, sign up, help docs, customer reviews</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-400 mt-0.5">✓</span>
                  <span><strong className="text-slate-100">Full video recordings</strong> — Playwright captures every session with video + trace artifacts</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-400 mt-0.5">✓</span>
                  <span><strong className="text-slate-100">AI judge + reports</strong> — Claude evaluates success/failure with detailed reasoning</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-400 mt-0.5">✓</span>
                  <span><strong className="text-slate-100">Success metrics</strong> — Overall % success rate per test run</span>
                </li>
              </ul>
            </div>

            {/* Full Vision */}
            <div className="rounded-xl border border-slate-700 bg-slate-900/50 p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-10 w-10 rounded-lg bg-red-500/20 flex items-center justify-center text-red-400 font-bold">🚀</div>
                <div>
                  <h3 className="text-xl font-bold text-slate-100">Full Vision</h3>
                  <p className="text-xs text-slate-500 uppercase tracking-wide">5-Week Roadmap</p>
                </div>
              </div>
              <ul className="space-y-3 text-sm text-slate-300">
                <li className="flex gap-3">
                  <span className="text-slate-500 mt-0.5">→</span>
                  <span><strong className="text-slate-100">Any GitHub repo</strong> — Accept any public agent URL, clone + run in Docker sandbox</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-slate-500 mt-0.5">→</span>
                  <span><strong className="text-slate-100">5,000+ sites</strong> — Shopify stores, SaaS pricing, gov forms, login walls scraped dynamically</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-slate-500 mt-0.5">→</span>
                  <span><strong className="text-slate-100">Custom goals</strong> — User-defined objectives for any workflow</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-slate-500 mt-0.5">→</span>
                  <span><strong className="text-slate-100">5 trials per site</strong> — Stochastic testing = 25,000 runs in 30 minutes</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-slate-500 mt-0.5">→</span>
                  <span><strong className="text-slate-100">Failure classification</strong> — Infinite loop, hallucination, CAPTCHA, tool error auto-tagged</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-slate-500 mt-0.5">→</span>
                  <span><strong className="text-slate-100">Auto-fix suggestions</strong> — Claude recommends prompt tweaks + predicts new success %</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-slate-500 mt-0.5">→</span>
                  <span><strong className="text-slate-100">Public leaderboard</strong> — Anonymized agent rankings (addictive for founders)</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-slate-500 mt-0.5">→</span>
                  <span><strong className="text-slate-100">Massive scale</strong> — 10,000 concurrent browser sessions via Browserless + residential proxies</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="border-b border-slate-800 py-20 bg-gradient-to-b from-slate-900 to-slate-950">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-50 mb-4">What You Get Today</h2>
            <p className="text-lg text-slate-400">Everything you need to validate your agent on real sites</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: "🎯",
                title: "Real-World Testing",
                desc: "10 carefully selected SaaS websites covering common use cases: CRMs, dev tools, productivity apps.",
              },
              {
                icon: "📊",
                title: "Success Metrics",
                desc: "Instant overall success rate + per-site breakdown. See which sites work and which don't.",
              },
              {
                icon: "🎥",
                title: "Video Recordings",
                desc: "Full Playwright video capture for every test. Watch exactly what your agent did (or tried to do).",
              },
              {
                icon: "📝",
                title: "AI-Generated Reports",
                desc: "Claude analyzes each session and writes a human-readable report explaining success or failure.",
              },
              {
                icon: "⚡",
                title: "Fast Execution",
                desc: "Run 10 sites in parallel. Get results in minutes, not hours. Background job tracking included.",
              },
              {
                icon: "🔒",
                title: "Production Ready",
                desc: "Deployed on AWS with S3 storage for videos. Built with Next.js + FastAPI for scale.",
              },
            ].map((feature, i) => (
              <div key={i} className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 hover:border-slate-700 transition">
                <div className="text-3xl mb-3">{feature.icon}</div>
                <h3 className="text-lg font-semibold text-slate-100 mb-2">{feature.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Milestones Section */}
      <section className="border-b border-slate-800 bg-slate-950 py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-50 mb-4">Product Milestones</h2>
            <p className="text-lg text-slate-400">Our journey from MVP to enterprise-grade platform</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            {/* Progress stats */}
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-6 text-center">
              <div className="text-4xl font-bold text-emerald-300 mb-2">2</div>
              <div className="text-xs uppercase tracking-wide text-emerald-400/70">Completed</div>
            </div>
            <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/5 p-6 text-center">
              <div className="text-4xl font-bold text-yellow-300 mb-2">1</div>
              <div className="text-xs uppercase tracking-wide text-yellow-400/70">In Progress</div>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-900/50 p-6 text-center">
              <div className="text-4xl font-bold text-slate-400 mb-2">2</div>
              <div className="text-xs uppercase tracking-wide text-slate-500">Upcoming</div>
            </div>
          </div>

          <div className="space-y-6">
            {[
              {
                milestone: "Milestone 1",
                status: "✅ Shipped",
                color: "emerald",
                title: "Core Agent Testing Infrastructure",
                subtitle: "Foundation for automated browser agent evaluation",
                desc: "Built the core runner using Playwright for browser automation with Claude AI for intelligent decision-making. Implemented video recording, trace capture, and parallel execution across real SaaS websites.",
                achievements: ["Playwright browser automation + Claude AI", "Video + HAR recording", "10 curated test sites", "Parallel test execution", "S3 storage integration"],
                impact: "Enables reliable, reproducible agent testing on production websites",
              },
              {
                milestone: "Milestone 2",
                status: "✅ Shipped",
                color: "emerald",
                title: "AI-Powered Evaluation & Insights",
                subtitle: "Automated success/failure analysis with Claude",
                desc: "Integrated Claude 3.5 Sonnet as LLM judge to evaluate agent performance. Generates detailed reports explaining why each test succeeded or failed.",
                achievements: ["Claude-based success evaluation", "Detailed failure reasoning", "Markdown report generation", "Per-site analysis", "Cost-efficient evaluation (<$0.001/run)"],
                impact: "Transforms raw execution data into actionable insights automatically",
              },
              {
                milestone: "Milestone 3",
                status: "🚧 In Progress",
                color: "yellow",
                title: "Production-Ready Dashboard",
                subtitle: "Enterprise UI for test management & reporting",
                desc: "Building a Next.js dashboard that rivals $10M products. Real-time job tracking, video playback, searchable test history, and rich data visualization.",
                achievements: ["Next.js + Tailwind + shadcn/ui", "Real-time background job polling", "Video modal with HTML5 player", "Test run history & search", "Responsive design"],
                impact: "Makes agent debugging delightful instead of painful",
              },
              {
                milestone: "Milestone 4",
                status: "⏳ Planned",
                color: "slate",
                title: "Massive Scale & Custom Agents",
                subtitle: "From 10 sites to 5,000+ with any GitHub repo",
                desc: "Accept any GitHub agent repo, clone and run in Docker sandbox. Scale to thousands of sites with residential proxies and distributed execution.",
                achievements: ["GitHub repo cloning + Docker sandboxing", "5,000+ test sites across verticals", "Residential proxy integration", "Distributed execution with Browserless", "Custom goal definitions"],
                impact: "Universal platform for any browser agent, any scale",
              },
              {
                milestone: "Milestone 5",
                status: "⏳ Planned",
                color: "slate",
                title: "Intelligence Layer & GTM",
                subtitle: "Auto-fix suggestions + public leaderboard + first customers",
                desc: "Add failure classification (loop, hallucination, CAPTCHA, tool error). Claude suggests prompt fixes and predicts improvement. Launch public leaderboard and land first 5 paying customers.",
                achievements: ["Automatic failure classification", "AI-suggested fixes with predicted impact", "Public anonymized leaderboard", "Outreach to 40 agent companies", "First $500 MRR"],
                impact: "From diagnostic tool to optimization copilot",
              },
            ].map((item, i) => (
              <div key={i} className={`rounded-xl border p-8 ${
                item.color === "emerald" ? "border-emerald-500/30 bg-emerald-500/5" :
                item.color === "yellow" ? "border-yellow-500/30 bg-yellow-500/5" :
                "border-slate-800 bg-slate-900/50"
              }`}>
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-xs font-bold text-red-400 tracking-[0.2em]">{item.milestone}</span>
                      <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                        item.color === "emerald" ? "bg-emerald-500/20 text-emerald-300" :
                        item.color === "yellow" ? "bg-yellow-500/20 text-yellow-300" :
                        "bg-slate-800 text-slate-400"
                      }`}>
                        {item.status}
                      </span>
                    </div>
                    <h3 className="text-2xl font-bold text-slate-50 mb-1">{item.title}</h3>
                    <p className="text-sm text-slate-400 italic">{item.subtitle}</p>
                  </div>
                </div>
                
                <p className="text-sm text-slate-300 mb-6 leading-relaxed">{item.desc}</p>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">Key Achievements</div>
                    <ul className="space-y-2">
                      {item.achievements.map((a, j) => (
                        <li key={j} className="flex gap-2 text-sm text-slate-300">
                          <span className="text-red-400 mt-1">▸</span>
                          <span>{a}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">Impact</div>
                    <div className="rounded-lg bg-slate-950/50 border border-slate-800/50 p-4">
                      <p className="text-sm text-slate-200 leading-relaxed italic">&ldquo;{item.impact}&rdquo;</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical Implementation Section */}
      <section className="border-b border-slate-800 py-20 bg-gradient-to-b from-slate-950 to-slate-900">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-50 mb-4">Technical Implementation</h2>
            <p className="text-lg text-slate-400">How we built the MVP</p>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
              <h3 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
                <span className="text-2xl">🎨</span>
                Frontend
              </h3>
              <ul className="space-y-2 text-sm text-slate-300">
                <li className="flex gap-2"><span className="text-red-400">•</span> Next.js 14 with App Router</li>
                <li className="flex gap-2"><span className="text-red-400">•</span> Tailwind CSS + shadcn/ui components</li>
                <li className="flex gap-2"><span className="text-red-400">•</span> Real-time polling for background jobs</li>
                <li className="flex gap-2"><span className="text-red-400">•</span> localStorage for test run persistence</li>
                <li className="flex gap-2"><span className="text-red-400">•</span> Video modal with HTML5 player</li>
                <li className="flex gap-2"><span className="text-red-400">•</span> Markdown report rendering</li>
              </ul>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
              <h3 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
                <span className="text-2xl">⚙️</span>
                Backend
              </h3>
              <ul className="space-y-2 text-sm text-slate-300">
                <li className="flex gap-2"><span className="text-red-400">•</span> FastAPI + Python 3.11</li>
                <li className="flex gap-2"><span className="text-red-400">•</span> Playwright for browser automation</li>
                <li className="flex gap-2"><span className="text-red-400">•</span> Claude 3.5 Sonnet (Anthropic API)</li>
                <li className="flex gap-2"><span className="text-red-400">•</span> Background jobs with asyncio</li>
                <li className="flex gap-2"><span className="text-red-400">•</span> S3 + CloudFront for video delivery</li>
                <li className="flex gap-2"><span className="text-red-400">•</span> In-memory run state management</li>
              </ul>
            </div>
          </div>
          <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <h3 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
              <span className="text-2xl">🏗️</span>
              Architecture Decisions
            </h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-semibold text-emerald-400 mb-3 uppercase tracking-wide">Static (MVP Implementation)</h4>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li className="flex gap-2">
                    <span className="text-emerald-400 mt-0.5">✓</span>
                    <div><strong className="text-slate-100">Built-in agent code</strong><br/><span className="text-xs text-slate-400">No GitHub repo cloning</span></div>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-emerald-400 mt-0.5">✓</span>
                    <div><strong className="text-slate-100">10 hardcoded test sites</strong><br/><span className="text-xs text-slate-400">Curated SaaS sites in sites.json</span></div>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-emerald-400 mt-0.5">✓</span>
                    <div><strong className="text-slate-100">5 predefined goals</strong><br/><span className="text-xs text-slate-400">Talk to sales, pricing, sign up, help, reviews</span></div>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-emerald-400 mt-0.5">✓</span>
                    <div><strong className="text-slate-100">Single agent implementation</strong><br/><span className="text-xs text-slate-400">One reference agent for all tests</span></div>
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wide">Dynamic (Future Vision)</h4>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li className="flex gap-2">
                    <span className="text-slate-500 mt-0.5">○</span>
                    <div><strong className="text-slate-100">Any GitHub repo</strong><br/><span className="text-xs text-slate-400">Clone + run in Docker sandbox</span></div>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-slate-500 mt-0.5">○</span>
                    <div><strong className="text-slate-100">5,000+ scraped sites</strong><br/><span className="text-xs text-slate-400">Shopify stores, SaaS, gov forms, auto-updated</span></div>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-slate-500 mt-0.5">○</span>
                    <div><strong className="text-slate-100">Custom user goals</strong><br/><span className="text-xs text-slate-400">Natural language objectives</span></div>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-slate-500 mt-0.5">○</span>
                    <div><strong className="text-slate-100">Multi-agent comparison</strong><br/><span className="text-xs text-slate-400">Test multiple agents side-by-side</span></div>
                  </li>
                </ul>
              </div>
            </div>
            <div className="mt-6 pt-6 border-t border-slate-800">
              <p className="text-sm text-slate-400 leading-relaxed">
                <strong className="text-slate-100">Why start static?</strong> Shipping a working product fast beats planning the perfect architecture. Static configuration gives us predictable results, easier debugging, and proves the core value proposition. Dynamic features add complexity that would delay launch by weeks.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-b from-slate-900 to-slate-950">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-slate-50 mb-6">Ready to See What's Breaking?</h2>
          <p className="text-xl text-slate-300 mb-8">
            Run your first test in <strong className="text-slate-100">under 5 minutes</strong>. No credit card, no signup.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link 
              href="/"
              className="inline-flex items-center rounded-xl bg-red-500 px-8 py-4 text-base font-semibold text-white shadow-xl shadow-red-500/25 transition hover:bg-red-600"
            >
              Launch Dashboard
            </Link>
          </div>
          <p className="mt-6 text-xs text-slate-500">
            Built by engineers who've debugged agent failures at 3 AM. We know the pain.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded bg-red-500/90 flex items-center justify-center text-xs font-bold tracking-wide">A</div>
              <span className="text-sm font-semibold tracking-wide text-slate-400">another.ai</span>
            </div>
            <p className="text-xs text-slate-500">Agent Reality Check Platform • 2025</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
