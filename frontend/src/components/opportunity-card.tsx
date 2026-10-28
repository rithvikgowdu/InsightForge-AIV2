"use client";

import React, { useState } from "react";
import { ProductOpportunity } from "@/lib/types";
import { getConfidenceBadgeColor } from "@/lib/utils";
import { EvidenceModal } from "./evidence-modal";
import {
  Lightbulb,
  AlertCircle,
  TrendingUp,
  Wrench,
  Users,
  CheckCircle,
  ExternalLink,
  ShieldAlert,
  Info,
} from "lucide-react";

interface OpportunityCardProps {
  opportunity: ProductOpportunity;
  index: number;
}

export function OpportunityCard({ opportunity, index }: OpportunityCardProps) {
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const badgeStyle = getConfidenceBadgeColor(opportunity.confidence_score);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs hover:shadow-md transition-all duration-200 overflow-hidden flex flex-col">
      {/* Top Header */}
      <div className="p-6 border-b border-slate-100 bg-gradient-to-r from-slate-50/70 to-white flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div className="space-y-1.5 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 border border-indigo-100 px-2.5 py-0.5 rounded-full">
              Opportunity #{index + 1}
            </span>
            <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-full">
              {opportunity.supporting_doc_count} Verified Issues
            </span>
            {opportunity.is_fallback && (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-800 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full" title="Synthesized using verified deterministic heuristic synthesis.">
                <ShieldAlert className="w-3 h-3 text-amber-600" />
                Heuristic Fallback
              </span>
            )}
          </div>
          <h3 className="text-xl font-bold text-slate-900 leading-snug">
            {opportunity.title}
          </h3>
        </div>

        {/* Confidence Score Pill */}
        <div className="shrink-0 flex sm:flex-col items-center sm:items-end justify-between gap-1">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-semibold text-slate-500">Confidence:</span>
            <span
              className={`text-sm font-bold px-2.5 py-0.5 rounded-md border ${badgeStyle.bg} ${badgeStyle.text} ${badgeStyle.border}`}
            >
              {Math.round(opportunity.confidence_score * 100)}%
            </span>
          </div>
          <span className="text-[11px] text-slate-400 font-medium">
            Market Potential:{" "}
            <strong className="text-slate-700">{opportunity.market_potential}</strong>
          </span>
        </div>
      </div>

      {/* Main Body Grid */}
      <div className="p-6 space-y-6 flex-1">
        {/* Problem Statement */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-rose-700 font-semibold text-xs tracking-wide uppercase">
            <AlertCircle className="w-4 h-4" />
            <span>Problem Statement</span>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed bg-rose-50/40 p-3.5 rounded-xl border border-rose-100/80">
            {opportunity.problem_statement}
          </p>
        </div>

        {/* 2-Column: Business Opportunity & Proposed Solution */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-indigo-700 font-semibold text-xs tracking-wide uppercase">
              <TrendingUp className="w-4 h-4" />
              <span>Business Opportunity</span>
            </div>
            <p className="text-sm text-slate-600 leading-relaxed bg-indigo-50/30 p-3.5 rounded-xl border border-indigo-100/60 h-full">
              {opportunity.business_opportunity}
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2 text-emerald-700 font-semibold text-xs tracking-wide uppercase">
              <Wrench className="w-4 h-4" />
              <span>Proposed Solution</span>
            </div>
            <p className="text-sm text-slate-600 leading-relaxed bg-emerald-50/30 p-3.5 rounded-xl border border-emerald-100/60 h-full">
              {opportunity.proposed_solution}
            </p>
          </div>
        </div>

        {/* Target Persona */}
        <div className="flex items-center gap-2 text-xs text-slate-600 bg-slate-50 px-3.5 py-2.5 rounded-xl border border-slate-100">
          <Users className="w-4 h-4 text-slate-500 shrink-0" />
          <span>
            <strong className="text-slate-800">Target Segment:</strong>{" "}
            {opportunity.target_customer_segment}
          </span>
        </div>

        {/* Suggested MVP Features */}
        <div className="space-y-2.5">
          <div className="flex items-center gap-2 text-slate-800 font-semibold text-xs tracking-wide uppercase">
            <Lightbulb className="w-4 h-4 text-amber-500" />
            <span>Recommended MVP Capabilities</span>
          </div>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {opportunity.suggested_mvp_features.map((feat, fIdx) => (
              <li
                key={fIdx}
                className="flex items-start gap-2 text-xs text-slate-700 bg-slate-50/80 p-2.5 rounded-lg border border-slate-200/60"
              >
                <CheckCircle className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>{feat}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Confidence Explanation */}
        <div className="flex items-start gap-2 text-xs text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-100">
          <Info className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
          <p>
            <strong className="text-slate-700">Confidence Logic:</strong>{" "}
            {opportunity.confidence_explanation}
          </p>
        </div>
      </div>

      {/* Footer / Evidence Action */}
      <div className="px-6 py-4 bg-slate-50/80 border-t border-slate-100 flex items-center justify-between">
        <span className="text-xs text-slate-500">
          Backed by {opportunity.supporting_evidence?.length || 0} traceable GitHub discussions
        </span>
        <button
          onClick={() => setEvidenceOpen(true)}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800 hover:underline cursor-pointer"
        >
          View Evidence Quotes & Sources <ExternalLink className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Modal */}
      <EvidenceModal
        isOpen={evidenceOpen}
        onClose={() => setEvidenceOpen(false)}
        title={opportunity.title}
        evidence={opportunity.supporting_evidence || []}
      />
    </div>
  );
}

