import React from 'react'
import { Card, CardContent } from '../ui/Card'
import { ArrowRight, CheckCircle2 } from 'lucide-react'
import { cn } from '../../lib/utils'

export interface ActionCardProps {
  title: string
  items: string[]
  icon?: React.ReactNode
  variant?: 'primary' | 'teal' | 'amber'
  className?: string
}

export function ActionCard({ title, items, icon, variant = 'primary', className }: ActionCardProps) {
  const accentBorder =
    variant === 'teal'
      ? 'border-l-4 border-l-teal-600'
      : variant === 'amber'
      ? 'border-l-4 border-l-amber-500'
      : 'border-l-4 border-l-blue-600'

  const titleColor =
    variant === 'teal' ? 'text-teal-900' : variant === 'amber' ? 'text-amber-900' : 'text-blue-900'

  return (
    <Card className={cn('bg-white border border-slate-200/90 shadow-xs h-full', accentBorder, className)}>
      <CardContent className="p-5">
        <div className="flex items-center gap-2 mb-3">
          {icon}
          <h4 className={cn('text-sm font-bold uppercase tracking-wider', titleColor)}>{title}</h4>
        </div>
        <ul className="space-y-2.5">
          {items.map((action, idx) => (
            <li key={idx} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-700 leading-relaxed">
              <span className="mt-0.5 shrink-0 text-blue-600">
                <CheckCircle2 className="w-4 h-4" />
              </span>
              <span>{action}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
