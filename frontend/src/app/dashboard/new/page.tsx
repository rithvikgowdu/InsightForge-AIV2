"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import {
  GitBranch,
  ArrowRight,
  AlertCircle,
  Loader2,
  Info,
} from "lucide-react";

export default function NewAnalysisPage() {
  const router = useRouter();
  const [repoInput, setRepoInput] = useState("");
  const [issueLimit, setIssueLimit] = useState(50);
  const [includeClosed, setIncludeClosed] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const presets = [
    { label: "fastapi/fastapi", desc: "Modern Python Web Framework" },
    { label: "astral-sh/uv", desc: "Fast Python Package Manager" },
    { label: "psf/requests", desc: "HTTP for Humans" },
    { label: "pallets/flask", desc: "Lightweight WSGI Web Framework" },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const input = repoInput.trim();
    if (!input) {
      setError("Please enter a GitHub repository owner and name (e.g., owner/repo).");
      return;
    }

    setLoading(true);
    try {
      const run = await api.analysis.create({
        repo_url: input,
        issue_limit: issueLimit,
        include_closed: includeClosed,
      });
      // Redirect to the analysis progress and details page
      router.push(`/dashboard/analysis/${run.id}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to start analysis. Please verify the repository name.");
      }
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Start New Repository Analysis
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Connect to any public GitHub repository to extract discussions and uncover unserved product demand.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Form Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-8 space-y-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Repo Input */}
          <div className="space-y-2">
            <label
              htmlFor="repo"
              className="block text-xs font-semibold text-slate-700 uppercase tracking-wider"
            >
              GitHub Repository <span className="text-rose-500">*</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <GitBranch className="w-4 h-4" />
              </div>
              <input
                id="repo"
                type="text"
                required
                value={repoInput}
                onChange={(e) => setRepoInput(e.target.value)}
                placeholder="owner/repository or https://github.com/owner/repository"
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-300 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition-colors"
              />
            </div>
            <p className="text-[11px] text-slate-400">
              Format: <code className="text-indigo-600 font-mono">owner/repo</code> or full GitHub repository URL.
            </p>
          </div>

          {/* Quick Presets */}
          <div className="space-y-2">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
              Quick Presets to Explore:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {presets.map((preset) => (
                <button
                  type="button"
                  key={preset.label}
                  onClick={() => setRepoInput(preset.label)}
                  className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                    repoInput === preset.label
                      ? "border-indigo-600 bg-indigo-50/50 text-indigo-900"
                      : "border-slate-200 hover:border-indigo-200 hover:bg-slate-50 text-slate-700"
                  }`}
                >
                  <div className="font-mono text-xs font-bold">{preset.label}</div>
                  <div className="text-[11px] text-slate-500">{preset.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="h-px bg-slate-100" />

          {/* Issue Limit */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Issue Analysis Depth
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 25, label: "25 Issues", sub: "Fast triage" },
                { value: 50, label: "50 Issues", sub: "Recommended" },
                { value: 100, label: "100 Issues", sub: "Deep discovery" },
              ].map((opt) => (
                <button
                  type="button"
                  key={opt.value}
                  onClick={() => setIssueLimit(opt.value)}
                  className={`p-3 rounded-xl border text-center transition-all cursor-pointer ${
                    issueLimit === opt.value
                      ? "border-indigo-600 bg-indigo-50/50 text-indigo-900 ring-1 ring-indigo-600"
                      : "border-slate-200 hover:border-slate-300 text-slate-700"
                  }`}
                >
                  <div className="text-xs font-bold">{opt.label}</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">{opt.sub}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Include Closed Checkbox */}
          <div className="flex items-center gap-2 pt-1">
            <input
              id="closed"
              type="checkbox"
              checked={includeClosed}
              onChange={(e) => setIncludeClosed(e.target.checked)}
              className="w-4 h-4 rounded text-indigo-600 border-slate-300 focus:ring-indigo-500"
            />
            <label htmlFor="closed" className="text-xs text-slate-700 font-medium cursor-pointer">
              Include closed issues (recommended to discover resolved pain points and feature nuances)
            </label>
          </div>

          {/* Information Notice */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 text-xs text-slate-600 flex items-start gap-2.5">
            <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-semibold text-slate-800">What happens next:</p>
              <p className="text-slate-500 leading-relaxed">
                InsightForge AI collects public issue discussions, cleans out template boilerplate, computes semantic embeddings, clusters related themes with density clustering, and synthesizes structured SaaS product opportunities.
              </p>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-6 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 shadow-md shadow-indigo-100 disabled:opacity-60 transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Initializing Pipeline...</span>
              </>
            ) : (
              <>
                <span>Launch Analysis Pipeline</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
