"use client";
import React, { useEffect, useState } from "react";
import { DashboardSummary } from "@/types";
import { fetchDashboardMetrics } from "@/services/api";
import { TrustChart } from "@/components/TrustChart";
import { RoundHistoryTable } from "@/components/RoundHistoryTable";
import { NetworkTopology } from "@/components/NetworkTopology";
import { AlertTriangle } from "lucide-react";

export default function TrustAnalyticsPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardMetrics()
      .then(setData)
      .catch((e) => setError(e.message || "Failed to load trust analytics data"));
  }, []);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 bg-[#090d16] text-rose-300 text-xs">
        <div className="flex items-center gap-2 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30">
          <AlertTriangle className="w-4 h-4 text-rose-400" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  if (!data) return <div className="min-h-screen flex items-center justify-center text-slate-400 text-sm">Loading...</div>;

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 pb-12">
      <main className="max-w-7xl mx-auto px-6 pt-8 space-y-6">
        <h1 className="text-xl font-bold text-white">Trust Analytics</h1>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TrustChart roundHistory={data.federated_round_history} />
          <NetworkTopology hospitals={data.hospitals} currentRound={data.current_round} />
        </div>
        <RoundHistoryTable roundHistory={data.federated_round_history} />
      </main>
    </div>
  );
}
