"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

interface MetricChartProps {
  roundHistory: any[];
}

export const MetricChart: React.FC<MetricChartProps> = ({ roundHistory }) => {
  const chartData = roundHistory.map((r) => ({
    round: `R${r.round_number}`,
    accuracy: (r.global_accuracy * 100).toFixed(1),
    loss: r.global_loss.toFixed(3),
  }));

  return (
    <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white">Global Healthcare AI Convergence</h3>
          <p className="text-xs text-slate-400">Global Accuracy &amp; Loss progression over federated rounds</p>
        </div>
      </div>

      <div className="h-64 w-full">
        {chartData.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-slate-500">
            No training rounds recorded yet
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="accGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="round" stroke="#64748b" fontSize={11} />
              <YAxis domain={[50, 100]} stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
              />
              <Area type="monotone" dataKey="accuracy" name="Global Accuracy (%)" stroke="#10b981" fillOpacity={1} fill="url(#accGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
