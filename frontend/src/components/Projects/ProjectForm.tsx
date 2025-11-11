/**
 * ProjectForm - Formulario para crear/editar proyectos
 */
import React, { useState, useEffect } from 'react';
import Input from '../common/Input';
import Textarea from '../common/Textarea';
import Button from '../common/Button';
import EmojiPicker from '../common/EmojiPicker';
import { Project } from '../../types/api';

interface ProjectFormProps {
  project?: Project; // Si existe, es modo edición
  onSubmit: (data: { name: string; description?: string; emoji_icon?: string }) => Promise<void>;
  onCancel: () => void;
}

const ProjectForm: React.FC<ProjectFormProps> = ({
  project,
  onSubmit,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    name: project?.name || '',
    description: project?.description || '',
    emoji_icon: project?.emoji_icon || '📁',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (project) {
      setFormData({
        name: project.name,
        description: project.description || '',
        emoji_icon: project.emoji_icon || '📁',
      });
    }
  }, [project]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre del proyecto es requerido';
    } else if (formData.name.length < 3) {
      newErrors.name = 'El nombre debe tener al menos 3 caracteres';
    } else if (formData.name.length > 255) {
      newErrors.name = 'El nombre no puede exceder 255 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    setLoading(true);
    try {
      await onSubmit({
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        emoji_icon: formData.emoji_icon,
      });
    } catch (error: any) {
      const errorMsg =
        error.response?.data?.detail || 'Error al guardar el proyecto';
      setErrors({ submit: errorMsg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
          {errors.submit}
        </div>
      )}

      {/* Emoji picker */}
      <EmojiPicker
        label="Icono del proyecto"
        value={formData.emoji_icon}
        onChange={(emoji) => setFormData({ ...formData, emoji_icon: emoji })}
      />

      {/* Nombre del proyecto */}
      <Input
        label="Nombre del proyecto"
        type="text"
        placeholder="Ej: Desarrollo Web, Marketing Q1..."
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        error={errors.name}
        required
      />

      {/* Descripción */}
      <Textarea
        label="Descripción"
        placeholder="Describe brevemente el proyecto..."
        rows={4}
        value={formData.description}
        onChange={(e) =>
          setFormData({ ...formData, description: e.target.value })
        }
        helperText="Opcional"
      />

      {/* Botones de acción */}
      <div className="flex items-center justify-end space-x-3 pt-4">
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" variant="primary" loading={loading}>
          {project ? 'Actualizar Proyecto' : 'Crear Proyecto'}
        </Button>
      </div>
    </form>
  );
};

export default ProjectForm;
