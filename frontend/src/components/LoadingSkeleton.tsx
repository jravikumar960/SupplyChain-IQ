import React from 'react';

interface LoadingSkeletonProps {
  variant?: 'card' | 'table' | 'chart' | 'text';
  rows?: number;
  className?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'card',
  rows = 4,
  className = '',
}) => {
  if (variant === 'card') {
    return (
      <div className={`bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 animate-pulse space-y-4 ${className}`}>
        <div className="flex justify-between items-center">
          <div className="h-4 bg-slate-200 rounded w-1/3" />
          <div className="w-10 h-10 bg-slate-100 rounded-xl" />
        </div>
        <div className="h-8 bg-slate-200 rounded w-1/2" />
        <div className="h-3 bg-slate-100 rounded w-2/3" />
      </div>
    );
  }

  if (variant === 'table') {
    return (
      <div className={`bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden animate-pulse ${className}`}>
        <div className="bg-slate-50 border-b border-slate-200 p-4 flex space-x-4">
          <div className="h-4 bg-slate-200 rounded w-1/4" />
          <div className="h-4 bg-slate-200 rounded w-1/4" />
          <div className="h-4 bg-slate-200 rounded w-1/4" />
          <div className="h-4 bg-slate-200 rounded w-1/4" />
        </div>
        <div className="divide-y divide-slate-100">
          {Array.from({ length: rows }).map((_, i) => (
            <div key={i} className="p-4 flex space-x-4">
              <div className="h-4 bg-slate-100 rounded w-1/4" />
              <div className="h-4 bg-slate-100 rounded w-1/4" />
              <div className="h-4 bg-slate-100 rounded w-1/4" />
              <div className="h-4 bg-slate-100 rounded w-1/4" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (variant === 'chart') {
    return (
      <div className={`bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 animate-pulse space-y-4 ${className}`}>
        <div className="h-5 bg-slate-200 rounded w-1/4" />
        <div className="h-64 bg-slate-50 rounded-xl border border-slate-100 flex items-end p-6 space-x-4">
          <div className="h-1/3 bg-slate-200 rounded w-full" />
          <div className="h-2/3 bg-slate-200 rounded w-full" />
          <div className="h-1/2 bg-slate-200 rounded w-full" />
          <div className="h-4/5 bg-slate-200 rounded w-full" />
          <div className="h-3/4 bg-slate-200 rounded w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className={`animate-pulse space-y-2.5 ${className}`}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-4 bg-slate-200 rounded w-full" />
      ))}
    </div>
  );
};
