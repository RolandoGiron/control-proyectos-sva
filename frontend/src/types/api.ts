/**
 * API Types - Interfaces para comunicación con el backend
 */

// Enums
export enum TaskStatus {
  SIN_EMPEZAR = 'sin_empezar',
  EN_CURSO = 'en_curso',
  COMPLETADO = 'completado',
}

export enum TaskPriority {
  BAJA = 'baja',
  MEDIA = 'media',
  ALTA = 'alta',
}

// User types
export interface User {
  id: string; // UUID
  email: string;
  full_name: string;
  phone_number?: string;
  telegram_chat_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  phone_number?: string;
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

// Project types
export interface Project {
  id: string; // UUID
  name: string;
  description?: string;
  emoji_icon?: string;
  owner_id: string; // UUID
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
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  emoji_icon?: string;
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
  created_by: string; // UUID
  created_at: string;
  updated_at: string;
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
