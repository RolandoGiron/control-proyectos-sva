/**
 * Areas Page - Gestión de áreas del sistema
 */
import React, { useState, useEffect } from 'react';
import { AreaWithStats, AreaCreate } from '../types/api';
import areaService from '../services/areaService';
import { useAuth } from '../contexts/AuthContext';
import MainLayout from '../components/Layout/MainLayout';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import AreaForm from '../components/Areas/AreaForm';
import AreaCard from '../components/Areas/AreaCard';

const Areas: React.FC = () => {
  const { user } = useAuth();
  const [areas, setAreas] = useState<AreaWithStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingArea, setEditingArea] = useState<AreaWithStats | null>(null);
  const [deletingArea, setDeletingArea] = useState<AreaWithStats | null>(null);
  const [showInactive, setShowInactive] = useState(false);

  const isAdmin = user?.role === 'administrador';

  useEffect(() => {
    loadAreas();
  }, [showInactive]);

  const loadAreas = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await areaService.getAllWithStats(!showInactive ? true : undefined);
      setAreas(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar las áreas');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (data: AreaCreate) => {
    try {
      await areaService.create(data);
      setShowCreateModal(false);
      await loadAreas();
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Error al crear el área');
    }
  };

  const handleUpdate = async (data: AreaCreate) => {
    if (!editingArea) return;

    try {
      await areaService.update(editingArea.id, data);
      setEditingArea(null);
      await loadAreas();
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Error al actualizar el área');
    }
  };

  const handleDelete = async () => {
    if (!deletingArea) return;

    try {
      await areaService.delete(deletingArea.id);
      setDeletingArea(null);
      await loadAreas();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar el área');
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Áreas</h1>
          <p className="text-gray-600 mt-1">
            Gestiona las áreas de tu organización
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant={showInactive ? 'primary' : 'secondary'}
            onClick={() => setShowInactive(!showInactive)}
          >
            {showInactive ? 'Ver solo activas' : 'Ver todas'}
          </Button>
          {isAdmin && (
            <Button variant="primary" onClick={() => setShowCreateModal(true)}>
              + Nueva Área
            </Button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Permission Notice */}
      {!isAdmin && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-700">
            Solo los administradores pueden crear, editar o eliminar áreas.
          </p>
        </div>
      )}

      {/* Areas Grid */}
      {areas.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📁</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No hay áreas
          </h3>
          <p className="text-gray-600 mb-4">
            {isAdmin
              ? 'Comienza creando tu primera área'
              : 'Aún no se han creado áreas en el sistema'}
          </p>
          {isAdmin && (
            <Button variant="primary" onClick={() => setShowCreateModal(true)}>
              Crear Primera Área
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {areas.map((area) => (
            <AreaCard
              key={area.id}
              area={area}
              onEdit={setEditingArea}
              onDelete={setDeletingArea}
              isAdmin={isAdmin}
            />
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Nueva Área"
      >
        <AreaForm
          onSubmit={handleCreate}
          onCancel={() => setShowCreateModal(false)}
        />
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={editingArea !== null}
        onClose={() => setEditingArea(null)}
        title="Editar Área"
      >
        {editingArea && (
          <AreaForm
            area={editingArea}
            onSubmit={handleUpdate}
            onCancel={() => setEditingArea(null)}
          />
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deletingArea !== null}
        onClose={() => setDeletingArea(null)}
        title="Eliminar Área"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            ¿Estás seguro de que deseas eliminar el área{' '}
            <strong>{deletingArea?.name}</strong>?
          </p>
          {deletingArea?.stats && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-800">
                <strong>Advertencia:</strong> Esta área tiene{' '}
                {deletingArea.stats.total_projects} proyecto(s) y{' '}
                {deletingArea.stats.total_tasks} tarea(s) asociadas.
              </p>
            </div>
          )}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <Button variant="secondary" onClick={() => setDeletingArea(null)}>
              Cancelar
            </Button>
            <Button variant="danger" onClick={handleDelete}>
              Eliminar
            </Button>
          </div>
        </div>
      </Modal>
      </div>
    </MainLayout>
  );
};

export default Areas;
