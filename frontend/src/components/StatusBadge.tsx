import React from 'react';

export type StatusVariant =
  | 'Critical'
  | 'High'
  | 'Medium'
  | 'Low'
  | 'Feasible'
  | 'Infeasible'
  | 'Unknown'
  | 'Approved'
  | 'Rejected'
  | 'Pending'
  | 'Received'
  | 'Delayed'
  | 'Cancelled'
  | 'Completed'
  | 'InProgress'
  | 'Planned'
  | 'Mitigated'
  | 'Open'
  | 'Active'
  | 'Flagged'
  | 'Resolved'
  | 'Detected'
  | string;

interface StatusBadgeProps {
  status: StatusVariant;
  withDot?: boolean;
  className?: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  withDot = true,
  className = '',
  size = 'md',
}) => {
  const normalized = (status || '').toLowerCase();

  let style = 'bg-slate-100 text-slate-700 border-slate-200';
  let dotColor = 'bg-slate-400';

  if (['critical', 'infeasible', 'cancelled', 'delayed', 'rejected'].includes(normalized)) {
    style = 'bg-rose-50 text-rose-700 border-rose-200';
    dotColor = 'bg-rose-500';
  } else if (['high', 'warning', 'flagged'].includes(normalized)) {
    style = 'bg-orange-50 text-orange-700 border-orange-200';
    dotColor = 'bg-orange-500';
  } else if (['medium', 'inprogress', 'pending', 'planned'].includes(normalized)) {
    style = 'bg-amber-50 text-amber-700 border-amber-200';
    dotColor = 'bg-amber-500';
  } else if (['feasible', 'approved', 'received', 'completed', 'mitigated', 'active', 'resolved'].includes(normalized)) {
    style = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    dotColor = 'bg-emerald-500';
  } else if (['low', 'info', 'open', 'detected'].includes(normalized)) {
    style = 'bg-blue-50 text-blue-700 border-blue-200';
    dotColor = 'bg-blue-500';
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center space-x-1.5 font-medium rounded-md border ${sizeClasses} ${style} ${className}`}
    >
      {withDot && <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />}
      <span className="capitalize">{status}</span>
    </span>
  );
};
