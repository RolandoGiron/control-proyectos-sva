/**
 * EmojiPicker - Selector de emojis para proyectos
 */
import React, { useState } from 'react';
import { Smile } from 'lucide-react';

interface EmojiPickerProps {
  value: string;
  onChange: (emoji: string) => void;
  label?: string;
}

const EmojiPicker: React.FC<EmojiPickerProps> = ({ value, onChange, label }) => {
  const [isOpen, setIsOpen] = useState(false);

  // Lista de emojis comunes para proyectos
  const emojis = [
    '📁', '📂', '📊', '📈', '📉', '📋',
    '📝', '📌', '📍', '📎', '📐', '📏',
    '🎯', '🎨', '🎭', '🎪', '🎬', '🎮',
    '💼', '💻', '💾', '💿', '📱', '⌚',
    '🔧', '🔨', '🔩', '⚙️', '🛠️', '⚡',
    '🚀', '🛸', '✈️', '🚁', '🚂', '🚗',
    '⭐', '🌟', '✨', '💫', '🔥', '💡',
    '🎓', '📚', '📖', '📕', '📗', '📘',
    '🏆', '🥇', '🥈', '🥉', '🏅', '🎖️',
    '🌍', '🌎', '🌏', '🗺️', '🧭', '🏔️',
  ];

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}

      <div className="relative">
        {/* Button para abrir el picker */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <span className="text-2xl">{value || '📁'}</span>
          <Smile className="w-4 h-4 text-gray-400" />
        </button>

        {/* Dropdown con emojis */}
        {isOpen && (
          <>
            {/* Overlay para cerrar */}
            <div
              className="fixed inset-0 z-10"
              onClick={() => setIsOpen(false)}
            />

            {/* Panel de emojis */}
            <div className="absolute z-20 mt-2 p-3 bg-white rounded-lg shadow-lg border border-gray-200 w-64">
              <div className="grid grid-cols-6 gap-2 max-h-48 overflow-y-auto">
                {emojis.map((emoji, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => {
                      onChange(emoji);
                      setIsOpen(false);
                    }}
                    className={`
                      text-2xl p-2 rounded hover:bg-gray-100 transition-colors
                      ${value === emoji ? 'bg-blue-50 ring-2 ring-blue-500' : ''}
                    `}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default EmojiPicker;
