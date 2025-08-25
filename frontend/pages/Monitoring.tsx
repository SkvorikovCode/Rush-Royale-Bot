import React, { useState, useEffect, useRef } from 'react';
import { useBotStore } from '../stores/botStore';
import { useDeviceStore } from '../stores/deviceStore';
import { useSystemStore } from '../stores/systemStore';
import { 
  Activity,
  AlertTriangle,
  Download,
  Info,
  Pause,
  Play,
  Search,
  Trash2,
  XCircle,
  Zap,
  Eye,
  EyeOff,
  RotateCw,
  Terminal
} from 'lucide-react';

type LogLevel = 'info' | 'warning' | 'error' | 'debug';

interface LogEntry {
  id: string;
  timestamp: Date;
  level: LogLevel;
  source: 'bot' | 'device' | 'system';
  message: string;
  details?: any;
}

const Monitoring: React.FC = () => {
  const {
    logs: botLogs,
    status: botStatus,
    stats,
    clearLogs: clearBotLogs
  } = useBotStore();

  const {
    logs: deviceLogs,
    clearLogs: clearDeviceLogs
  } = useDeviceStore();

  const {
    performance: performanceMetrics,
    refreshPerformanceMetrics: updatePerformanceMetrics
  } = useSystemStore();

  const [activeTab, setActiveTab] = useState<'logs' | 'performance' | 'network'>('logs');
  const [logFilter, setLogFilter] = useState<LogLevel | 'all'>('all');
  const [sourceFilter, setSourceFilter] = useState<'all' | 'bot' | 'device' | 'system'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isAutoScroll, setIsAutoScroll] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const [displayedLogs, setDisplayedLogs] = useState<LogEntry[]>([]);

  // Combine logs from all sources with proper timestamp conversion
  const allLogs: LogEntry[] = [
    ...botLogs.map(log => ({ 
      ...log, 
      source: 'bot' as const,
      timestamp: new Date(log.timestamp) // Convert string to Date
    })),
    ...deviceLogs.map(log => ({ 
      ...log, 
      source: 'device' as const,
      timestamp: log.timestamp instanceof Date ? log.timestamp : new Date(log.timestamp)
    }))
  ].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

  // Filter logs
  const filteredLogs = allLogs.filter(log => {
    if (logFilter !== 'all' && log.level !== logFilter) return false;
    if (sourceFilter !== 'all' && log.source !== sourceFilter) return false;
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  // Auto-scroll to bottom
  useEffect(() => {
    if (isAutoScroll && !isPaused && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [filteredLogs, isAutoScroll, isPaused]);

  // Update displayed logs when not paused
  useEffect(() => {
    if (!isPaused) {
      setDisplayedLogs(filteredLogs);
    }
  }, [filteredLogs, isPaused]);

  // Update performance metrics periodically
  useEffect(() => {
    const interval = setInterval(() => {
      if (activeTab === 'performance') {
        updatePerformanceMetrics();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [activeTab, updatePerformanceMetrics]);

  const getLogIcon = (level: LogLevel) => {
    switch (level) {
      case 'info':
        return <Info className="w-4 h-4 text-blue-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'debug':
        return <Info className="w-4 h-4 text-gray-500" />;
    }
  };

  const getLogLevelColor = (level: LogLevel) => {
    switch (level) {
      case 'info':
        return 'text-blue-600 dark:text-blue-400';
      case 'warning':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'error':
        return 'text-red-600 dark:text-red-400';
      case 'debug':
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'bot':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'device':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'system':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const exportLogs = () => {
    const logsText = displayedLogs.map(log => 
      `[${log.timestamp.toISOString()}] [${log.level.toUpperCase()}] [${log.source.toUpperCase()}] ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rush-royale-bot-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const clearAllLogs = () => {
    clearBotLogs();
    clearDeviceLogs();
  };

  const renderLogs = () => (
    <div className="space-y-4">
      {/* Controls */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="flex-1 min-w-64">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Level Filter */}
          <select
            value={logFilter}
            onChange={(e) => setLogFilter(e.target.value as LogLevel | 'all')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Levels</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="debug">Debug</option>
          </select>

          {/* Source Filter */}
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value as 'all' | 'bot' | 'device' | 'system')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Sources</option>
            <option value="bot">Bot</option>
            <option value="device">Device</option>
            <option value="system">System</option>
          </select>

          {/* Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsPaused(!isPaused)}
              className={`p-2 rounded-lg transition-colors ${
                isPaused
                  ? 'bg-green-100 text-green-600 hover:bg-green-200 dark:bg-green-900 dark:text-green-400'
                  : 'bg-yellow-100 text-yellow-600 hover:bg-yellow-200 dark:bg-yellow-900 dark:text-yellow-400'
              }`}
              title={isPaused ? 'Resume' : 'Pause'}
            >
              {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
            </button>

            <button
              onClick={() => setIsAutoScroll(!isAutoScroll)}
              className={`p-2 rounded-lg transition-colors ${
                isAutoScroll
                  ? 'bg-blue-100 text-blue-600 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-400'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-900 dark:text-gray-400'
              }`}
              title={isAutoScroll ? 'Disable Auto-scroll' : 'Enable Auto-scroll'}
            >
              {isAutoScroll ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>

            <button
              onClick={exportLogs}
              className="p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-900 dark:text-gray-400 transition-colors"
              title="Export Logs"
            >
              <Download className="w-4 h-4" />
            </button>

            <button
              onClick={clearAllLogs}
              className="p-2 rounded-lg bg-red-100 text-red-600 hover:bg-red-200 dark:bg-red-900 dark:text-red-400 transition-colors"
              title="Clear All Logs"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Logs Display */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Logs ({displayedLogs.length})
            </h3>
            {isPaused && (
              <div className="flex items-center text-yellow-600 dark:text-yellow-400">
                <Pause className="w-4 h-4 mr-1" />
                <span className="text-sm font-medium">Paused</span>
              </div>
            )}
          </div>
        </div>
        
        <div className="h-96 overflow-y-auto p-4 space-y-2 font-mono text-sm">
          {displayedLogs.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
              <Terminal className="w-8 h-8 mr-3" />
              <span>No logs to display</span>
            </div>
          ) : (
            displayedLogs.map((log) => (
              <div
                key={log.id}
                className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getLogIcon(log.level)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {log.timestamp.toLocaleTimeString()}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${getSourceColor(log.source)}`}>
                      {log.source.toUpperCase()}
                    </span>
                    <span className={`text-xs font-medium ${getLogLevelColor(log.level)}`}>
                      {log.level.toUpperCase()}
                    </span>
                  </div>
                  
                  <p className="text-gray-900 dark:text-white break-words">
                    {log.message}
                  </p>
                  
                  {log.details && (
                    <details className="mt-2">
                      <summary className="text-xs text-gray-500 dark:text-gray-400 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
                        Show details
                      </summary>
                      <pre className="mt-2 p-2 bg-gray-100 dark:bg-gray-900 rounded text-xs overflow-x-auto">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  );

  const renderPerformance = () => (
    <div className="space-y-6">
      {/* Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* CPU Usage */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">CPU Usage</h3>
            <Zap className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {performanceMetrics?.cpuUsage?.toFixed(1) || '0.0'}%
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(performanceMetrics?.cpuUsage || 0, 100)}%` }}
            />
          </div>
        </div>

        {/* Memory Usage */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Memory Usage</h3>
            <Activity className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {performanceMetrics?.memoryUsage?.percentage?.toFixed(1) || '0.0'}%
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(performanceMetrics?.memoryUsage?.percentage || 0, 100)}%` }}
            />
          </div>
        </div>

        {/* Disk Usage */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Disk Usage</h3>
            <RotateCw className="w-5 h-5 text-yellow-500" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {performanceMetrics?.diskUsage?.percentage?.toFixed(1) || '0.0'}%
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(performanceMetrics?.diskUsage?.percentage || 0, 100)}%` }}
            />
          </div>
        </div>

        {/* Network Activity */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Network</h3>
            <Activity className="w-5 h-5 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {(((performanceMetrics?.networkActivity?.bytesReceived || 0) + (performanceMetrics?.networkActivity?.bytesSent || 0)) / 1024 / 1024).toFixed(1)} MB/s
            </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Network throughput
          </div>
        </div>
      </div>

      {/* Detailed Performance Metrics */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Detailed Metrics
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* System Temperature */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              System Temperature
            </h4>
            <div className="text-xl font-semibold text-gray-900 dark:text-white">
              {performanceMetrics?.temperature?.cpu?.toFixed(0) || '0'}°C
            </div>
          </div>

          {/* Fan Speed */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              Fan Speed
            </h4>
            <div className="text-xl font-semibold text-gray-900 dark:text-white">
              {performanceMetrics?.fanSpeed || 0} RPM
            </div>
          </div>
        </div>
      </div>

      {/* Bot Performance */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Bot Performance
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Games Played */}
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {stats.gamesPlayed}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Games Played
            </div>
          </div>

          {/* Win Rate */}
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {stats.winRate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Win Rate
            </div>
          </div>

          {/* Average Game Time */}
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {Math.floor(stats.totalPlayTime / stats.gamesPlayed / 60) || 0}m
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Avg Game Time
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNetwork = () => (
    <div className="space-y-6">
      {/* Network Status */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Network Status
        </h3>
        
        <div className="text-center py-8">
          <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            Network monitoring features will be available in a future update.
          </p>
        </div>
      </div>
    </div>
  );

  const tabs = [
    { id: 'logs', label: 'Logs', icon: Terminal },
    { id: 'performance', label: 'Performance', icon: Activity },
    { id: 'network', label: 'Network', icon: Zap }
  ];

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Monitoring
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Real-time logs, performance metrics, and system monitoring
          </p>
        </div>
        
        {/* Status Indicator */}
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${
            botStatus === 'running' ? 'bg-green-500' :
            botStatus === 'paused' ? 'bg-yellow-500' :
            botStatus === 'error' ? 'bg-red-500' :
            'bg-gray-400'
          }`} />
          <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
            Bot {botStatus}
          </span>
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
        {activeTab === 'logs' && renderLogs()}
        {activeTab === 'performance' && renderPerformance()}
        {activeTab === 'network' && renderNetwork()}
      </div>
    </div>
  );
};

export default Monitoring;