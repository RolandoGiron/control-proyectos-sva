/**
 * AuthContext - Contexto de autenticación para React
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginRequest, RegisterRequest } from '../types/api';
import authService from '../services/authService';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  refreshUser: () => Promise<void>;
  updateUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Cargar usuario al iniciar la aplicación
  useEffect(() => {
    const initAuth = () => {
      const currentUser = authService.getCurrentUser();
      setUser(currentUser);
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (data: LoginRequest): Promise<void> => {
    const response = await authService.login(data);
    setUser(response.user);
  };

  const register = async (data: RegisterRequest): Promise<void> => {
    await authService.register(data);
    // Auto-login después del registro
    await login({ email: data.email, password: data.password });
  };

  const logout = (): void => {
    authService.logout();
    setUser(null);
  };

  const refreshUser = async (): Promise<void> => {
    try {
      const updatedUser = await authService.getProfile();
      setUser(updatedUser);
    } catch (error) {
      console.error('Error al refrescar usuario:', error);
      logout();
    }
  };

  const updateUser = (user: User): void => {
    setUser(user);
    localStorage.setItem('user', JSON.stringify(user));
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    refreshUser,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook personalizado para usar el contexto
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};
