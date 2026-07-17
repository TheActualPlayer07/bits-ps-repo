import { ThemeName } from "./types";

export type ThemeClasses = {
  gradient: string;
  accentText: string;
  accentBg: string;
  accentBgHover: string;
  accentRing: string;
  chipBg: string;
  chipText: string;
};

/**
 * Tailwind's compiler only includes classes it can see written literally
 * in source — so every theme's classes are spelled out in full below
 * instead of built with template strings like `bg-${theme}-600`.
 */
export const THEMES: Record<ThemeName, ThemeClasses> = {
  violet: {
    gradient: "from-violet-600 to-indigo-600",
    accentText: "text-violet-600",
    accentBg: "bg-violet-600",
    accentBgHover: "hover:bg-violet-700",
    accentRing: "focus-visible:ring-violet-500",
    chipBg: "bg-violet-100",
    chipText: "text-violet-700",
  },
  emerald: {
    gradient: "from-emerald-600 to-teal-600",
    accentText: "text-emerald-600",
    accentBg: "bg-emerald-600",
    accentBgHover: "hover:bg-emerald-700",
    accentRing: "focus-visible:ring-emerald-500",
    chipBg: "bg-emerald-100",
    chipText: "text-emerald-700",
  },
  amber: {
    gradient: "from-amber-500 to-orange-600",
    accentText: "text-amber-600",
    accentBg: "bg-amber-500",
    accentBgHover: "hover:bg-amber-600",
    accentRing: "focus-visible:ring-amber-500",
    chipBg: "bg-amber-100",
    chipText: "text-amber-700",
  },
  rose: {
    gradient: "from-rose-600 to-pink-600",
    accentText: "text-rose-600",
    accentBg: "bg-rose-600",
    accentBgHover: "hover:bg-rose-700",
    accentRing: "focus-visible:ring-rose-500",
    chipBg: "bg-rose-100",
    chipText: "text-rose-700",
  },
  slate: {
    gradient: "from-slate-700 to-slate-900",
    accentText: "text-slate-700",
    accentBg: "bg-slate-800",
    accentBgHover: "hover:bg-slate-900",
    accentRing: "focus-visible:ring-slate-500",
    chipBg: "bg-slate-200",
    chipText: "text-slate-800",
  },
  cyan: {
    gradient: "from-cyan-600 to-blue-600",
    accentText: "text-cyan-600",
    accentBg: "bg-cyan-600",
    accentBgHover: "hover:bg-cyan-700",
    accentRing: "focus-visible:ring-cyan-500",
    chipBg: "bg-cyan-100",
    chipText: "text-cyan-700",
  },
};
