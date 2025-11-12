/**
 * AreaCard - Tarjeta para mostrar información de un área
 */
import React from 'react';
import { AreaWithStats } from '../../types/api';
import Button from '../common/Button';

interface AreaCardProps {
  area: AreaWithStats;
  onEdit: (area: AreaWithStats) => void;
  onDelete: (area: AreaWithStats) => void;
  isAdmin: boolean;
}

const AreaCard: React.FC<AreaCardProps> = ({ area, onEdit, onDelete, isAdmin }) => {
  return (
    <div
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow"
      style={{ borderLeftColor: area.color, borderLeftWidth: '4px' }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {area.icon && <span className="text-2xl">{area.icon}</span>}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{area.name}</h3>
            {!area.is_active && (
              <span className="text-xs text-gray-500 italic">Inactiva</span>
            )}
          </div>
        </div>
        {isAdmin && (
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={() => onEdit(area)}>
              Editar
            </Button>
            <Button variant="danger" size="sm" onClick={() => onDelete(area)}>
              Eliminar
            </Button>
          </div>
        )}
      </div>

      {/* Description */}
      {area.description && (
        <p className="text-sm text-gray-600 mb-4">{area.description}</p>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
        <div>
          <p className="text-xs text-gray-500 mb-1">Proyectos</p>
          <p className="text-2xl font-bold" style={{ color: area.color }}>
            {area.stats?.total_projects || 0}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Tareas</p>
          <p className="text-2xl font-bold" style={{ color: area.color }}>
            {area.stats?.total_tasks || 0}
          </p>
        </div>
      </div>

      {/* Task breakdown */}
      {area.stats && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <span>Sin empezar: {area.stats.tasks_sin_empezar}</span>
            <span>En curso: {area.stats.tasks_en_curso}</span>
            <span>Completadas: {area.stats.tasks_completado}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AreaCard;
