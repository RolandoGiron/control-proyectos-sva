/**
 * AreaBadge - Badge para mostrar áreas con color e ícono
 */
import React from 'react';

interface AreaBadgeProps {
  name: string;
  color: string;
  icon?: string;
  size?: 'sm' | 'md' | 'lg';
}

const AreaBadge: React.FC<AreaBadgeProps> = ({ name, color, icon, size = 'md' }) => {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-medium ${sizeClasses[size]}`}
      style={{
        backgroundColor: `${color}20`,
        color: color,
        border: `1px solid ${color}40`,
      }}
    >
      {icon && <span>{icon}</span>}
      <span>{name}</span>
    </span>
  );
};

export default AreaBadge;
