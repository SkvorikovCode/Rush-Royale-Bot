# macOS UI/UX Design System & Specifications

## 1. Design Philosophy

### 1.1 Core Principles

**Native macOS Experience**
- Следование Human Interface Guidelines от Apple
- Использование системных компонентов и паттернов
- Интеграция с macOS ecosystem (Dock, Menu Bar, Notifications)

**Performance-First Design**
- Оптимизация для Apple Silicon (M1/M2)
- Эффективное использование Unified Memory Architecture
- Плавные анимации с 60+ FPS

**Accessibility & Inclusivity**
- Поддержка VoiceOver и других assistive technologies
- Высокий контраст и читаемость
- Keyboard navigation и shortcuts

### 1.2 Visual Language

**Depth & Layering**
- Использование системных теней и размытия
- Vibrancy effects для прозрачности
- Z-index hierarchy для логической группировки

**Motion & Animation**
- Easing functions: `cubic-bezier(0.25, 0.46, 0.45, 0.94)` (ease-out)
- Duration: 200ms для micro-interactions, 400ms для transitions
- Spring animations для естественного движения

## 2. Color System

### 2.1 Semantic Colors

```css
:root {
  /* Primary Colors */
  --color-primary: #007AFF;           /* System Blue */
  --color-primary-hover: #0056CC;
  --color-primary-active: #004499;
  
  /* Secondary Colors */
  --color-secondary: #34C759;         /* System Green */
  --color-secondary-hover: #28A745;
  --color-secondary-active: #1E7E34;
  
  /* Status Colors */
  --color-success: #34C759;           /* System Green */
  --color-warning: #FF9500;           /* System Orange */
  --color-error: #FF3B30;             /* System Red */
  --color-info: #5AC8FA;              /* System Light Blue */
  
  /* Neutral Colors - Light Mode */
  --color-background: #FFFFFF;
  --color-background-secondary: #F2F2F7;
  --color-background-tertiary: #FFFFFF;
  --color-surface: #FFFFFF;
  --color-surface-secondary: #F2F2F7;
  
  /* Text Colors - Light Mode */
  --color-text-primary: #000000;
  --color-text-secondary: #3C3C43;
  --color-text-tertiary: #3C3C4399;   /* 60% opacity */
  --color-text-quaternary: #3C3C434D; /* 30% opacity */
  
  /* Border Colors */
  --color-border: #3C3C4329;          /* 16% opacity */
  --color-border-secondary: #3C3C431F; /* 12% opacity */
}

@media (prefers-color-scheme: dark) {
  :root {
    /* Neutral Colors - Dark Mode */
    --color-background: #000000;
    --color-background-secondary: #1C1C1E;
    --color-background-tertiary: #2C2C2E;
    --color-surface: #1C1C1E;
    --color-surface-secondary: #2C2C2E;
    
    /* Text Colors - Dark Mode */
    --color-text-primary: #FFFFFF;
    --color-text-secondary: #EBEBF5;
    --color-text-tertiary: #EBEBF599;   /* 60% opacity */
    --color-text-quaternary: #EBEBF54D; /* 30% opacity */
    
    /* Border Colors - Dark Mode */
    --color-border: #EBEBF529;          /* 16% opacity */
    --color-border-secondary: #EBEBF51F; /* 12% opacity */
  }
}
```

### 2.2 Game-Specific Colors

```css
:root {
  /* Rush Royale Themed Colors */
  --color-game-primary: #8B5CF6;      /* Purple for magic theme */
  --color-game-secondary: #F59E0B;    /* Gold for rewards */
  --color-game-accent: #EF4444;       /* Red for combat */
  
  /* Unit Type Colors */
  --color-unit-dps: #DC2626;          /* Red for DPS units */
  --color-unit-support: #059669;      /* Green for support */
  --color-unit-tank: #1D4ED8;         /* Blue for tanks */
  --color-unit-special: #7C3AED;      /* Purple for special */
  
  /* Battle Status Colors */
  --color-battle-active: #F59E0B;     /* Orange for active battle */
  --color-battle-victory: #10B981;    /* Green for victory */
  --color-battle-defeat: #EF4444;     /* Red for defeat */
  --color-battle-waiting: #6B7280;    /* Gray for waiting */
}
```

## 3. Typography System

### 3.1 Font Stack

```css
:root {
  /* Primary Font Family - SF Pro */
  --font-family-primary: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-secondary: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-mono: 'SF Mono', 'Monaco', 'Consolas', monospace;
  
  /* Font Weights */
  --font-weight-light: 300;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-heavy: 800;
}
```

### 3.2 Type Scale

```css
/* Typography Scale - Following Apple's guidelines */
.text-caption2 {
  font-family: var(--font-family-secondary);
  font-size: 11px;
  line-height: 13px;
  font-weight: var(--font-weight-regular);
}

.text-caption1 {
  font-family: var(--font-family-secondary);
  font-size: 12px;
  line-height: 16px;
  font-weight: var(--font-weight-regular);
}

.text-footnote {
  font-family: var(--font-family-secondary);
  font-size: 13px;
  line-height: 18px;
  font-weight: var(--font-weight-regular);
}

.text-subheadline {
  font-family: var(--font-family-secondary);
  font-size: 15px;
  line-height: 20px;
  font-weight: var(--font-weight-regular);
}

.text-callout {
  font-family: var(--font-family-secondary);
  font-size: 16px;
  line-height: 21px;
  font-weight: var(--font-weight-regular);
}

.text-body {
  font-family: var(--font-family-secondary);
  font-size: 17px;
  line-height: 22px;
  font-weight: var(--font-weight-regular);
}

.text-headline {
  font-family: var(--font-family-primary);
  font-size: 17px;
  line-height: 22px;
  font-weight: var(--font-weight-semibold);
}

.text-title3 {
  font-family: var(--font-family-primary);
  font-size: 20px;
  line-height: 25px;
  font-weight: var(--font-weight-regular);
}

.text-title2 {
  font-family: var(--font-family-primary);
  font-size: 22px;
  line-height: 28px;
  font-weight: var(--font-weight-bold);
}

.text-title1 {
  font-family: var(--font-family-primary);
  font-size: 28px;
  line-height: 34px;
  font-weight: var(--font-weight-bold);
}

.text-large-title {
  font-family: var(--font-family-primary);
  font-size: 34px;
  line-height: 41px;
  font-weight: var(--font-weight-regular);
}
```

## 4. Component Library

### 4.1 Button Components

```tsx
// components/Button/Button.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600',
        destructive: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
        ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:bg-gray-800',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  className,
  variant,
  size,
  loading,
  children,
  disabled,
  ...props
}) => {
  return (
    <button
      className={buttonVariants({ variant, size, className })}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )}
      {children}
    </button>
  );
};
```

### 4.2 Card Components

```tsx
// components/Card/Card.tsx
import React from 'react';
import { cn } from '../../utils/cn';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card: React.FC<CardProps> = ({
  className,
  variant = 'default',
  padding = 'md',
  children,
  ...props
}) => {
  const cardClasses = cn(
    'rounded-xl transition-all duration-200',
    {
      // Variants
      'bg-white dark:bg-gray-800 shadow-sm': variant === 'default',
      'bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl': variant === 'elevated',
      'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700': variant === 'outlined',
      
      // Padding
      'p-0': padding === 'none',
      'p-3': padding === 'sm',
      'p-4': padding === 'md',
      'p-6': padding === 'lg',
    },
    className
  );

  return (
    <div className={cardClasses} {...props}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={cn('pb-3 border-b border-gray-200 dark:border-gray-700', className)} {...props}>
    {children}
  </div>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={cn('pt-3', className)} {...props}>
    {children}
  </div>
);
```

### 4.3 Status Indicator Components

```tsx
// components/StatusIndicator/StatusIndicator.tsx
import React from 'react';
import { cn } from '../../utils/cn';

type StatusType = 'online' | 'offline' | 'connecting' | 'error' | 'warning';

interface StatusIndicatorProps {
  status: StatusType;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  showPulse?: boolean;
}

const statusConfig = {
  online: {
    color: 'bg-green-500',
    label: 'Онлайн',
    textColor: 'text-green-700 dark:text-green-400'
  },
  offline: {
    color: 'bg-gray-400',
    label: 'Офлайн',
    textColor: 'text-gray-700 dark:text-gray-400'
  },
  connecting: {
    color: 'bg-yellow-500',
    label: 'Подключение...',
    textColor: 'text-yellow-700 dark:text-yellow-400'
  },
  error: {
    color: 'bg-red-500',
    label: 'Ошибка',
    textColor: 'text-red-700 dark:text-red-400'
  },
  warning: {
    color: 'bg-orange-500',
    label: 'Предупреждение',
    textColor: 'text-orange-700 dark:text-orange-400'
  }
};

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  size = 'md',
  showPulse = false
}) => {
  const config = statusConfig[status];
  const displayLabel = label || config.label;
  
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };

  return (
    <div className="flex items-center space-x-2">
      <div className="relative">
        <div className={cn(
          'rounded-full',
          config.color,
          sizeClasses[size]
        )} />
        {showPulse && (
          <div className={cn(
            'absolute inset-0 rounded-full animate-ping',
            config.color,
            'opacity-75'
          )} />
        )}
      </div>
      {displayLabel && (
        <span className={cn('text-sm font-medium', config.textColor)}>
          {displayLabel}
        </span>
      )}
    </div>
  );
};
```

## 5. Layout System

### 5.1 Sidebar Navigation

```tsx
// components/Layout/Sidebar.tsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '../../utils/cn';

interface SidebarItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  badge?: string | number;
}

interface SidebarProps {
  items: SidebarItem[];
  collapsed?: boolean;
  onToggle?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  items,
  collapsed = false,
  onToggle
}) => {
  return (
    <div className={cn(
      'flex flex-col h-full bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transition-all duration-300',
      collapsed ? 'w-16' : 'w-64'
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        {!collapsed && (
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
            Rush Royale Bot
          </h1>
        )}
        <button
          onClick={onToggle}
          className="p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1">
        {items.map((item) => (
          <NavLink
            key={item.id}
            to={item.path}
            className={({ isActive }) => cn(
              'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              'hover:bg-gray-200 dark:hover:bg-gray-800',
              isActive
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                : 'text-gray-700 dark:text-gray-300'
            )}
          >
            <item.icon className={cn('flex-shrink-0 w-5 h-5', !collapsed && 'mr-3')} />
            {!collapsed && (
              <>
                <span className="flex-1">{item.label}</span>
                {item.badge && (
                  <span className="ml-2 px-2 py-1 text-xs bg-red-500 text-white rounded-full">
                    {item.badge}
                  </span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </div>
  );
};
```

### 5.2 Main Layout

```tsx
// components/Layout/MainLayout.tsx
import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { useGestures } from '../../hooks/useGestures';
import { sidebarItems } from '../../config/navigation';

export const MainLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Настройка жестов трекпада
  useGestures({
    onSwipeLeft: () => setSidebarCollapsed(true),
    onSwipeRight: () => setSidebarCollapsed(false),
    onPinch: (scale) => {
      // Масштабирование интерфейса
      document.documentElement.style.fontSize = `${Math.max(12, Math.min(20, 16 * scale))}px`;
    }
  });

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      <Sidebar
        items={sidebarItems}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar />
        
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
```

## 6. Animation System

### 6.1 Transition Utilities

```css
/* animations.css */
@keyframes slideInFromLeft {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideInFromRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* Utility classes */
.animate-slide-in-left {
  animation: slideInFromLeft 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.animate-slide-in-right {
  animation: slideInFromRight 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.animate-fade-in-up {
  animation: fadeInUp 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.animate-scale-in {
  animation: scaleIn 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* Stagger animations */
.stagger-children > * {
  animation-delay: calc(var(--stagger-delay, 0.1s) * var(--index, 0));
}
```

### 6.2 React Animation Components

```tsx
// components/Animation/FadeIn.tsx
import React, { useEffect, useRef, useState } from 'react';
import { cn } from '../../utils/cn';

interface FadeInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  direction?: 'up' | 'down' | 'left' | 'right' | 'none';
  className?: string;
}

export const FadeIn: React.FC<FadeInProps> = ({
  children,
  delay = 0,
  duration = 400,
  direction = 'up',
  className
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTimeout(() => setIsVisible(true), delay);
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [delay]);

  const getTransform = () => {
    if (isVisible) return 'translate3d(0, 0, 0)';
    
    switch (direction) {
      case 'up': return 'translate3d(0, 20px, 0)';
      case 'down': return 'translate3d(0, -20px, 0)';
      case 'left': return 'translate3d(-20px, 0, 0)';
      case 'right': return 'translate3d(20px, 0, 0)';
      default: return 'translate3d(0, 0, 0)';
    }
  };

  return (
    <div
      ref={ref}
      className={cn('transition-all ease-out', className)}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: getTransform(),
        transitionDuration: `${duration}ms`
      }}
    >
      {children}
    </div>
  );
};
```

## 7. Responsive Design

### 7.1 Breakpoint System

```css
/* Tailwind CSS custom breakpoints for macOS */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  /* Custom breakpoints for macOS screen sizes */
  .container {
    @apply mx-auto px-4;
  }
  
  /* MacBook Air 13" */
  @media (min-width: 1280px) {
    .container {
      max-width: 1200px;
    }
  }
  
  /* MacBook Pro 14" */
  @media (min-width: 1512px) {
    .container {
      max-width: 1400px;
    }
  }
  
  /* MacBook Pro 16" */
  @media (min-width: 1728px) {
    .container {
      max-width: 1600px;
    }
  }
  
  /* iMac 24" */
  @media (min-width: 2240px) {
    .container {
      max-width: 2000px;
    }
  }
  
  /* Studio Display / Pro Display XDR */
  @media (min-width: 2560px) {
    .container {
      max-width: 2400px;
    }
  }
}
```

### 7.2 Retina Display Optimization

```css
/* Retina display optimizations */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  /* High-DPI optimizations */
  .icon {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
  }
  
  /* Thin borders for Retina */
  .border-thin {
    border-width: 0.5px;
  }
  
  /* Sharp text rendering */
  body {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
}

/* 3x Retina displays (Pro Display XDR) */
@media (-webkit-min-device-pixel-ratio: 3), (min-resolution: 288dpi) {
  .ultra-sharp {
    image-rendering: pixelated;
  }
}
```

## 8. Accessibility Features

### 8.1 Focus Management

```css
/* Focus styles following macOS guidelines */
.focus-ring {
  @apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2;
}

.focus-ring-inset {
  @apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .focus-ring {
    @apply focus:ring-4 focus:ring-blue-600;
  }
  
  .border {
    @apply border-2;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 8.2 Screen Reader Support

```tsx
// components/Accessibility/ScreenReaderOnly.tsx
import React from 'react';

interface ScreenReaderOnlyProps {
  children: React.ReactNode;
}

export const ScreenReaderOnly: React.FC<ScreenReaderOnlyProps> = ({ children }) => (
  <span className="sr-only">
    {children}
  </span>
);

// components/Accessibility/LiveRegion.tsx
import React, { useEffect, useRef } from 'react';

interface LiveRegionProps {
  message: string;
  politeness?: 'polite' | 'assertive';
}

export const LiveRegion: React.FC<LiveRegionProps> = ({ 
  message, 
  politeness = 'polite' 
}) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current && message) {
      ref.current.textContent = message;
    }
  }, [message]);

  return (
    <div
      ref={ref}
      aria-live={politeness}
      aria-atomic="true"
      className="sr-only"
    />
  );
};
```

Эта дизайн-система обеспечивает полную интеграцию с macOS, следуя всем стандартам платформы и обеспечивая современный, доступный и производительный пользовательский интерфейс для Rush Royale Bot.