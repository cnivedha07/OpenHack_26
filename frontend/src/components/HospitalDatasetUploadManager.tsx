"use client";

import React, { useState, useEffect } from "react";
import { Upload, Database, Activity, CheckCircle2, ShieldAlert, Cpu, FileSpreadsheet, RefreshCw } from "lucide-react";
import { uploadHospitalDataset, fetchHospitalDatasets, fetchTrainingRuns, getAuthUser } from "@/services/api";

interface HospitalDatasetUploadManagerProps {
  onTrainingTriggered?: () => void;
}

export const HospitalDatasetUploadManager: React.FC<HospitalDatasetUploadManagerProps> = ({ onTrainingTriggered }) => {
  const user = getAuthUser();
  const defaultHospital = user?.role === "hospital" && user?.hospital_id ? user.hospital_id : "hospital_1";

  const [hospitalId, setHospitalId] = useState(defaultHospital);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [datasets, setDatasets] = useState<any[]>([]);
  const [trainingRuns, setTrainingRuns] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const loadHistory = async () => {
    setLoadingHistory(true);
    try {
      const [dsRes, trRes] = await Promise.all([
        fetchHospitalDatasets(hospitalId),
        fetchTrainingRuns(hospitalId),
      ]);
      setDatasets(dsRes.datasets || []);
      setTrainingRuns(trRes.runs || []);
    } catch (e: any) {
      console.error("Failed to load hospital dataset history", e);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [hospitalId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUploadAndTrain = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError("Please select a patient dataset file (CSV, TXT, or JSON).");
      return;
    }

    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const res = await uploadHospitalDataset(hospitalId, selectedFile);
      setUploadResult(res);
      setSelectedFile(null);
      await loadHistory();
      if (onTrainingTriggered) onTrainingTriggered();
    } catch (e: any) {
      console.error("Dataset upload & training trigger failed", e);
      setError(e.message || "Failed to upload dataset and trigger training.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload & Automated Training Trigger Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-md relative overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <Upload className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Upload Patient Dataset &amp; Auto-Trigger FL Training</h2>
              <p className="text-xs text-slate-400">
                Schema validation &rarr; Privacy Shield de-identification &rarr; Auto PyTorch local training round &rarr; DB Persistence
              </p>
            </div>
          </div>
          <button
            onClick={loadHistory}
            disabled={loadingHistory}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingHistory ? "animate-spin" : ""}`} /> Refresh
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleUploadAndTrain} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide">
              Target Hospital Node
            </label>
            <select
              value={hospitalId}
              onChange={(e) => setHospitalId(e.target.value)}
              disabled={user?.role === "hospital"}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-emerald-500/60 transition-all disabled:opacity-60"
            >
              <option value="hospital_1">Hospital 1 (Metro General)</option>
              <option value="hospital_2">Hospital 2 (City Care Medical)</option>
              <option value="hospital_3">Hospital 3 (Apex Research)</option>
              <option value="hospital_4">Hospital 4 (St. Jude Children's)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide">
              Patient Dataset File (CSV / TXT)
            </label>
            <input
              type="file"
              accept=".csv,.txt,.json,.dat"
              onChange={handleFileChange}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 file:mr-3 file:py-1 file:px-2.5 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-emerald-500/20 file:text-emerald-300 hover:file:bg-emerald-500/30 transition-all"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={uploading || !selectedFile}
              className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-xs shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Running De-ID &amp; PyTorch Training...
                </>
              ) : (
                <>
                  <Upload className="w-3.5 h-3.5" /> Upload &amp; Train First Round
                </>
              )}
            </button>
          </div>
        </form>

        {/* Upload & Training Result Summary Card */}
        {uploadResult && (
          <div className="mt-5 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-emerald-300 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                Dataset Saved to DB &amp; Local Training Round Complete!
              </span>
              <span className="text-[10px] text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded font-mono">
                Dataset #{uploadResult.dataset_id}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-slate-300">
              <div>
                <span className="text-[10px] text-slate-500 block">Filename</span>
                <span className="font-semibold text-white truncate block">{uploadResult.filename}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block">PII Redact Count</span>
                <span className="font-semibold text-emerald-400">
                  {uploadResult.privacy_shield?.redaction_audit?.length || 0} tokens
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block">Local Accuracy</span>
                <span className="font-semibold text-teal-300">
                  {uploadResult.training_run?.accuracy != null
                    ? `${(uploadResult.training_run.accuracy * 100).toFixed(1)}%`
                    : "—"}
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block">F1 Score</span>
                <span className="font-semibold text-indigo-300">
                  {uploadResult.training_run?.f1_score != null
                    ? uploadResult.training_run.f1_score.toFixed(3)
                    : "—"}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Persistent Datasets & Training History Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Uploaded Datasets Table */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
            Uploaded Patient Datasets ({datasets.length})
          </h3>

          {datasets.length === 0 ? (
            <p className="text-xs text-slate-500 py-4 text-center">No datasets uploaded yet for {hospitalId}.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 uppercase text-[10px]">
                    <th className="py-2">ID</th>
                    <th className="py-2">Filename</th>
                    <th className="py-2">Type</th>
                    <th className="py-2">Rows</th>
                    <th className="py-2">PII Scrubbed</th>
                    <th className="py-2">Uploaded At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {datasets.map((d) => (
                    <tr key={d.id} className="hover:bg-slate-800/40">
                      <td className="py-2 font-mono text-[11px] text-slate-400">#{d.id}</td>
                      <td className="py-2 font-semibold text-white truncate max-w-[120px]">{d.filename}</td>
                      <td className="py-2">{d.data_type}</td>
                      <td className="py-2">{d.row_count}</td>
                      <td className="py-2 text-emerald-400">{d.pii_detected_count}</td>
                      <td className="py-2 text-slate-500 text-[10px]">
                        {d.uploaded_at ? new Date(d.uploaded_at).toLocaleTimeString() : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Training Runs History Table */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-teal-400" />
            Persisted Local Training Runs ({trainingRuns.length})
          </h3>

          {trainingRuns.length === 0 ? (
            <p className="text-xs text-slate-500 py-4 text-center">No training runs recorded yet for {hospitalId}.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 uppercase text-[10px]">
                    <th className="py-2">Run ID</th>
                    <th className="py-2">Status</th>
                    <th className="py-2">Accuracy</th>
                    <th className="py-2">Loss</th>
                    <th className="py-2">F1 Score</th>
                    <th className="py-2">Started</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {trainingRuns.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-800/40">
                      <td className="py-2 font-mono text-[11px] text-slate-400">Run #{r.id}</td>
                      <td className="py-2">
                        <span
                          className={`px-2 py-0.5 text-[10px] rounded-full font-semibold ${
                            r.status === "done"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                              : r.status === "running"
                              ? "bg-blue-500/10 text-blue-400 border border-blue-500/30"
                              : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                          }`}
                        >
                          {r.status}
                        </span>
                      </td>
                      <td className="py-2 text-teal-300 font-semibold">
                        {r.accuracy != null ? `${(r.accuracy * 100).toFixed(1)}%` : "—"}
                      </td>
                      <td className="py-2 text-amber-300">{r.loss != null ? r.loss.toFixed(4) : "—"}</td>
                      <td className="py-2 text-indigo-300">{r.f1_score != null ? r.f1_score.toFixed(3) : "—"}</td>
                      <td className="py-2 text-slate-500 text-[10px]">
                        {r.started_at ? new Date(r.started_at).toLocaleTimeString() : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
