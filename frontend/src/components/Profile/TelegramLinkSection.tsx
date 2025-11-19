/**
 * TelegramLinkSection - Sección de vinculación con Telegram
 */
import React, { useState, useEffect } from 'react';
import { Send, RefreshCw, X, Check } from 'lucide-react';
import Button from '../common/Button';
import Modal from '../common/Modal';
import telegramService, {
  TelegramLinkCode,
} from '../../services/telegramService';
import { useAuth } from '../../contexts/AuthContext';

const TelegramLinkSection: React.FC = () => {
  const { user, updateUser } = useAuth();

  // States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [linkCode, setLinkCode] = useState<TelegramLinkCode | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Countdown state (segundos restantes)
  const [countdown, setCountdown] = useState<number>(0);

  // Efecto para calcular countdown
  useEffect(() => {
    if (!linkCode) {
      setCountdown(0);
      return;
    }

    const calculateCountdown = () => {
      const expiresAt = new Date(linkCode.expires_at).getTime();
      const now = Date.now();
      const secondsRemaining = Math.max(
        0,
        Math.floor((expiresAt - now) / 1000)
      );
      setCountdown(secondsRemaining);

      if (secondsRemaining === 0) {
        setLinkCode(null);
      }
    };

    calculateCountdown();
    const interval = setInterval(calculateCountdown, 1000);

    return () => clearInterval(interval);
  }, [linkCode]);

  const handleGenerateCode = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const code = await telegramService.generateLinkCode();
      setLinkCode(code);
      setIsModalOpen(true);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Error al generar código de vinculación'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleUnlink = async () => {
    if (!confirm('¿Estás seguro de desvincular tu cuenta de Telegram?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await telegramService.unlinkTelegram();
      // Actualizar usuario en contexto
      if (user) {
        updateUser({
          ...user,
          telegram_chat_id: null,
        });
      }
      setSuccess('Cuenta desvinculada exitosamente');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Error al desvincular cuenta'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshCode = () => {
    setLinkCode(null);
    handleGenerateCode();
  };

  const formatCountdown = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const isLinked = !!user?.telegram_chat_id;

  return (
    <div>
      {/* Success/Error messages */}
      {success && (
        <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <Check className="w-5 h-5" />
          <span>{success}</span>
        </div>
      )}

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <X className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Status */}
      {isLinked ? (
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              <Check className="w-4 h-4 mr-1" />
              Conectado
            </span>
            <span className="text-sm text-gray-600">
              Recibirás notificaciones en Telegram
            </span>
          </div>
          <Button
            variant="danger"
            size="sm"
            onClick={handleUnlink}
            loading={loading}
          >
            Desconectar
          </Button>
        </div>
      ) : (
        <div>
          <p className="text-gray-600 text-sm mb-3">
            Vincula tu cuenta con Telegram para recibir notificaciones en tiempo
            real sobre tus tareas y proyectos.
          </p>
          <Button
            variant="primary"
            onClick={handleGenerateCode}
            loading={loading}
          >
            <Send className="w-4 h-4 mr-2" />
            Vincular Telegram
          </Button>
        </div>
      )}

      {/* Modal de código de vinculación */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Vincular Telegram"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Para vincular tu cuenta con Telegram, sigue estos pasos:
          </p>

          <ol className="space-y-3 text-sm text-gray-700">
            <li className="flex items-start space-x-2">
              <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-medium">
                1
              </span>
              <span>
                Abre Telegram y busca el bot{' '}
                <strong className="font-mono text-blue-600">
                  @control_proyecto_hg_bot
                </strong>
              </span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-medium">
                2
              </span>
              <span>Inicia una conversación con el bot haciendo clic en "Start"</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-medium">
                3
              </span>
              <span>
                Envía el comando{' '}
                <strong className="font-mono">/start</strong> seguido de tu
                código:
              </span>
            </li>
          </ol>

          {/* Código de vinculación */}
          {linkCode && countdown > 0 ? (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 text-center">
              <p className="text-sm text-gray-600 mb-2">Tu código es:</p>
              <div className="text-4xl font-bold text-blue-600 tracking-wider font-mono mb-3">
                {linkCode.code}
              </div>
              <div className="flex items-center justify-center space-x-4 text-sm">
                <div className="flex items-center space-x-2 text-gray-600">
                  <span>Expira en:</span>
                  <span className="font-mono font-semibold text-red-600">
                    {formatCountdown(countdown)}
                  </span>
                </div>
                <button
                  onClick={handleRefreshCode}
                  className="text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                  disabled={loading}
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Generar nuevo</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
              <p className="text-red-700 text-sm">
                El código ha expirado. Genera uno nuevo.
              </p>
              <Button
                variant="primary"
                size="sm"
                onClick={handleRefreshCode}
                loading={loading}
                className="mt-3"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Generar nuevo código
              </Button>
            </div>
          )}

          {/* Comando de ejemplo */}
          <div className="bg-gray-100 border border-gray-200 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">
              Ejemplo del comando a enviar:
            </p>
            <code className="text-sm font-mono text-gray-800">
              /start {linkCode?.code || 'ABC123'}
            </code>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="secondary"
              onClick={() => setIsModalOpen(false)}
            >
              Cerrar
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default TelegramLinkSection;
