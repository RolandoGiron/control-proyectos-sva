/**
 * Dashboard Page - Página principal del dashboard con layout
 */
import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import MainLayout from '../components/Layout/MainLayout';
import { FolderKanban, CheckSquare, CheckCircle2, Clock } from 'lucide-react';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  // Stats de ejemplo (en el futuro se obtendrán del backend)
  const stats = [
    {
      title: 'Proyectos Activos',
      value: '0',
      icon: <FolderKanban className="w-8 h-8" />,
      color: 'blue',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600',
      borderColor: 'border-blue-200',
    },
    {
      title: 'Tareas Pendientes',
      value: '0',
      icon: <Clock className="w-8 h-8" />,
      color: 'yellow',
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-600',
      borderColor: 'border-yellow-200',
    },
    {
      title: 'En Progreso',
      value: '0',
      icon: <CheckSquare className="w-8 h-8" />,
      color: 'purple',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600',
      borderColor: 'border-purple-200',
    },
    {
      title: 'Completadas',
      value: '0',
      icon: <CheckCircle2 className="w-8 h-8" />,
      color: 'green',
      bgColor: 'bg-green-50',
      textColor: 'text-green-600',
      borderColor: 'border-green-200',
    },
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Welcome section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-3xl font-bold text-gray-900">
            ¡Bienvenido, {user?.full_name}! 👋
          </h1>
          <p className="text-gray-600 mt-2">
            Este es tu panel de control. Aquí puedes ver el resumen de tus
            proyectos y tareas.
          </p>
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <div
              key={index}
              className={`${stat.bgColor} border ${stat.borderColor} rounded-lg p-6 transition-transform hover:scale-105`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${stat.textColor}`}>
                    {stat.title}
                  </p>
                  <p className={`text-3xl font-bold ${stat.textColor} mt-2`}>
                    {stat.value}
                  </p>
                </div>
                <div className={stat.textColor}>{stat.icon}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Recent activity section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Proyectos recientes */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Proyectos Recientes
              </h2>
              <a
                href="/projects"
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Ver todos →
              </a>
            </div>
            <div className="space-y-3">
              {/* Placeholder cuando no hay proyectos */}
              <div className="text-center py-8 text-gray-500">
                <FolderKanban className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p>No tienes proyectos aún</p>
                <a
                  href="/projects"
                  className="text-blue-600 hover:text-blue-700 text-sm mt-2 inline-block"
                >
                  Crear tu primer proyecto
                </a>
              </div>
            </div>
          </div>

          {/* Tareas recientes */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Tareas Recientes
              </h2>
              <a
                href="/tasks"
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Ver todas →
              </a>
            </div>
            <div className="space-y-3">
              {/* Placeholder cuando no hay tareas */}
              <div className="text-center py-8 text-gray-500">
                <CheckSquare className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p>No tienes tareas pendientes</p>
                <a
                  href="/tasks"
                  className="text-blue-600 hover:text-blue-700 text-sm mt-2 inline-block"
                >
                  Crear tu primera tarea
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* User info card */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Información de la Cuenta
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500">
                Nombre Completo
              </label>
              <p className="text-gray-900 mt-1">{user?.full_name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">
                Email
              </label>
              <p className="text-gray-900 mt-1">{user?.email}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">
                Teléfono
              </label>
              <p className="text-gray-900 mt-1">
                {user?.phone_number || 'No especificado'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">
                Estado
              </label>
              <div className="mt-1">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    user?.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {user?.is_active ? 'Activo' : 'Inactivo'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Dashboard;
