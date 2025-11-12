/**
 * Area Service - Servicio para gestión de áreas
 */
import apiClient from './api';
import { Area, AreaWithStats, AreaCreate, AreaUpdate } from '../types/api';

const areaService = {
  /**
   * Obtener todas las áreas
   */
  getAll: async (isActive?: boolean): Promise<Area[]> => {
    const params = isActive !== undefined ? { is_active: isActive } : {};
    const response = await apiClient.get<Area[]>('/areas', { params });
    return response.data;
  },

  /**
   * Obtener áreas con estadísticas
   */
  getAllWithStats: async (isActive?: boolean): Promise<AreaWithStats[]> => {
    const params = isActive !== undefined ? { is_active: isActive } : {};
    const response = await apiClient.get<AreaWithStats[]>('/areas/with-stats', { params });
    return response.data;
  },

  /**
   * Obtener un área por ID
   */
  getById: async (id: string): Promise<Area> => {
    const response = await apiClient.get<Area>(`/areas/${id}`);
    return response.data;
  },

  /**
   * Crear nueva área (solo administradores)
   */
  create: async (data: AreaCreate): Promise<Area> => {
    const response = await apiClient.post<Area>('/areas', data);
    return response.data;
  },

  /**
   * Actualizar área (solo administradores)
   */
  update: async (id: string, data: AreaUpdate): Promise<Area> => {
    const response = await apiClient.put<Area>(`/areas/${id}`, data);
    return response.data;
  },

  /**
   * Eliminar área (solo administradores)
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/areas/${id}`);
  },
};

export default areaService;
