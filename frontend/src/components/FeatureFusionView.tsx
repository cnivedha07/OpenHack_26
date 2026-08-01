"use client";

import React from "react";
import { FeatureFusionStats } from "@/types";
import { Layers, Image as ImageIcon, FileText, Binary } from "lucide-react";

interface FeatureFusionViewProps {
  stats: FeatureFusionStats;
}

export const FeatureFusionView: React.FC<FeatureFusionViewProps> = ({ stats }) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
      <div className="flex items-center space-x-2 mb-4">
        <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
          <Layers className="w-4 h-4" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">Multimodal Feature Fusion Engine</h3>
          <p className="text-xs text-slate-400">Step 7 Multi-Head Cross-Attention Gated Projection (128-d Unified Representation)</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
            <ImageIcon className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block">CNN Module (Images)</span>
            <span className="text-sm font-bold text-white">{stats.cnn_usage_pct}%</span>
          </div>
        </div>

        <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
            <Binary className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block">ANN Module (Vitals)</span>
            <span className="text-sm font-bold text-white">{stats.ann_usage_pct}%</span>
          </div>
        </div>

        <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block">BERT Module (Clinical)</span>
            <span className="text-sm font-bold text-white">{stats.bert_usage_pct}%</span>
          </div>
        </div>
      </div>

      <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
        <span className="text-xs text-slate-400 block mb-1">Attention Weight Fusion Distribution</span>
        <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden flex">
          <div className="bg-blue-500 h-full" style={{ width: `${stats.cnn_usage_pct}%` }} />
          <div className="bg-emerald-500 h-full" style={{ width: `${stats.ann_usage_pct}%` }} />
          <div className="bg-purple-500 h-full" style={{ width: `${stats.bert_usage_pct}%` }} />
        </div>
      </div>
    </div>
  );
};
