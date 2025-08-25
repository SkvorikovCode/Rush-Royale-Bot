import { ReactNode } from 'react';
import { useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import StatusBar from './StatusBar';
import { useBotStore, useDeviceStore, useSystemStore } from '../stores';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const { status: botStatus } = useBotStore();
  const { devices } = useDeviceStore();
  const connectedDevices = devices.filter(device => device.status === 'connected');
  const { systemInfo } = useSystemStore();

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Sidebar */}
      <Sidebar currentPath={location.pathname} />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header 
          title={getPageTitle(location.pathname)}
          botStatus={botStatus}
          connectedDevices={connectedDevices.length}
          systemInfo={systemInfo}
        />
        
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-white dark:bg-gray-800 transition-colors duration-200">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
        
        {/* Status Bar */}
        <StatusBar 
          botStatus={botStatus}
          deviceCount={connectedDevices.length}
          systemInfo={systemInfo}
        />
      </div>
    </div>
  );
}

function getPageTitle(pathname: string): string {
  switch (pathname) {
    case '/':
    case '/dashboard':
      return 'Dashboard';
    case '/settings':
      return 'Settings';
    case '/monitoring':
      return 'Monitoring';
    case '/devices':
      return 'Devices';
    case '/system':
      return 'System';
    default:
      return 'Rush Royale Bot';
  }
}