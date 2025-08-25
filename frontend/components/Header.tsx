import { Bell, Search, Settings, Moon, Sun } from 'lucide-react';
import { useSystemStore } from '../stores/systemStore';
import { cn } from '../utils/cn';

interface HeaderProps {
  title: string;
  botStatus: string;
  connectedDevices: number;
  systemInfo: any;
}

export default function Header({ title, botStatus, connectedDevices, systemInfo }: HeaderProps) {
  const { preferences, updatePreferences } = useSystemStore();
  
  const toggleTheme = () => {
    const newTheme = preferences.theme === 'dark' ? 'light' : 'dark';
    updatePreferences({ theme: newTheme });
  };

  const handleWindowAction = (action: string) => {
    if (window.electronAPI) {
      switch (action) {
        case 'minimize':
          window.electronAPI.minimizeWindow();
          break;
        case 'maximize':
          window.electronAPI.maximizeWindow();
          break;
        case 'close':
          window.electronAPI.closeWindow();
          break;
      }
    }
  };

  return (
    <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 transition-colors duration-200">
      {/* Left Section - Title and Status */}
      <div className="flex items-center space-x-4">
        <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
          {title}
        </h1>
        
        {/* Status Indicators */}
        <div className="flex items-center space-x-3">
          {/* Bot Status */}
          <div className="flex items-center space-x-2">
            <div className={cn(
              "w-2 h-2 rounded-full",
              botStatus === 'running' ? "bg-green-500" :
              botStatus === 'paused' ? "bg-yellow-500" :
              botStatus === 'error' ? "bg-red-500" : "bg-gray-400"
            )} />
            <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
              {botStatus || 'Stopped'}
            </span>
          </div>
          
          {/* Device Count */}
          <div className="flex items-center space-x-1 text-sm text-gray-600 dark:text-gray-400">
            <span>•</span>
            <span>{connectedDevices} device{connectedDevices !== 1 ? 's' : ''}</span>
          </div>
          
          {/* System Info */}
          {systemInfo && (
            <div className="flex items-center space-x-1 text-sm text-gray-600 dark:text-gray-400">
              <span>•</span>
              <span>{systemInfo.platform}</span>
              {systemInfo.arch && (
                <span className="text-xs">({systemInfo.arch})</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Center Section - Search */}
      <div className="flex-1 max-w-md mx-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search logs, devices, settings..."
            className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-700 border border-transparent rounded-lg text-sm text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
          />
        </div>
      </div>

      {/* Right Section - Actions */}
      <div className="flex items-center space-x-3">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 transition-colors"
          title={`Switch to ${preferences.theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {preferences.theme === 'dark' ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </button>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 transition-colors">
          <Bell className="w-5 h-5" />
          {/* Notification Badge */}
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full text-xs flex items-center justify-center">
            <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
          </span>
        </button>

        {/* Settings */}
        <button className="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 transition-colors">
          <Settings className="w-5 h-5" />
        </button>

        {/* Window Controls (macOS style) */}
        <div className="flex items-center space-x-2 ml-4 pl-4 border-l border-gray-200 dark:border-gray-700">
          <button
            onClick={() => handleWindowAction('minimize')}
            className="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-colors"
            title="Minimize"
          />
          <button
            onClick={() => handleWindowAction('maximize')}
            className="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-colors"
            title="Maximize"
          />
          <button
            onClick={() => handleWindowAction('close')}
            className="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors"
            title="Close"
          />
        </div>
      </div>
    </header>
  );
}