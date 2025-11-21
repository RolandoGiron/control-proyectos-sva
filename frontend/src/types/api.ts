/**
 * API Types - Interfaces para comunicación con el backend
 */

// Task enums as literal types
export type TaskStatus = 'sin_empezar' | 'en_curso' | 'completado';
export type TaskPriority = 'baja' | 'media' | 'alta';

// User role types
export type UserRole = 'administrador' | 'supervisor' | 'analista';

// User types
export interface User {
  id: string; // UUID
  email: string;
  full_name: string;
  phone_number?: string;
  telegram_chat_id?: number;
  is_active: boolean;
  role: UserRole;
  area_id?: string; // UUID
  created_at: string;
  updated_at: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  phone_number?: string;
  area_id?: string; // UUID del área
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

// Area types
export interface Area {
  id: string; // UUID
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AreaWithStats extends Area {
  total_users: number;
  total_projects: number;
}

export interface AreaCreate {
  name: string;
  description?: string;
  is_active?: boolean;
}

export interface AreaUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
}

// Project types
export interface Project {
  id: string; // UUID
  name: string;
  description?: string;
  emoji_icon?: string;
  owner_id: string; // UUID
  area_id?: string; // UUID
  area?: Area; // Información completa del área
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProjectWithStats extends Project {
  total_tasks: number;
  completed_tasks: number;
  in_progress_tasks: number;
  pending_tasks: number;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  emoji_icon?: string;
  area_id?: string; // UUID
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  emoji_icon?: string;
  area_id?: string; // UUID
}

// Task types
export interface Task {
  id: string; // UUID
  project_id: string; // UUID
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  responsible_id?: string; // UUID
  deadline?: string; // ISO datetime
  reminder_hours_before?: number;
  completed_at?: string; // ISO datetime
  is_archived: boolean;
  created_by: string; // UUID
  created_at: string;
  updated_at: string;
  // Campos adicionales de TaskWithDetails
  project_name?: string;
  responsible_name?: string;
  creator_name?: string;
}

export interface TaskCreate {
  project_id: string; // UUID
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  responsible_id?: string; // UUID
  deadline?: string; // ISO datetime
  reminder_hours_before?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  responsible_id?: string; // UUID (puede ser null para remover)
  deadline?: string; // ISO datetime
  reminder_hours_before?: number;
}

export interface TaskStatusUpdate {
  status: TaskStatus;
}

// API Error response
export interface ApiError {
  detail: string;
}
