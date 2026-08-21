"use client";

import React, { useState } from "react";
import { Lock, ShieldCheck, ShieldAlert } from "lucide-react";
import { anonymizeSampleText } from "@/services/api";

export default function PrivacyShieldPage() {
  const [rawText, setRawText] = useState(
    `Patient Name: Rahul Sharma\nPatient ID: PID-99213\nMRN: MRN-4471203\nDate of Birth: 12/04/1986\nAddress: 42 MG Road, Bangalore\nPhone: +91 98450 12345\nEmail: rahul.sharma@gmail.com\nAadhaar: 4123 8890 5521\nInsurance No: INS-88213445\nReferred by: Dr. Anita Verma\nEmergency Contact: Priya Sharma\n\nDiagnosis: Community-acquired pneumonia, right lower lobe.\nImpression: Consolidation with mild pleural effusion. Recommend antibiotics and follow-up chest X-ray in 2 weeks.`
  );
  const [anonymizedText, setAnonymizedText] = useState("");
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasRun, setHasRun] = useState(false);

  const runScan = async () => {
    setLoading(true);
    try {
      const res = await anonymizeSampleText(rawText);
      setAnonymizedText(res.redacted_text);
      setLogs(res.redaction_logs || []);
      setHasRun(true);
    } catch (e) {
      console.error("Privacy scan failed", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 pb-12">
      <main className="max-w-6xl mx-auto px-6 pt-8 space-y-6">
        <div>
          <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Module 1 · Anonymization</p>
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <Lock className="w-5 h-5 text-emerald-400" /> Privacy Shield Engine
            </h1>
            <span className="flex items-center gap-1.5 text-[11px] text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5" /> Original never stored · never transmitted
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
            <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-2">Raw Medical Record (Local Only)</p>
            <textarea
              rows={14}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
            />
            <button
              onClick={runScan}
              disabled={loading}
              className="mt-4 w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2"
            >
              {loading ? "Scanning..." : "Run Privacy Shield"}
            </button>

          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
            <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-2">Anonymized Output (Safe for Training)</p>
            <div className="w-full h-[calc(100%-2.5rem)] min-h-[19rem] p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-emerald-300 font-mono overflow-y-auto whitespace-pre-wrap flex items-center justify-center text-center">
              {hasRun ? (
                <pre className="whitespace-pre-wrap text-left w-full">{anonymizedText}</pre>
              ) : (
                <div className="flex flex-col items-center gap-2 text-slate-500">
                  <ShieldCheck className="w-8 h-8" />
                  <span>Run a scan to detect and mask PII.</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {logs.length > 0 && (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
            <h4 className="text-xs font-bold text-slate-300 mb-3 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              Redacted Entities Audit Trail ({logs.length} items detected)
            </h4>
            <div className="flex flex-wrap gap-2">
              {logs.map((item, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 rounded bg-rose-500/10 border border-rose-500/30 text-rose-300 text-[10px] font-mono"
                >
                  [{item.entity_type}] → [REDACTED]
                </span>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
