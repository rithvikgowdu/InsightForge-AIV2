"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { AnalysisDetail, AnalysisStatusResponse } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/status-badge";
import { OpportunityCard } from "@/components/opportunity-card";
import {
  GitBranch,
  ExternalLink,
  ArrowLeft,
  Loader2,
  AlertTriangle,
  Layers,
  TrendingUp,
  MessageSquare,
  Search,
  ShieldAlert,
} from "lucide-react";

export default function AnalysisDetailPage() {
  const params = useParams();
  const id = params?.id as string;

  const [detail, setDetail] = useState<AnalysisDetail | null>(null);
  const [statusInfo, setStatusInfo] = useState<AnalysisStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"opportunities" | "clusters" | "evidence">("opportunities");
  const [evidenceFilter, setEvidenceFilter] = useState("");

  const fetchDetail = useCallback(async () => {
    try {
      const data = await api.analysis.get(id);
      setDetail(data);
      setStatusInfo(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load analysis results.");
      }
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (!id) return;
    fetchDetail();
  }, [id, fetchDetail]);

  const isFinished = Boolean(detail && detail.status !== "QUEUED" && detail.status !== "RUNNING");

  // Polling while active
  useEffect(() => {
    if (!id || isFinished) return;

    const interval = setInterval(async () => {
      try {
        const stat = await api.analysis.getStatus(id);
        setStatusInfo(stat);

        // If it just transitioned to completed or failed, fetch full details
        if (stat.status === "COMPLETED" || stat.status === "FAILED") {
          fetchDetail();
          clearInterval(interval);
        }
      } catch {
        // Ignore transient poll error
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [id, isFinished, fetchDetail]);

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
        <p className="text-sm font-medium text-slate-500">Retrieving analysis report...</p>
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="max-w-2xl mx-auto py-12 space-y-6">
        <div className="p-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 space-y-3">
          <div className="flex items-center gap-2 font-bold text-base">
            <AlertTriangle className="w-5 h-5 text-rose-600" />
            <span>Analysis Not Accessible</span>
          </div>
          <p className="text-sm text-rose-700 leading-relaxed">
            {error || "We could not find or access this analysis report."}
          </p>
        </div>
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 text-sm font-semibold text-indigo-600 hover:text-indigo-800"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>
      </div>
    );
  }

  const currentStatus = statusInfo?.status || detail.status;
  const currentStep = statusInfo?.current_step || detail.current_step;
  const progressPct = statusInfo?.progress_pct ?? detail.progress_pct;
  const isRunning = currentStatus === "QUEUED" || currentStatus === "RUNNING";

  // Filter sample issues
  const filteredIssues = (detail.sample_issues || []).filter((iss) => {
    if (!evidenceFilter) return true;
    const q = evidenceFilter.toLowerCase();
    return (
      iss.title.toLowerCase().includes(q) ||
      (iss.body && iss.body.toLowerCase().includes(q)) ||
      (iss.author && iss.author.toLowerCase().includes(q)) ||
      (iss.labels && iss.labels.some((l) => l.toLowerCase().includes(q)))
    );
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>

        <div className="flex items-center gap-3">
          <a
            href={detail.repo_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <GitBranch className="w-3.5 h-3.5" />
            <span>View GitHub Repository</span>
            <ExternalLink className="w-3 h-3 text-slate-400" />
          </a>
        </div>
      </div>

      {/* Main Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
                {detail.repo_owner}/{detail.repo_name}
              </h1>
              <StatusBadge status={currentStatus} />
              {detail.is_fallback && (
                <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-800 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full">
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
                  Deterministic Heuristic Pipeline
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400">
              Submitted on {formatDate(detail.created_at)}
              {detail.completed_at && ` • Completed on ${formatDate(detail.completed_at)}`}
            </p>
          </div>

          {/* Quick Metrics */}
          {!isRunning && currentStatus === "COMPLETED" && (
            <div className="flex items-center gap-4 text-center sm:text-right">
              <div className="px-3 py-2 bg-slate-50 rounded-xl border border-slate-100">
                <span className="block text-xl font-black text-slate-900">
                  {detail.total_opportunities}
                </span>
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                  Opportunities
                </span>
              </div>
              <div className="px-3 py-2 bg-slate-50 rounded-xl border border-slate-100">
                <span className="block text-xl font-black text-slate-900">
                  {detail.total_clusters}
                </span>
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                  Clusters
                </span>
              </div>
              <div className="px-3 py-2 bg-slate-50 rounded-xl border border-slate-100">
                <span className="block text-xl font-black text-slate-900">
                  {detail.total_issues_collected}
                </span>
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                  Issues
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Live Progress Bar if Running */}
        {isRunning && (
          <div className="p-6 rounded-2xl bg-indigo-50/60 border border-indigo-100 space-y-3">
            <div className="flex items-center justify-between text-xs font-bold text-indigo-900">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                <span>{currentStep}</span>
              </div>
              <span>{progressPct}%</span>
            </div>
            <div className="w-full h-2.5 bg-indigo-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-600 to-violet-500 rounded-full transition-all duration-500"
                style={{ width: `${Math.max(5, progressPct)}%` }}
              />
            </div>
            <p className="text-[11px] text-indigo-700/80">
              Analysis pipeline is actively polling GitHub, computing semantic embeddings, and clustering problem themes in background.
            </p>
          </div>
        )}

        {/* Failure Banner */}
        {currentStatus === "FAILED" && (
          <div className="p-5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 space-y-2">
            <div className="flex items-center gap-2 font-bold text-sm text-rose-900">
              <AlertTriangle className="w-4 h-4 text-rose-600" />
              <span>Analysis Failed</span>
            </div>
            <p className="text-xs text-rose-700 leading-relaxed">
              {detail.error_message || "An error occurred while executing the analysis pipeline."}
            </p>
            <div className="pt-2">
              <Link
                href="/dashboard/new"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-800 bg-white border border-rose-200 px-3 py-1.5 rounded-lg hover:bg-rose-50"
              >
                <span>Try Another Repository</span>
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Results View (Completed) */}
      {!isRunning && currentStatus === "COMPLETED" && (
        <div className="space-y-6">
          {/* Tabs */}
          <div className="border-b border-slate-200 flex gap-6 text-sm font-semibold">
            <button
              onClick={() => setActiveTab("opportunities")}
              className={`pb-3 border-b-2 flex items-center gap-2 cursor-pointer transition-colors ${
                activeTab === "opportunities"
                  ? "border-indigo-600 text-indigo-600"
                  : "border-transparent text-slate-500 hover:text-slate-900"
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              <span>Product Opportunities ({detail.opportunities?.length || 0})</span>
            </button>

            <button
              onClick={() => setActiveTab("clusters")}
              className={`pb-3 border-b-2 flex items-center gap-2 cursor-pointer transition-colors ${
                activeTab === "clusters"
                  ? "border-indigo-600 text-indigo-600"
                  : "border-transparent text-slate-500 hover:text-slate-900"
              }`}
            >
              <Layers className="w-4 h-4" />
              <span>Problem Clusters ({detail.clusters?.length || 0})</span>
            </button>

            <button
              onClick={() => setActiveTab("evidence")}
              className={`pb-3 border-b-2 flex items-center gap-2 cursor-pointer transition-colors ${
                activeTab === "evidence"
                  ? "border-indigo-600 text-indigo-600"
                  : "border-transparent text-slate-500 hover:text-slate-900"
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>Source Evidence ({detail.sample_issues?.length || 0})</span>
            </button>
          </div>

          {/* Tab 1: Product Opportunities */}
          {activeTab === "opportunities" && (
            <div className="space-y-6">
              {detail.opportunities && detail.opportunities.length > 0 ? (
                detail.opportunities.map((opp, idx) => (
                  <OpportunityCard key={opp.id} opportunity={opp} index={idx} />
                ))
              ) : (
                <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
                  <p className="text-sm text-slate-500">
                    No clear product opportunities could be synthesized from this repository&apos;s issues.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Problem Clusters */}
          {activeTab === "clusters" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {detail.clusters && detail.clusters.length > 0 ? (
                detail.clusters.map((cluster, cIdx) => (
                  <div
                    key={cluster.id}
                    className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs space-y-4 flex flex-col justify-between"
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 border border-indigo-100 px-2.5 py-0.5 rounded-full">
                          Cluster #{cIdx + 1}
                        </span>
                        <span className="text-xs font-semibold text-slate-500">
                          {cluster.size} Discussions
                        </span>
                      </div>
                      <h3 className="text-base font-bold text-slate-900 leading-snug">
                        {cluster.title}
                      </h3>
                      <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                        {cluster.summary}
                      </p>
                    </div>

                    {cluster.recurring_themes && cluster.recurring_themes.length > 0 && (
                      <div className="space-y-1.5 pt-2 border-t border-slate-100">
                        <span className="text-[10px] font-bold uppercase text-slate-400">
                          Recurring Themes:
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {cluster.recurring_themes.map((theme, tIdx) => (
                            <span
                              key={tIdx}
                              className="text-[11px] font-medium text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-md"
                            >
                              {theme}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="col-span-2 p-12 text-center bg-white rounded-2xl border border-slate-200">
                  <p className="text-sm text-slate-500">No clusters formed.</p>
                </div>
              )}
            </div>
          )}

          {/* Tab 3: Source Evidence */}
          {activeTab === "evidence" && (
            <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden space-y-4 p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="relative flex-1 max-w-md">
                  <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="text"
                    value={evidenceFilter}
                    onChange={(e) => setEvidenceFilter(e.target.value)}
                    placeholder="Search collected issues by keyword, author, or label..."
                    className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-300 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
                  />
                </div>
                <span className="text-xs text-slate-500">
                  Showing {filteredIssues.length} of {detail.sample_issues?.length || 0} issues
                </span>
              </div>

              <div className="divide-y divide-slate-100">
                {filteredIssues.map((iss) => (
                  <div key={iss.id} className="py-4 space-y-2">
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded">
                            #{iss.issue_number}
                          </span>
                          <span className="text-sm font-semibold text-slate-900">
                            {iss.title}
                          </span>
                        </div>
                        {iss.clean_text && (
                          <p className="text-xs text-slate-600 line-clamp-2">
                            {iss.clean_text}
                          </p>
                        )}
                      </div>

                      <a
                        href={iss.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="shrink-0 text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1 hover:underline"
                      >
                        GitHub <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>

                    <div className="flex items-center gap-4 text-[11px] text-slate-400">
                      {iss.author && <span>By @{iss.author}</span>}
                      <span>{iss.comments_count} comments</span>
                      {iss.labels && iss.labels.length > 0 && (
                        <div className="flex items-center gap-1 flex-wrap">
                          {iss.labels.map((l, idx) => (
                            <span
                              key={idx}
                              className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded text-[10px]"
                            >
                              {l}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
