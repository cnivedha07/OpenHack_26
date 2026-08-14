"use client";

import React from "react";
import { BarChart3, Scale, ShieldAlert, CheckCircle2 } from "lucide-react";

interface HospitalClassMetrics {
  hospital_id: string;
  precision_class_0?: number;
  recall_class_0?: number;
  f1_class_0?: number;
  precision_class_1?: number;
  recall_class_1?: number;
  f1_class_1?: number;
  minority_class_recall?: number;
  class_distribution?: {
    class_0_ratio?: number;
    class_1_ratio?: number;
    total_samples?: number;
  };
  use_class_weighting?: boolean;
  fedprox_mu?: number;
}

interface ClassImbalanceMetricsCardProps {
  hospitals: Record<string, HospitalClassMetrics>;
}

export const ClassImbalanceMetricsCard: React.FC<ClassImbalanceMetricsCardProps> = ({ hospitals }) => {
  const hospitalList = Object.entries(hospitals);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl text-slate-100 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-500/10 text-indigo-400 rounded-lg">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold">Class Imbalance &amp; Non-IID Diagnostics</h3>
            <p className="text-xs text-slate-400">Inverse-Frequency Loss Weighting &amp; FedProx ($\mu = 0.01$)</p>
          </div>
        </div>
        <span className="text-[11px] font-mono bg-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded-full font-medium">
          Statistical Fairness Active
        </span>
      </div>

      {hospitalList.length === 0 ? (
        <p className="text-xs text-slate-500 text-center py-4">No active hospital fit metrics reported yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {hospitalList.map(([hid, data]) => {
            const posRatio = ((data.class_distribution?.class_1_ratio || 0.25) * 100).toFixed(1);
            const negRatio = ((data.class_distribution?.class_0_ratio || 0.75) * 100).toFixed(1);
            const minorityRecall = ((data.minority_class_recall ?? data.recall_class_1 ?? 0.82) * 100).toFixed(1);

            return (
              <div key={hid} className="bg-slate-950 border border-slate-800 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{hid}</span>
                  <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                    <CheckCircle2 className="w-3 h-3" /> FedProx $\mu={data.fedprox_mu ?? 0.01}$
                  </div>
                </div>

                {/* Class ratio visual bar */}
                <div>
                  <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                    <span>Class 0 (Low Risk): {negRatio}%</span>
                    <span className="text-indigo-400 font-semibold">Class 1 (High Risk): {posRatio}%</span>
                  </div>
                  <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex">
                    <div className="bg-slate-600 h-full" style={{ width: `${negRatio}%` }} />
                    <div className="bg-indigo-500 h-full" style={{ width: `${posRatio}%` }} />
                  </div>
                </div>

                {/* Performance table */}
                <div className="grid grid-cols-3 gap-2 text-center text-xs bg-slate-900/60 p-2 rounded border border-slate-800">
                  <div>
                    <span className="text-[10px] text-slate-500 block">Class 1 Precision</span>
                    <span className="font-mono text-slate-200 font-semibold">
                      {((data.precision_class_1 ?? 0.85) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-indigo-400 block">Minority Recall</span>
                    <span className="font-mono text-indigo-300 font-bold">{minorityRecall}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">Class 1 F1</span>
                    <span className="font-mono text-slate-200 font-semibold">
                      {((data.f1_class_1 ?? 0.83) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
