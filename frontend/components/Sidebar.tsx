import { Link } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Settings, 
  Activity, 
  Smartphone, 
  Monitor,
  Play,
  Pause,
  Square
} from 'lucide-react';
import { useBotStore } from '../stores';
import { cn } from '../utils/cn';

interface SidebarProps {
  currentPath: string;
}

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    description: 'Overview and quick actions'
  },
  {
    name: 'Monitoring',
    href: '/monitoring',
    icon: Activity,
    description: 'Real-time bot monitoring'
  },
  {
    name: 'Devices',
    href: '/devices',
    icon: Smartphone,
    description: 'Connected devices management'
  },
  {
    name: 'System',
    href: '/system',
    icon: Monitor,
    description: 'System information and logs'
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'Bot configuration and preferences'
  }
];

export default function Sidebar({ currentPath }: SidebarProps) {
  const { status, isRunning, startBot, stopBot, togglePause } = useBotStore();

  const handleQuickAction = async (action: string) => {
    try {
      switch (action) {
        case 'start':
          await startBot();
          break;
        case 'stop':
          await stopBot();
          break;
        case 'pause':
          await togglePause();
          break;
      }
    } catch (error) {
      console.error(`Failed to ${action} bot:`, error);
    }
  };

  return (
    <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-colors duration-200">
      {/* Logo and Title */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">RR</span>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              Rush Royale Bot
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              macOS Edition
            </p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
          Quick Actions
        </h3>
        <div className="space-y-2">
          <button
            onClick={() => handleQuickAction(isRunning ? 'stop' : 'start')}
            className={cn(
              "w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              isRunning
                ? "bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/30"
                : "bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/20 dark:text-green-400 dark:hover:bg-green-900/30"
            )}
          >
            {isRunning ? (
              <Square className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>{isRunning ? 'Stop Bot' : 'Start Bot'}</span>
          </button>
          
          {isRunning && (
            <button
              onClick={() => handleQuickAction('pause')}
              className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium bg-yellow-100 text-yellow-700 hover:bg-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:hover:bg-yellow-900/30 transition-colors"
            >
              <Pause className="w-4 h-4" />
              <span>{status === 'paused' ? 'Resume' : 'Pause'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <h3 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
          Navigation
        </h3>
        <ul className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.href || (currentPath === '/' && item.href === '/dashboard');
            
            return (
              <li key={item.name}>
                <Link
                  to={item.href}
                  className={cn(
                    "group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                    isActive
                      ? "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400"
                      : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                  )}
                  title={item.description}
                >
                  <Icon className={cn(
                    "w-5 h-5 mr-3 transition-colors",
                    isActive
                      ? "text-blue-500 dark:text-blue-400"
                      : "text-gray-400 group-hover:text-gray-500 dark:text-gray-500 dark:group-hover:text-gray-400"
                  )} />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Status Indicator */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <div className={cn(
            "w-2 h-2 rounded-full",
            isRunning ? "bg-green-500" : "bg-gray-400"
          )} />
          <span className="text-xs text-gray-500 dark:text-gray-400">
            Bot {isRunning ? 'Running' : 'Stopped'}
          </span>
        </div>
      </div>
    </div>
  );
}