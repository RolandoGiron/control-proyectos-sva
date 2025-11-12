import React, { useState, useEffect } from 'react';
import { Task, TaskCreate, TaskUpdate, Project } from '../../types/api';
import Input from '../common/Input';
import Textarea from '../common/Textarea';
import Select from '../common/Select';
import UserAutocomplete from '../common/UserAutocomplete';
import Button from '../common/Button';

interface TaskFormProps {
  task?: Task; // If provided, form is in edit mode
  projects: Project[];
  onSubmit: ((data: TaskCreate) => Promise<void>) | ((data: TaskUpdate) => Promise<void>);
  onCancel: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({
  task,
  projects,
  onSubmit,
  onCancel,
}) => {
  const [formData, setFormData] = useState<TaskCreate>({
    title: '',
    description: '',
    project_id: '',
    status: 'sin_empezar',
    priority: 'media',
    responsible_id: '',
    deadline: '',
    reminder_hours_before: 24,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEditMode = !!task;

  // Populate form in edit mode
  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description || '',
        project_id: task.project_id,
        status: task.status,
        priority: task.priority,
        responsible_id: task.responsible_id || '',
        deadline: task.deadline ? task.deadline.slice(0, 16) : '', // Format for datetime-local
        reminder_hours_before: task.reminder_hours_before || 24,
      });
    }
  }, [task]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'El título es requerido';
    }

    if (!formData.project_id) {
      newErrors.project_id = 'Debe seleccionar un proyecto';
    }

    if (formData.reminder_hours_before && formData.reminder_hours_before < 0) {
      newErrors.reminder_hours_before = 'Las horas deben ser positivas';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);

      // Prepare data for submission
      const submitData = {
        ...formData,
        description: formData.description || undefined,
        responsible_id: formData.responsible_id || undefined,
        deadline: formData.deadline || undefined,
        reminder_hours_before: formData.reminder_hours_before || 24,
      };

      await onSubmit(submitData as any);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar la tarea');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof TaskCreate, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const statusOptions = [
    { value: 'sin_empezar', label: 'Sin Empezar' },
    { value: 'en_curso', label: 'En Curso' },
    { value: 'completado', label: 'Completado' },
  ];

  const priorityOptions = [
    { value: 'baja', label: 'Baja' },
    { value: 'media', label: 'Media' },
    { value: 'alta', label: 'Alta' },
  ];

  const projectOptions = projects.map((project) => ({
    value: project.id,
    label: `${project.emoji_icon || '📁'} ${project.name}`,
  }));

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Title */}
      <Input
        label="Título"
        value={formData.title}
        onChange={(e) => handleChange('title', e.target.value)}
        error={errors.title}
        placeholder="Ej: Implementar sistema de autenticación"
        required
      />

      {/* Description */}
      <Textarea
        label="Descripción"
        value={formData.description}
        onChange={(e) => handleChange('description', e.target.value)}
        placeholder="Descripción detallada de la tarea..."
        rows={4}
      />

      {/* Project */}
      <Select
        label="Proyecto"
        value={formData.project_id}
        onChange={(value) => handleChange('project_id', value)}
        options={projectOptions}
        error={errors.project_id}
        placeholder="Seleccionar proyecto..."
        required
      />

      {/* Status and Priority - Side by side */}
      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Estado"
          value={formData.status || ''}
          onChange={(value) => handleChange('status', value)}
          options={statusOptions}
          required
        />
        <Select
          label="Prioridad"
          value={formData.priority || ''}
          onChange={(value) => handleChange('priority', value)}
          options={priorityOptions}
          required
        />
      </div>

      {/* Responsible User */}
      <UserAutocomplete
        label="Responsable"
        value={formData.responsible_id || ''}
        onChange={(value) => handleChange('responsible_id', value)}
        placeholder="Buscar usuario..."
        allowEmpty
      />

      {/* Deadline */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Fecha límite
        </label>
        <input
          type="datetime-local"
          value={formData.deadline || ''}
          onChange={(e) => handleChange('deadline', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Reminder Hours Before */}
      <Input
        label="Recordatorio (horas antes)"
        type="number"
        value={formData.reminder_hours_before?.toString() || '24'}
        onChange={(e) => handleChange('reminder_hours_before', parseInt(e.target.value) || 24)}
        error={errors.reminder_hours_before}
        helperText="Recibirás un recordatorio X horas antes del deadline"
        min="0"
      />

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={loading}
        >
          Cancelar
        </Button>
        <Button
          type="submit"
          variant="primary"
          loading={loading}
        >
          {isEditMode ? 'Guardar Cambios' : 'Crear Tarea'}
        </Button>
      </div>
    </form>
  );
};

export default TaskForm;
