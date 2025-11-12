import React from 'react';

type BadgeVariant = 'status' | 'priority';
type StatusValue = 'sin_empezar' | 'en_curso' | 'completado';
type PriorityValue = 'baja' | 'media' | 'alta';

interface BadgeProps {
  variant: BadgeVariant;
  value: StatusValue | PriorityValue;
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({ variant, value, className = '' }) => {
  const getStatusStyles = (status: StatusValue): string => {
    switch (status) {
      case 'sin_empezar':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'en_curso':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'completado':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getPriorityStyles = (priority: PriorityValue): string => {
    switch (priority) {
      case 'baja':
        return 'bg-gray-100 text-gray-700 border-gray-300';
      case 'media':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'alta':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const getStatusLabel = (status: StatusValue): string => {
    switch (status) {
      case 'sin_empezar':
        return 'Sin Empezar';
      case 'en_curso':
        return 'En Curso';
      case 'completado':
        return 'Completado';
      default:
        return status;
    }
  };

  const getPriorityLabel = (priority: PriorityValue): string => {
    switch (priority) {
      case 'baja':
        return 'Baja';
      case 'media':
        return 'Media';
      case 'alta':
        return 'Alta';
      default:
        return priority;
    }
  };

  const styles = variant === 'status'
    ? getStatusStyles(value as StatusValue)
    : getPriorityStyles(value as PriorityValue);

  const label = variant === 'status'
    ? getStatusLabel(value as StatusValue)
    : getPriorityLabel(value as PriorityValue);

  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border
        ${styles}
        ${className}
      `}
    >
      {label}
    </span>
  );
};

export default Badge;
