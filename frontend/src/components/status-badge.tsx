import React from "react";
import { AnalysisStatus } from "@/lib/types";
import { cn } from "@/lib/utils";
import { CheckCircle2, Clock, AlertTriangle, Loader2 } from "lucide-react";

interface StatusBadgeProps {
  status: AnalysisStatus;
  className?: string;
  size?: "sm" | "md";
}

export function StatusBadge({ status, className, size = "md" }: StatusBadgeProps) {
  const configs: Record<
    AnalysisStatus,
    { label: string; icon: React.ReactNode; bg: string; text: string; border: string }
  > = {
    QUEUED: {
      label: "Queued",
      icon: <Clock className="w-3.5 h-3.5 animate-pulse" />,
      bg: "bg-slate-100",
      text: "text-slate-700",
      border: "border-slate-200",
    },
    RUNNING: {
      label: "Processing",
      icon: <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-600" />,
      bg: "bg-indigo-50",
      text: "text-indigo-700",
      border: "border-indigo-200",
    },
    COMPLETED: {
      label: "Completed",
      icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />,
      bg: "bg-emerald-50",
      text: "text-emerald-700",
      border: "border-emerald-200",
    },
    FAILED: {
      label: "Failed",
      icon: <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />,
      bg: "bg-rose-50",
      text: "text-rose-700",
      border: "border-rose-200",
    },
  };

  const config = configs[status] || configs.QUEUED;
  const isSm = size === "sm";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 font-medium rounded-full border transition-colors",
        config.bg,
        config.text,
        config.border,
        isSm ? "text-xs px-2.5 py-0.5" : "text-sm px-3 py-1",
        className
      )}
    >
      {config.icon}
      <span>{config.label}</span>
    </span>
  );
}

