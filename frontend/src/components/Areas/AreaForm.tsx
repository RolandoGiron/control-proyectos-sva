/**
 * AreaForm - Formulario para crear/editar áreas
 */
import React, { useState, useEffect } from 'react';
import { Area, AreaCreate } from '../../types/api';
import Input from '../common/Input';
import Textarea from '../common/Textarea';
import Button from '../common/Button';
import EmojiPicker from '../common/EmojiPicker';

interface AreaFormProps {
  area?: Area;
  onSubmit: (data: AreaCreate) => Promise<void>;
  onCancel: () => void;
}

const AreaForm: React.FC<AreaFormProps> = ({ area, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<AreaCreate>({
    name: '',
    description: '',
    color: '#3B82F6',
    icon: '📁',
    is_active: true,
  });
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);

  useEffect(() => {
    if (area) {
      setFormData({
        name: area.name,
        description: area.description || '',
        color: area.color,
        icon: area.icon || '📁',
        is_active: area.is_active,
      });
    }
  }, [area]);

  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es obligatorio';
    } else if (formData.name.length > 100) {
      newErrors.name = 'El nombre no puede exceder 100 caracteres';
    }

    if (formData.description && formData.description.length > 500) {
      newErrors.description = 'La descripción no puede exceder 500 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      await onSubmit(formData);
    } catch (error: any) {
      setErrors({ submit: error.response?.data?.detail || 'Error al guardar el área' });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof AreaCreate, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const predefinedColors = [
    '#EF4444', // Red
    '#F59E0B', // Amber
    '#10B981', // Green
    '#3B82F6', // Blue
    '#6366F1', // Indigo
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#14B8A6', // Teal
    '#F97316', // Orange
    '#84CC16', // Lime
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name */}
      <Input
        label="Nombre del Área"
        name="name"
        value={formData.name}
        onChange={(e) => handleChange('name', e.target.value)}
        error={errors.name}
        placeholder="Ej: Desarrollo, Marketing, Finanzas"
        required
      />

      {/* Description */}
      <Textarea
        label="Descripción"
        name="description"
        value={formData.description || ''}
        onChange={(e) => handleChange('description', e.target.value)}
        error={errors.description}
        placeholder="Descripción opcional del área"
        rows={3}
      />

      {/* Icon Picker */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Ícono
        </label>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setShowEmojiPicker(!showEmojiPicker)}
            className="w-16 h-16 flex items-center justify-center text-4xl bg-gray-50 hover:bg-gray-100 border-2 border-gray-300 rounded-lg transition-colors"
          >
            {formData.icon}
          </button>
          <p className="text-sm text-gray-500">
            Haz clic para seleccionar un ícono
          </p>
        </div>
        {showEmojiPicker && (
          <div className="mt-3">
            <EmojiPicker
              value={formData.icon || '📁'}
              onChange={(emoji) => {
                handleChange('icon', emoji);
                setShowEmojiPicker(false);
              }}
            />
          </div>
        )}
      </div>

      {/* Color Picker */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Color
        </label>
        <div className="grid grid-cols-5 gap-2 mb-3">
          {predefinedColors.map((color) => (
            <button
              key={color}
              type="button"
              onClick={() => handleChange('color', color)}
              className={`w-full h-10 rounded-lg border-2 transition-all ${
                formData.color === color
                  ? 'border-gray-900 scale-105'
                  : 'border-gray-300 hover:scale-105'
              }`}
              style={{ backgroundColor: color }}
            />
          ))}
        </div>
        <Input
          label="Color personalizado (hex)"
          name="color"
          type="text"
          value={formData.color}
          onChange={(e) => handleChange('color', e.target.value)}
          placeholder="#3B82F6"
        />
      </div>

      {/* Active Status */}
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          id="is_active"
          checked={formData.is_active}
          onChange={(e) => handleChange('is_active', e.target.checked)}
          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
        <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
          Área activa
        </label>
      </div>

      {/* Submit Error */}
      {errors.submit && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{errors.submit}</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" variant="primary" loading={loading}>
          {area ? 'Actualizar Área' : 'Crear Área'}
        </Button>
      </div>
    </form>
  );
};

export default AreaForm;
