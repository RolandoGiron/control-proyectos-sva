/**
 * Profile Page - Página de perfil del usuario
 */
import React from 'react';
import MainLayout from '../components/Layout/MainLayout';
import { useAuth } from '../contexts/AuthContext';
import { User, Mail, Phone, Calendar } from 'lucide-react';

const Profile: React.FC = () => {
  const { user } = useAuth();

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

              <button className="mt-4 md:mt-0 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
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
            <button className="w-full md:w-auto px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
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
      </div>
    </MainLayout>
  );
};

export default Profile;
