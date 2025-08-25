import React, { useState, useEffect } from 'react';
import { useSystemStore } from '../stores/systemStore';
import { 
  Monitor,
  Cpu,
  HardDrive,
  Battery,
  Thermometer,
  Fan,
  Activity,
  Settings,
  RefreshCw,
  Zap,
  MemoryStick,
  Clock,
  Apple,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  X
} from 'lucide-react';

const System: React.FC = () => {
  const {
    systemInfo,
    powerInfo,
    preferences,
    performance,
    displays,
    initializeSystem,
    refreshSystemInfo,
    refreshPerformanceMetrics
  } = useSystemStore();

  const [activeTab, setActiveTab] = useState<'overview' | 'performance' | 'displays' | 'power' | 'preferences'>('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);

  // Initialize system store on component mount
  useEffect(() => {
    initializeSystem();
  }, [initializeSystem]);

  // Auto-refresh system information
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refreshSystemInfo();
      refreshPerformanceMetrics();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refreshSystemInfo, refreshPerformanceMetrics]);

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  const getPerformanceColor = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return 'text-red-600 dark:text-red-400';
    if (value >= thresholds.warning) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-green-600 dark:text-green-400';
  };

  const getPerformanceIcon = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return <AlertTriangle className="w-4 h-4 text-red-500" />;
    if (value >= thresholds.warning) return <TrendingUp className="w-4 h-4 text-yellow-500" />;
    return <CheckCircle className="w-4 h-4 text-green-500" />;
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* System Information */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          System Information
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Platform */}
          <div className="flex items-center space-x-3">
            <Apple className="w-6 h-6 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {systemInfo?.platform} {systemInfo?.version}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Platform
              </p>
            </div>
          </div>
          
          {/* Architecture */}
          <div className="flex items-center space-x-3">
            <Cpu className="w-6 h-6 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {systemInfo?.arch} {systemInfo?.isAppleSilicon ? '(Apple Silicon)' : ''}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Architecture
              </p>
            </div>
          </div>
          
          {/* Hostname */}
          <div className="flex items-center space-x-3">
            <Monitor className="w-6 h-6 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {systemInfo?.hostname}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Hostname
              </p>
            </div>
          </div>
          
          {/* CPU Model */}
          <div className="flex items-center space-x-3">
            <Zap className="w-6 h-6 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {systemInfo?.cpuModel}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                CPU ({systemInfo?.cpuCores} cores)
              </p>
            </div>
          </div>
          
          {/* Total Memory */}
          <div className="flex items-center space-x-3">
            <MemoryStick className="w-6 h-6 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {formatBytes(systemInfo?.totalMemory || 0)}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Total Memory
              </p>
            </div>
          </div>
          
          {/* Uptime */}
          <div className="flex items-center space-x-3">
            <Clock className="w-6 h-6 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {formatUptime(systemInfo?.uptime || 0)}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Uptime
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* CPU Usage */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Cpu className="w-5 h-5 text-blue-500" />
              <span className="text-sm font-medium text-gray-900 dark:text-white">CPU</span>
            </div>
            {getPerformanceIcon(performance?.cpuUsage || 0, { warning: 70, critical: 90 })}
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className={`text-2xl font-bold ${getPerformanceColor(performance?.cpuUsage || 0, { warning: 70, critical: 90 })}`}>
                 {(performance?.cpuUsage || 0).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  (performance?.cpuUsage || 0) >= 90 ? 'bg-red-500' :
                   (performance?.cpuUsage || 0) >= 70 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(performance?.cpuUsage || 0, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Memory Usage */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <MemoryStick className="w-5 h-5 text-green-500" />
              <span className="text-sm font-medium text-gray-900 dark:text-white">Memory</span>
            </div>
            {getPerformanceIcon(performance?.memoryUsage?.percentage || 0, { warning: 80, critical: 95 })}
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className={`text-2xl font-bold ${getPerformanceColor(performance?.memoryUsage?.percentage || 0, { warning: 80, critical: 95 })}`}>
                 {(performance?.memoryUsage?.percentage || 0).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  (performance?.memoryUsage?.percentage || 0) >= 95 ? 'bg-red-500' :
                   (performance?.memoryUsage?.percentage || 0) >= 80 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(performance?.memoryUsage?.percentage || 0, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Disk Usage */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <HardDrive className="w-5 h-5 text-purple-500" />
              <span className="text-sm font-medium text-gray-900 dark:text-white">Disk</span>
            </div>
            {getPerformanceIcon(performance?.diskUsage?.percentage || 0, { warning: 85, critical: 95 })}
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className={`text-2xl font-bold ${getPerformanceColor(performance?.diskUsage?.percentage || 0, { warning: 85, critical: 95 })}`}>
                 {(performance?.diskUsage?.percentage || 0).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  (performance?.diskUsage?.percentage || 0) >= 95 ? 'bg-red-500' :
                   (performance?.diskUsage?.percentage || 0) >= 85 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(performance?.diskUsage?.percentage || 0, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Temperature */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Thermometer className="w-5 h-5 text-red-500" />
              <span className="text-sm font-medium text-gray-900 dark:text-white">Temp</span>
            </div>
            {getPerformanceIcon(performance?.temperature?.cpu || 0, { warning: 70, critical: 85 })}
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className={`text-2xl font-bold ${getPerformanceColor(performance?.temperature?.cpu || 0, { warning: 70, critical: 85 })}`}>
                 {(performance?.temperature?.cpu || 0).toFixed(0)}°C
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  (performance?.temperature?.cpu || 0) >= 85 ? 'bg-red-500' :
                   (performance?.temperature?.cpu || 0) >= 70 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(((performance?.temperature?.cpu || 0) / 100) * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Power Information */}
      {powerInfo?.batteryLevel !== undefined && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Power Status
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center space-x-3">
              <Battery className="w-6 h-6 text-green-500" />
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {powerInfo?.batteryLevel}%
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Battery Level
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Zap className="w-6 h-6 text-blue-500" />
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {powerInfo?.isCharging ? 'Charging' : 'Not Charging'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Charging Status
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Clock className="w-6 h-6 text-purple-500" />
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {powerInfo?.timeRemaining ? `${Math.floor(powerInfo.timeRemaining / 60)}h ${powerInfo.timeRemaining % 60}m` : 'Unknown'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Time Remaining
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderPerformance = () => (
    <div className="space-y-6">
      {/* Performance Metrics */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Performance Metrics
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* CPU Details */}
          <div className="space-y-4">
            <h4 className="text-md font-medium text-gray-900 dark:text-white">CPU Usage</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Overall</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {(performance?.cpuUsage || 0).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(performance?.cpuUsage || 0, 100)}%` }}
                />
              </div>
            </div>
          </div>

          {/* Memory Details */}
          <div className="space-y-4">
            <h4 className="text-md font-medium text-gray-900 dark:text-white">Memory Usage</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Used</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {formatBytes(performance?.memoryUsage?.used || 0)} / {formatBytes(systemInfo?.totalMemory || 0)}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(performance?.memoryUsage?.percentage || 0, 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Network Activity */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Network Activity
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-6 h-6 text-green-500" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {formatBytes(performance?.networkActivity?.bytesSent || 0)}/s
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Upload Speed
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <TrendingDown className="w-6 h-6 text-blue-500" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {formatBytes(performance?.networkActivity?.bytesReceived || 0)}/s
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Download Speed
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Thermal Information */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Thermal Information
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-center space-x-3">
            <Thermometer className="w-6 h-6 text-red-500" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {(performance?.temperature?.cpu || 0).toFixed(1)}°C
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                CPU Temperature
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Fan className="w-6 h-6 text-blue-500" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {(performance?.fanSpeed || 0).toFixed(0)} RPM
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Fan Speed
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderDisplays = () => (
    <div className="space-y-6">
      {displays.map((display) => (
        <div key={display.id} className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {display.name} {display.isPrimary && '(Primary)'}
            </h3>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 text-xs rounded-full ${
                display.isInternal 
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                  : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              }`}>
                {display.isInternal ? 'Internal' : 'External'}
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {display.bounds.width} × {display.bounds.height}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Resolution</p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {display.scaleFactor}×
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Scale Factor</p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {display.rotation}°
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Rotation</p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {display.colorSpace}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Color Space</p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {display.colorDepth}-bit
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Color Depth</p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {display.workArea.width} × {display.workArea.height}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Work Area</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderPower = () => (
    <div className="space-y-6">
      {powerInfo?.batteryLevel !== undefined ? (
        <>
          {/* Battery Status */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Battery Status
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Battery Level</span>
                <span className="text-lg font-semibold text-gray-900 dark:text-white">
                  {powerInfo.batteryLevel}%
                </span>
              </div>
              
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all duration-300 ${
                    (powerInfo?.batteryLevel || 0) <= 20 ? 'bg-red-500' :
                    (powerInfo?.batteryLevel || 0) <= 50 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${powerInfo?.batteryLevel || 0}%` }}
                />
              </div>
            </div>
          </div>

          {/* Power Details */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Power Details
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-center space-x-3">
                <Zap className="w-6 h-6 text-blue-500" />
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {powerInfo?.isCharging ? 'Charging' : 'Not Charging'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Charging Status
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Battery className="w-6 h-6 text-green-500" />
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {powerInfo?.powerSource}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Power Source
                  </p>
                </div>
              </div>
              
              {powerInfo?.timeRemaining && (
                <div className="flex items-center space-x-3">
                  <Clock className="w-6 h-6 text-purple-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {Math.floor(powerInfo.timeRemaining / 60)}h {powerInfo.timeRemaining % 60}m
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Time Remaining
                    </p>
                  </div>
                </div>
              )}
              
              <div className="flex items-center space-x-3">
                <Thermometer className="w-6 h-6 text-red-500" />
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {powerInfo?.thermalState}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Thermal State
                  </p>
                </div>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm border border-gray-200 dark:border-gray-700 text-center">
          <Battery className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            No battery information available
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
            This device appears to be connected to external power
          </p>
        </div>
      )}
    </div>
  );

  const renderPreferences = () => (
    <div className="space-y-6">
      {/* System Preferences */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          System Preferences
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Theme</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                {preferences.theme}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Accent Color</span>
              <div className="flex items-center space-x-2">
                <div 
                  className="w-4 h-4 rounded-full border border-gray-300 dark:border-gray-600"
                  style={{ backgroundColor: preferences.accentColor }}
                />
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {preferences.accentColor}
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Reduce Motion</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {preferences.reducedMotion ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">High Contrast</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {preferences.highContrast ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Transparency</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {preferences.transparency ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Window Controls */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Window Controls
        </h3>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={() => window.electronAPI?.minimizeWindow?.()}
            className="flex items-center px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg transition-colors"
          >
            <Minimize2 className="w-4 h-4 mr-2" />
            Minimize
          </button>
          
          <button
            onClick={() => window.electronAPI?.maximizeWindow?.()}
            className="flex items-center px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
          >
            <Maximize2 className="w-4 h-4 mr-2" />
            Maximize
          </button>
          
          <button
            onClick={() => window.close()}
            className="flex items-center px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
          >
            <X className="w-4 h-4 mr-2" />
            Close
          </button>
        </div>
      </div>
    </div>
  );

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Monitor },
    { id: 'performance', label: 'Performance', icon: Activity },
    { id: 'displays', label: 'Displays', icon: Monitor },
    { id: 'power', label: 'Power', icon: Battery },
    { id: 'preferences', label: 'Preferences', icon: Settings }
  ];

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            System
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitor system performance and manage macOS settings
          </p>
        </div>
        
        {/* Controls */}
        <div className="flex items-center space-x-4">
          {/* Auto Refresh Toggle */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`p-2 rounded-lg transition-colors ${
                autoRefresh 
                  ? 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
              }`}
            >
              {autoRefresh ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Auto Refresh
            </span>
          </div>
          
          {/* Refresh Interval */}
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            disabled={!autoRefresh}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          >
            <option value={1000}>1s</option>
            <option value={5000}>5s</option>
            <option value={10000}>10s</option>
            <option value={30000}>30s</option>
          </select>
          
          {/* Manual Refresh */}
          <button
            onClick={() => {
              refreshSystemInfo();
              refreshPerformanceMetrics();
            }}
            className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-6 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id as any)}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === id
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <Icon className="w-4 h-4 mr-2" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'performance' && renderPerformance()}
        {activeTab === 'displays' && renderDisplays()}
        {activeTab === 'power' && renderPower()}
        {activeTab === 'preferences' && renderPreferences()}
      </div>
    </div>
  );
};

export default System;