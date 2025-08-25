import React, { useState, useEffect } from 'react';
import { useDeviceStore } from '../stores/deviceStore';
import { 
  Smartphone,
  Wifi,
  WifiOff,
  RefreshCw,
  Settings,
  Download,
  Camera,
  Keyboard,
  Play,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  Monitor,
  Battery,
  Cpu,
  HardDrive,
  Info,
  Terminal,
  Search
} from 'lucide-react';

const Devices: React.FC = () => {
  const {
    devices,
    selectedDevice,
    adbStatus,
    isScanning,
    isConnecting,
    scanDevices,
    connectDevice,
    disconnectDevice,
    selectDevice,
    installApp,
    takeScreenshot,
    sendInput,
    checkRushRoyale,
    getDeviceInfo
  } = useDeviceStore();

  const [activeTab, setActiveTab] = useState<'devices' | 'actions' | 'info'>('devices');
  const [inputText, setInputText] = useState('');
  const [appFile, setAppFile] = useState<File | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'connected' | 'disconnected' | 'unauthorized' | 'offline'>('all');



  // Auto-scan for devices periodically
  useEffect(() => {
    const interval = setInterval(() => {
      if (!isScanning && !isConnecting) {
        scanDevices();
      }
    }, 10000); // Scan every 10 seconds

    return () => clearInterval(interval);
  }, [isScanning, isConnecting, scanDevices]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'disconnected':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'unauthorized':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'offline':
        return <WifiOff className="w-5 h-5 text-gray-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'text-green-600 dark:text-green-400';
      case 'disconnected':
        return 'text-red-600 dark:text-red-400';
      case 'unauthorized':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'offline':
        return 'text-gray-600 dark:text-gray-400';
      default:
        return 'text-gray-500 dark:text-gray-500';
    }
  };

  const filteredDevices = devices.filter(device => {
    if (statusFilter !== 'all' && device.status !== statusFilter) return false;
    if (searchQuery && !device.name.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !device.id.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.name.endsWith('.apk')) {
      setAppFile(file);
    }
  };

  const handleInstallApp = async () => {
    if (appFile && selectedDevice) {
      await installApp(selectedDevice.id, appFile.name);
      setAppFile(null);
    }
  };

  const handleTakeScreenshot = async () => {
    if (selectedDevice) {
      await takeScreenshot(selectedDevice.id);
    }
  };

  const handleSendInput = async () => {
    if (selectedDevice && inputText.trim()) {
      // Simulate tap at center of screen
      await sendInput(selectedDevice.id, 500, 500, 'tap');
      setInputText('');
    }
  };

  const renderDevices = () => (
    <div className="space-y-6">
      {/* ADB Status */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            ADB Status
          </h3>

        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              adbStatus.isInstalled ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              ADB {adbStatus.isInstalled ? 'Installed' : 'Not Installed'}
            </span>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              adbStatus.isRunning ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Server {adbStatus.isRunning ? 'Running' : 'Stopped'}
            </span>
          </div>
          
          <div className="flex items-center space-x-3">
            <Terminal className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Version: {adbStatus.version || 'Unknown'}
            </span>
          </div>
        </div>
      </div>

      {/* Device Controls */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="flex-1 min-w-64">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search devices..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Status</option>
            <option value="connected">Connected</option>
            <option value="disconnected">Disconnected</option>
            <option value="unauthorized">Unauthorized</option>
            <option value="offline">Offline</option>
          </select>

          {/* Scan Button */}
          <button
            onClick={scanDevices}
            disabled={isScanning}
            className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isScanning ? 'animate-spin' : ''}`} />
            {isScanning ? 'Scanning...' : 'Scan Devices'}
          </button>
        </div>
      </div>

      {/* Devices List */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Devices ({filteredDevices.length})
          </h3>
        </div>
        
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {filteredDevices.length === 0 ? (
            <div className="p-8 text-center">
              <Smartphone className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                {devices.length === 0 ? 'No devices found' : 'No devices match your filters'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                Make sure USB debugging is enabled on your Android device
              </p>
            </div>
          ) : (
            filteredDevices.map((device) => (
              <div
                key={device.id}
                className={`p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                  selectedDevice?.id === device.id ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      {getStatusIcon(device.status)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {device.name}
                        </h4>
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                          device.status === 'connected' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                          device.status === 'disconnected' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                          device.status === 'unauthorized' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                          'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                        }`}>
                          {device.status}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-4 mt-1">
                        <p className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                          {device.id}
                        </p>
                        {device.model && (
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {device.model}
                          </p>
                        )}
                        {device.androidVersion && (
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            Android {device.androidVersion}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {device.status === 'connected' && (
                      <button
                        onClick={() => selectDevice(device)}
                        className={`px-3 py-1 text-xs rounded-lg transition-colors ${
                          selectedDevice?.id === device.id
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-600'
                        }`}
                      >
                        {selectedDevice?.id === device.id ? 'Selected' : 'Select'}
                      </button>
                    )}
                    
                    {device.status === 'connected' ? (
                      <button
                        onClick={() => disconnectDevice(device.id)}
                        disabled={isConnecting}
                        className="px-3 py-1 text-xs bg-red-100 text-red-600 hover:bg-red-200 dark:bg-red-900 dark:text-red-400 rounded-lg transition-colors disabled:opacity-50"
                      >
                        Disconnect
                      </button>
                    ) : (
                      <button
                        onClick={() => connectDevice(device.id)}
                        disabled={isConnecting}
                        className="px-3 py-1 text-xs bg-green-100 text-green-600 hover:bg-green-200 dark:bg-green-900 dark:text-green-400 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {isConnecting ? 'Connecting...' : 'Connect'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );

  const renderActions = () => (
    <div className="space-y-6">
      {!selectedDevice ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm border border-gray-200 dark:border-gray-700 text-center">
          <Smartphone className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            Select a connected device to perform actions
          </p>
        </div>
      ) : (
        <>
          {/* Selected Device Info */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Selected Device
            </h3>
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                {getStatusIcon(selectedDevice.status)}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                  {selectedDevice.name}
                </h4>
                <p className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                  {selectedDevice.id}
                </p>
              </div>
            </div>
          </div>

          {/* App Management */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              App Management
            </h3>
            
            <div className="space-y-4">
              {/* Install APK */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Install APK
                </label>
                <div className="flex items-center space-x-3">
                  <input
                    type="file"
                    accept=".apk"
                    onChange={handleFileUpload}
                    className="flex-1 text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900 dark:file:text-blue-300"
                  />
                  <button
                    onClick={handleInstallApp}
                    disabled={!appFile}
                    className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Install
                  </button>
                </div>
              </div>

              {/* Check Rush Royale */}
              <div>
                <button
                  onClick={() => checkRushRoyale(selectedDevice.id)}
                  className="flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Check Rush Royale
                </button>
              </div>
            </div>
          </div>

          {/* Device Control */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Device Control
            </h3>
            
            <div className="space-y-4">
              {/* Screenshot */}
              <div>
                <button
                  onClick={handleTakeScreenshot}
                  className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  <Camera className="w-4 h-4 mr-2" />
                  Take Screenshot
                </button>
              </div>

              {/* Send Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Send Text Input
                </label>
                <div className="flex items-center space-x-3">
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Enter text to send..."
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyPress={(e) => e.key === 'Enter' && handleSendInput()}
                  />
                  <button
                    onClick={handleSendInput}
                    disabled={!inputText.trim()}
                    className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
                  >
                    <Keyboard className="w-4 h-4 mr-2" />
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderInfo = () => (
    <div className="space-y-6">
      {!selectedDevice ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm border border-gray-200 dark:border-gray-700 text-center">
          <Info className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            Select a device to view detailed information
          </p>
        </div>
      ) : (
        <>
          {/* Device Information */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Device Information
              </h3>
              <button
                onClick={() => getDeviceInfo(selectedDevice.id)}
                className="flex items-center px-3 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Basic Info */}
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Smartphone className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {selectedDevice.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Device Name
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Terminal className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white font-mono">
                      {selectedDevice.id}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Device ID
                    </p>
                  </div>
                </div>
                
                {selectedDevice.model && (
                  <div className="flex items-center space-x-3">
                    <Monitor className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {selectedDevice.model}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Model
                      </p>
                    </div>
                  </div>
                )}
                
                {selectedDevice.androidVersion && (
                  <div className="flex items-center space-x-3">
                    <Zap className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        Android {selectedDevice.androidVersion}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        OS Version
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Hardware Info */}
              <div className="space-y-3">
                {selectedDevice.batteryLevel !== undefined && (
                  <div className="flex items-center space-x-3">
                    <Battery className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {selectedDevice.batteryLevel}%
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Battery Level
                      </p>
                    </div>
                  </div>
                )}
                
                {selectedDevice.cpuAbi && (
                  <div className="flex items-center space-x-3">
                    <Cpu className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {selectedDevice.cpuAbi}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        CPU Architecture
                      </p>
                    </div>
                  </div>
                )}
                
                {selectedDevice.totalMemory && (
                  <div className="flex items-center space-x-3">
                    <HardDrive className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {(selectedDevice.totalMemory / 1024 / 1024 / 1024).toFixed(1)} GB
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Total Memory
                      </p>
                    </div>
                  </div>
                )}
                
                {selectedDevice.availableMemory && (
                  <div className="flex items-center space-x-3">
                    <HardDrive className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {(selectedDevice.availableMemory / 1024 / 1024 / 1024).toFixed(1)} GB
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Available Memory
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Connection Status */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Connection Status
            </h3>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {getStatusIcon(selectedDevice.status)}
                <span className={`text-sm font-medium ${getStatusColor(selectedDevice.status)}`}>
                  {selectedDevice.status.charAt(0).toUpperCase() + selectedDevice.status.slice(1)}
                </span>
              </div>
              
              {selectedDevice.connectionType && (
                <div className="flex items-center space-x-2">
                  <Wifi className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {selectedDevice.connectionType}
                  </span>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );

  const tabs = [
    { id: 'devices', label: 'Devices', icon: Smartphone },
    { id: 'actions', label: 'Actions', icon: Settings },
    { id: 'info', label: 'Device Info', icon: Info }
  ];

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Devices
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage Android device connections and perform device operations
          </p>
        </div>
        
        {/* Connection Status */}
        <div className="flex items-center space-x-4">
          {selectedDevice && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Selected:</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {selectedDevice.name}
              </span>
            </div>
          )}
          
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              adbStatus.isRunning ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              ADB {adbStatus.isRunning ? 'Connected' : 'Disconnected'}
            </span>
          </div>
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
        {activeTab === 'devices' && renderDevices()}
        {activeTab === 'actions' && renderActions()}
        {activeTab === 'info' && renderInfo()}
      </div>
    </div>
  );
};

export default Devices;