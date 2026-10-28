"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { AnalysisRun } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/status-badge";
import {
  History,
  GitBranch,
  Trash2,
  Search,
  PlusCircle,
  Loader2,
  AlertCircle,
} from "lucide-react";

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<AnalysisRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    setError(null);
    try {
      const data = await api.analysis.list(0, 100);
      setAnalyses(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load analysis history.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();

    if (!confirm("Are you sure you want to delete this analysis run? This action cannot be undone.")) {
      return;
    }

    setDeletingId(id);
    try {
      await api.analysis.delete(id);
      setAnalyses((prev) => prev.filter((a) => a.id !== id));
    } catch {
      alert("Failed to delete analysis.");
    } finally {
      setDeletingId(null);
    }
  };

  const filtered = analyses.filter((a) => {
    if (!filter) return true;
    const q = filter.toLowerCase();
    return (
      a.repo_owner.toLowerCase().includes(q) ||
      a.repo_name.toLowerCase().includes(q) ||
      a.status.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Analysis History
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Review past repository analyses, cluster distributions, and generated roadmaps.
          </p>
        </div>

        <Link
          href="/dashboard/new"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition-all"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Analysis</span>
        </Link>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Filter and Table Container */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden space-y-4">
        {/* Search Input */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Search by repo or status..."
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-300 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>
          <span className="text-xs text-slate-400 font-medium">
            {filtered.length} {filtered.length === 1 ? "record" : "records"}
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-sm text-slate-400 animate-pulse">
            Loading analysis history...
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center max-w-md mx-auto space-y-3">
            <History className="w-8 h-8 text-slate-400 mx-auto" />
            <h3 className="text-base font-bold text-slate-800">
              {filter ? "No matching analyses found" : "No analysis history"}
            </h3>
            <p className="text-xs text-slate-500">
              {filter
                ? "Try searching for a different repository name or status."
                : "Submit a public repository to run your first product intelligence scan."}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/70 text-slate-500 font-bold uppercase tracking-wider">
                  <th className="py-3.5 px-6">Repository</th>
                  <th className="py-3.5 px-6">Status</th>
                  <th className="py-3.5 px-6">Opportunities</th>
                  <th className="py-3.5 px-6">Clusters</th>
                  <th className="py-3.5 px-6">Issues Analyzed</th>
                  <th className="py-3.5 px-6">Created</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-slate-50/70 transition-colors group cursor-pointer"
                  >
                    <td className="py-4 px-6 font-bold text-slate-900">
                      <Link
                        href={`/dashboard/analysis/${item.id}`}
                        className="group-hover:text-indigo-600 transition-colors flex items-center gap-2"
                      >
                        <GitBranch className="w-4 h-4 text-slate-400" />
                        <span>
                          {item.repo_owner}/{item.repo_name}
                        </span>
                      </Link>
                    </td>

                    <td className="py-4 px-6">
                      <StatusBadge status={item.status} size="sm" />
                    </td>

                    <td className="py-4 px-6 font-semibold text-slate-800">
                      {item.total_opportunities}
                    </td>

                    <td className="py-4 px-6 text-slate-600 font-medium">
                      {item.total_clusters}
                    </td>

                    <td className="py-4 px-6 text-slate-600 font-medium">
                      {item.total_issues_collected}
                    </td>

                    <td className="py-4 px-6 text-slate-500">
                      {formatDate(item.created_at)}
                    </td>

                    <td className="py-4 px-6 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/dashboard/analysis/${item.id}`}
                          className="px-2.5 py-1 rounded-lg text-indigo-600 bg-indigo-50 hover:bg-indigo-100 font-semibold transition-colors"
                        >
                          View
                        </Link>
                        <button
                          onClick={(e) => handleDelete(e, item.id)}
                          disabled={deletingId === item.id}
                          className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
                          title="Delete Analysis"
                        >
                          {deletingId === item.id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin text-rose-600" />
                          ) : (
                            <Trash2 className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
