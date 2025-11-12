/**
 * AreaSelect - Selector de áreas con preview visual
 */
import React, { useState, useEffect } from 'react';
import { Area } from '../../types/api';
import areaService from '../../services/areaService';

interface AreaSelectProps {
  label?: string;
  value: string | null;
  onChange: (areaId: string | null) => void;
  error?: string;
  required?: boolean;
  allowNull?: boolean;
}

const AreaSelect: React.FC<AreaSelectProps> = ({
  label = 'Área',
  value,
  onChange,
  error,
  required = false,
  allowNull = false,
}) => {
  const [areas, setAreas] = useState<Area[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAreas();
  }, []);

  const loadAreas = async () => {
    try {
      setLoading(true);
      const data = await areaService.getAll(true); // Solo áreas activas
      setAreas(data);
    } catch (error) {
      console.error('Error loading areas:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectedArea = areas.find((a) => a.id === value);

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      {loading ? (
        <div className="animate-pulse bg-gray-200 h-10 rounded-lg"></div>
      ) : (
        <>
          <select
            value={value || ''}
            onChange={(e) => onChange(e.target.value || null)}
            className={`
              w-full px-4 py-2 border rounded-lg
              focus:outline-none focus:ring-2 focus:ring-blue-500
              ${error ? 'border-red-500' : 'border-gray-300'}
            `}
            required={required}
          >
            {allowNull && <option value="">Sin área</option>}
            {!allowNull && areas.length === 0 && (
              <option value="">No hay áreas disponibles</option>
            )}
            {areas.map((area) => (
              <option key={area.id} value={area.id}>
                {area.icon ? `${area.icon} ` : ''}
                {area.name}
              </option>
            ))}
          </select>

          {/* Preview del área seleccionada */}
          {selectedArea && (
            <div
              className="mt-2 p-3 rounded-lg border flex items-center gap-3"
              style={{
                backgroundColor: `${selectedArea.color}10`,
                borderColor: `${selectedArea.color}40`,
              }}
            >
              {selectedArea.icon && (
                <span className="text-2xl">{selectedArea.icon}</span>
              )}
              <div>
                <p
                  className="font-medium text-sm"
                  style={{ color: selectedArea.color }}
                >
                  {selectedArea.name}
                </p>
                {selectedArea.description && (
                  <p className="text-xs text-gray-600 mt-0.5">
                    {selectedArea.description}
                  </p>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
    </div>
  );
};

export default AreaSelect;
