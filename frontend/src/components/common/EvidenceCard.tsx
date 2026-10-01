import React from 'react'
import { Card, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { AlertCircle, CheckCircle, Info } from 'lucide-react'
import { cn } from '../../lib/utils'

export interface EvidenceCardProps {
  indicator: string
  value: string
  direction: 'concern' | 'positive' | 'neutral'
  category?: string
  threshold?: string
  source?: string
  className?: string
}

export function EvidenceCard({
  indicator,
  value,
  direction,
  category,
  threshold,
  source,
  className,
}: EvidenceCardProps) {
  const isConcern = direction === 'concern'
  const isPositive = direction === 'positive'

  const borderClass = isConcern
    ? 'border-l-4 border-l-rose-500'
    : isPositive
    ? 'border-l-4 border-l-emerald-500'
    : 'border-l-4 border-l-slate-300'

  const badgeVariant = isConcern ? 'high' : isPositive ? 'low' : 'neutral'
  const badgeLabel = isConcern ? 'Attention Area' : isPositive ? 'Healthy Marker' : 'Contextual Note'

  return (
    <Card className={cn('bg-white border border-slate-200/90 shadow-xs p-0 overflow-hidden', borderClass, className)}>
      <CardContent className="p-4 sm:p-5">
        <div className="flex items-start justify-between gap-3 mb-2">
          <div>
            {category && (
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-0.5">
                {category}
              </span>
            )}
            <h4 className="text-sm sm:text-base font-semibold text-slate-900 leading-snug">{indicator}</h4>
          </div>
          <Badge variant={badgeVariant} className="text-[11px] shrink-0">
            {isConcern ? (
              <AlertCircle className="w-3 h-3 mr-1" />
            ) : isPositive ? (
              <CheckCircle className="w-3 h-3 mr-1" />
            ) : (
              <Info className="w-3 h-3 mr-1" />
            )}
            {badgeLabel}
          </Badge>
        </div>

        <div className="text-lg font-bold text-slate-800 my-2">{value}</div>

        <div className="text-xs text-slate-500 space-y-1 pt-1 border-t border-slate-100">
          {threshold && (
            <div>
              <span className="font-medium text-slate-600">Threshold:</span> {threshold}
            </div>
          )}
          {source && (
            <div className="truncate">
              <span className="font-medium text-slate-600">Traceability:</span>{' '}
              <span className="text-slate-500 italic">{source}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
