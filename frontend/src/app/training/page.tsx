"use client";

import React, { useEffect, useState } from "react";
import {
  Play,
  Pause,
  RotateCcw,
  Square,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";
import { DashboardSummary } from "@/types";
import {
  fetchDashboardMetrics,
  startFederatedRound,
  stopFederatedRound,
  pauseFederatedRound,
  resumeFederatedRound,
  resetFederatedTraining,
  toggleDifferentialPrivacy,
  fetchSystemLogs,
} from "@/services/api";

const PIPELINE = [
  "Privacy Shield",
  "OCR / PII Detect",
  "Anonymization",
  "Classification",
  "CNN · ANN · Transformer",
  "Feature Fusion",
  "Local Training",
  "TrustFed Aggregation",
  "Global Model",
];

export default function TrainingControlPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    try {
      const [summary, logRes] = await Promise.all([fetchDashboardMetrics(), fetchSystemLogs()]);
      setData(summary);
      setLogs(logRes.logs || []);
    } catch (err: any) {
      console.error("Failed to refresh training status:", err);
      setError(err.message || "Failed to connect to backend server.");
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const run = async (fn: () => Promise<any>) => {
    setBusy(true);
    setError(null);
    try {
      await fn();
      await refresh();
    } catch (err: any) {
      console.error("Failed to execute training round action:", err);
      setError(err.message || "An error occurred while executing the training operation.");
    } finally {
      setBusy(false);
    }
  };

  if (!data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-slate-400 text-sm space-y-4">
        {error ? (
          <div className="max-w-md p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-center space-y-3">
            <AlertTriangle className="w-8 h-8 mx-auto text-rose-400" />
            <p className="font-semibold text-rose-200">Unable to load Training Controls</p>
            <p className="text-xs text-rose-300/80">{error}</p>
            <button
              onClick={refresh}
              className="px-4 py-2 text-xs font-semibold rounded-xl bg-rose-600 hover:bg-rose-500 text-white"
            >
              Retry Connection
            </button>
          </div>
        ) : (
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span>Loading Training Control System...</span>
          </div>
        )}
      </div>
    );
  }

  const status = data.is_training_active ? "Training" : data.is_paused ? "Paused" : "Idle";

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 pb-12">
      <main className="max-w-6xl mx-auto px-6 pt-8 space-y-6">
        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-rose-400 hover:text-rose-200 font-bold">
              Dismiss
            </button>
          </div>
        )}

        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Orchestration</p>
            <h1 className="text-xl font-bold text-white">Training Control</h1>
          </div>
          <span className="text-xs text-slate-400">
            <span className="text-slate-200 font-semibold">{status}</span> · Round {data.current_round}/{data.total_rounds}
          </span>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 flex flex-wrap gap-3">
          <button
            disabled={busy}
            onClick={() => run(startFederatedRound)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
          >
            <Play className="w-3.5 h-3.5" /> Start Round
          </button>
          <button
            disabled={busy}
            onClick={() => run(pauseFederatedRound)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
          >
            <Pause className="w-3.5 h-3.5" /> Pause
          </button>
          <button
            disabled={busy}
            onClick={() => run(resumeFederatedRound)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
          >
            <Play className="w-3.5 h-3.5" /> Resume
          </button>
          <button
            disabled={busy}
            onClick={() => run(stopFederatedRound)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 border border-rose-600/40 text-rose-300 text-xs font-semibold"
          >
            <Square className="w-3.5 h-3.5" /> Stop
          </button>
          <button
            disabled={busy}
            onClick={() => run(resetFederatedTraining)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 ml-auto"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset
          </button>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 flex items-center justify-between">
          <div className="flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-blue-400 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-white flex items-center gap-2">
                Differential Privacy
                <span className={`text-[10px] px-2 py-0.5 rounded-full border ${data.dp_enabled ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" : "bg-slate-800 text-slate-400 border-slate-700"}`}>
                  {data.dp_enabled ? "ON" : "OFF"}
                </span>
              </p>
              <p className="text-xs text-slate-500 max-w-xl mt-1">
                Gaussian mechanism: per-client L2 clip C=3, noise σ=0.15. Calibrated noise is added to the
                aggregated update each round so no single hospital's contribution can be reverse-engineered.
              </p>
            </div>
          </div>
          <button
            disabled={busy}
            onClick={() => run(() => toggleDifferentialPrivacy(!data.dp_enabled))}
            className={`w-12 h-6 rounded-full relative transition-colors ${data.dp_enabled ? "bg-emerald-500" : "bg-slate-700"}`}
          >
            <span className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-all ${data.dp_enabled ? "left-6" : "left-0.5"}`} />
          </button>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-4">Privacy-Preserving Training Pipeline</p>
          <div className="flex flex-wrap items-center gap-2">
            {PIPELINE.map((step, i) => (
              <React.Fragment key={step}>
                <span className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200">
                  {step}
                </span>
                {i < PIPELINE.length - 1 && <span className="text-slate-600">→</span>}
              </React.Fragment>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-3">Recent Training Events</p>
          <div className="space-y-1.5 max-h-72 overflow-y-auto font-mono text-[11px]">
            {logs.map((line, i) => (
              <p key={i} className="text-slate-400">{line}</p>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
