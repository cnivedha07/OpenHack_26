"use client";

import React from "react";
import { ShieldCheck, Activity, Cpu, Lock, Terminal } from "lucide-react";

interface NavbarProps {
  currentRound: number;
  modelVersion: string;
  globalAccuracy: number;
  onOpenPrivacyModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentRound,
  modelVersion,
  globalAccuracy,
  onOpenPrivacyModal,
}) => {
  return (
    <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="p-2.5 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 shadow-lg shadow-blue-500/20">
          <ShieldCheck className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            TrustFed <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">2.0 Enterprise</span>
          </h1>
          <p className="text-xs text-slate-400">Privacy-Preserving Healthcare FL Platform</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl text-xs">
          <div className="flex items-center gap-1.5 text-slate-300">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span>Model: <strong className="text-white">{modelVersion}</strong></span>
          </div>
          <div className="h-4 w-px bg-slate-800" />
          <div className="flex items-center gap-1.5 text-slate-300">
            <Activity className="w-4 h-4 text-blue-400" />
            <span>Round: <strong className="text-white">{currentRound}</strong></span>
          </div>
          <div className="h-4 w-px bg-slate-800" />
          <div className="flex items-center gap-1.5 text-slate-300">
            <span>Accuracy: <strong className="text-emerald-400">{(globalAccuracy * 100).toFixed(1)}%</strong></span>
          </div>
        </div>

        <button
          onClick={onOpenPrivacyModal}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-semibold transition-all shadow-md"
        >
          <Lock className="w-4 h-4" />
          Privacy Shield Audit
        </button>
      </div>
    </header>
  );
};
