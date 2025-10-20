import React, { ChangeEvent } from 'react';

interface FormFieldProps {
  label: string;
  type: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  required?: boolean;
  autoComplete?: string;
  id: string;
  placeholder?: string;
  disabled?: boolean;
  helpText?: string;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  type,
  value,
  onChange,
  error,
  required = false,
  autoComplete,
  id,
  placeholder,
  disabled = false,
  helpText,
}) => {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <div style={{ marginBottom: 16 }}>
      <label htmlFor={id} style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>
        {label}
        {required && <span style={{ color: '#dc2626' }}> *</span>}
      </label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={handleChange}
        required={required}
        autoComplete={autoComplete}
        placeholder={placeholder}
        disabled={disabled}
        aria-invalid={!!error}
        aria-describedby={
          error ? `${id}-error` : helpText ? `${id}-help` : undefined
        }
        style={{
          display: 'block',
          width: '100%',
          padding: 8,
          border: error ? '1px solid #dc2626' : '1px solid #d1d5db',
          borderRadius: 4,
          fontSize: 14,
          backgroundColor: disabled ? '#f3f4f6' : 'white',
        }}
      />
      {helpText && !error && (
        <div id={`${id}-help`} style={{ fontSize: 12, color: '#6b7280', marginTop: 4 }}>
          {helpText}
        </div>
      )}
      {error && (
        <div
          id={`${id}-error`}
          role="alert"
          style={{ color: '#dc2626', fontSize: 12, marginTop: 4 }}
        >
          {error}
        </div>
      )}
    </div>
  );
};