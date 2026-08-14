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

"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { getAuthUser, logout } from "@/services/api";
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
  LogOut,
  UserCheck
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard, role: "all" },
  { href: "/hospitals", label: "Hospitals", icon: Building2, role: "admin" },
  { href: "/training", label: "Training Control", icon: SlidersHorizontal, role: "admin" },
  { href: "/trust-analytics", label: "Trust Analytics", icon: BarChart3, role: "admin" },
  { href: "/attack-simulation", label: "Attack Simulation", icon: Zap, role: "admin" },
  { href: "/privacy-shield", label: "Privacy Shield", icon: Lock, role: "all" },
  { href: "/compliance", label: "Compliance", icon: ClipboardCheck, role: "all" },
  { href: "/logs", label: "Live Logs", icon: Terminal, role: "admin" },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const [user, setUser] = useState<{ username: string; role: string; hospital_id: string | null } | null>(null);

  useEffect(() => {
    setUser(getAuthUser());
  }, [pathname]);

  if (pathname === "/login") {
    return null;
  }

  const role = user?.role || "guest";
  const filteredNavItems = NAV_ITEMS.filter(
    (item) => item.role === "all" || (role === "admin" && item.role === "admin")
  );

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
        {filteredNavItems.map(({ href, label, icon: Icon }) => {
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

      <div className="p-3 border-t border-slate-800">
        {user ? (
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                <UserCheck className="w-3.5 h-3.5" />
              </div>
              <div className="text-[11px] overflow-hidden">
                <p className="text-slate-200 font-semibold truncate leading-tight">{user.username}</p>
                <p className="text-slate-400 text-[10px] capitalize leading-tight">
                  {user.role} {user.hospital_id ? `(${user.hospital_id})` : ""}
                </p>
              </div>
            </div>
            <button
              onClick={() => logout()}
              className="w-full mt-1 py-1.5 px-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" />
              Sign Out
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="w-full py-2 px-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 shadow-sm transition-all"
          >
            Sign In / Login
          </Link>
        )}
      </div>
    </aside>
  );
};

