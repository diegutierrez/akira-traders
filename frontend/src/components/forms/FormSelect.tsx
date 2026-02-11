import { forwardRef } from 'react';
import { cn } from '../../utils/cn';

interface Option {
  value: string;
  label: string;
}

interface FormSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  options: Option[];
  error?: string;
  hint?: string;
}

export const FormSelect = forwardRef<HTMLSelectElement, FormSelectProps>(
  ({ label, options, error, hint, className, ...props }, ref) => {
    return (
      <div className="space-y-1">
        <label className="block text-sm font-medium text-text-secondary">
          {label}
          {props.required && <span className="text-danger ml-1">*</span>}
        </label>
        <select
          ref={ref}
          className={cn(
            'w-full px-3 py-2 bg-bg-tertiary border rounded-lg text-text-primary',
            'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            error ? 'border-danger' : 'border-border hover:border-border-hover',
            className,
          )}
          {...props}
        >
          <option value="">Seleccionar...</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {hint && !error && <p className="text-xs text-text-tertiary">{hint}</p>}
        {error && <p className="text-xs text-danger">{error}</p>}
      </div>
    );
  },
);

FormSelect.displayName = 'FormSelect';
