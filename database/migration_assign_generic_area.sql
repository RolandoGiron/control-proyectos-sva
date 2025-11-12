-- Migración: Crear área genérica y asignar a proyectos existentes
-- Fecha: 2024-11-11
-- Descripción: Crea un área "General" por defecto y la asigna a todos los proyectos
--              que actualmente no tienen área asignada.

USE proyectos_sva_db;

-- 1. Insertar área genérica si no existe
-- Generamos un UUID válido
SET @generic_area_id = UUID();

INSERT INTO areas (id, name, description, color, icon, is_active, created_at, updated_at)
VALUES (
    @generic_area_id,
    'General',
    'Área general para proyectos sin clasificación específica',
    '#6B7280', -- Color gris neutral
    '📁', -- Icono de carpeta
    TRUE,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE
    name = 'General',
    description = 'Área general para proyectos sin clasificación específica',
    updated_at = NOW();

-- 2. Asignar área genérica a todos los proyectos que no tienen área
UPDATE projects
SET area_id = @generic_area_id,
    updated_at = NOW()
WHERE area_id IS NULL;

-- 3. Verificar resultados
SELECT
    'Área genérica creada' as mensaje,
    id,
    name,
    color,
    icon
FROM areas
WHERE id = @generic_area_id;

SELECT
    CONCAT('Proyectos asignados al área General: ', COUNT(*)) as mensaje
FROM projects
WHERE area_id = @generic_area_id;

-- 4. Mostrar resumen de proyectos por área
SELECT
    COALESCE(a.name, 'Sin área') as area_nombre,
    COUNT(p.id) as total_proyectos,
    a.color,
    a.icon
FROM projects p
LEFT JOIN areas a ON p.area_id = a.id
GROUP BY a.id, a.name, a.color, a.icon
ORDER BY total_proyectos DESC;
