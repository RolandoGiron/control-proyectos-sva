/**
 * Project Service - Servicio para gestión de proyectos
 */
import apiClient from './api';
import { Project, ProjectWithStats, ProjectCreate, ProjectUpdate } from '../types/api';

const projectService = {
  /**
   * Obtener todos los proyectos del usuario
   */
  getAll: async (includeArchived: boolean = false): Promise<Project[]> => {
    const params = includeArchived ? '?include_archived=true' : '';
    const response = await apiClient.get<Project[]>(`/projects${params}`);
    return response.data;
  },

  /**
   * Obtener proyectos con estadísticas de tareas
   */
  getAllWithStats: async (includeArchived: boolean = false): Promise<ProjectWithStats[]> => {
    const params = includeArchived ? '?include_archived=true' : '';
    const response = await apiClient.get<ProjectWithStats[]>(`/projects/with-stats${params}`);
    return response.data;
  },

  /**
   * Obtener un proyecto por ID
   */
  getById: async (id: string): Promise<Project> => {
    const response = await apiClient.get<Project>(`/projects/${id}`);
    return response.data;
  },

  /**
   * Crear un nuevo proyecto
   */
  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post<Project>('/projects', data);
    return response.data;
  },

  /**
   * Actualizar un proyecto
   */
  update: async (id: string, data: ProjectUpdate): Promise<Project> => {
    const response = await apiClient.put<Project>(`/projects/${id}`, data);
    return response.data;
  },

  /**
   * Eliminar un proyecto
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/projects/${id}`);
  },

  /**
   * Archivar un proyecto
   */
  archive: async (id: string): Promise<Project> => {
    const response = await apiClient.patch<Project>(`/projects/${id}/archive`);
    return response.data;
  },

  /**
   * Desarchivar un proyecto
   */
  unarchive: async (id: string): Promise<Project> => {
    const response = await apiClient.patch<Project>(`/projects/${id}/unarchive`);
    return response.data;
  },
};

export default projectService;
