import { cn } from '../../utils/cn';

interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function FormSection({ title, description, children, className }: FormSectionProps) {
  return (
    <div className={cn('space-y-4', className)}>
      <div className="border-b border-border pb-2">
        <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
        {description && (
          <p className="text-sm text-text-tertiary mt-1">{description}</p>
        )}
      </div>
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
}
