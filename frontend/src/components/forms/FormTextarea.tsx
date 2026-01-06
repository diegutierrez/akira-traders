import { forwardRef } from 'react';
import { cn } from '../../utils/cn';

interface FormTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  error?: string;
  hint?: string;
}

export const FormTextarea = forwardRef<HTMLTextAreaElement, FormTextareaProps>(
  ({ label, error, hint, className, ...props }, ref) => {
    return (
      <div className="space-y-1">
        <label className="block text-sm font-medium text-text-secondary">
          {label}
          {props.required && <span className="text-danger ml-1">*</span>}
        </label>
        <textarea
          ref={ref}
          className={cn(
            'w-full px-3 py-2 bg-bg-tertiary border rounded-lg text-text-primary',
            'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder:text-text-tertiary resize-y min-h-[100px]',
            error ? 'border-danger' : 'border-border hover:border-border-hover',
            className
          )}
          {...props}
        />
        {hint && !error && (
          <p className="text-xs text-text-tertiary">{hint}</p>
        )}
        {error && (
          <p className="text-xs text-danger">{error}</p>
        )}
      </div>
    );
  }
);

FormTextarea.displayName = 'FormTextarea';
