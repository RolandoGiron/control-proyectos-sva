/**
 * Auth Service - Servicio de autenticación
 */
import apiClient from './api';
import {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  User,
  ChangePasswordRequest,
} from '../types/api';

const authService = {
  /**
   * Registrar nuevo usuario
   */
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },

  /**
   * Login de usuario
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/login', data);
    const { access_token, user } = response.data;

    // Guardar token y usuario en localStorage
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user', JSON.stringify(user));

    return response.data;
  },

  /**
   * Logout de usuario
   */
  logout: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  /**
   * Obtener usuario actual desde localStorage
   */
  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  },

  /**
   * Verificar si el usuario está autenticado
   */
  isAuthenticated: (): boolean => {
    const token = localStorage.getItem('access_token');
    return !!token;
  },

  /**
   * Obtener perfil del usuario (desde API)
   */
  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me');
    // Actualizar usuario en localStorage
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  },

  /**
   * Actualizar perfil del usuario
   */
  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.put<User>('/users/me', data);
    // Actualizar usuario en localStorage
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  },

  /**
   * Cambiar contraseña
   */
  changePassword: async (data: ChangePasswordRequest): Promise<void> => {
    await apiClient.post('/users/me/change-password', data);
  },

  /**
   * Obtener lista de usuarios
   */
  getUsers: async (): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/users');
    return response.data;
  },
};

export default authService;
