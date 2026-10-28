"use client";

import React from "react";
import { SupportingEvidence } from "@/lib/types";
import { X, ExternalLink, MessageSquare, Quote } from "lucide-react";

interface EvidenceModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  evidence: SupportingEvidence[];
}

export function EvidenceModal({
  isOpen,
  onClose,
  title,
  evidence,
}: EvidenceModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-2">
            <Quote className="w-5 h-5 text-indigo-600" />
            <h3 className="text-base font-semibold text-slate-900 truncate">
              Supporting Evidence for &ldquo;{title}&rdquo;
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-200/50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Evidence List */}
        <div className="p-6 max-h-[70vh] overflow-y-auto space-y-4">
          <p className="text-xs text-slate-500 font-medium">
            Showing {evidence.length} verified GitHub discussion sources that corroborates this product opportunity:
          </p>

          {evidence.length === 0 ? (
            <p className="text-sm text-slate-500 py-4 text-center">
              No direct snippet quotes available for this item.
            </p>
          ) : (
            evidence.map((item, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:border-indigo-200 transition-all space-y-2.5"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    {item.issue_number && (
                      <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded">
                        #{item.issue_number}
                      </span>
                    )}
                    <h4 className="text-sm font-semibold text-slate-900 leading-snug">
                      {item.title}
                    </h4>
                  </div>
                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1 hover:underline"
                    >
                      View on GitHub <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </div>

                {item.snippet && (
                  <p className="text-xs text-slate-600 italic bg-white p-3 rounded-lg border border-slate-100">
                    &ldquo;{item.snippet}&rdquo;
                  </p>
                )}

                {item.comments_count !== undefined && item.comments_count > 0 && (
                  <div className="flex items-center gap-1.5 text-[11px] text-slate-500 font-medium">
                    <MessageSquare className="w-3.5 h-3.5 text-slate-400" />
                    <span>{item.comments_count} community discussion comments</span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors shadow-2xs"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

