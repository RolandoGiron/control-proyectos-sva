/**
 * Task Service - Servicio para gestión de tareas
 */
import apiClient from './api';
import {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskStatus,
  TaskPriority,
  TaskStatusUpdate,
} from '../types/api';

interface TaskFilters {
  project_id?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  responsible_id?: string;
  include_archived?: boolean;
  skip?: number;
  limit?: number;
}

const taskService = {
  /**
   * Obtener todas las tareas con filtros opcionales
   */
  getAll: async (filters?: TaskFilters): Promise<Task[]> => {
    const params = new URLSearchParams();

    if (filters?.project_id) params.append('project_id', filters.project_id);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.priority) params.append('priority', filters.priority);
    if (filters?.responsible_id) params.append('responsible_id', filters.responsible_id);
    if (filters?.include_archived !== undefined) params.append('include_archived', filters.include_archived.toString());
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());

    const queryString = params.toString();
    const url = queryString ? `/tasks?${queryString}` : '/tasks';

    const response = await apiClient.get<Task[]>(url);
    return response.data;
  },

  /**
   * Obtener una tarea por ID
   */
  getById: async (id: string): Promise<Task> => {
    const response = await apiClient.get<Task>(`/tasks/${id}`);
    return response.data;
  },

  /**
   * Crear una nueva tarea
   */
  create: async (data: TaskCreate): Promise<Task> => {
    const response = await apiClient.post<Task>('/tasks', data);
    return response.data;
  },

  /**
   * Actualizar una tarea
   */
  update: async (id: string, data: TaskUpdate): Promise<Task> => {
    const response = await apiClient.put<Task>(`/tasks/${id}`, data);
    return response.data;
  },

  /**
   * Eliminar una tarea
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/tasks/${id}`);
  },

  /**
   * Actualizar solo el estado de una tarea
   */
  updateStatus: async (id: string, status: TaskStatus): Promise<Task> => {
    const data: TaskStatusUpdate = { status };
    const response = await apiClient.patch<Task>(`/tasks/${id}/status`, data);
    return response.data;
  },

  /**
   * Marcar tarea como completada
   */
  complete: async (id: string): Promise<Task> => {
    const response = await apiClient.patch<Task>(`/tasks/${id}/complete`);
    return response.data;
  },

  /**
   * Archivar una tarea
   */
  archive: async (id: string): Promise<Task> => {
    const response = await apiClient.patch<Task>(`/tasks/${id}/archive`);
    return response.data;
  },

  /**
   * Desarchivar una tarea
   */
  unarchive: async (id: string): Promise<Task> => {
    const response = await apiClient.patch<Task>(`/tasks/${id}/unarchive`);
    return response.data;
  },
};

export default taskService;
