"use client";

import React from "react";
import { Hospital } from "@/types";
import { Server, ShieldCheck, Activity } from "lucide-react";

interface NetworkTopologyProps {
  hospitals: Hospital[];
  currentRound: number;
}

export const NetworkTopology: React.FC<NetworkTopologyProps> = ({ hospitals, currentRound }) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white">Federated Network Topology &amp; Trust Guard</h3>
          <p className="text-xs text-slate-400">Encrypted parameter aggregation hub with real-time anomaly isolation</p>
        </div>
        <span className="px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-mono">
          Round #{currentRound}
        </span>
      </div>

      <div className="relative h-64 w-full bg-slate-950/80 rounded-xl border border-slate-800/80 flex items-center justify-center p-4 overflow-hidden">
        {/* Connection lines SVG overlay */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          <line x1="20%" y1="30%" x2="50%" y2="50%" stroke="#334155" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="80%" y1="30%" x2="50%" y2="50%" stroke="#334155" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="20%" y1="70%" x2="50%" y2="50%" stroke="#334155" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="80%" y1="70%" x2="50%" y2="50%" stroke="#334155" strokeWidth="2" strokeDasharray="4 4" />
        </svg>

        {/* Central Trust Aggregator Node */}
        <div className="z-10 flex flex-col items-center">
          <div className="p-4 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 border border-blue-400/40 shadow-xl shadow-blue-500/20 animate-pulse">
            <Server className="w-8 h-8 text-white" />
          </div>
          <span className="mt-2 text-xs font-bold text-white bg-slate-900/90 px-3 py-1 rounded-full border border-slate-700 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
            Trust FedAvg Hub
          </span>
        </div>

        {/* Hospital 1 Node (Top-Left) */}
        <div className="absolute top-6 left-6 z-10 flex flex-col items-center">
          <div className="p-3 rounded-xl bg-slate-900 border border-blue-500/40 text-blue-400">
            <Activity className="w-5 h-5" />
          </div>
          <span className="mt-1 text-[11px] font-medium text-slate-300">Hospital 1</span>
        </div>

        {/* Hospital 2 Node (Top-Right) */}
        <div className="absolute top-6 right-6 z-10 flex flex-col items-center">
          <div className="p-3 rounded-xl bg-slate-900 border border-emerald-500/40 text-emerald-400">
            <Activity className="w-5 h-5" />
          </div>
          <span className="mt-1 text-[11px] font-medium text-slate-300">Hospital 2</span>
        </div>

        {/* Hospital 3 Node (Bottom-Left) */}
        <div className="absolute bottom-6 left-6 z-10 flex flex-col items-center">
          <div className={`p-3 rounded-xl bg-slate-900 border text-slate-300 ${
            hospitals.find(h => h.id === "hospital_3")?.trust_score! < 40 ? "border-rose-500 text-rose-400 shadow-lg shadow-rose-500/20" : "border-amber-500/40 text-amber-400"
          }`}>
            <Activity className="w-5 h-5" />
          </div>
          <span className="mt-1 text-[11px] font-medium text-slate-300">
            Hospital 3 {hospitals.find(h => h.id === "hospital_3")?.trust_score! < 40 && "(Isolated)"}
          </span>
        </div>

        {/* Hospital 4 Node (Bottom-Right) */}
        <div className="absolute bottom-6 right-6 z-10 flex flex-col items-center">
          <div className="p-3 rounded-xl bg-slate-900 border border-indigo-500/40 text-indigo-400">
            <Activity className="w-5 h-5" />
          </div>
          <span className="mt-1 text-[11px] font-medium text-slate-300">Hospital 4</span>
        </div>
      </div>
    </div>
  );
};
