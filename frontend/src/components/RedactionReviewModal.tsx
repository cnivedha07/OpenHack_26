"use client";

import React, { useState } from "react";
import { ShieldCheck, X, CheckCircle, AlertTriangle, Eye } from "lucide-react";

interface RedactionProposal {
  entity_type: string;
  matched_value: string;
  start_index: number;
  end_index: number;
  proposed_token: string;
  review_status: string;
}

interface RedactionReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  text: string;
  proposals: RedactionProposal[];
  onConfirmSanitization: (approvedProposals: RedactionProposal[]) => void;
}

export const RedactionReviewModal: React.FC<RedactionReviewModalProps> = ({
  isOpen,
  onClose,
  text,
  proposals,
  onConfirmSanitization
}) => {
  const [approvedItems, setApprovedItems] = useState<Record<number, boolean>>(() => {
    const initial: Record<number, boolean> = {};
    proposals.forEach((_, idx) => {
      initial[idx] = true;
    });
    return initial;
  });

  if (!isOpen) return null;

  const toggleApproval = (idx: number) => {
    setApprovedItems((prev) => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  const handleConfirm = () => {
    const selected = proposals.filter((_, idx) => approvedItems[idx]);
    onConfirmSanitization(selected);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl max-w-2xl w-full text-slate-100 overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Privacy Shield — Redaction Review</h3>
              <p className="text-xs text-slate-400">Human-in-the-Loop PII Entity Proposal Verification</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 transition-colors p-1 rounded-lg hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Raw Text Preview */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-2">
              <Eye className="w-4 h-4 text-cyan-400" /> Clinical Document Payload Sample
            </label>
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 font-mono max-h-32 overflow-y-auto">
              {text || "No text payload provided for preview."}
            </div>
          </div>

          {/* Proposals List */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-slate-200">
                Proposed PII Entities Detected ({proposals.length})
              </h4>
              <span className="text-xs text-emerald-400 font-medium">
                {Object.values(approvedItems).filter(Boolean).length} / {proposals.length} Approved
              </span>
            </div>

            {proposals.length === 0 ? (
              <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 text-center text-xs text-slate-400">
                No sensitive PII identifiers detected in payload.
              </div>
            ) : (
              <div className="space-y-2">
                {proposals.map((item, idx) => (
                  <div
                    key={idx}
                    onClick={() => toggleApproval(idx)}
                    className={`p-3 rounded-lg border text-xs flex items-center justify-between cursor-pointer transition-all ${
                      approvedItems[idx]
                        ? "bg-slate-950 border-emerald-500/40 text-slate-200"
                        : "bg-slate-950/50 border-slate-800 text-slate-500 opacity-60"
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-1.5 rounded-full ${approvedItems[idx] ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-800 text-slate-500"}`}>
                        <CheckCircle className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="font-semibold text-cyan-400">{item.entity_type}</span>
                        <div className="font-mono text-[11px] mt-0.5">
                          Detected: <span className="text-rose-300">{item.matched_value}</span> &rarr; Target: <span className="text-emerald-400 font-semibold">{item.proposed_token}</span>
                        </div>
                      </div>
                    </div>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${approvedItems[idx] ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-800 text-slate-400"}`}>
                      {approvedItems[idx] ? "REDACT" : "SKIP"}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer Controls */}
        <div className="px-6 py-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between">
          <div className="flex items-center text-xs text-amber-400 gap-1.5">
            <AlertTriangle className="w-4 h-4" />
            <span>Zero unredacted data written to disk.</span>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              className="px-4 py-2 text-xs font-semibold text-slate-950 bg-emerald-400 hover:bg-emerald-300 rounded-lg transition-colors flex items-center gap-2 shadow-lg shadow-emerald-500/20"
            >
              <ShieldCheck className="w-4 h-4" /> Approve &amp; Route to Pipeline
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
