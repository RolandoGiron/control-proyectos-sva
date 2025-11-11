/**
 * Tasks Page - Página de gestión de tareas
 */
import React from 'react';
import MainLayout from '../components/Layout/MainLayout';
import { CheckSquare, Plus } from 'lucide-react';

const Tasks: React.FC = () => {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Tareas</h1>
            <p className="text-gray-600 mt-2">
              Administra todas tus tareas y haz seguimiento de tu progreso
            </p>
          </div>
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Plus className="w-5 h-5" />
            <span>Nueva Tarea</span>
          </button>
        </div>

        {/* Empty state */}
        <div className="bg-white rounded-lg shadow-sm p-12">
          <div className="text-center">
            <CheckSquare className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No hay tareas todavía
            </h3>
            <p className="text-gray-600 mb-6">
              Crea tu primera tarea para comenzar a organizarte
            </p>
            <button className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <Plus className="w-5 h-5" />
              <span>Crear Primera Tarea</span>
            </button>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Tasks;
