import { Cpu, HardDrive, Wifi, Battery, Clock } from 'lucide-react';
import { useState, useEffect } from 'react';
import { cn } from '../utils/cn';

interface StatusBarProps {
  botStatus: string;
  deviceCount: number;
  systemInfo: any;
}

export default function StatusBar({ botStatus, deviceCount, systemInfo }: StatusBarProps) {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [systemStats, setSystemStats] = useState({
    cpu: 0,
    memory: 0,
    battery: 100,
    isCharging: false
  });

  useEffect(() => {
    // Listen for system performance updates
    if (window.electronAPI) {
      const perfHandler = (_event: any, stats: any) => {
        if (stats && stats.cpu !== undefined && stats.memory !== undefined) {
          setSystemStats(prev => ({
            ...prev,
            cpu: stats.cpu,
            memory: stats.memory
          }));
        }
      };

      const batteryHandler = (_event: any, level: number) => {
        setSystemStats(prev => ({
          ...prev,
          battery: level
        }));
      };

      window.electronAPI.on('system:performance-stats', perfHandler);
      window.electronAPI.on('system:battery-level', batteryHandler);

      // Update time every second
      const timeInterval = setInterval(() => {
        setCurrentTime(new Date());
      }, 1000);

      return () => {
        window.electronAPI.off('system:performance-stats', perfHandler);
        window.electronAPI.off('system:battery-level', batteryHandler);
        clearInterval(timeInterval);
      };
    }

    // Fallback: only update time if electronAPI is not available
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => {
      clearInterval(timeInterval);
    };
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-green-600 dark:text-green-400';
      case 'paused':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'error':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getBatteryColor = (level: number) => {
    if (level > 50) return 'text-green-600 dark:text-green-400';
    if (level > 20) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="h-8 bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between px-4 text-xs transition-colors duration-200">
      {/* Left Section - Bot Status */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className={cn(
            "w-1.5 h-1.5 rounded-full",
            botStatus === 'running' ? "bg-green-500" :
            botStatus === 'paused' ? "bg-yellow-500" :
            botStatus === 'error' ? "bg-red-500" : "bg-gray-400"
          )} />
          <span className={cn("font-medium", getStatusColor(botStatus))}>
            Bot: {botStatus || 'Stopped'}
          </span>
        </div>
        
        <div className="text-gray-600 dark:text-gray-400">
          Devices: {deviceCount}
        </div>
      </div>

      {/* Center Section - System Stats */}
      <div className="flex items-center space-x-6">
        {/* CPU Usage */}
        <div className="flex items-center space-x-1">
          <Cpu className="w-3 h-3 text-gray-500" />
          <span className="text-gray-600 dark:text-gray-400">
            CPU: {systemStats.cpu.toFixed(1)}%
          </span>
        </div>

        {/* Memory Usage */}
        <div className="flex items-center space-x-1">
          <HardDrive className="w-3 h-3 text-gray-500" />
          <span className="text-gray-600 dark:text-gray-400">
            RAM: {systemStats.memory.toFixed(1)}%
          </span>
        </div>

        {/* Network Status */}
        <div className="flex items-center space-x-1">
          <Wifi className="w-3 h-3 text-green-500" />
          <span className="text-gray-600 dark:text-gray-400">
            Connected
          </span>
        </div>

        {/* Battery (if available) */}
        {systemInfo?.platform === 'darwin' && (
          <div className="flex items-center space-x-1">
            <Battery className={cn("w-3 h-3", getBatteryColor(systemStats.battery))} />
            <span className={cn(getBatteryColor(systemStats.battery))}>
              {systemStats.battery}%{systemStats.isCharging ? ' ⚡' : ''}
            </span>
          </div>
        )}
      </div>

      {/* Right Section - Time and System Info */}
      <div className="flex items-center space-x-4">
        {/* System Info */}
        {systemInfo && (
          <div className="text-gray-600 dark:text-gray-400">
            {systemInfo.platform} {systemInfo.arch}
          </div>
        )}
        
        {/* Current Time */}
        <div className="flex items-center space-x-1">
          <Clock className="w-3 h-3 text-gray-500" />
          <span className="text-gray-600 dark:text-gray-400 font-mono">
            {formatTime(currentTime)}
          </span>
        </div>
      </div>
    </div>
  );
}