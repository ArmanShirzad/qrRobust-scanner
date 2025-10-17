// Frontend Performance Optimizations

import React, { memo, useMemo, useCallback } from 'react';
import { debounce } from 'lodash';

// Memoized components for better performance
export const MemoizedQRCodeCard = memo(({ qrCode, onEdit, onDelete }) => {
  const handleEdit = useCallback(() => {
    onEdit(qrCode.id);
  }, [qrCode.id, onEdit]);

  const handleDelete = useCallback(() => {
    onDelete(qrCode.id);
  }, [qrCode.id, onDelete]);

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <h3 className="text-lg font-semibold text-gray-800">{qrCode.title}</h3>
      <p className="text-gray-600 text-sm mt-1">{qrCode.description}</p>
      <div className="mt-3 flex justify-between items-center">
        <span className="text-sm text-gray-500">
          {qrCode.scan_count} scans
        </span>
        <div className="flex space-x-2">
          <button
            onClick={handleEdit}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
});

// Debounced search hook
export const useDebouncedSearch = (searchTerm, delay = 300) => {
  const [debouncedTerm, setDebouncedTerm] = React.useState(searchTerm);

  React.useEffect(() => {
    const handler = debounce(() => {
      setDebouncedTerm(searchTerm);
    }, delay);

    handler();

    return () => {
      handler.cancel();
    };
  }, [searchTerm, delay]);

  return debouncedTerm;
};

// Virtual scrolling for large lists
export const VirtualizedList = ({ items, itemHeight, renderItem }) => {
  const [scrollTop, setScrollTop] = React.useState(0);
  const containerHeight = 400; // Fixed container height

  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight),
      items.length
    );

    return items.slice(startIndex, endIndex).map((item, index) => ({
      ...item,
      index: startIndex + index,
    }));
  }, [items, scrollTop, itemHeight, containerHeight]);

  const totalHeight = items.length * itemHeight;
  const offsetY = Math.floor(scrollTop / itemHeight) * itemHeight;

  return (
    <div
      className="overflow-auto"
      style={{ height: containerHeight }}
      onScroll={(e) => setScrollTop(e.target.scrollTop)}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
          }}
        >
          {visibleItems.map((item) => (
            <div
              key={item.id}
              style={{ height: itemHeight }}
              className="border-b border-gray-200"
            >
              {renderItem(item)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Image lazy loading component
export const LazyImage = ({ src, alt, className, placeholder }) => {
  const [isLoaded, setIsLoaded] = React.useState(false);
  const [isInView, setIsInView] = React.useState(false);
  const imgRef = React.useRef();

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={imgRef} className={className}>
      {isInView && (
        <img
          src={src}
          alt={alt}
          onLoad={() => setIsLoaded(true)}
          className={`transition-opacity duration-300 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          }`}
        />
      )}
      {!isLoaded && placeholder && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-200">
          {placeholder}
        </div>
      )}
    </div>
  );
};

// Error boundary for better error handling
export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Here you would typically log to an error reporting service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg
                  className="h-8 w-8 text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-gray-800">
                  Something went wrong
                </h3>
                <div className="mt-2 text-sm text-gray-500">
                  <p>We're sorry, but something unexpected happened.</p>
                </div>
                <div className="mt-4">
                  <button
                    onClick={() => window.location.reload()}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                  >
                    Reload Page
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Performance monitoring hook
export const usePerformanceMonitor = (componentName) => {
  React.useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      if (renderTime > 16) { // More than one frame (16ms)
        console.warn(`${componentName} took ${renderTime.toFixed(2)}ms to render`);
      }
    };
  }, [componentName]);
};

// Bundle size optimization utilities
export const loadComponent = (importFunc) => {
  return React.lazy(() => importFunc());
};

// Preload critical components
export const preloadComponents = () => {
  // Preload components that are likely to be used
  import('./components/Dashboard');
  import('./components/QRCodeList');
  import('./components/Analytics');
};
