/**
 * Risk Badge Component
 * Displays risk level with color, icon, and text
 */

import React from 'react';
import { AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react';

interface RiskBadgeProps {
  level: 'LOW' | 'MEDIUM' | 'HIGH';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  size = 'md',
  showLabel = true,
}) => {
  const styles = {
    LOW: {
      bg: 'bg-green-500/20',
      border: 'border-green-500/50',
      text: 'text-green-400',
      icon: <CheckCircle className={getSizeClass(size, 'icon')} />,
      label: 'Low Risk',
    },
    MEDIUM: {
      bg: 'bg-yellow-500/20',
      border: 'border-yellow-500/50',
      text: 'text-yellow-400',
      icon: <AlertCircle className={getSizeClass(size, 'icon')} />,
      label: 'Medium Risk',
    },
    HIGH: {
      bg: 'bg-red-500/20',
      border: 'border-red-500/50',
      text: 'text-red-400',
      icon: <AlertTriangle className={getSizeClass(size, 'icon')} />,
      label: 'High Risk',
    },
  };

  const style = styles[level];
  const sizeClass = getSizeClass(size, 'badge');

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${style.bg} ${style.border} ${sizeClass}`}>
      <div className={style.text}>{style.icon}</div>
      {showLabel && <span className={`font-medium ${style.text}`}>{style.label}</span>}
    </div>
  );
};

function getSizeClass(size: 'sm' | 'md' | 'lg', type: 'badge' | 'icon'): string {
  if (type === 'icon') {
    return {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-6 h-6',
    }[size];
  }
  return {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  }[size];
}
