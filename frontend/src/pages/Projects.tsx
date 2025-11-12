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
import areaService from '../services/areaService';
import { ProjectWithStats, Area } from '../types/api';
import { FolderKanban, Plus, Loader } from 'lucide-react';

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<ProjectWithStats[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<ProjectWithStats[]>([]);
  const [areas, setAreas] = useState<Area[]>([]);
  const [selectedAreaId, setSelectedAreaId] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState<ProjectWithStats | null>(null);
  const [error, setError] = useState<string>('');

  // Cargar proyectos y áreas al montar el componente
  useEffect(() => {
    loadProjects();
    loadAreas();
  }, []);

  // Filtrar proyectos cuando cambia el área seleccionada
  useEffect(() => {
    if (selectedAreaId === 'all') {
      setFilteredProjects(projects);
    } else if (selectedAreaId === 'none') {
      setFilteredProjects(projects.filter((p) => !p.area_id));
    } else {
      setFilteredProjects(projects.filter((p) => p.area_id === selectedAreaId));
    }
  }, [selectedAreaId, projects]);

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

  const loadAreas = async () => {
    try {
      const data = await areaService.getAll(true); // Solo áreas activas
      setAreas(data);
    } catch (err: any) {
      console.error('Error loading areas:', err);
    }
  };

  const handleCreate = async (data: {
    name: string;
    description?: string;
    emoji_icon?: string;
    area_id?: string | null;
  }) => {
    await projectService.create(data);
    await loadProjects();
    setShowCreateModal(false);
  };

  const handleEdit = async (data: {
    name: string;
    description?: string;
    emoji_icon?: string;
    area_id?: string | null;
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

        {/* Area Filter */}
        {areas.length > 0 && (
          <div className="flex items-center gap-3">
            <label className="text-sm font-medium text-gray-700">
              Filtrar por área:
            </label>
            <select
              value={selectedAreaId}
              onChange={(e) => setSelectedAreaId(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Todas las áreas</option>
              <option value="none">Sin área</option>
              {areas.map((area) => (
                <option key={area.id} value={area.id}>
                  {area.icon} {area.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
        )}

        {/* Projects grid */}
        {!loading && filteredProjects.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
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

        {/* Empty state - No projects match filter */}
        {!loading && projects.length > 0 && filteredProjects.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm p-12">
            <div className="text-center">
              <FolderKanban className="w-16 h-16 mx-auto text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No hay proyectos en esta área
              </h3>
              <p className="text-gray-600 mb-6">
                Cambia el filtro para ver proyectos de otras áreas
              </p>
            </div>
          </div>
        )}

        {/* Empty state - No projects at all */}
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
