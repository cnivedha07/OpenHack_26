import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "TrustFed AI – Federated Health Intelligence",
  description: "Production-ready healthcare federated learning platform with Privacy Shield & Z-Score Trust Aggregation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#090d16] text-slate-100 antialiased min-h-screen">
        <Sidebar />
        <div className="pl-56 min-h-screen">{children}</div>
      </body>
    </html>
  );
}
