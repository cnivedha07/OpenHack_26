"use client";

import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

interface TrustChartProps {
  roundHistory: any[];
}

export const TrustChart: React.FC<TrustChartProps> = ({ roundHistory }) => {
  const chartData = roundHistory.map((r) => ({
    round: `R${r.round_number}`,
    h1: r.active_trust_scores?.hospital_1 ?? 100,
    h2: r.active_trust_scores?.hospital_2 ?? 100,
    h3: r.active_trust_scores?.hospital_3 ?? 100,
    h4: r.active_trust_scores?.hospital_4 ?? 100,
  }));

  return (
    <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white">Trust Score Evolution Across Rounds</h3>
          <p className="text-xs text-slate-400">Dynamic Z-Score penalty system (Exclusion threshold: &lt; 40)</p>
        </div>
      </div>

      <div className="h-64 w-full">
        {chartData.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-slate-500">
            Execute FL rounds to visualize dynamic trust scores
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="round" stroke="#64748b" fontSize={11} />
              <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
              />
              <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
              <Line type="monotone" dataKey="h1" name="Hospital 1" stroke="#3b82f6" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="h2" name="Hospital 2" stroke="#10b981" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="h3" name="Hospital 3 (Attacker)" stroke="#ef4444" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="h4" name="Hospital 4" stroke="#8b5cf6" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
