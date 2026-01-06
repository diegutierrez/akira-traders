# 🎨 Guía de Componentes y Estilos - Akira Traders

## 📋 Índice

1. [Sistema de Diseño](#sistema-de-diseño)
2. [Componentes Base](#componentes-base)
3. [Componentes de Negocio](#componentes-de-negocio)
4. [Patrones de Diseño](#patrones-de-diseño)
5. [Guía de Estilos](#guía-de-estilos)
6. [Animaciones](#animaciones)
7. [Responsive Design](#responsive-design)

---

## 🎨 Sistema de Diseño

### Paleta de Colores Binance-inspired

```css
/* tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      colors: {
        // Primarios
        primary: {
          DEFAULT: '#F0B90B',
          dark: '#C99C0A',
          light: '#F3C94D',
        },
        
        // Fondos
        bg: {
          primary: '#0B0E11',
          secondary: '#1E2329',
          tertiary: '#2B3139',
        },
        
        // Texto
        text: {
          primary: '#EAECEF',
          secondary: '#848E9C',
          tertiary: '#5E6673',
        },
        
        // Estados
        success: '#0ECB81',
        danger: '#F6465D',
        warning: '#F0B90B',
        info: '#3DCFFF',
        
        // Bordes
        border: {
          DEFAULT: '#2B3139',
          hover: '#474D57',
        },
      },
    },
  },
};
```

### Tipografía

```css
/* globals.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Clases de utilidad */
.text-display {
  @apply text-4xl font-bold tracking-tight;
}

.text-heading-1 {
  @apply text-3xl font-bold;
}

.text-heading-2 {
  @apply text-2xl font-semibold;
}

.text-heading-3 {
  @apply text-xl font-semibold;
}

.text-body {
  @apply text-base font-normal;
}

.text-small {
  @apply text-sm font-normal;
}

.text-caption {
  @apply text-xs font-normal;
}
```

### Espaciado y Layout

```css
/* Sistema de espaciado basado en 4px */
.space-1 { @apply p-1; }    /* 4px */
.space-2 { @apply p-2; }    /* 8px */
.space-3 { @apply p-3; }    /* 12px */
.space-4 { @apply p-4; }    /* 16px */
.space-6 { @apply p-6; }    /* 24px */
.space-8 { @apply p-8; }    /* 32px */
.space-12 { @apply p-12; }  /* 48px */
.space-16 { @apply p-16; }  /* 64px */
```

---

## 🧩 Componentes Base

### Button

```tsx
// src/components/common/Button/Button.tsx
import { forwardRef } from 'react';
import { cn } from '@/utils/cn';
import { Spinner } from '../Spinner';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      leftIcon,
      rightIcon,
      children,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
    
    const variants = {
      primary: 'bg-primary hover:bg-primary-dark text-black focus:ring-primary',
      secondary: 'bg-bg-secondary hover:bg-bg-tertiary text-text-primary focus:ring-bg-tertiary',
      danger: 'bg-danger hover:bg-danger/90 text-white focus:ring-danger',
      ghost: 'bg-transparent hover:bg-bg-secondary text-text-primary',
      outline: 'border-2 border-border hover:border-border-hover text-text-primary',
    };
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-4 py-2 text-base gap-2',
      lg: 'px-6 py-3 text-lg gap-2.5',
    };
    
    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <Spinner size={size === 'sm' ? 'xs' : 'sm'} />
        ) : (
          leftIcon
        )}
        {children}
        {!loading && rightIcon}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

**Uso**:

```tsx
<Button variant="primary" size="md">
  Crear Evaluación
</Button>

<Button variant="secondary" leftIcon={<PlusIcon />}>
  Agregar Trader
</Button>

<Button variant="danger" loading>
  Eliminando...
</Button>
```

---

### Card

```tsx
// src/components/common/Card/Card.tsx
import { cn } from '@/utils/cn';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export function Card({ children, className, hover = false }: CardProps) {
  return (
    <div
      className={cn(
        'bg-bg-secondary rounded-lg border border-border',
        hover && 'hover:border-border-hover transition-colors cursor-pointer',
        className
      )}
    >
      {children}
    </div>
  );
}

Card.Header = function CardHeader({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('p-4 border-b border-border', className)}>
      {children}
    </div>
  );
};

Card.Title = function CardTitle({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <h3 className={cn('text-lg font-semibold text-text-primary', className)}>
      {children}
    </h3>
  );
};

Card.Body = function CardBody({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <div className={cn('p-4', className)}>{children}</div>;
};

Card.Footer = function CardFooter({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('p-4 border-t border-border', className)}>
      {children}
    </div>
  );
};
```

**Uso**:

```tsx
<Card hover>
  <Card.Header>
    <Card.Title>Trader Performance</Card.Title>
  </Card.Header>
  <Card.Body>
    <p>ROI 90d: 42.7%</p>
  </Card.Body>
  <Card.Footer>
    <Button>Ver Detalles</Button>
  </Card.Footer>
</Card>
```

---

### Input

```tsx
// src/components/common/Input/Input.tsx
import { forwardRef } from 'react';
import { cn } from '@/utils/cn';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      className,
      ...props
    },
    ref
  ) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-primary mb-1.5">
            {label}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary">
              {leftIcon}
            </div>
          )}
          
          <input
            ref={ref}
            className={cn(
              'w-full px-4 py-2 bg-bg-tertiary border border-border rounded-lg',
              'text-text-primary placeholder:text-text-tertiary',
              'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'transition-all',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-danger focus:ring-danger',
              className
            )}
            {...props}
          />
          
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary">
              {rightIcon}
            </div>
          )}
        </div>
        
        {error && (
          <p className="mt-1.5 text-sm text-danger">{error}</p>
        )}
        
        {helperText && !error && (
          <p className="mt-1.5 text-sm text-text-secondary">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
```

**Uso**:

```tsx
<Input
  label="Nombre del Trader"
  placeholder="Ingrese el nombre"
  leftIcon={<UserIcon />}
  error={errors.name?.message}
/>
```

---

### Badge

```tsx
// src/components/common/Badge/Badge.tsx
import { cn } from '@/utils/cn';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'danger' | 'warning' | 'info' | 'neutral';
  size?: 'sm' | 'md' | 'lg';
}

export function Badge({ children, variant = 'neutral', size = 'md' }: BadgeProps) {
  const variants = {
    success: 'bg-success/10 text-success border-success/20',
    danger: 'bg-danger/10 text-danger border-danger/20',
    warning: 'bg-warning/10 text-warning border-warning/20',
    info: 'bg-info/10 text-info border-info/20',
    neutral: 'bg-bg-tertiary text-text-secondary border-border',
  };
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };
  
  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full border',
        variants[variant],
        sizes[size]
      )}
    >
      {children}
    </span>
  );
}
```

**Uso**:

```tsx
<Badge variant="success">Aprobado</Badge>
<Badge variant="danger">Rechazado</Badge>
<Badge variant="warning">Pendiente</Badge>
```

---

### Modal

```tsx
// src/components/common/Modal/Modal.tsx
import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { cn } from '@/utils/cn';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
}: ModalProps) {
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-7xl',
  };
  
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/75" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel
                className={cn(
                  'w-full transform overflow-hidden rounded-lg',
                  'bg-bg-secondary border border-border',
                  'text-left align-middle shadow-xl transition-all',
                  sizes[size]
                )}
              >
                {title && (
                  <div className="flex items-center justify-between p-6 border-b border-border">
                    <Dialog.Title className="text-lg font-semibold text-text-primary">
                      {title}
                    </Dialog.Title>
                    <button
                      onClick={onClose}
                      className="text-text-secondary hover:text-text-primary transition-colors"
                    >
                      <XMarkIcon className="w-5 h-5" />
                    </button>
                  </div>
                )}
                
                <div className="p-6">{children}</div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
```

**Uso**:

```tsx
const [isOpen, setIsOpen] = useState(false);

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirmar Eliminación"
  size="md"
>
  <p>¿Estás seguro de eliminar este trader?</p>
  <div className="flex gap-3 mt-6">
    <Button variant="danger" onClick={handleDelete}>
      Eliminar
    </Button>
    <Button variant="ghost" onClick={() => setIsOpen(false)}>
      Cancelar
    </Button>
  </div>
</Modal>
```

---

## 💼 Componentes de Negocio

### TraderCard

```tsx
// src/components/traders/TraderCard/TraderCard.tsx
import { motion } from 'framer-motion';
import { Badge } from '@/components/common/Badge';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { formatPercent, formatNumber } from '@/utils/formatters';

interface TraderCardProps {
  trader: Trader;
  onView: (id: string) => void;
}

export function TraderCard({ trader, onView }: TraderCardProps) {
  const getScoreBadge = (score: number) => {
    if (score >= 85) return { variant: 'success', label: 'Excelente' };
    if (score >= 70) return { variant: 'info', label: 'Bueno' };
    if (score >= 55) return { variant: 'warning', label: 'Aceptable' };
    return { variant: 'danger', label: 'Marginal' };
  };
  
  const scoreBadge = getScoreBadge(trader.score);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
    >
      <Card hover className="h-full">
        <Card.Header>
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-text-primary">
                {trader.display_name}
              </h3>
              <p className="text-sm text-text-secondary mt-1">
                {trader.style}
              </p>
            </div>
            <Badge variant={scoreBadge.variant as any}>
              {scoreBadge.label}
            </Badge>
          </div>
        </Card.Header>
        
        <Card.Body>
          <div className="grid grid-cols-2 gap-4">
            <MetricItem
              label="ROI 90d"
              value={formatPercent(trader.metrics.roi_90d)}
              positive={trader.metrics.roi_90d > 0}
            />
            <MetricItem
              label="Max DD"
              value={formatPercent(trader.metrics.max_drawdown)}
              positive={false}
            />
            <MetricItem
              label="Win Rate"
              value={formatPercent(trader.metrics.win_rate)}
              positive={trader.metrics.win_rate > 50}
            />
            <MetricItem
              label="Score"
              value={trader.score.toFixed(1)}
              positive={trader.score >= 70}
            />
          </div>
        </Card.Body>
        
        <Card.Footer>
          <Button
            variant="primary"
            className="w-full"
            onClick={() => onView(trader.id)}
          >
            Ver Detalles
          </Button>
        </Card.Footer>
      </Card>
    </motion.div>
  );
}

function MetricItem({
  label,
  value,
  positive,
}: {
  label: string;
  value: string;
  positive: boolean;
}) {
  return (
    <div>
      <p className="text-xs text-text-secondary mb-1">{label}</p>
      <p
        className={cn(
          'text-lg font-semibold',
          positive ? 'text-success' : 'text-danger'
        )}
      >
        {value}
      </p>
    </div>
  );
}
```

---

### PerformanceChart

```tsx
// src/components/charts/PerformanceChart/PerformanceChart.tsx
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface PerformanceChartProps {
  data: Array<{ date: string; roi: number }>;
}

export function PerformanceChart({ data }: PerformanceChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2B3139" />
        <XAxis
          dataKey="date"
          stroke="#848E9C"
          style={{ fontSize: '12px' }}
        />
        <YAxis
          stroke="#848E9C"
          style={{ fontSize: '12px' }}
          tickFormatter={(value) => `${value}%`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1E2329',
            border: '1px solid #2B3139',
            borderRadius: '8px',
          }}
          labelStyle={{ color: '#EAECEF' }}
        />
        <Line
          type="monotone"
          dataKey="roi"
          stroke="#F0B90B"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

---

## 🎭 Patrones de Diseño

### Compound Components

```tsx
// Componente padre que maneja el estado
export function Tabs({ children, defaultValue }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultValue);
  
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="w-full">{children}</div>
    </TabsContext.Provider>
  );
}

// Subcomponentes que consumen el contexto
Tabs.List = function TabsList({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex border-b border-border">
      {children}
    </div>
  );
};

Tabs.Trigger = function TabsTrigger({
  value,
  children,
}: {
  value: string;
  children: React.ReactNode;
}) {
  const { activeTab, setActiveTab } = useTabsContext();
  
  return (
    <button
      onClick={() => setActiveTab(value)}
      className={cn(
        'px-4 py-2 font-medium transition-colors',
        activeTab === value
          ? 'text-primary border-b-2 border-primary'
          : 'text-text-secondary hover:text-text-primary'
      )}
    >
      {children}
    </button>
  );
};

Tabs.Content = function TabsContent({
  value,
  children,
}: {
  value: string;
  children: React.ReactNode;
}) {
  const { activeTab } = useTabsContext();
  
  if (activeTab !== value) return null;
  
  return <div className="py-4">{children}</div>;
};

// Uso
<Tabs defaultValue="overview">
  <Tabs.List>
    <Tabs.Trigger value="overview">Overview</Tabs.Trigger>
    <Tabs.Trigger value="metrics">Metrics</Tabs.Trigger>
    <Tabs.Trigger value="history">History</Tabs.Trigger>
  </Tabs.List>
  
  <Tabs.Content value="overview">
    <OverviewPanel />
  </Tabs.Content>
  <Tabs.Content value="metrics">
    <MetricsPanel />
  </Tabs.Content>
  <Tabs.Content value="history">
    <HistoryPanel />
  </Tabs.Content>
</Tabs>
```

### Render Props

```tsx
// Componente con render prop
function DataFetcher<T>({
  url,
  children,
}: {
  url: string;
  children: (data: {
    data: T | null;
    loading: boolean;
    error: Error | null;
  }) => React.ReactNode;
}) {
  const { data, isLoading, error } = useQuery({
    queryKey: [url],
    queryFn: () => fetch(url).then(res => res.json()),
  });
  
  return <>{children({ data, loading: isLoading, error })}</>;
}

// Uso
<DataFetcher<Trader[]> url="/api/traders">
  {({ data, loading, error }) => {
    if (loading) return <Spinner />;
    if (error) return <ErrorMessage error={error} />;
    return <TraderList traders={data} />;
  }}
</DataFetcher>
```

---

## 🎬 Animaciones

### Framer Motion

```tsx
// Animación de entrada
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  <Card>...</Card>
</motion.div>

// Animación de lista
<motion.div
  variants={{
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }}
  initial="hidden"
  animate="show"
>
  {traders.map((trader) => (
    <motion.div
      key={trader.id}
      variants={{
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0 },
      }}
    >
      <TraderCard trader={trader} />
    </motion.div>
  ))}
</motion.div>

// Animación de hover
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  Click me
</motion.button>
```

---

## 📱 Responsive Design

### Breakpoints

```tsx
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    },
  },
};
```

### Uso

```tsx
<div className="
  grid
  grid-cols-1
  sm:grid-cols-2
  lg:grid-cols-3
  xl:grid-cols-4
  gap-4
">
  {traders.map((trader) => (
    <TraderCard key={trader.id} trader={trader} />
  ))}
</div>
```

---

## 📚 Recursos

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Headless UI](https://headlessui.com/)
- [Framer Motion](https://www.framer.com/motion/)
- [Recharts](https://recharts.org/)

---

**Última actualización**: 2025-01-08  
**Versión**: 1.0.0  
**Autor**: Akira Traders Team