import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import MainLayout from '../components/Layout/MainLayout';
import projectService from '../services/projectService';
import taskService from '../services/taskService';
import { Project, Task } from '../types/api';
import Badge from '../components/common/Badge';
import { useNavigate } from 'react-router-dom';

interface DashboardStats {
  totalProjects: number;
  pendingTasks: number;
  inProgressTasks: number;
  completedTasks: number;
  overdueTasks: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats] = useState<DashboardStats>({
    totalProjects: 0,
    pendingTasks: 0,
    inProgressTasks: 0,
    completedTasks: 0,
    overdueTasks: 0,
  });
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [upcomingTasks, setUpcomingTasks] = useState<Task[]>([]);
  const [overdueTasks, setOverdueTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [projects, allTasks] = await Promise.all([
        projectService.getAll(),
        taskService.getAll(),
      ]);

      // Calculate stats
      const now = new Date();
      const pendingTasks = allTasks.filter((t: Task) => t.status === 'sin_empezar');
      const inProgressTasks = allTasks.filter((t: Task) => t.status === 'en_curso');
      const completedTasks = allTasks.filter((t: Task) => t.status === 'completado');
      const overdue = allTasks.filter((t: Task) => {
        if (t.status === 'completado' || !t.deadline) return false;
        return new Date(t.deadline) < now;
      });

      setStats({
        totalProjects: projects.length,
        pendingTasks: pendingTasks.length,
        inProgressTasks: inProgressTasks.length,
        completedTasks: completedTasks.length,
        overdueTasks: overdue.length,
      });

      // Recent projects (last 5, not archived)
      const activeProjects = projects
        .filter((p: Project) => !p.is_archived)
        .sort((a: Project, b: Project) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, 5);
      setRecentProjects(activeProjects);

      // Upcoming tasks (incomplete with nearest deadline)
      const incompleteTasks = allTasks.filter((t: Task) => t.status !== 'completado');
      const tasksWithDeadline = incompleteTasks.filter((t: Task) => t.deadline);
      const sortedTasks = tasksWithDeadline
        .sort((a: Task, b: Task) => {
          if (!a.deadline || !b.deadline) return 0;
          return new Date(a.deadline).getTime() - new Date(b.deadline).getTime();
        })
        .slice(0, 5);
      setUpcomingTasks(sortedTasks);

      // Overdue tasks (incomplete with past deadline, sorted by oldest first)
      const overdueTasksList = overdue
        .sort((a: Task, b: Task) => {
          if (!a.deadline || !b.deadline) return 0;
          return new Date(a.deadline).getTime() - new Date(b.deadline).getTime();
        })
        .slice(0, 5);
      setOverdueTasks(overdueTasksList);
    } catch (err: any) {
      console.error('Error loading dashboard:', err);
      setError(err.response?.data?.detail || 'Error al cargar el dashboard');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return 'Vencido';
    } else if (diffDays === 0) {
      return 'Hoy';
    } else if (diffDays === 1) {
      return 'Mañana';
    } else if (diffDays <= 7) {
      return `En ${diffDays} días`;
    }

    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
    });
  };

  const getDeadlineColor = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return 'text-red-600';
    if (diffDays <= 1) return 'text-orange-600';
    if (diffDays <= 3) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const statsCards = [
    {
      title: 'Proyectos Activos',
      value: stats.totalProjects.toString(),
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
      ),
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600',
      borderColor: 'border-blue-200',
      path: '/projects',
    },
    {
      title: 'Tareas Vencidas',
      value: stats.overdueTasks.toString(),
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      bgColor: 'bg-red-50',
      textColor: 'text-red-600',
      borderColor: 'border-red-200',
      path: '/tasks?overdue=true',
    },
    {
      title: 'Tareas Pendientes',
      value: stats.pendingTasks.toString(),
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-600',
      borderColor: 'border-yellow-200',
      path: '/tasks?status=sin_empezar',
    },
    {
      title: 'En Progreso',
      value: stats.inProgressTasks.toString(),
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      ),
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600',
      borderColor: 'border-purple-200',
      path: '/tasks?status=en_curso',
    },
    {
      title: 'Completadas',
      value: stats.completedTasks.toString(),
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      bgColor: 'bg-green-50',
      textColor: 'text-green-600',
      borderColor: 'border-green-200',
      path: '/tasks?status=completado',
    },
  ];

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <svg className="animate-spin h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Welcome section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-3xl font-bold text-gray-900">
            ¡Bienvenido, {user?.full_name}! 👋
          </h1>
          <p className="text-gray-600 mt-2">
            Este es tu panel de control. Aquí puedes ver el resumen de tus proyectos y tareas.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Stats cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {statsCards.map((stat, index) => (
            <div
              key={index}
              className={`${stat.bgColor} border ${stat.borderColor} rounded-lg p-6 transition-transform hover:scale-105 cursor-pointer`}
              onClick={() => navigate(stat.path)}
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Proyectos recientes */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Proyectos Recientes
              </h2>
              <button
                onClick={() => navigate('/projects')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Ver todos →
              </button>
            </div>
            <div className="space-y-3">
              {recentProjects.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                  <p>No tienes proyectos aún</p>
                  <button
                    onClick={() => navigate('/projects')}
                    className="text-blue-600 hover:text-blue-700 text-sm mt-2 inline-block"
                  >
                    Crear tu primer proyecto
                  </button>
                </div>
              ) : (
                recentProjects.map((project) => (
                  <div
                    key={project.id}
                    onClick={() => navigate('/projects')}
                    className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
                  >
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <span className="text-2xl flex-shrink-0">
                        {project.emoji_icon || '📁'}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-gray-900 truncate">
                          {project.name}
                        </p>
                        {project.description && (
                          <p className="text-sm text-gray-500 truncate">
                            {project.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <svg className="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Tareas próximas */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Próximas Tareas
              </h2>
              <button
                onClick={() => navigate('/tasks')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Ver todas →
              </button>
            </div>
            <div className="space-y-3">
              {upcomingTasks.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <p>No tienes tareas pendientes</p>
                  <button
                    onClick={() => navigate('/tasks')}
                    className="text-blue-600 hover:text-blue-700 text-sm mt-2 inline-block"
                  >
                    Crear tu primera tarea
                  </button>
                </div>
              ) : (
                upcomingTasks.map((task) => (
                  <div
                    key={task.id}
                    onClick={() => navigate('/tasks')}
                    className="p-3 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors border border-gray-100"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <p className="font-medium text-gray-900 flex-1 pr-2">
                        {task.title}
                      </p>
                      {task.deadline && (
                        <span className={`text-xs font-medium flex-shrink-0 ${getDeadlineColor(task.deadline)}`}>
                          {formatDate(task.deadline)}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="status" value={task.status} />
                      <Badge variant="priority" value={task.priority} />
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Tareas vencidas */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                Tareas Vencidas
                {stats.overdueTasks > 0 && (
                  <span className="bg-red-100 text-red-700 text-xs font-bold px-2 py-1 rounded-full">
                    {stats.overdueTasks}
                  </span>
                )}
              </h2>
              <button
                onClick={() => navigate('/tasks')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Ver todas →
              </button>
            </div>
            <div className="space-y-3">
              {overdueTasks.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <svg className="w-12 h-12 mx-auto mb-3 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-green-600 font-medium">¡Excelente!</p>
                  <p className="text-sm">No tienes tareas vencidas</p>
                </div>
              ) : (
                overdueTasks.map((task) => (
                  <div
                    key={task.id}
                    onClick={() => navigate('/tasks')}
                    className="p-3 hover:bg-red-50 rounded-lg cursor-pointer transition-colors border border-red-200 bg-red-50"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <p className="font-medium text-gray-900 flex-1 pr-2">
                        {task.title}
                      </p>
                      {task.deadline && (
                        <span className="text-xs font-medium flex-shrink-0 text-red-600">
                          {formatDate(task.deadline)}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="status" value={task.status} />
                      <Badge variant="priority" value={task.priority} />
                    </div>
                  </div>
                ))
              )}
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
              <label className="text-sm font-medium text-gray-500">Email</label>
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
              <label className="text-sm font-medium text-gray-500">Estado</label>
              <div className="mt-1">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${user?.is_active
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
