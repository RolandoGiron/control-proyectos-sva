/**
 * Profile Page - Página de perfil del usuario
 */
import React, { useState } from 'react';
import MainLayout from '../components/Layout/MainLayout';
import { useAuth } from '../contexts/AuthContext';
import { User, Mail, Phone, Calendar, X } from 'lucide-react';
import Modal from '../components/common/Modal';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import authService from '../services/authService';

interface EditProfileForm {
  full_name: string;
  phone_number: string;
}

interface ChangePasswordForm {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

const Profile: React.FC = () => {
  const { user, updateUser } = useAuth();

  // Modal states
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);

  // Form states
  const [editForm, setEditForm] = useState<EditProfileForm>({
    full_name: user?.full_name || '',
    phone_number: user?.phone_number || '',
  });

  const [passwordForm, setPasswordForm] = useState<ChangePasswordForm>({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // Loading and error states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Validation errors
  const [passwordErrors, setPasswordErrors] = useState<{
    current_password?: string;
    new_password?: string;
    confirm_password?: string;
  }>({});

  const openEditModal = () => {
    setEditForm({
      full_name: user?.full_name || '',
      phone_number: user?.phone_number || '',
    });
    setError(null);
    setSuccess(null);
    setIsEditModalOpen(true);
  };

  const openPasswordModal = () => {
    setPasswordForm({
      current_password: '',
      new_password: '',
      confirm_password: '',
    });
    setPasswordErrors({});
    setError(null);
    setSuccess(null);
    setIsPasswordModalOpen(true);
  };

  const handleEditProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const updatedUser = await authService.updateProfile({
        full_name: editForm.full_name,
        phone_number: editForm.phone_number || null,
      });

      updateUser(updatedUser);
      setSuccess('Perfil actualizado exitosamente');
      setTimeout(() => {
        setIsEditModalOpen(false);
        setSuccess(null);
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar perfil');
    } finally {
      setLoading(false);
    }
  };

  const validatePassword = (): boolean => {
    const errors: typeof passwordErrors = {};

    if (!passwordForm.current_password) {
      errors.current_password = 'La contraseña actual es requerida';
    }

    if (!passwordForm.new_password) {
      errors.new_password = 'La nueva contraseña es requerida';
    } else if (passwordForm.new_password.length < 8) {
      errors.new_password = 'La contraseña debe tener al menos 8 caracteres';
    } else if (!/[A-Z]/.test(passwordForm.new_password)) {
      errors.new_password = 'Debe contener al menos una mayúscula';
    } else if (!/[0-9]/.test(passwordForm.new_password)) {
      errors.new_password = 'Debe contener al menos un número';
    }

    if (!passwordForm.confirm_password) {
      errors.confirm_password = 'Confirma la nueva contraseña';
    } else if (passwordForm.new_password !== passwordForm.confirm_password) {
      errors.confirm_password = 'Las contraseñas no coinciden';
    }

    setPasswordErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!validatePassword()) {
      return;
    }

    setLoading(true);

    try {
      await authService.changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      });

      setSuccess('Contraseña cambiada exitosamente');
      setTimeout(() => {
        setIsPasswordModalOpen(false);
        setSuccess(null);
        setPasswordForm({
          current_password: '',
          new_password: '',
          confirm_password: '',
        });
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cambiar contraseña');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mi Perfil</h1>
          <p className="text-gray-600 mt-2">
            Gestiona tu información personal y configuración de cuenta
          </p>
        </div>

        {/* Profile card */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {/* Banner */}
          <div className="h-32 bg-gradient-to-r from-blue-500 to-blue-600"></div>

          {/* Profile info */}
          <div className="px-6 pb-6">
            <div className="flex flex-col md:flex-row md:items-end md:space-x-6 -mt-16">
              {/* Avatar */}
              <div className="w-32 h-32 bg-white rounded-full border-4 border-white shadow-lg flex items-center justify-center">
                <span className="text-4xl font-bold text-blue-600">
                  {user?.full_name.charAt(0).toUpperCase()}
                </span>
              </div>

              {/* Name and actions */}
              <div className="mt-4 md:mt-0 flex-1">
                <h2 className="text-2xl font-bold text-gray-900">
                  {user?.full_name}
                </h2>
                <p className="text-gray-600">{user?.email}</p>
              </div>

              <button
                onClick={openEditModal}
                className="mt-4 md:mt-0 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Editar Perfil
              </button>
            </div>

            {/* Info grid */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                  <User className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Nombre Completo
                  </label>
                  <p className="text-gray-900 mt-1">{user?.full_name}</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                  <Mail className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Email
                  </label>
                  <p className="text-gray-900 mt-1">{user?.email}</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                  <Phone className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Teléfono
                  </label>
                  <p className="text-gray-900 mt-1">
                    {user?.phone_number || 'No especificado'}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Miembro desde
                  </label>
                  <p className="text-gray-900 mt-1">
                    {user?.created_at
                      ? new Date(user.created_at).toLocaleDateString('es-ES', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })
                      : 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Security section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Seguridad
          </h3>
          <div className="space-y-3">
            <button
              onClick={openPasswordModal}
              className="w-full md:w-auto px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cambiar Contraseña
            </button>
          </div>
        </div>

        {/* Telegram integration section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Integración con Telegram
          </h3>
          <div className="space-y-3">
            {user?.telegram_chat_id ? (
              <div className="flex items-center space-x-3">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  ✓ Conectado
                </span>
                <button className="text-sm text-red-600 hover:text-red-700">
                  Desconectar
                </button>
              </div>
            ) : (
              <div>
                <p className="text-gray-600 text-sm mb-3">
                  Vincula tu cuenta con Telegram para recibir notificaciones
                </p>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Vincular Telegram
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Edit Profile Modal */}
        <Modal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          title="Editar Perfil"
        >
          <form onSubmit={handleEditProfile} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                {success}
              </div>
            )}

            <Input
              label="Nombre Completo"
              value={editForm.full_name}
              onChange={(e) =>
                setEditForm({ ...editForm, full_name: e.target.value })
              }
              required
              placeholder="Ej: Juan Pérez"
            />

            <Input
              label="Teléfono (opcional)"
              value={editForm.phone_number}
              onChange={(e) =>
                setEditForm({ ...editForm, phone_number: e.target.value })
              }
              placeholder="Ej: +502 1234-5678"
            />

            <div className="flex justify-end gap-3 mt-6">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setIsEditModalOpen(false)}
                disabled={loading}
              >
                Cancelar
              </Button>
              <Button type="submit" variant="primary" loading={loading}>
                Guardar Cambios
              </Button>
            </div>
          </form>
        </Modal>

        {/* Change Password Modal */}
        <Modal
          isOpen={isPasswordModalOpen}
          onClose={() => setIsPasswordModalOpen(false)}
          title="Cambiar Contraseña"
        >
          <form onSubmit={handleChangePassword} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                {success}
              </div>
            )}

            <Input
              label="Contraseña Actual"
              type="password"
              value={passwordForm.current_password}
              onChange={(e) =>
                setPasswordForm({
                  ...passwordForm,
                  current_password: e.target.value,
                })
              }
              required
              error={passwordErrors.current_password}
            />

            <Input
              label="Nueva Contraseña"
              type="password"
              value={passwordForm.new_password}
              onChange={(e) =>
                setPasswordForm({
                  ...passwordForm,
                  new_password: e.target.value,
                })
              }
              required
              error={passwordErrors.new_password}
              helperText="Mínimo 8 caracteres, una mayúscula y un número"
            />

            <Input
              label="Confirmar Nueva Contraseña"
              type="password"
              value={passwordForm.confirm_password}
              onChange={(e) =>
                setPasswordForm({
                  ...passwordForm,
                  confirm_password: e.target.value,
                })
              }
              required
              error={passwordErrors.confirm_password}
            />

            <div className="flex justify-end gap-3 mt-6">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setIsPasswordModalOpen(false)}
                disabled={loading}
              >
                Cancelar
              </Button>
              <Button type="submit" variant="primary" loading={loading}>
                Cambiar Contraseña
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </MainLayout>
  );
};

export default Profile;
