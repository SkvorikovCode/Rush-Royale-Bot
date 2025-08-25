import React, { useEffect, useState } from 'react';
import { useBotStore } from '../stores/botStore';
import { useDeviceStore } from '../stores/deviceStore';
import { useSystemStore } from '../stores/systemStore';
import { 
  Play, 
  Pause, 
  Square, 
  Smartphone, 
  Cpu, 
  Clock,
  TrendingUp,
  CheckCircle,
  XCircle
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const {
    status: botStatus,
    isRunning,
    isPaused,
    stats,
    currentGame,
    togglePause,
    quickStart
  } = useBotStore();

  const {
    devices,
    selectedDevice,
    scanDevices
  } = useDeviceStore();

  const {
    performance,
    powerInfo
  } = useSystemStore();

  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-500';
      case 'paused': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <CheckCircle className="w-5 h-5" />;
      case 'paused': return <Pause className="w-5 h-5" />;
      case 'error': return <XCircle className="w-5 h-5" />;
      default: return <Square className="w-5 h-5" />;
    }
  };

  const connectedDevices = devices.filter(d => d.status === 'connected');
  const winRate = stats.gamesPlayed > 0 ? (stats.gamesWon / stats.gamesPlayed * 100).toFixed(1) : '0';

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitor your Rush Royale bot performance and system status
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
          <Clock className="w-4 h-4" />
          <span>{currentTime.toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Bot Status */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Bot Status
              </p>
              <div className={`flex items-center space-x-2 mt-2 ${getStatusColor(botStatus)}`}>
                {getStatusIcon(botStatus)}
                <span className="text-lg font-semibold capitalize">
                  {botStatus}
                </span>
              </div>
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Play className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </div>

        {/* Connected Devices */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Connected Devices
              </p>
              <div className="flex items-center space-x-2 mt-2">
                <span className="text-2xl font-bold text-gray-900 dark:text-white">
                  {connectedDevices.length}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  / {devices.length}
                </span>
              </div>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <Smartphone className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>

        {/* Win Rate */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Win Rate
              </p>
              <div className="flex items-center space-x-2 mt-2">
                <span className="text-2xl font-bold text-gray-900 dark:text-white">
                  {winRate}%
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  ({stats.gamesWon}/{stats.gamesPlayed})
                </span>
              </div>
            </div>
            <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </div>

        {/* System Performance */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                CPU Usage
              </p>
              <div className="flex items-center space-x-2 mt-2">
                <span className="text-2xl font-bold text-gray-900 dark:text-white">
                  {performance?.cpuUsage?.toFixed(1) || '0'}%
                </span>
              </div>
            </div>
            <div className="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
              <Cpu className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bot Control Panel */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Bot Control
            </h2>
            
            {/* Quick Actions */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <button
                onClick={() => quickStart()}
                disabled={isRunning}
                className="flex flex-col items-center p-4 bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Play className="w-6 h-6 text-green-600 dark:text-green-400 mb-2" />
                <span className="text-sm font-medium text-green-700 dark:text-green-300">
                  Quick Start
                </span>
              </button>

              <button
                onClick={() => togglePause()}
                disabled={!isRunning}
                className="flex flex-col items-center p-4 bg-yellow-50 dark:bg-yellow-900/20 hover:bg-yellow-100 dark:hover:bg-yellow-900/30 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Pause className="w-6 h-6 text-yellow-600 dark:text-yellow-400 mb-2" />
                <span className="text-sm font-medium text-yellow-700 dark:text-yellow-300">
                  {isPaused ? 'Resume' : 'Pause'}
                </span>
              </button>



              <button
                onClick={() => scanDevices()}
                className="flex flex-col items-center p-4 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
              >
                <Smartphone className="w-6 h-6 text-blue-600 dark:text-blue-400 mb-2" />
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                  Scan Devices
                </span>
              </button>
            </div>

            {/* Current Game Info */}
            {currentGame.game_id && (
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                  Current Game
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Mode:</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {currentGame.mode || 'Unknown'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Round:</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {currentGame.round}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Score:</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {currentGame.score.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Duration:</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {currentGame.start_time 
                        ? Math.floor((Date.now() - new Date(currentGame.start_time).getTime()) / 60000) + 'm'
                        : '0m'
                      }
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Statistics */}
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                Session Statistics
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stats.gamesPlayed}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Games Played
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {stats.gamesWon}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Wins
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                    {stats.coinsEarned.toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Coins Earned
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {Math.floor(stats.totalPlayTime / 60)}h {stats.totalPlayTime % 60}m
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Play Time
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="space-y-6">
          {/* Device Status */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Device Status
            </h3>
            
            {selectedDevice ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Selected Device
                  </span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {selectedDevice.name}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Status
                  </span>
                  <span className={`text-sm font-medium capitalize ${
                    selectedDevice.status === 'connected' ? 'text-green-600 dark:text-green-400' :
                    selectedDevice.status === 'disconnected' ? 'text-red-600 dark:text-red-400' :
                    'text-yellow-600 dark:text-yellow-400'
                  }`}>
                    {selectedDevice.status}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Resolution
                  </span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {selectedDevice.resolution.width}×{selectedDevice.resolution.height}
                  </span>
                </div>
                {selectedDevice.batteryLevel && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Battery
                    </span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {selectedDevice.batteryLevel}%
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-4">
                <Smartphone className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  No device selected
                </p>
              </div>
            )}
          </div>

          {/* System Performance */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              System Performance
            </h3>
            
            <div className="space-y-4">
              {/* CPU */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    CPU Usage
                  </span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {performance?.cpuUsage?.toFixed(1) || '0'}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${performance?.cpuUsage || 0}%` }}
                  />
                </div>
              </div>

              {/* Memory */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Memory Usage
                  </span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {performance?.memoryUsage?.percentage?.toFixed(1) || '0'}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${performance?.memoryUsage?.percentage || 0}%` }}
                  />
                </div>
              </div>

              {/* Battery (macOS) */}
              {powerInfo && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Battery
                    </span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {powerInfo.batteryLevel}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        powerInfo.batteryLevel > 50 ? 'bg-green-600' :
                        powerInfo.batteryLevel > 20 ? 'bg-yellow-600' : 'bg-red-600'
                      }`}
                      style={{ width: `${powerInfo.batteryLevel}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;