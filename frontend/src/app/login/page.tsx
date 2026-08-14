"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { loginAdmin, loginHospital } from "@/services/api";
import { Shield, Lock, Building2, User, KeyRound, AlertCircle, CheckCircle2 } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [roleMode, setRoleMode] = useState<"hospital" | "admin">("hospital");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      if (roleMode === "admin") {
        const res = await loginAdmin(username, password);
        setSuccess(`Welcome Administrator ${res.username}. Redirecting to portal...`);
        setTimeout(() => router.push("/"), 1200);
      } else {
        const res = await loginHospital(username, password);
        setSuccess(`Welcome Hospital User (${res.hospital_id}). Redirecting to portal...`);
        setTimeout(() => router.push("/"), 1200);
      }
    } catch (err: any) {
      setError(err.message || "Failed to authenticate. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = (type: "admin" | "hosp1" | "hosp2") => {
    setError(null);
    if (type === "admin") {
      setRoleMode("admin");
      setUsername("admin");
      setPassword("admin123");
    } else if (type === "hosp1") {
      setRoleMode("hospital");
      setUsername("hospital_1_user");
      setPassword("hospital123");
    } else {
      setRoleMode("hospital");
      setUsername("hospital_2_user");
      setPassword("hospital123");
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] flex items-center justify-center p-6 text-slate-100">
      <div className="w-full max-w-md bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        {/* Glow Effects */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        {/* Header */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="p-3 bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 rounded-2xl mb-4 text-cyan-400">
            <Shield className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            TrustFed 2.0
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Enterprise Multi-Tenant Healthcare FL Platform
          </p>
        </div>

        {/* Role Toggle Tabs */}
        <div className="grid grid-cols-2 p-1 bg-slate-950/60 border border-slate-800 rounded-xl mb-6">
          <button
            type="button"
            onClick={() => {
              setRoleMode("hospital");
              setError(null);
            }}
            className={`flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
              roleMode === "hospital"
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Building2 className="w-4 h-4" />
            Hospital Login
          </button>
          <button
            type="button"
            onClick={() => {
              setRoleMode("admin");
              setError(null);
            }}
            className={`flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
              roleMode === "admin"
                ? "bg-blue-500/20 text-blue-400 border border-blue-500/40 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Lock className="w-4 h-4" />
            Admin Portal
          </button>
        </div>

        {/* Feedback Alerts */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-start gap-3 text-red-400 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-start gap-3 text-emerald-400 text-sm">
            <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{success}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Username
            </label>
            <div className="relative">
              <User className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-500" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={roleMode === "admin" ? "admin" : "hospital_1_user"}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/60 transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Password
            </label>
            <div className="relative">
              <KeyRound className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/60 transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? "Authenticating..." : roleMode === "admin" ? "Sign In to Admin Portal" : "Sign In to Hospital Workspace"}
          </button>
        </form>

        {/* Development Helper Credentials */}
        <div className="mt-8 pt-6 border-t border-slate-800/80 text-center">
          <p className="text-xs text-slate-500 mb-3">Development Quick-Fill Options:</p>
          <div className="flex items-center justify-center gap-2">
            <button
              type="button"
              onClick={() => handleQuickFill("hosp1")}
              className="px-3 py-1.5 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 rounded-lg text-xs text-slate-300 transition-colors"
            >
              Hospital 1
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill("hosp2")}
              className="px-3 py-1.5 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 rounded-lg text-xs text-slate-300 transition-colors"
            >
              Hospital 2
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill("admin")}
              className="px-3 py-1.5 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 rounded-lg text-xs text-blue-300 transition-colors font-medium"
            >
              Admin
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
