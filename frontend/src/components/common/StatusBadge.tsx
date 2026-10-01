import React from 'react'
import { Badge } from '../ui/Badge'
import { CheckCircle2, AlertTriangle, AlertCircle, HelpCircle } from 'lucide-react'

export interface StatusBadgeProps {
  level: string
  className?: string
  showIcon?: boolean
}

export function StatusBadge({ level, className, showIcon = true }: StatusBadgeProps) {
  const norm = (level || '').toLowerCase()
  let variant: 'low' | 'moderate' | 'high' | 'info' | 'neutral' = 'neutral'
  let icon = <HelpCircle className="w-3.5 h-3.5" />
  let label = level

  if (norm.includes('low')) {
    variant = 'low'
    icon = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
    label = 'Low Support Needed'
  } else if (norm.includes('mod')) {
    variant = 'moderate'
    icon = <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
    label = 'Moderate Support'
  } else if (norm.includes('high')) {
    variant = 'high'
    icon = <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
    label = 'High Priority Support'
  } else if (norm.includes('need') || norm.includes('data')) {
    variant = 'info'
    icon = <HelpCircle className="w-3.5 h-3.5 text-blue-600" />
    label = 'Needs More Data'
  }

  return (
    <Badge variant={variant} className={`font-semibold py-1 px-3 gap-1.5 text-xs ${className || ''}`}>
      {showIcon && icon}
      <span>{label}</span>
    </Badge>
  )
}
