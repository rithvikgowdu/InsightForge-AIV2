"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { AnalysisRun } from "@/lib/types";
import { formatRelativeTime } from "@/lib/utils";
import { StatusBadge } from "@/components/status-badge";
import {
  PlusCircle,
  TrendingUp,
  Layers,
  GitBranch,
  ArrowRight,
  RefreshCw,
  AlertCircle,
  FileSearch,
} from "lucide-react";

export default function DashboardPage() {
  const [analyses, setAnalyses] = useState<AnalysisRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalyses = useCallback(async (isBackground = false) => {
    if (isBackground) setRefreshing(true);
    setError(null);

    try {
      const data = await api.analysis.list(0, 20);
      setAnalyses(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load your analysis history.");
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalyses(false);

    // Auto-refresh active analyses every 5 seconds
    const interval = setInterval(() => {
      setAnalyses((prev) => {
        const hasActive = prev.some((a) => a.status === "QUEUED" || a.status === "RUNNING");
        if (hasActive) {
          fetchAnalyses(true);
        }
        return prev;
      });
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchAnalyses]);

  // Calculate high-level summary metrics
  const totalAnalyses = analyses.length;
  const totalOpportunities = analyses.reduce((sum, a) => sum + (a.total_opportunities || 0), 0);
  const totalIssues = analyses.reduce((sum, a) => sum + (a.total_issues_collected || 0), 0);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Product Opportunity Dashboard
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Discover and track SaaS product opportunities across public software ecosystems.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchAnalyses(true)}
            disabled={refreshing || loading}
            className="p-2.5 text-slate-500 hover:text-slate-800 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer"
            title="Refresh Analysis List"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin text-indigo-600" : ""}`} />
          </button>
          <Link
            href="/dashboard/new"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm shadow-indigo-100 hover:shadow transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Analysis</span>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Total Repositories</span>
            <GitBranch className="w-5 h-5 text-indigo-600" />
          </div>
          <div className="text-3xl font-black text-slate-900">{totalAnalyses}</div>
          <p className="text-xs text-slate-400">Repositories analyzed in your workspace</p>
        </div>

        <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Opportunities Synthesized</span>
            <TrendingUp className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="text-3xl font-black text-slate-900">{totalOpportunities}</div>
          <p className="text-xs text-slate-400">Actionable, evidence-backed SaaS features</p>
        </div>

        <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Issues Processed</span>
            <Layers className="w-5 h-5 text-violet-600" />
          </div>
          <div className="text-3xl font-black text-slate-900">{totalIssues}</div>
          <p className="text-xs text-slate-400">Community problems semantically embedded</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Recent Analyses List */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900">Recent Analyses</h2>
          <Link
            href="/dashboard/history"
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 hover:underline"
          >
            View Full History <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="p-12 text-center text-sm text-slate-400 animate-pulse">
            Loading analysis runs...
          </div>
        ) : analyses.length === 0 ? (
          /* Empty State */
          <div className="p-12 text-center max-w-md mx-auto space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center mx-auto">
              <FileSearch className="w-7 h-7" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">
              No analyses yet
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Connect to any public GitHub repository to extract discussions, cluster recurring complaints, and discover structured product opportunities.
            </p>
            <div className="pt-2">
              <Link
                href="/dashboard/new"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition-all"
              >
                <PlusCircle className="w-4 h-4" />
                <span>Start Your First Analysis</span>
              </Link>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {analyses.slice(0, 10).map((run) => (
              <Link
                key={run.id}
                href={`/dashboard/analysis/${run.id}`}
                className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/80 transition-colors group"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <span className="font-bold text-base text-slate-900 group-hover:text-indigo-600 transition-colors">
                      {run.repo_owner}/{run.repo_name}
                    </span>
                    <StatusBadge status={run.status} size="sm" />
                    {run.is_fallback && (
                      <span className="text-[10px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                        Fallback
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 flex items-center gap-2">
                    <span>{run.current_step}</span>
                    <span>•</span>
                    <span>{formatRelativeTime(run.created_at)}</span>
                  </p>
                </div>

                <div className="flex items-center gap-6 text-xs text-slate-600">
                  {run.status === "RUNNING" || run.status === "QUEUED" ? (
                    <div className="w-32 space-y-1">
                      <div className="flex justify-between text-[11px] font-medium text-slate-500">
                        <span>Progress</span>
                        <span>{run.progress_pct}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-600 rounded-full transition-all duration-300"
                          style={{ width: `${run.progress_pct}%` }}
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-4 text-right">
                      <div>
                        <span className="font-bold text-slate-900 text-sm">
                          {run.total_opportunities}
                        </span>
                        <span className="text-[11px] text-slate-400 block">Opportunities</span>
                      </div>
                      <div>
                        <span className="font-bold text-slate-900 text-sm">
                          {run.total_clusters}
                        </span>
                        <span className="text-[11px] text-slate-400 block">Clusters</span>
                      </div>
                      <div>
                        <span className="font-bold text-slate-900 text-sm">
                          {run.total_issues_collected}
                        </span>
                        <span className="text-[11px] text-slate-400 block">Issues</span>
                      </div>
                    </div>
                  )}

                  <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
