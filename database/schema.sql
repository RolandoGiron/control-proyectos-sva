-- ============================================================================
-- Sistema de Gestión de Proyectos y Tareas SVA
-- Schema de Base de Datos MySQL 8.0
-- ============================================================================
-- Fecha: 2024-11-10
-- Versión: 1.0
-- ============================================================================

-- Configuración inicial
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- ============================================================================
-- Tabla: users
-- Descripción: Usuarios del sistema
-- ============================================================================
CREATE TABLE IF NOT EXISTS `users` (
  `id` CHAR(36) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(255) NOT NULL,
  `phone_number` VARCHAR(20) DEFAULT NULL,
  `telegram_chat_id` BIGINT DEFAULT NULL COMMENT 'Chat ID de Telegram para notificaciones',
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_users_email` (`email`),
  UNIQUE KEY `uk_users_phone` (`phone_number`),
  UNIQUE KEY `uk_users_telegram_chat_id` (`telegram_chat_id`),
  INDEX `idx_users_is_active` (`is_active`),
  INDEX `idx_users_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Usuarios del sistema';

-- ============================================================================
-- Tabla: projects
-- Descripción: Proyectos que agrupan tareas
-- ============================================================================
CREATE TABLE IF NOT EXISTS `projects` (
  `id` CHAR(36) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` TEXT DEFAULT NULL,
  `emoji_icon` VARCHAR(10) DEFAULT '📁' COMMENT 'Emoji o icono del proyecto',
  `owner_id` CHAR(36) NOT NULL COMMENT 'Usuario creador del proyecto',
  `is_archived` BOOLEAN NOT NULL DEFAULT FALSE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_projects_owner_id` (`owner_id`),
  INDEX `idx_projects_is_archived` (`is_archived`),
  INDEX `idx_projects_created_at` (`created_at`),
  CONSTRAINT `fk_projects_owner`
    FOREIGN KEY (`owner_id`)
    REFERENCES `users` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Proyectos del sistema';

-- ============================================================================
-- Tabla: tasks
-- Descripción: Tareas asociadas a proyectos
-- ============================================================================
CREATE TABLE IF NOT EXISTS `tasks` (
  `id` CHAR(36) NOT NULL,
  `project_id` CHAR(36) NOT NULL,
  `title` VARCHAR(500) NOT NULL,
  `description` TEXT DEFAULT NULL,
  `status` ENUM('sin_empezar', 'en_curso', 'completado') NOT NULL DEFAULT 'sin_empezar',
  `priority` ENUM('baja', 'media', 'alta') NOT NULL DEFAULT 'media',
  `responsible_id` CHAR(36) DEFAULT NULL COMMENT 'Usuario responsable de la tarea',
  `deadline` DATETIME DEFAULT NULL COMMENT 'Fecha límite para completar la tarea',
  `reminder_hours_before` INT UNSIGNED DEFAULT 24 COMMENT 'Horas antes del deadline para enviar recordatorio',
  `completed_at` DATETIME DEFAULT NULL COMMENT 'Fecha y hora de completado',
  `created_by` CHAR(36) NOT NULL COMMENT 'Usuario que creó la tarea',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_tasks_project_id` (`project_id`),
  INDEX `idx_tasks_status` (`status`),
  INDEX `idx_tasks_priority` (`priority`),
  INDEX `idx_tasks_responsible_id` (`responsible_id`),
  INDEX `idx_tasks_deadline` (`deadline`),
  INDEX `idx_tasks_created_by` (`created_by`),
  INDEX `idx_tasks_created_at` (`created_at`),
  INDEX `idx_tasks_status_deadline` (`status`, `deadline`),
  CONSTRAINT `fk_tasks_project`
    FOREIGN KEY (`project_id`)
    REFERENCES `projects` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_tasks_responsible`
    FOREIGN KEY (`responsible_id`)
    REFERENCES `users` (`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_tasks_created_by`
    FOREIGN KEY (`created_by`)
    REFERENCES `users` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tareas del sistema';

-- ============================================================================
-- Tabla: notifications
-- Descripción: Registro de notificaciones enviadas
-- ============================================================================
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL COMMENT 'Usuario destinatario',
  `task_id` CHAR(36) DEFAULT NULL COMMENT 'Tarea relacionada (si aplica)',
  `type` ENUM('nueva_tarea', 'recordatorio', 'completada', 'resumen_diario', 'resumen_semanal', 'cambio_estado') NOT NULL,
  `message` TEXT NOT NULL COMMENT 'Contenido del mensaje',
  `sent_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de envío',
  `read_at` TIMESTAMP NULL DEFAULT NULL COMMENT 'Fecha de lectura (si aplica)',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_notifications_user_id` (`user_id`),
  INDEX `idx_notifications_task_id` (`task_id`),
  INDEX `idx_notifications_type` (`type`),
  INDEX `idx_notifications_sent_at` (`sent_at`),
  INDEX `idx_notifications_read_at` (`read_at`),
  CONSTRAINT `fk_notifications_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `users` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_notifications_task`
    FOREIGN KEY (`task_id`)
    REFERENCES `tasks` (`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Historial de notificaciones';

-- ============================================================================
-- Tabla: task_comments (OPCIONAL - Fase futura)
-- Descripción: Comentarios en las tareas
-- ============================================================================
CREATE TABLE IF NOT EXISTS `task_comments` (
  `id` CHAR(36) NOT NULL,
  `task_id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_task_comments_task_id` (`task_id`),
  INDEX `idx_task_comments_user_id` (`user_id`),
  INDEX `idx_task_comments_created_at` (`created_at`),
  CONSTRAINT `fk_task_comments_task`
    FOREIGN KEY (`task_id`)
    REFERENCES `tasks` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_task_comments_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `users` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Comentarios en tareas';

-- ============================================================================
-- Tabla: telegram_link_codes (Para vincular cuentas)
-- Descripción: Códigos temporales para vincular Telegram con usuario
-- ============================================================================
CREATE TABLE IF NOT EXISTS `telegram_link_codes` (
  `id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `code` VARCHAR(10) NOT NULL COMMENT 'Código de 6-8 caracteres',
  `expires_at` TIMESTAMP NOT NULL COMMENT 'Tiempo de expiración (15 minutos)',
  `used_at` TIMESTAMP NULL DEFAULT NULL COMMENT 'Cuando fue usado',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_telegram_link_codes_code` (`code`),
  INDEX `idx_telegram_link_codes_user_id` (`user_id`),
  INDEX `idx_telegram_link_codes_expires_at` (`expires_at`),
  CONSTRAINT `fk_telegram_link_codes_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `users` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Códigos de vinculación Telegram';

-- ============================================================================
-- Triggers
-- ============================================================================

-- Trigger: Marcar fecha de completado cuando se cambia estado a 'completado'
DELIMITER $$
CREATE TRIGGER `tr_tasks_set_completed_at`
BEFORE UPDATE ON `tasks`
FOR EACH ROW
BEGIN
  IF NEW.status = 'completado' AND OLD.status != 'completado' THEN
    SET NEW.completed_at = NOW();
  END IF;

  IF NEW.status != 'completado' AND OLD.status = 'completado' THEN
    SET NEW.completed_at = NULL;
  END IF;
END$$
DELIMITER ;

-- ============================================================================
-- Datos de ejemplo (SOLO PARA DESARROLLO)
-- ============================================================================
-- NOTA: Los datos de ejemplo se crearán via API después de la migración a UUID

-- Usuario de prueba (password: Test123!)
-- Hash bcrypt de "Test123!": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lXz.peWnh3jK
-- Registrar usuarios via API POST /api/v1/auth/register

-- ============================================================================
-- Vistas útiles
-- ============================================================================

-- Vista: Tareas con información completa
CREATE OR REPLACE VIEW `v_tasks_full` AS
SELECT
  t.id,
  t.title,
  t.description,
  t.status,
  t.priority,
  t.deadline,
  t.reminder_hours_before,
  t.completed_at,
  t.created_at,
  t.updated_at,
  p.id AS project_id,
  p.name AS project_name,
  p.emoji_icon AS project_icon,
  u_resp.id AS responsible_id,
  u_resp.full_name AS responsible_name,
  u_resp.email AS responsible_email,
  u_creator.id AS creator_id,
  u_creator.full_name AS creator_name,
  CASE
    WHEN t.status = 'completado' THEN 'Completado'
    WHEN t.deadline IS NULL THEN 'Sin deadline'
    WHEN t.deadline < NOW() THEN 'Vencido'
    WHEN t.deadline < DATE_ADD(NOW(), INTERVAL 24 HOUR) THEN 'Urgente'
    ELSE 'En plazo'
  END AS deadline_status
FROM tasks t
INNER JOIN projects p ON t.project_id = p.id
LEFT JOIN users u_resp ON t.responsible_id = u_resp.id
INNER JOIN users u_creator ON t.created_by = u_creator.id;

-- Vista: Resumen de proyectos con contadores
CREATE OR REPLACE VIEW `v_projects_summary` AS
SELECT
  p.id,
  p.name,
  p.emoji_icon,
  p.description,
  p.is_archived,
  p.created_at,
  u.full_name AS owner_name,
  COUNT(DISTINCT t.id) AS total_tasks,
  COUNT(DISTINCT CASE WHEN t.status = 'completado' THEN t.id END) AS completed_tasks,
  COUNT(DISTINCT CASE WHEN t.status = 'en_curso' THEN t.id END) AS in_progress_tasks,
  COUNT(DISTINCT CASE WHEN t.status = 'sin_empezar' THEN t.id END) AS pending_tasks,
  COUNT(DISTINCT CASE WHEN t.deadline < NOW() AND t.status != 'completado' THEN t.id END) AS overdue_tasks
FROM projects p
INNER JOIN users u ON p.owner_id = u.id
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id, p.name, p.emoji_icon, p.description, p.is_archived, p.created_at, u.full_name;

-- ============================================================================
-- Stored Procedures útiles
-- ============================================================================

-- Procedimiento: Obtener tareas próximas a vencer (para recordatorios)
DELIMITER $$
CREATE PROCEDURE `sp_get_upcoming_deadline_tasks`()
BEGIN
  SELECT
    t.id,
    t.title,
    t.deadline,
    t.reminder_hours_before,
    u.id AS user_id,
    u.full_name AS user_name,
    u.telegram_chat_id,
    p.name AS project_name,
    TIMESTAMPDIFF(HOUR, NOW(), t.deadline) AS hours_until_deadline
  FROM tasks t
  INNER JOIN users u ON t.responsible_id = u.id
  INNER JOIN projects p ON t.project_id = p.id
  WHERE t.status != 'completado'
    AND t.deadline IS NOT NULL
    AND u.telegram_chat_id IS NOT NULL
    AND TIMESTAMPDIFF(HOUR, NOW(), t.deadline) <= t.reminder_hours_before
    AND TIMESTAMPDIFF(HOUR, NOW(), t.deadline) > 0
    AND NOT EXISTS (
      SELECT 1 FROM notifications n
      WHERE n.task_id = t.id
        AND n.type = 'recordatorio'
        AND n.sent_at > DATE_SUB(NOW(), INTERVAL t.reminder_hours_before HOUR)
    )
  ORDER BY t.deadline ASC;
END$$
DELIMITER ;

-- Procedimiento: Marcar notificación como leída
DELIMITER $$
CREATE PROCEDURE `sp_mark_notification_read`(IN p_notification_id CHAR(36))
BEGIN
  UPDATE notifications
  SET read_at = NOW()
  WHERE id = p_notification_id
    AND read_at IS NULL;
END$$
DELIMITER ;

-- Procedimiento: Limpiar códigos de vinculación expirados
DELIMITER $$
CREATE PROCEDURE `sp_cleanup_expired_link_codes`()
BEGIN
  DELETE FROM telegram_link_codes
  WHERE expires_at < NOW()
    AND used_at IS NULL;
END$$
DELIMITER ;

-- ============================================================================
-- Índices adicionales para optimización
-- ============================================================================

-- Índice compuesto para búsquedas frecuentes
ALTER TABLE tasks
ADD INDEX idx_tasks_responsible_status (responsible_id, status);

ALTER TABLE tasks
ADD INDEX idx_tasks_project_status (project_id, status);

-- ============================================================================
-- Restaurar configuración
-- ============================================================================

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- ============================================================================
-- Fin del schema
-- ============================================================================
