"use client";

import React, { useEffect, useState } from "react";
import { DashboardSummary } from "@/types";
import { fetchDashboardMetrics } from "@/services/api";
import { createWebSocketConnection } from "@/services/websocket";
import { HospitalCard } from "@/components/HospitalCard";
import { TrustChart } from "@/components/TrustChart";
import { MetricChart } from "@/components/MetricChart";
import { NetworkTopology } from "@/components/NetworkTopology";
import { RoundHistoryTable } from "@/components/RoundHistoryTable";
import { FeatureFusionView } from "@/components/FeatureFusionView";
import { Gauge, TrendingDown, Target, ShieldCheck, Users, Building2, Flag, Radio } from "lucide-react";

function StatCard({ icon: Icon, label, value, sub, color }: any) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] uppercase tracking-wide text-slate-500">{label}</span>
        <Icon className={`w-4 h-4 ${color}`} />
      </div>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-[11px] text-slate-500 mt-1">{sub}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setError(null);
    try {
      const summary = await fetchDashboardMetrics();
      setData(summary);
    } catch (e: any) {
      console.error("Failed to load metrics", e);
      setError(e.message || "Unable to load federation metrics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const ws = createWebSocketConnection((wsMsg) => {
      if (wsMsg.dashboard) {
        setData(wsMsg.dashboard);
        setError(null);
      }
    });
    return () => ws.close();
  }, []);

  if (loading || !data) {
    return (
      <div className="min-h-screen bg-[#090d16] flex items-center justify-center text-slate-400 text-sm">
        {error ? (
          <div className="max-w-md p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-center space-y-3">
            <p className="font-semibold text-rose-200">Backend Connection Error</p>
            <p className="text-xs text-rose-300/80">{error}</p>
            <button
              onClick={() => { setLoading(true); loadData(); }}
              className="px-4 py-2 text-xs font-semibold rounded-xl bg-blue-600 hover:bg-blue-500 text-white"
            >
              Retry Connection
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center space-y-3">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span>Initializing TrustFed Engine...</span>
          </div>
        )}
      </div>
    );
  }

  const progressPct = Math.min(100, Math.round((data.current_round / Math.max(1, data.total_rounds)) * 100));
  const f1Approx = (data.global_accuracy * 0.99).toFixed(3);

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 pb-12">
      <header className="sticky top-0 z-30 bg-slate-950/80 backdrop-blur-md border-b border-slate-800 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <Radio className="w-3.5 h-3.5 text-emerald-400" />
          Round <strong className="text-white">{data.current_round}</strong> ·{" "}
          {data.is_training_active ? "Training" : data.is_paused ? "Paused" : "Idle"}
        </div>
        <span className="flex items-center gap-1.5 text-[11px] text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Live
        </span>
      </header>

      <main className="max-w-7xl mx-auto px-6 pt-6 space-y-6">
        <div>
          <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Global Model Overview</p>
          <h1 className="text-xl font-bold text-white">Federation Dashboard</h1>
        </div>

        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon={Gauge} label="Global Accuracy" value={`${(data.global_accuracy * 100).toFixed(1)}%`} color="text-blue-400" />
          <StatCard icon={TrendingDown} label="Global Loss" value={data.global_loss.toFixed(4)} sub="cross-entropy" color="text-amber-400" />
          <StatCard icon={Target} label="F1 Score (approx.)" value={f1Approx} color="text-emerald-400" />
          <StatCard icon={ShieldCheck} label="Global Trust" value={`${(data.global_trust ?? 0).toFixed(1)}%`} color="text-indigo-400" />
        </section>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-slate-400">Training Progress</span>
            <span className="text-slate-400">Round {data.current_round}/{data.total_rounds}</span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 transition-all" style={{ width: `${progressPct}%` }} />
          </div>
        </section>

        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon={Users} label="Active Nodes" value={data.hospitals.filter(h => h.status === "Active").length} color="text-slate-100" />
          <StatCard icon={Building2} label="Total Hospitals" value={data.hospitals.length} color="text-slate-100" />
          <StatCard icon={Flag} label="Flagged / Excluded" value={data.flagged_count ?? 0} color="text-rose-400" />
          <StatCard icon={Radio} label="Attacks Live" value={data.attacks_live ?? 0} color="text-amber-400" />
        </section>

        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold text-white tracking-wide uppercase">
              Participating Hospital Nodes ({data.hospitals.length})
            </h2>
            <span className="text-xs text-slate-400">Zero Patient Data Transmitted • Encrypted Local Models Only</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {data.hospitals.map((hospital) => (
              <HospitalCard key={hospital.id} hospital={hospital} />
            ))}
          </div>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TrustChart roundHistory={data.federated_round_history} />
          <NetworkTopology hospitals={data.hospitals} currentRound={data.current_round} />
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MetricChart roundHistory={data.federated_round_history} />
          <FeatureFusionView stats={data.feature_fusion_stats} />
        </section>

        <section>
          <RoundHistoryTable roundHistory={data.federated_round_history} />
        </section>
      </main>
    </div>
  );
}
