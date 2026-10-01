import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPercentage(val: number | null | undefined, fallback = "N/A"): string {
  if (val === null || val === undefined || isNaN(val)) return fallback
  return `${val.toFixed(1)}%`
}

export function formatNumber(val: number | null | undefined, decimals = 1, fallback = "N/A"): string {
  if (val === null || val === undefined || isNaN(val)) return fallback
  return val.toFixed(decimals)
}
