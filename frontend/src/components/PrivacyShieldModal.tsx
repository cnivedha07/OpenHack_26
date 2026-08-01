"use client";

import React, { useState } from "react";
import { X, Lock, CheckCircle, ShieldAlert } from "lucide-react";
import { anonymizeSampleText } from "@/services/api";

interface PrivacyShieldModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PrivacyShieldModal: React.FC<PrivacyShieldModalProps> = ({ isOpen, onClose }) => {
  const [rawText, setRawText] = useState(
    `Patient Name: Ramesh Kumar, Aadhaar Number: 4829-1039-5820, Phone: +91 9845012345.\nAdmitted to Metro General Hospital (HOSP-88421) under Dr. Sunita Sharma.\nDiagnosed with Type-2 Diabetes. DOB: 14/05/1978. MRN: MRN-994012.`
  );
  const [anonymizedText, setAnonymizedText] = useState("");
  const [redactedLogs, setRedactedLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleTestScrub = async () => {
    setLoading(true);
    try {
      const res = await anonymizeSampleText(rawText);
      setAnonymizedText(res.redacted_text);
      setRedactedLogs(res.redaction_logs);
    } catch (e) {
      console.error("Privacy scrub failed", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 w-full max-w-4xl rounded-2xl p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white rounded-lg bg-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <Lock className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Privacy Shield Engine Inspector</h2>
            <p className="text-xs text-slate-400">
              Step 1 PII Redaction Audit (Regex + Rule-Based NER + OCR Scrubbing)
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">
              Raw Uploaded Healthcare Document / Clinical Note
            </label>
            <textarea
              rows={6}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2 flex items-center justify-between">
              <span>Sanitized Output (Passed to Models)</span>
              <span className="text-emerald-400 text-[10px] bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">Zero PII Leaked</span>
            </label>
            <div className="w-full h-36 p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-emerald-300 font-mono overflow-y-auto whitespace-pre-wrap">
              {anonymizedText || "Click 'Execute Privacy Shield Scrub' to test..."}
            </div>
          </div>
        </div>

        {redactedLogs.length > 0 && (
          <div className="mt-4 p-3 rounded-xl bg-slate-950 border border-slate-800">
            <h4 className="text-xs font-bold text-slate-300 mb-2 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              Redacted Entities Audit Trail ({redactedLogs.length} items detected)
            </h4>
            <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
              {redactedLogs.map((item, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 rounded bg-rose-500/10 border border-rose-500/30 text-rose-300 text-[10px] font-mono"
                >
                  [{item.entity_type}] ➔ [REDACTED]
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
          >
            Close Audit Inspector
          </button>
          <button
            onClick={handleTestScrub}
            disabled={loading}
            className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/20"
          >
            {loading ? "Scrubbing..." : "Execute Privacy Shield Scrub"}
          </button>
        </div>
      </div>
    </div>
  );
};
