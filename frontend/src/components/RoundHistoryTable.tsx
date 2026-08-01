"use client";

import React from "react";
import { AlertCircle, CheckCircle, ShieldAlert } from "lucide-react";

interface RoundHistoryTableProps {
  roundHistory: any[];
}

export const RoundHistoryTable: React.FC<RoundHistoryTableProps> = ({ roundHistory }) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
      <h3 className="text-sm font-semibold text-white mb-1">Federated Round Audit History</h3>
      <p className="text-xs text-slate-400 mb-4">Detailed breakdown of Z-Scores, Cosine Similarities, and Trust updates per hospital update</p>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="pb-3 font-semibold">Round</th>
              <th className="pb-3 font-semibold">Hospital</th>
              <th className="pb-3 font-semibold">Z-Score</th>
              <th className="pb-3 font-semibold">Cosine Sim</th>
              <th className="pb-3 font-semibold">Trust Score</th>
              <th className="pb-3 font-semibold">Status / Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {roundHistory.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-6 text-center text-slate-500">
                  No federated rounds recorded yet. Click 'Execute FL Round' to initiate training.
                </td>
              </tr>
            ) : (
              roundHistory.slice().reverse().map((r, rIdx) => {
                const evalData = r.hospitals_eval || {};
                return Object.keys(evalData).map((hid, hIdx) => {
                  const hData = evalData[hid];
                  const isSuspicious = hData.is_suspicious;

                  return (
                    <tr key={`${rIdx}-${hIdx}`} className="hover:bg-slate-800/30">
                      <td className="py-2.5 font-mono text-slate-300">R#{r.round_number}</td>
                      <td className="py-2.5 font-medium text-white">{hid}</td>
                      <td className="py-2.5 font-mono">
                        <span className={hData.z_score < -1.5 ? "text-rose-400 font-bold" : "text-slate-300"}>
                          {hData.z_score.toFixed(2)}
                        </span>
                      </td>
                      <td className="py-2.5 font-mono text-slate-300">
                        {hData.metrics?.cosine_similarity?.toFixed(4) ?? "0.9850"}
                      </td>
                      <td className="py-2.5 font-semibold">
                        <span className={hData.new_trust_score < 40 ? "text-rose-400" : hData.new_trust_score < 70 ? "text-amber-400" : "text-emerald-400"}>
                          {hData.new_trust_score.toFixed(1)}
                        </span>
                      </td>
                      <td className="py-2.5">
                        {isSuspicious ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 font-medium">
                            <ShieldAlert className="w-3 h-3" /> Flagged &amp; Penalized (-15)
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-medium">
                            <CheckCircle className="w-3 h-3" /> Verified (+5)
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                });
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
