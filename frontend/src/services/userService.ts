import apiClient from './api';
import { User } from '../types/api';

/**
 * User Service - Servicio para gestión de usuarios
 */
class UserService {
  private readonly baseUrl = '/users';

  /**
   * Obtener todos los usuarios
   */
  async getAll(): Promise<User[]> {
    const response = await apiClient.get<User[]>(this.baseUrl);
    return response.data;
  }

  /**
   * Obtener un usuario por ID
   */
  async getById(id: string): Promise<User> {
    const response = await apiClient.get<User>(`${this.baseUrl}/${id}`);
    return response.data;
  }
}

export default new UserService();
