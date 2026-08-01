"use client";
import React, { useEffect, useState } from "react";
import { fetchSystemLogs } from "@/services/api";

export default function LogsPage() {
  const [logs, setLogs] = useState<string[]>([]);
  useEffect(() => {
    const load = () => fetchSystemLogs().then((r) => setLogs(r.logs || [])).catch(() => {});
    load();
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, []);
  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 pb-12">
      <main className="max-w-4xl mx-auto px-6 pt-8 space-y-6">
        <h1 className="text-xl font-bold text-white">Live Logs</h1>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 font-mono text-xs space-y-1.5">
          {logs.length > 0 ? (
            logs.map((l, i) => <p key={i} className="text-slate-400">{l}</p>)
          ) : (
            <p className="text-slate-500 italic">No logs available or server connecting...</p>
          )}
        </div>
      </main>
    </div>
  );
}
