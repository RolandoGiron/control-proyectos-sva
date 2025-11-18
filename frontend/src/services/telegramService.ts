/**
 * Telegram Service - Gestión de vinculación con Telegram
 */
import apiClient from './api';

export interface TelegramLinkCode {
  code: string;
  expires_at: string;
}

export interface TelegramStatus {
  is_linked: boolean;
  telegram_chat_id: number | null;
}

/**
 * Generar código de vinculación de Telegram
 */
export const generateLinkCode = async (): Promise<TelegramLinkCode> => {
  const response = await apiClient.post<TelegramLinkCode>(
    '/users/me/telegram/generate-code'
  );
  return response.data;
};

/**
 * Obtener estado de vinculación con Telegram
 */
export const getTelegramStatus = async (): Promise<TelegramStatus> => {
  const response = await apiClient.get<TelegramStatus>(
    '/users/me/telegram/status'
  );
  return response.data;
};

/**
 * Desvincular cuenta de Telegram
 */
export const unlinkTelegram = async (): Promise<void> => {
  await apiClient.delete('/users/me/telegram/unlink');
};

const telegramService = {
  generateLinkCode,
  getTelegramStatus,
  unlinkTelegram,
};

export default telegramService;
