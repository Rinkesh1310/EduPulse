import React from 'react'
import { Card, CardContent } from '../ui/Card'
import { StatusBadge } from './StatusBadge'
import { ArrowUpRight, ArrowDownRight, Minus, LucideIcon } from 'lucide-react'
import { cn } from '../../lib/utils'

export interface MetricCardProps {
  title: string
  value: string
  subtext?: string
  statusLevel?: string
  trend?: 'Stable' | 'Attention' | 'Improving' | 'Declining' | string
  icon?: LucideIcon
  onClick?: () => void
  className?: string
}

export function MetricCard({
  title,
  value,
  subtext,
  statusLevel,
  trend,
  icon: Icon,
  onClick,
  className,
}: MetricCardProps) {
  return (
    <Card
      onClick={onClick}
      className={cn(
        'relative overflow-hidden border border-slate-200/90 bg-white transition-all',
        onClick && 'cursor-pointer hover:border-blue-400 hover:shadow-md hover:-translate-y-0.5',
        className
      )}
    >
      <CardContent className="p-5">
        <div className="flex items-center justify-between gap-2 mb-2">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">{title}</span>
          <div className="flex items-center gap-1.5">
            {statusLevel && <StatusBadge level={statusLevel} showIcon={false} className="text-[10px] py-0 px-2" />}
            {Icon && <Icon className="w-4 h-4 text-slate-400" />}
          </div>
        </div>

        <div className="flex items-baseline justify-between mt-1 mb-1.5">
          <div className="text-2xl font-extrabold tracking-tight text-slate-900">{value}</div>
          {trend && (
            <div
              className={cn(
                'inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-md gap-0.5',
                trend === 'Stable' || trend === 'Improving'
                  ? 'bg-emerald-50 text-emerald-700'
                  : 'bg-amber-50 text-amber-700'
              )}
            >
              {trend === 'Improving' ? (
                <ArrowUpRight className="w-3.5 h-3.5" />
              ) : trend === 'Declining' || trend === 'Attention' ? (
                <ArrowDownRight className="w-3.5 h-3.5" />
              ) : (
                <Minus className="w-3 h-3" />
              )}
              <span>{trend}</span>
            </div>
          )}
        </div>

        {subtext && <p className="text-xs text-slate-500 font-normal line-clamp-1">{subtext}</p>}
      </CardContent>
    </Card>
  )
}
