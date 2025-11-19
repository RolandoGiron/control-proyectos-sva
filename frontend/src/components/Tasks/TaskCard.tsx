import React, { useState, useRef, useEffect } from 'react';
import { Task, Project } from '../../types/api';
import Badge from '../common/Badge';
import AreaBadge from '../Areas/AreaBadge';

interface TaskCardProps {
  task: Task;
  project?: Project;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
  onComplete: (task: Task) => void;
  className?: string;
}

const TaskCard: React.FC<TaskCardProps> = ({
  task,
  project,
  onEdit,
  onDelete,
  onComplete,
  className = '',
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isMenuOpen]);

  const formatDate = (dateString?: string): string => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    // Format date
    const formatted = date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });

    // Add urgency indicator
    if (diffDays < 0) {
      return `${formatted} (Vencido)`;
    } else if (diffDays === 0) {
      return `${formatted} (Hoy)`;
    } else if (diffDays === 1) {
      return `${formatted} (Mañana)`;
    } else if (diffDays <= 3) {
      return `${formatted} (${diffDays} días)`;
    }

    return formatted;
  };

  const getDeadlineColor = (dateString?: string): string => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return 'text-red-600';
    if (diffDays <= 1) return 'text-orange-600';
    if (diffDays <= 3) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const handleMenuToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsMenuOpen(!isMenuOpen);
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsMenuOpen(false);
    onEdit(task);
  };

  const handleComplete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsMenuOpen(false);
    onComplete(task);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsMenuOpen(false);
    onDelete(task);
  };

  const isCompleted = task.status === 'completado';

  return (
    <div
      className={`
        bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow
        ${isCompleted ? 'opacity-75' : ''}
        ${className}
      `}
      onClick={() => onEdit(task)}
    >
      {/* Header with project name and menu */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 min-w-0 flex-1">
          {project && (
            <span className="text-2xl flex-shrink-0" title={project.name}>
              {project.emoji_icon || '📁'}
            </span>
          )}
          <span className="text-sm font-semibold text-gray-700 truncate">
            {project?.name || 'Sin proyecto'}
          </span>
        </div>
        <div className="relative" ref={menuRef}>
          <button
            onClick={handleMenuToggle}
            className="text-gray-400 hover:text-gray-600 p-1 -mr-1"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
            </svg>
          </button>

          {isMenuOpen && (
            <div className="absolute right-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
              <button
                onClick={handleEdit}
                className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Editar
              </button>
              {!isCompleted && (
                <button
                  onClick={handleComplete}
                  className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center gap-2 text-green-600"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Completar
                </button>
              )}
              <button
                onClick={handleDelete}
                className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center gap-2 text-red-600 border-t"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Eliminar
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Title */}
      <h3 className={`font-medium text-gray-900 mb-2 ${isCompleted ? 'line-through' : ''}`}>
        {task.title}
      </h3>

      {/* Description (if present) */}
      {task.description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* Badges */}
      <div className="flex flex-wrap gap-2 mb-3">
        <Badge variant="status" value={task.status} />
        <Badge variant="priority" value={task.priority} />
        {project?.area && (
          <AreaBadge
            name={project.area.name}
            color={project.area.color}
            icon={project.area.icon}
            size="sm"
          />
        )}
      </div>

      {/* Footer with responsible and deadline */}
      <div className="flex items-center justify-between text-sm text-gray-500 pt-3 border-t">
        <div className="flex items-center gap-1 min-w-0 flex-1">
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span className="truncate" title={task.responsible_name || 'Sin asignar'}>
            {task.responsible_name || 'Sin asignar'}
          </span>
        </div>
        {task.deadline && (
          <div className={`flex items-center gap-1 flex-shrink-0 ${getDeadlineColor(task.deadline)}`}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-xs">{formatDate(task.deadline)}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskCard;
