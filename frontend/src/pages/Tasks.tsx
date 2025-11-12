import React, { useState, useEffect } from 'react';
import MainLayout from '../components/Layout/MainLayout';
import { Task, Project, TaskCreate, TaskUpdate } from '../types/api';
import taskService from '../services/taskService';
import projectService from '../services/projectService';
import TaskCard from '../components/Tasks/TaskCard';
import TaskForm from '../components/Tasks/TaskForm';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Select from '../components/common/Select';

type ViewMode = 'list' | 'kanban';

const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // View mode
  const [viewMode, setViewMode] = useState<ViewMode>('list');

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [filterProject, setFilterProject] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterPriority, setFilterPriority] = useState('');

  // Modals
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadTasks();
  }, [filterProject, filterStatus, filterPriority]);

  const loadData = async () => {
    try {
      setLoading(true);
      await Promise.all([loadProjects(), loadTasks()]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };

  const loadProjects = async () => {
    try {
      const data = await projectService.getAll();
      setProjects(data);
    } catch (err: any) {
      console.error('Error loading projects:', err);
    }
  };

  const loadTasks = async () => {
    try {
      const filters: any = {};
      if (filterProject) filters.project_id = filterProject;
      if (filterStatus) filters.status = filterStatus;
      if (filterPriority) filters.priority = filterPriority;

      const data = await taskService.getAll(filters);
      setTasks(data);
    } catch (err: any) {
      console.error('Error loading tasks:', err);
      setError(err.response?.data?.detail || 'Error al cargar tareas');
    }
  };

  const handleCreateTask = async (data: TaskCreate) => {
    await taskService.create(data);
    setIsCreateModalOpen(false);
    await loadTasks();
  };

  const handleUpdateTask = async (data: TaskUpdate) => {
    if (!selectedTask) return;
    await taskService.update(selectedTask.id, data);
    setIsEditModalOpen(false);
    setSelectedTask(null);
    await loadTasks();
  };

  const handleDeleteTask = async () => {
    if (!selectedTask) return;
    try {
      await taskService.delete(selectedTask.id);
      setIsDeleteModalOpen(false);
      setSelectedTask(null);
      await loadTasks();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar tarea');
    }
  };

  const handleCompleteTask = async (task: Task) => {
    try {
      await taskService.complete(task.id);
      await loadTasks();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al completar tarea');
    }
  };

  const openEditModal = (task: Task) => {
    setSelectedTask(task);
    setIsEditModalOpen(true);
  };

  const openDeleteModal = (task: Task) => {
    setSelectedTask(task);
    setIsDeleteModalOpen(true);
  };

  const getProjectById = (projectId: string): Project | undefined => {
    return projects.find((p) => p.id === projectId);
  };

  // Filter tasks by search term
  const filteredTasks = tasks.filter((task) => {
    if (!searchTerm.trim()) return true;
    const search = searchTerm.toLowerCase();
    return (
      task.title.toLowerCase().includes(search) ||
      task.description?.toLowerCase().includes(search)
    );
  });

  // Group tasks by status for Kanban view
  const tasksByStatus = {
    sin_empezar: filteredTasks.filter((t) => t.status === 'sin_empezar'),
    en_curso: filteredTasks.filter((t) => t.status === 'en_curso'),
    completado: filteredTasks.filter((t) => t.status === 'completado'),
  };

  const statusOptions = [
    { value: '', label: 'Todos los estados' },
    { value: 'sin_empezar', label: 'Sin Empezar' },
    { value: 'en_curso', label: 'En Curso' },
    { value: 'completado', label: 'Completado' },
  ];

  const priorityOptions = [
    { value: '', label: 'Todas las prioridades' },
    { value: 'baja', label: 'Baja' },
    { value: 'media', label: 'Media' },
    { value: 'alta', label: 'Alta' },
  ];

  const projectOptions = [
    { value: '', label: 'Todos los proyectos' },
    ...projects.map((p) => ({
      value: p.id,
      label: `${p.emoji_icon || '📁'} ${p.name}`,
    })),
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
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Tareas</h1>
            <p className="text-gray-600 mt-2">
              {filteredTasks.length} {filteredTasks.length === 1 ? 'tarea' : 'tareas'}
            </p>
          </div>
          <Button
            variant="primary"
            onClick={() => setIsCreateModalOpen(true)}
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Nueva Tarea
          </Button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Filters and View Toggle */}
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Buscar tareas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 lg:w-auto">
              <Select
                value={filterProject}
                onChange={setFilterProject}
                options={projectOptions}
                placeholder="Proyecto"
              />
              <Select
                value={filterStatus}
                onChange={setFilterStatus}
                options={statusOptions}
                placeholder="Estado"
              />
              <Select
                value={filterPriority}
                onChange={setFilterPriority}
                options={priorityOptions}
                placeholder="Prioridad"
              />
            </div>

            {/* View Toggle */}
            <div className="flex border border-gray-300 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 text-sm font-medium ${
                  viewMode === 'list'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
                title="Vista Lista"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <button
                onClick={() => setViewMode('kanban')}
                className={`px-4 py-2 text-sm font-medium border-l border-gray-300 ${
                  viewMode === 'kanban'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
                title="Vista Kanban"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        {filteredTasks.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12">
            <div className="text-center">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No hay tareas
              </h3>
              <p className="text-gray-600 mb-6">
                {searchTerm || filterProject || filterStatus || filterPriority
                  ? 'No se encontraron tareas con los filtros aplicados'
                  : 'Crea tu primera tarea para comenzar a organizarte'}
              </p>
              <Button
                variant="primary"
                onClick={() => setIsCreateModalOpen(true)}
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Crear Primera Tarea
              </Button>
            </div>
          </div>
        ) : (
          <>
            {/* List View */}
            {viewMode === 'list' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    project={getProjectById(task.project_id)}
                    onEdit={openEditModal}
                    onDelete={openDeleteModal}
                    onComplete={handleCompleteTask}
                  />
                ))}
              </div>
            )}

            {/* Kanban View */}
            {viewMode === 'kanban' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Sin Empezar Column */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">Sin Empezar</h3>
                    <span className="bg-gray-200 text-gray-700 text-sm px-2 py-1 rounded-full">
                      {tasksByStatus.sin_empezar.length}
                    </span>
                  </div>
                  <div className="space-y-3">
                    {tasksByStatus.sin_empezar.map((task) => (
                      <TaskCard
                        key={task.id}
                        task={task}
                        project={getProjectById(task.project_id)}
                        onEdit={openEditModal}
                        onDelete={openDeleteModal}
                        onComplete={handleCompleteTask}
                      />
                    ))}
                  </div>
                </div>

                {/* En Curso Column */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">En Curso</h3>
                    <span className="bg-blue-200 text-blue-700 text-sm px-2 py-1 rounded-full">
                      {tasksByStatus.en_curso.length}
                    </span>
                  </div>
                  <div className="space-y-3">
                    {tasksByStatus.en_curso.map((task) => (
                      <TaskCard
                        key={task.id}
                        task={task}
                        project={getProjectById(task.project_id)}
                        onEdit={openEditModal}
                        onDelete={openDeleteModal}
                        onComplete={handleCompleteTask}
                      />
                    ))}
                  </div>
                </div>

                {/* Completado Column */}
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">Completado</h3>
                    <span className="bg-green-200 text-green-700 text-sm px-2 py-1 rounded-full">
                      {tasksByStatus.completado.length}
                    </span>
                  </div>
                  <div className="space-y-3">
                    {tasksByStatus.completado.map((task) => (
                      <TaskCard
                        key={task.id}
                        task={task}
                        project={getProjectById(task.project_id)}
                        onEdit={openEditModal}
                        onDelete={openDeleteModal}
                        onComplete={handleCompleteTask}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Create Task Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Crear Nueva Tarea"
        size="lg"
      >
        <TaskForm
          projects={projects}
          onSubmit={handleCreateTask}
          onCancel={() => setIsCreateModalOpen(false)}
        />
      </Modal>

      {/* Edit Task Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedTask(null);
        }}
        title="Editar Tarea"
        size="lg"
      >
        {selectedTask && (
          <TaskForm
            task={selectedTask}
            projects={projects}
            onSubmit={handleUpdateTask}
            onCancel={() => {
              setIsEditModalOpen(false);
              setSelectedTask(null);
            }}
          />
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setSelectedTask(null);
        }}
        title="Eliminar Tarea"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            ¿Estás seguro de que deseas eliminar la tarea{' '}
            <span className="font-semibold">"{selectedTask?.title}"</span>?
          </p>
          <p className="text-sm text-gray-500">
            Esta acción no se puede deshacer.
          </p>
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button
              variant="secondary"
              onClick={() => {
                setIsDeleteModalOpen(false);
                setSelectedTask(null);
              }}
            >
              Cancelar
            </Button>
            <Button variant="danger" onClick={handleDeleteTask}>
              Eliminar
            </Button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
};

export default Tasks;
