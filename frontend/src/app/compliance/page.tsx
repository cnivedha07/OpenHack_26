"use client";
import React, { useEffect, useState } from "react";
import { fetchValidationReport } from "@/services/api";

export default function CompliancePage() {
  const [report, setReport] = useState<any>(null);
  useEffect(() => { fetchValidationReport().then(setReport); }, []);
  if (!report) return <div className="min-h-screen flex items-center justify-center text-slate-400 text-sm">Loading...</div>;
  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 pb-12">
      <main className="max-w-4xl mx-auto px-6 pt-8 space-y-6">
        <h1 className="text-xl font-bold text-white">Compliance & Validation</h1>
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-[11px] text-slate-500 uppercase">Total Validated</p>
            <p className="text-2xl font-bold text-white">{report.total_validated}</p>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-[11px] text-slate-500 uppercase">Passed</p>
            <p className="text-2xl font-bold text-emerald-400">{report.passed}</p>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-[11px] text-slate-500 uppercase">Rejected</p>
            <p className="text-2xl font-bold text-rose-400">{report.rejected}</p>
          </div>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <p className="text-[11px] uppercase text-slate-500 mb-3">Rejection Reasons</p>
          {Object.entries(report.rejection_reasons || {}).map(([k, v]: any) => (
            <div key={k} className="flex justify-between text-xs py-1.5 border-b border-slate-800/60 text-slate-300">
              <span>{k}</span><span>{v}</span>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
