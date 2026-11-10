import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  badge?: {
    text: string;
    variant?: 'positive' | 'negative' | 'neutral' | 'warning' | 'info';
  };
  icon: LucideIcon;
  iconColor?: 'blue' | 'indigo' | 'emerald' | 'amber' | 'rose' | 'purple' | 'cyan';
  className?: string;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  subtitle,
  badge,
  icon: Icon,
  iconColor = 'blue',
  className = '',
}) => {
  const iconColorStyles = {
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    indigo: 'bg-indigo-50 text-indigo-600 border-indigo-100',
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    rose: 'bg-rose-50 text-rose-600 border-rose-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
    cyan: 'bg-cyan-50 text-cyan-600 border-cyan-100',
  };

  const badgeStyles = {
    positive: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    negative: 'bg-rose-50 text-rose-700 border-rose-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  return (
    <div className={`bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 hover:shadow-md transition-shadow relative overflow-hidden ${className}`}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
          <div className="text-2xl font-bold text-slate-900 tracking-tight">{value}</div>
          <div className="flex items-center space-x-2 pt-1">
            {badge && (
              <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold border ${badgeStyles[badge.variant || 'neutral']}`}>
                {badge.text}
              </span>
            )}
            {subtitle && (
              <span className="text-xs text-slate-500">{subtitle}</span>
            )}
          </div>
        </div>
        <div className={`p-3 rounded-xl border ${iconColorStyles[iconColor]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
};
