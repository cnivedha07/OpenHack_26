"use client";

import React, { useState } from "react";
import { Zap, ShieldAlert, Play, Square } from "lucide-react";
import { toggleAttack, startFederatedRound } from "@/services/api";

interface AttackControlPanelProps {
  onRoundComplete: () => void;
}

export const AttackControlPanel: React.FC<AttackControlPanelProps> = ({ onRoundComplete }) => {
  const [selectedHospital, setSelectedHospital] = useState("hospital_3");
  const [attackType, setAttackType] = useState("Gradient Poisoning");
  const [loading, setLoading] = useState(false);
  const [activeAlert, setActiveAlert] = useState<string | null>(null);

  const ATTACK_OPTIONS = [
    "Gradient Poisoning",
    "Random Noise Injection",
    "Label Flipping",
    "Model Poisoning",
    "Backdoor Attack",
    "Sybil Attack",
    "Data Poisoning",
  ];

  const handleInjectAttack = async () => {
    setLoading(true);
    try {
      await toggleAttack(selectedHospital, attackType);
      setActiveAlert(`Injected '${attackType}' into ${selectedHospital}. Next round will test Z-score defense!`);
      onRoundComplete();
    } catch (e: any) {
      console.error(e);
      setActiveAlert(`Failed to inject attack: ${e.message || "Network error"}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClearAttack = async () => {
    setLoading(true);
    try {
      await toggleAttack(selectedHospital, "None");
      setActiveAlert(`Cleared attacks on ${selectedHospital}.`);
      onRoundComplete();
    } catch (e: any) {
      console.error(e);
      setActiveAlert(`Failed to clear attack: ${e.message || "Network error"}`);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteRound = async () => {
    setLoading(true);
    try {
      await startFederatedRound();
      onRoundComplete();
    } catch (e: any) {
      console.error(e);
      setActiveAlert(`Failed to execute FL round: ${e.message || "Network error"}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Attack Simulation &amp; Defense Tester</h3>
            <p className="text-xs text-slate-400">Inject adversarial updates to verify Trust-Based Z-Score isolation</p>
          </div>
        </div>

        <button
          onClick={handleExecuteRound}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-blue-500/20"
        >
          <Play className="w-4 h-4 fill-white" />
          {loading ? "Running Round..." : "Execute FL Round"}
        </button>
      </div>

      {activeAlert && (
        <div className="mb-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4" />
            {activeAlert}
          </span>
          <button onClick={() => setActiveAlert(null)} className="text-amber-400 font-bold hover:underline">Dismiss</button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <div>
          <label className="block text-slate-400 mb-1">Target Hospital Node</label>
          <select
            value={selectedHospital}
            onChange={(e) => setSelectedHospital(e.target.value)}
            className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-blue-500"
          >
            <option value="hospital_1">Hospital 1 (Metro General)</option>
            <option value="hospital_2">Hospital 2 (City Care)</option>
            <option value="hospital_3">Hospital 3 (Apex Research)</option>
            <option value="hospital_4">Hospital 4 (St. Jude Children's)</option>
          </select>
        </div>

        <div>
          <label className="block text-slate-400 mb-1">Malicious Attack Vector</label>
          <select
            value={attackType}
            onChange={(e) => setAttackType(e.target.value)}
            className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-blue-500"
          >
            {ATTACK_OPTIONS.map((at) => (
              <option key={at} value={at}>{at}</option>
            ))}
          </select>
        </div>

        <div className="flex items-end space-x-2">
          <button
            onClick={handleInjectAttack}
            disabled={loading}
            className="flex-1 py-2.5 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/40 text-rose-300 font-semibold transition-all"
          >
            Inject Attack
          </button>
          <button
            onClick={handleClearAttack}
            disabled={loading}
            className="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold"
          >
            Clear
          </button>
        </div>
      </div>
    </div>
  );
};
