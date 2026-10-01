import React from 'react'
import { Badge } from '../ui/Badge'
import { Database, FileSpreadsheet, ShieldAlert, Sparkles } from 'lucide-react'

export interface DataSourceBadgeProps {
  provenance?: string
  className?: string
}

export function DataSourceBadge({ provenance = 'Demo data', className }: DataSourceBadgeProps) {
  let variant: 'low' | 'moderate' | 'high' | 'info' | 'neutral' = 'neutral'
  let icon = <Database className="w-3 h-3" />
  let label = provenance

  if (provenance.toLowerCase().includes('demo') || provenance.toLowerCase().includes('synth')) {
    variant = 'info'
    icon = <Sparkles className="w-3 h-3 text-blue-600" />
    label = 'Demo data'
  } else if (provenance.toLowerCase().includes('import') || provenance.toLowerCase().includes('self')) {
    variant = 'low'
    icon = <FileSpreadsheet className="w-3 h-3 text-emerald-600" />
    label = 'Imported data'
  } else if (provenance.toLowerCase().includes('reference')) {
    variant = 'moderate'
    icon = <Database className="w-3 h-3 text-amber-600" />
    label = 'Reference data'
  } else if (provenance.toLowerCase().includes('verif') || provenance.toLowerCase().includes('insufficient')) {
    variant = 'high'
    icon = <ShieldAlert className="w-3 h-3 text-rose-600" />
    label = 'Needs verification'
  }

  return (
    <Badge variant={variant} className={`normal-case font-medium gap-1.5 py-1 px-2.5 text-xs ${className || ''}`}>
      {icon}
      <span>{label}</span>
    </Badge>
  )
}
