import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useSystemStore } from './stores/systemStore';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import Monitoring from './pages/Monitoring';
import Devices from './pages/Devices';
import System from './pages/System';
import { Loader2 } from 'lucide-react';

const AppContent: React.FC = () => {
  const { preferences, initializeSystem } = useSystemStore();
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();

  // Initialize the application
  useEffect(() => {
    const initApp = async () => {
      try {
        await initializeSystem();
      } catch (error) {
        console.error('Failed to initialize application:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initApp();
  }, [initializeSystem]);

  // Apply theme preferences
  useEffect(() => {
    const root = document.documentElement;
    
    // Apply theme
    if (preferences.theme === 'dark' || (preferences.theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [preferences.theme]);

  // Apply accessibility preferences
  useEffect(() => {
    const root = document.documentElement;
    
    // Reduce motion
    if (preferences.reducedMotion) {
      root.style.setProperty('--motion-reduce', '1');
    } else {
      root.style.removeProperty('--motion-reduce');
    }
    
    // High contrast
    if (preferences.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }
    
    // Transparency
    if (!preferences.transparency) {
      root.classList.add('no-transparency');
    } else {
      root.classList.remove('no-transparency');
    }
  }, [preferences.reducedMotion, preferences.highContrast, preferences.transparency]);

  // Apply accent color
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--accent-color', preferences.accentColor);
  }, [preferences.accentColor]);

  // Loading screen
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Rush Royale Bot
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Initializing application...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Sidebar */}
      <Sidebar currentPath={location.pathname} />
      
      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/monitoring" element={<Monitoring />} />
          <Route path="/devices" element={<Devices />} />
          <Route path="/system" element={<System />} />
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;
