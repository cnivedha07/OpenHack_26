"use client";

import React from "react";
import { Server, Activity, ShieldCheck, Wifi, Lock } from "lucide-react";

interface NetworkTopologyDiagramProps {
  serverAddress?: string;
  isTrainingActive?: boolean;
  currentRound?: number;
}

export const NetworkTopologyDiagram: React.FC<NetworkTopologyDiagramProps> = ({
  serverAddress = "127.0.0.1:8080",
  isTrainingActive = false,
  currentRound = 0
}) => {
  const hospitals = [
    { id: "hospital_1", name: "Metro General Hospital", region: "Us-East", status: "Connected (gRPC)" },
    { id: "hospital_2", name: "St. Jude Children's", region: "Us-West", status: "Connected (gRPC)" },
    { id: "hospital_3", name: "City Care Clinic", region: "Eu-Central", status: "Connected (gRPC)" },
    { id: "hospital_4", name: "Apex Heart Center", region: "Ap-South", status: "Connected (gRPC)" }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl text-slate-100 space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <Wifi className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold">Multi-Hospital Network Topology</h3>
            <p className="text-xs text-slate-400">gRPC Flower Transport &amp; Local On-Premises Containers</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="flex h-2.5 w-2.5 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="font-mono text-emerald-400 font-medium">{serverAddress}</span>
        </div>
      </div>

      {/* Network Architecture Diagram */}
      <div className="relative bg-slate-950 border border-slate-800 rounded-xl p-6 overflow-hidden">
        {/* Central Server Node */}
        <div className="flex justify-center mb-8">
          <div className="bg-slate-900 border-2 border-emerald-500/50 rounded-xl p-4 shadow-lg shadow-emerald-500/10 flex items-center space-x-4 max-w-md w-full">
            <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl">
              <Server className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-100 uppercase tracking-wider">Central FL Server</span>
                <span className="text-[10px] bg-emerald-500/20 text-emerald-300 font-mono px-2 py-0.5 rounded">
                  Round #{currentRound}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">Trust-Weighted Z-Score Aggregator Engine</p>
            </div>
          </div>
        </div>

        {/* Client Nodes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {hospitals.map((h) => (
            <div
              key={h.id}
              className="bg-slate-900/80 border border-slate-800 hover:border-slate-700 rounded-lg p-3 text-xs space-y-2 transition-all"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-cyan-400">{h.id}</span>
                <span className="flex items-center gap-1 text-[10px] text-emerald-400">
                  <Lock className="w-3 h-3" /> TLS
                </span>
              </div>
              <div className="font-medium text-slate-200 truncate">{h.name}</div>
              <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800">
                <span>{h.region}</span>
                <span className="text-emerald-400 font-mono">{h.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
