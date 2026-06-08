import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const sans = Geist({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const mono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "PROMETHEE II — Apoio à Decisão Multicritério",
  description:
    "Aplicação web para resolver problemas de decisão com o método PROMETHEE II e visualização GAIA.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className={cn(sans.variable, mono.variable, "font-sans")}>
      <body>{children}</body>
    </html>
  );
}
