"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Navbar } from "@/components/navbar";
import {
  Sparkles,
  ArrowRight,
  GitBranch,
  Layers,
  BrainCircuit,
  Compass,
  ShieldCheck,
  CheckCircle2,
  Database,
  BarChart3,
} from "lucide-react";

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState<"problem" | "solution" | "evidence">("problem");

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 selection:bg-indigo-500 selection:text-white">
      <Navbar />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden pt-20 pb-28 md:pt-28 md:pb-36 bg-gradient-to-b from-white via-indigo-50/25 to-slate-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
            {/* Pill tag */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-indigo-200/80 bg-indigo-50/70 text-indigo-700 text-xs font-semibold shadow-2xs animate-fade-in">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              <span>Turning Real User Problems into Product Opportunities</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-slate-900 tracking-tight max-w-4xl mx-auto leading-[1.12]">
              Stop guessing roadmaps. <br />
              <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-indigo-500 bg-clip-text text-transparent">
                Discover unserved user demand.
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
              InsightForge AI analyzes thousands of public GitHub issues and discussions.
              Using semantic clustering and product intelligence models, it synthesizes
              recurring friction into high-confidence, actionable SaaS opportunities.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link
                href="/register"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl text-base font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-200 hover:shadow-lg hover:-translate-y-0.5 transition-all"
              >
                Start Free Analysis
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="#sample-report"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl text-base font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-200/90 shadow-2xs transition-all"
              >
                View Example Report
              </Link>
            </div>

            {/* Trust Bar */}
            <div className="pt-12 flex flex-wrap items-center justify-center gap-6 sm:gap-12 text-xs text-slate-500 font-medium">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>100% Real Public Evidence</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Zero Hallucinated Demand</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Transparent Confidence Metrics</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Private & User-Isolated History</span>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="py-24 bg-white border-y border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
              <span className="text-xs font-bold uppercase tracking-widest text-indigo-600">
                End-to-End Pipeline
              </span>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
                How InsightForge AI discovers real product demand
              </h2>
              <p className="text-base text-slate-600">
                A rigorous AI pipeline from raw community discussions to quantified product roadmaps.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {[
                {
                  step: "01",
                  icon: <GitBranch className="w-6 h-6 text-indigo-600" />,
                  title: "Public Discussion Ingestion",
                  desc: "Connects to public GitHub repositories to ingest live issues, feature requests, and community discussions with full traceability.",
                },
                {
                  step: "02",
                  icon: <Layers className="w-6 h-6 text-violet-600" />,
                  title: "Deduplication & Embeddings",
                  desc: "Strips template noise and bot boilerplate, producing dense semantic embeddings using Sentence-Transformers.",
                },
                {
                  step: "03",
                  icon: <BrainCircuit className="w-6 h-6 text-indigo-600" />,
                  title: "Semantic Problem Clustering",
                  desc: "Identifies recurring problem clusters and feature requests through unsupervised density and agglomerative clustering algorithms.",
                },
                {
                  step: "04",
                  icon: <Compass className="w-6 h-6 text-emerald-600" />,
                  title: "Opportunity Synthesis",
                  desc: "Extracts validated pain points, generates actionable MVP requirements, and quantifies confidence scores based on real corroborating data.",
                },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="relative p-6 rounded-2xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:border-indigo-200 hover:shadow-md transition-all space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="p-3 bg-white rounded-xl shadow-2xs border border-slate-100">
                      {item.icon}
                    </div>
                    <span className="font-mono text-2xl font-black text-slate-300">
                      {item.step}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900">{item.title}</h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Interactive Example Report Section */}
        <section id="sample-report" className="py-24 bg-slate-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto space-y-4 mb-14">
              <span className="text-xs font-bold uppercase tracking-widest text-indigo-600">
                Live Sample Output
              </span>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
                Inspect a real Opportunity Report
              </h2>
              <p className="text-base text-slate-600">
                Here is an actual opportunity synthesized from community discussions in open-source database connectors:
              </p>
            </div>

            {/* Sample Card */}
            <div className="max-w-4xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-lg overflow-hidden">
              <div className="p-6 bg-slate-900 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-950 px-2.5 py-0.5 rounded border border-indigo-800">
                      TARGET: postgresql / connection-pool
                    </span>
                    <span className="text-xs font-semibold text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                      Confidence 88%
                    </span>
                  </div>
                  <h3 className="text-xl font-bold">
                    Automated Connection Pool Healing & Transient Failover Management
                  </h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">14 Supporting Issues</span>
                </div>
              </div>

              {/* Sample Tabs */}
              <div className="border-b border-slate-200 bg-slate-50 px-6 flex gap-4 text-xs font-semibold">
                <button
                  onClick={() => setActiveTab("problem")}
                  className={`py-3 border-b-2 transition-colors cursor-pointer ${
                    activeTab === "problem"
                      ? "border-indigo-600 text-indigo-600"
                      : "border-transparent text-slate-600 hover:text-slate-900"
                  }`}
                >
                  Problem & Impact
                </button>
                <button
                  onClick={() => setActiveTab("solution")}
                  className={`py-3 border-b-2 transition-colors cursor-pointer ${
                    activeTab === "solution"
                      ? "border-indigo-600 text-indigo-600"
                      : "border-transparent text-slate-600 hover:text-slate-900"
                  }`}
                >
                  Proposed Solution & MVP
                </button>
                <button
                  onClick={() => setActiveTab("evidence")}
                  className={`py-3 border-b-2 transition-colors cursor-pointer ${
                    activeTab === "evidence"
                      ? "border-indigo-600 text-indigo-600"
                      : "border-transparent text-slate-600 hover:text-slate-900"
                  }`}
                >
                  Traceable Evidence (3)
                </button>
              </div>

              <div className="p-6">
                {activeTab === "problem" && (
                  <div className="space-y-4 animate-fade-in">
                    <div>
                      <h4 className="text-xs font-bold uppercase text-slate-500 mb-1">
                        Core User Friction
                      </h4>
                      <p className="text-sm text-slate-700 leading-relaxed bg-rose-50/50 p-4 rounded-xl border border-rose-100">
                        Developers building distributed Python microservices face recurring socket dropouts during AWS RDS multi-AZ failovers. Existing clients throw unhandled disconnect errors and exhaust thread pools, requiring manual cluster restarts.
                      </p>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold uppercase text-slate-500 mb-1">
                        Business Opportunity
                      </h4>
                      <p className="text-sm text-slate-700 leading-relaxed bg-indigo-50/50 p-4 rounded-xl border border-indigo-100">
                        Over 40% of open complaints in serverless deployments involve reconnect storm handling. Providing a zero-configuration proxy or client-side resilience wrapper eliminates production downtime and unlocks enterprise tier adoption.
                      </p>
                    </div>
                  </div>
                )}

                {activeTab === "solution" && (
                  <div className="space-y-4 animate-fade-in">
                    <div>
                      <h4 className="text-xs font-bold uppercase text-slate-500 mb-1">
                        Proposed Architecture
                      </h4>
                      <p className="text-sm text-slate-700 leading-relaxed bg-emerald-50/50 p-4 rounded-xl border border-emerald-100">
                        Build an adaptive backoff and circuit-breaking connection adapter with proactive health probing and transparent TCP socket reuse before raising unhandled runtime exceptions.
                      </p>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold uppercase text-slate-500 mb-2">
                        Suggested MVP Requirements
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                        <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                          <span>Configurable circuit breaker with jitter</span>
                        </div>
                        <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                          <span>Async background health ping on idle sockets</span>
                        </div>
                        <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                          <span>OpenTelemetry metric hooks for pool saturation</span>
                        </div>
                        <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                          <span>Automated reconnection test suite</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === "evidence" && (
                  <div className="space-y-3 animate-fade-in">
                    {[
                      {
                        num: 4812,
                        title: "Socket timeout during AWS RDS Aurora replica restart",
                        snippet: "Under load testing, failover produces 100% 500 errors because stale connections remain in the local pool.",
                        comments: 24,
                      },
                      {
                        num: 4930,
                        title: "Connection pool exhaustion under burst traffic",
                        snippet: "Pool locks up and blocks all threads when backend reconnect takes > 2 seconds.",
                        comments: 11,
                      },
                      {
                        num: 5104,
                        title: "Support transparent backoff retry on broken pipe",
                        snippet: "Need a built-in retry mechanism instead of catching OperationalError in every route.",
                        comments: 19,
                      },
                    ].map((iss, i) => (
                      <div
                        key={i}
                        className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/60 flex flex-col gap-1.5"
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-mono font-bold text-indigo-700">
                            Issue #{iss.num}: {iss.title}
                          </span>
                          <span className="text-slate-400">{iss.comments} comments</span>
                        </div>
                        <p className="text-xs text-slate-600 italic">
                          &ldquo;{iss.snippet}&rdquo;
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Trust & Methodology Section */}
        <section className="py-20 bg-white border-t border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="space-y-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">
                  Read-Only Public API Connectors
                </h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  InsightForge AI strictly accesses publicly available GitHub issues and metadata. We never require write access or scrape private code.
                </p>
              </div>

              <div className="space-y-3">
                <div className="w-10 h-10 rounded-xl bg-violet-50 border border-violet-200 flex items-center justify-center text-violet-600">
                  <BarChart3 className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">
                  Transparent Confidence Scores
                </h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Confidence scores reflect real corroborating issue density, discussion comment engagement, and semantic similarity. Every score includes its math explanation.
                </p>
              </div>

              <div className="space-y-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600">
                  <Database className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">
                  Deterministic Heuristic Fallback
                </h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  When third-party LLMs are unavailable, our deterministic NLP pipeline extracts pain points and clusters without inventing fake data or hallucinating evidence.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-20 bg-gradient-to-tr from-slate-900 via-indigo-950 to-slate-900 text-white">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight">
              Start finding high-value product opportunities today.
            </h2>
            <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto">
              Analyze any public repository in minutes. Uncover what developers and users are struggling with right now.
            </p>
            <div className="pt-2">
              <Link
                href="/register"
                className="inline-flex items-center gap-2 px-8 py-4 rounded-xl text-base font-bold text-slate-950 bg-white hover:bg-slate-100 shadow-lg hover:scale-105 transition-all"
              >
                Create Free Account
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-950 text-slate-400 py-12 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg overflow-hidden bg-white p-0.5 flex items-center justify-center">
              <Image src="/logo.png" alt="InsightForge AI" width={24} height={24} className="object-contain" />
            </div>
            <span className="text-slate-200 font-bold">InsightForge AI</span>
            <span className="text-slate-600">|</span>
            <span className="text-xs">Product Opportunity Intelligence</span>
          </div>

          <p className="text-xs text-slate-500">
            &copy; 2026 InsightForge AI. Built for product engineers and founders.
          </p>
        </div>
      </footer>
    </div>
  );
}
