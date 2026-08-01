"use client";

import React from "react";
import { Hospital } from "@/types";
import { Building2, Shield, AlertTriangle, CheckCircle2, XCircle } from "lucide-react";

interface HospitalCardProps {
  hospital: Hospital;
}

export const HospitalCard: React.FC<HospitalCardProps> = ({ hospital }) => {
  const isExcluded = hospital.trust_score < 40;
  const isSuspicious = hospital.trust_score >= 40 && hospital.trust_score < 70;

  const statusColor = isExcluded
    ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
    : isSuspicious
    ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
    : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";

  return (
    <div
      className={`relative p-5 rounded-2xl border bg-slate-900/60 backdrop-blur-md transition-all hover:border-slate-700 ${
        isExcluded
          ? "border-rose-900/40 bg-rose-950/10"
          : hospital.attack_active
          ? "border-amber-500/40 animate-pulse"
          : "border-slate-800"
      }`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-blue-400">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">{hospital.name}</h3>
            <p className="text-xs text-slate-400">ID: {hospital.id} • {hospital.sample_count} samples</p>
          </div>
        </div>

        <span className={`px-2.5 py-1 text-xs rounded-full border font-medium flex items-center gap-1 ${statusColor}`}>
          {isExcluded ? (
            <>
              <XCircle className="w-3.5 h-3.5" /> Excluded
            </>
          ) : isSuspicious ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5" /> Suspicious
            </>
          ) : (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" /> Verified
            </>
          )}
        </span>
      </div>

      {hospital.attack_active && (
        <div className="mb-3 px-3 py-1.5 rounded-lg bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs flex items-center justify-between">
          <span className="font-semibold">⚠️ Active Attack Injecting:</span>
          <span>{hospital.active_attack}</span>
        </div>
      )}

      <div className="mt-4 space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-400">Trust Score</span>
          <span
            className={`font-bold ${
              hospital.trust_score < 40
                ? "text-rose-400"
                : hospital.trust_score < 70
                ? "text-amber-400"
                : "text-emerald-400"
            }`}
          >
            {hospital.trust_score.toFixed(1)} / 100
          </span>
        </div>
        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              hospital.trust_score < 40
                ? "bg-rose-500"
                : hospital.trust_score < 70
                ? "bg-amber-500"
                : "bg-emerald-500"
            }`}
            style={{ width: `${Math.max(5, hospital.trust_score)}%` }}
          />
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-xs">
        <div>
          <span className="text-slate-500 block">Train Acc.</span>
          <span className="text-slate-200 font-semibold">
            {hospital.train_accuracy != null ? `${(hospital.train_accuracy * 100).toFixed(1)}%` : "—"}
          </span>
        </div>
        <div>
          <span className="text-slate-500 block">Val Acc.</span>
          <span className="text-slate-200 font-semibold">
            {hospital.val_accuracy != null ? `${(hospital.val_accuracy * 100).toFixed(1)}%` : "—"}
          </span>
        </div>
        <div>
          <span className="text-slate-500 block">Privacy Shield</span>
          <span className="text-emerald-400 font-semibold flex items-center gap-1">
            <Shield className="w-3 h-3" /> Active
          </span>
        </div>
        <div>
          <span className="text-slate-500 block">Fit Status</span>
          <span
            className={`font-semibold ${
              hospital.fit_status === "Overfit"
                ? "text-amber-400"
                : hospital.fit_status === "Underfit"
                ? "text-orange-400"
                : hospital.fit_status === "Compromised"
                ? "text-rose-400"
                : hospital.fit_status === "Well-fit"
                ? "text-emerald-400"
                : "text-slate-500"
            }`}
          >
            {hospital.fit_status ?? "Not Trained Yet"}
            {hospital.generalization_gap != null && hospital.fit_status && hospital.fit_status !== "Not Trained Yet"
              ? ` (Δ${(hospital.generalization_gap * 100).toFixed(1)}%)`
              : ""}
          </span>
        </div>
      </div>
    </div>
  );
};
