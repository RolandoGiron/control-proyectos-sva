/**
 * Projects Page - Página de gestión de proyectos
 */
import React, { useState, useEffect } from 'react';
import MainLayout from '../components/Layout/MainLayout';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import ProjectForm from '../components/Projects/ProjectForm';
import ProjectCard from '../components/Projects/ProjectCard';
import projectService from '../services/projectService';
import { ProjectWithStats } from '../types/api';
import { FolderKanban, Plus, Loader } from 'lucide-react';

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<ProjectWithStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState<ProjectWithStats | null>(null);
  const [error, setError] = useState<string>('');

  // Cargar proyectos al montar el componente
  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await projectService.getAllWithStats();
      setProjects(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar proyectos');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (data: {
    name: string;
    description?: string;
    emoji_icon?: string;
  }) => {
    await projectService.create(data);
    await loadProjects();
    setShowCreateModal(false);
  };

  const handleEdit = async (data: {
    name: string;
    description?: string;
    emoji_icon?: string;
  }) => {
    if (!selectedProject) return;
    await projectService.update(selectedProject.id, data);
    await loadProjects();
    setShowEditModal(false);
    setSelectedProject(null);
  };

  const handleDelete = async () => {
    if (!selectedProject) return;
    try {
      await projectService.delete(selectedProject.id);
      await loadProjects();
      setShowDeleteModal(false);
      setSelectedProject(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar proyecto');
    }
  };

  const handleArchive = async (project: ProjectWithStats) => {
    try {
      if (project.is_archived) {
        await projectService.unarchive(project.id);
      } else {
        await projectService.archive(project.id);
      }
      await loadProjects();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al archivar proyecto');
    }
  };

  const openEditModal = (project: ProjectWithStats) => {
    setSelectedProject(project);
    setShowEditModal(true);
  };

  const openDeleteModal = (project: ProjectWithStats) => {
    setSelectedProject(project);
    setShowDeleteModal(true);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Proyectos</h1>
            <p className="text-gray-600 mt-2">
              Gestiona tus proyectos y organiza tus tareas
            </p>
          </div>
          <Button
            variant="primary"
            onClick={() => setShowCreateModal(true)}
          >
            <Plus className="w-5 h-5 mr-2" />
            Nuevo Proyecto
          </Button>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
        )}

        {/* Projects grid */}
        {!loading && projects.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onEdit={openEditModal}
                onDelete={openDeleteModal}
                onArchive={handleArchive}
              />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && projects.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm p-12">
            <div className="text-center">
              <FolderKanban className="w-16 h-16 mx-auto text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No hay proyectos todavía
              </h3>
              <p className="text-gray-600 mb-6">
                Comienza creando tu primer proyecto para organizar tus tareas
              </p>
              <Button
                variant="primary"
                onClick={() => setShowCreateModal(true)}
              >
                <Plus className="w-5 h-5 mr-2" />
                Crear Primer Proyecto
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Modal crear proyecto */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Crear Nuevo Proyecto"
      >
        <ProjectForm
          onSubmit={handleCreate}
          onCancel={() => setShowCreateModal(false)}
        />
      </Modal>

      {/* Modal editar proyecto */}
      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedProject(null);
        }}
        title="Editar Proyecto"
      >
        <ProjectForm
          project={selectedProject || undefined}
          onSubmit={handleEdit}
          onCancel={() => {
            setShowEditModal(false);
            setSelectedProject(null);
          }}
        />
      </Modal>

      {/* Modal confirmar eliminación */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setSelectedProject(null);
        }}
        title="Eliminar Proyecto"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            ¿Estás seguro de que deseas eliminar el proyecto{' '}
            <span className="font-semibold">{selectedProject?.name}</span>?
          </p>
          <p className="text-sm text-red-600">
            Esta acción no se puede deshacer y eliminará todas las tareas
            asociadas.
          </p>
          <div className="flex items-center justify-end space-x-3 pt-4">
            <Button
              variant="ghost"
              onClick={() => {
                setShowDeleteModal(false);
                setSelectedProject(null);
              }}
            >
              Cancelar
            </Button>
            <Button variant="danger" onClick={handleDelete}>
              Eliminar Proyecto
            </Button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
};

export default Projects;
