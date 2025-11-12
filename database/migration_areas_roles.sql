-- ============================================================================
-- Migración: Áreas y Roles de Usuario
-- Fecha: 2024-11-11
-- Versión: 2.0
-- Descripción: Agrega tablas de áreas y roles al sistema
-- ============================================================================

USE proyectos_sva_db;

-- ============================================================================
-- Tabla: areas
-- Descripción: Áreas o departamentos de la organización
-- ============================================================================
CREATE TABLE IF NOT EXISTS `areas` (
  `id` CHAR(36) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT DEFAULT NULL,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_areas_name` (`name`),
  INDEX `idx_areas_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Áreas o departamentos';

-- ============================================================================
-- Modificar tabla users: Agregar role y area_id
-- ============================================================================
ALTER TABLE `users`
  ADD COLUMN `role` ENUM('administrador', 'supervisor', 'analista') NOT NULL DEFAULT 'analista' COMMENT 'Rol del usuario en el sistema' AFTER `is_active`,
  ADD COLUMN `area_id` CHAR(36) DEFAULT NULL COMMENT 'Área a la que pertenece el usuario' AFTER `role`,
  ADD INDEX `idx_users_role` (`role`),
  ADD INDEX `idx_users_area_id` (`area_id`),
  ADD CONSTRAINT `fk_users_area`
    FOREIGN KEY (`area_id`)
    REFERENCES `areas` (`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE;

-- ============================================================================
-- Modificar tabla projects: Agregar area_id
-- ============================================================================
ALTER TABLE `projects`
  ADD COLUMN `area_id` CHAR(36) DEFAULT NULL COMMENT 'Área a la que pertenece el proyecto' AFTER `owner_id`,
  ADD INDEX `idx_projects_area_id` (`area_id`),
  ADD CONSTRAINT `fk_projects_area`
    FOREIGN KEY (`area_id`)
    REFERENCES `areas` (`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE;

-- ============================================================================
-- Datos iniciales: Áreas predeterminadas
-- ============================================================================
INSERT INTO `areas` (`id`, `name`, `description`, `is_active`) VALUES
  (UUID(), 'SVA', 'Área de SVA - Servicios de Valor Agregado', TRUE),
  (UUID(), 'Productos', 'Área de Productos y Desarrollo', TRUE),
  (UUID(), 'QA', 'Área de Quality Assurance y Testing', TRUE),
  (UUID(), 'IT', 'Área de Tecnologías de la Información', TRUE),
  (UUID(), 'General', 'Área general para proyectos transversales', TRUE);

-- ============================================================================
-- Actualizar usuarios existentes
-- ============================================================================
-- Asignar rol de administrador al primer usuario (si existe)
UPDATE `users`
SET `role` = 'administrador'
WHERE `id` = (SELECT `id` FROM (SELECT `id` FROM `users` ORDER BY `created_at` ASC LIMIT 1) AS temp)
LIMIT 1;

-- Asignar área "General" por defecto a usuarios sin área
UPDATE `users` u
SET u.`area_id` = (SELECT `id` FROM `areas` WHERE `name` = 'General' LIMIT 1)
WHERE u.`area_id` IS NULL;

-- ============================================================================
-- Comentarios de documentación
-- ============================================================================
-- Roles del sistema:
-- - administrador: Acceso total a todos los proyectos y tareas
-- - supervisor: Acceso a proyectos y tareas de su área
-- - analista: Acceso solo a sus propios proyectos y tareas

COMMIT;
