import React, { useState, useEffect, useRef } from 'react';
import { User } from '../../types/api';
import authService from '../../services/authService';

interface UserAutocompleteProps {
  label?: string;
  value: string; // UUID of selected user
  onChange: (userId: string) => void;
  error?: string;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
  allowEmpty?: boolean;
  className?: string;
}

const UserAutocomplete: React.FC<UserAutocompleteProps> = ({
  label,
  value,
  onChange,
  error,
  helperText,
  required = false,
  disabled = false,
  placeholder = 'Buscar usuario...',
  allowEmpty = true,
  className = '',
}) => {
  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Load all users on mount
  useEffect(() => {
    loadUsers();
  }, []);

  // Find selected user when value changes
  useEffect(() => {
    if (value && users.length > 0) {
      const user = users.find((u) => u.id === value);
      setSelectedUser(user || null);
      setSearchTerm(user ? user.full_name : '');
    } else {
      setSelectedUser(null);
      setSearchTerm('');
    }
  }, [value, users]);

  // Filter users based on search term
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredUsers(users);
    } else {
      const filtered = users.filter(
        (user) =>
          user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          user.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredUsers(filtered);
    }
  }, [searchTerm, users]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        // Restore selected user name if user clicked outside
        if (selectedUser) {
          setSearchTerm(selectedUser.full_name);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [selectedUser]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await authService.getUsers();
      setUsers(data);
      setFilteredUsers(data);
    } catch (err) {
      console.error('Error loading users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (user: User) => {
    setSelectedUser(user);
    setSearchTerm(user.full_name);
    onChange(user.id);
    setIsOpen(false);
  };

  const handleClear = () => {
    setSelectedUser(null);
    setSearchTerm('');
    onChange('');
    setIsOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setIsOpen(true);
    // Clear selection if user is typing
    if (selectedUser) {
      setSelectedUser(null);
      onChange('');
    }
  };

  const handleInputFocus = () => {
    setIsOpen(true);
  };

  return (
    <div className={`relative w-full ${className}`} ref={wrapperRef}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        <input
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          disabled={disabled}
          placeholder={placeholder}
          className={`
            w-full px-3 py-2 pr-10 border rounded-lg
            bg-white text-gray-900 placeholder-gray-400
            focus:outline-none focus:ring-2 focus:ring-blue-500
            disabled:bg-gray-100 disabled:cursor-not-allowed
            ${error ? 'border-red-500' : 'border-gray-300'}
          `}
        />
        {selectedUser && allowEmpty && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
        {loading && (
          <div className="absolute right-2 top-1/2 -translate-y-1/2">
            <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        )}
      </div>

      {/* Dropdown */}
      {isOpen && !disabled && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {filteredUsers.length === 0 ? (
            <div className="px-4 py-3 text-sm text-gray-500 text-center">
              {loading ? 'Cargando...' : 'No se encontraron usuarios'}
            </div>
          ) : (
            <>
              {allowEmpty && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 text-gray-500 border-b"
                >
                  (Sin asignar)
                </button>
              )}
              {filteredUsers.map((user) => (
                <button
                  key={user.id}
                  type="button"
                  onClick={() => handleSelect(user)}
                  className={`
                    w-full px-4 py-2 text-left text-sm hover:bg-blue-50
                    ${selectedUser?.id === user.id ? 'bg-blue-50' : ''}
                  `}
                >
                  <div className="font-medium text-gray-900">{user.full_name}</div>
                  <div className="text-xs text-gray-500">{user.email}</div>
                </button>
              ))}
            </>
          )}
        </div>
      )}

      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}
      {helperText && !error && (
        <p className="mt-1 text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

export default UserAutocomplete;
