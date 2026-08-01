"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Building2,
  SlidersHorizontal,
  BarChart3,
  Zap,
  Lock,
  ClipboardCheck,
  Terminal,
  ShieldCheck,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/hospitals", label: "Hospitals", icon: Building2 },
  { href: "/training", label: "Training Control", icon: SlidersHorizontal },
  { href: "/trust-analytics", label: "Trust Analytics", icon: BarChart3 },
  { href: "/attack-simulation", label: "Attack Simulation", icon: Zap },
  { href: "/privacy-shield", label: "Privacy Shield", icon: Lock },
  { href: "/compliance", label: "Compliance", icon: ClipboardCheck },
  { href: "/logs", label: "Live Logs", icon: Terminal },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-56 bg-slate-950/95 border-r border-slate-800 flex flex-col z-40">
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-slate-800">
        <div className="p-2 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 shadow-lg shadow-blue-500/20">
          <ShieldCheck className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-white leading-tight">TrustFed AI</h1>
          <p className="text-[10px] text-slate-500 leading-tight">Federated Health Intelligence</p>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                active
                  ? "bg-blue-500/10 text-blue-400 border border-blue-500/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="px-4 py-4 border-t border-slate-800 flex items-center gap-2">
        <div className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-300">
          S
        </div>
        <div className="text-[11px]">
          <p className="text-slate-200 font-medium leading-tight">System Administrator</p>
          <p className="text-slate-500 leading-tight">Admin</p>
        </div>
      </div>
    </aside>
  );
};
