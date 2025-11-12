/**
 * ProjectCard - Tarjeta de proyecto con estadísticas
 */
import React, { useState } from 'react';
import { MoreVertical, Edit2, Trash2, Archive, ArchiveRestore } from 'lucide-react';
import { ProjectWithStats } from '../../types/api';
import { Link } from 'react-router-dom';
import AreaBadge from '../Areas/AreaBadge';

interface ProjectCardProps {
  project: ProjectWithStats;
  onEdit: (project: ProjectWithStats) => void;
  onDelete: (project: ProjectWithStats) => void;
  onArchive: (project: ProjectWithStats) => void;
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onEdit,
  onDelete,
  onArchive,
}) => {
  const [showMenu, setShowMenu] = useState(false);

  const completionPercentage =
    project.total_tasks > 0
      ? Math.round((project.completed_tasks / project.total_tasks) * 100)
      : 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <span className="text-3xl">{project.emoji_icon || '📁'}</span>
            <div>
              <Link
                to={`/projects/${project.id}`}
                className="text-lg font-semibold text-gray-900 hover:text-blue-600"
              >
                {project.name}
              </Link>
              {project.is_archived && (
                <span className="ml-2 text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                  Archivado
                </span>
              )}
            </div>
          </div>

          {/* Menu dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="text-gray-400 hover:text-gray-600 p-1"
            >
              <MoreVertical className="w-5 h-5" />
            </button>

            {showMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowMenu(false)}
                />
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                  <button
                    onClick={() => {
                      onEdit(project);
                      setShowMenu(false);
                    }}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Edit2 className="w-4 h-4" />
                    <span>Editar</span>
                  </button>

                  <button
                    onClick={() => {
                      onArchive(project);
                      setShowMenu(false);
                    }}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    {project.is_archived ? (
                      <>
                        <ArchiveRestore className="w-4 h-4" />
                        <span>Desarchivar</span>
                      </>
                    ) : (
                      <>
                        <Archive className="w-4 h-4" />
                        <span>Archivar</span>
                      </>
                    )}
                  </button>

                  <div className="border-t border-gray-200 my-1" />

                  <button
                    onClick={() => {
                      onDelete(project);
                      setShowMenu(false);
                    }}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Eliminar</span>
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Area Badge */}
        {project.area && (
          <div className="mb-3">
            <AreaBadge
              name={project.area.name}
              color={project.area.color}
              icon={project.area.icon}
              size="sm"
            />
          </div>
        )}

        {/* Description */}
        {project.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {project.description}
          </p>
        )}

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">
              {project.total_tasks}
            </p>
            <p className="text-xs text-gray-500">Total</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">
              {project.in_progress_tasks}
            </p>
            <p className="text-xs text-gray-500">En curso</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">
              {project.completed_tasks}
            </p>
            <p className="text-xs text-gray-500">Completas</p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <span>Progreso</span>
            <span className="font-medium">{completionPercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectCard;
