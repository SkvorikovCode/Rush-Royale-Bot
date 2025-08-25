import React, { useState } from 'react';
import { useBotStore } from '../stores/botStore';
import { useSystemStore } from '../stores/systemStore';
import type { BotConfig, SystemPreferences, NotificationSettings } from '../stores';
import { 
  Settings as SettingsIcon,
  Bot,
  Monitor,
  Bell,
  Shield,
  Zap,
  Save,
  RotateCcw
} from 'lucide-react';

const Settings: React.FC = () => {
  const {
    config: botConfig,
    updateConfig: updateBotConfig
  } = useBotStore();

  const {
    preferences: systemPreferences,
    notificationSettings,
    updatePreferences,
    updateNotificationSettings
  } = useSystemStore();

  const [activeTab, setActiveTab] = useState<'bot' | 'system' | 'notifications' | 'advanced'>('bot');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [localBotConfig, setLocalBotConfig] = useState(botConfig);
  const [localSystemPreferences, setLocalSystemPreferences] = useState(systemPreferences);
  const [localNotificationSettings, setLocalNotificationSettings] = useState(notificationSettings);

  const tabs = [
    { id: 'bot', label: 'Bot Settings', icon: Bot },
    { id: 'system', label: 'System', icon: Monitor },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'advanced', label: 'Advanced', icon: SettingsIcon }
  ];

  const handleBotConfigChange = (key: keyof BotConfig, value: any) => {
    setLocalBotConfig(prev => ({ ...prev, [key]: value }));
    setHasUnsavedChanges(true);
  };

  const handleSystemPreferencesChange = (key: keyof SystemPreferences, value: any) => {
    setLocalSystemPreferences(prev => ({ ...prev, [key]: value }));
    setHasUnsavedChanges(true);
  };

  const handleNotificationSettingsChange = (key: keyof NotificationSettings, value: any) => {
    setLocalNotificationSettings(prev => ({ ...prev, [key]: value }));
    setHasUnsavedChanges(true);
  };

  const saveSettings = async () => {
    try {
      updateBotConfig(localBotConfig);
      await updatePreferences(localSystemPreferences);
      await updateNotificationSettings(localNotificationSettings);
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  };

  const resetSettings = () => {
    setLocalBotConfig(botConfig);
    setLocalSystemPreferences(systemPreferences);
    setLocalNotificationSettings(notificationSettings);
    setHasUnsavedChanges(false);
  };

  const renderBotSettings = () => (
    <div className="space-y-6">
      {/* Game Configuration */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Game Configuration
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Game Mode */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Game Mode
            </label>
            <select
              value={localBotConfig.game_mode}
              onChange={(e) => handleBotConfigChange('game_mode', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="coop">Co-op</option>
              <option value="pvp">PvP</option>
              <option value="tournament">Tournament</option>
            </select>
          </div>

          {/* Difficulty */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Difficulty
            </label>
            <select
              value={localBotConfig.difficulty}
              onChange={(e) => handleBotConfigChange('difficulty', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>

          {/* Max Games */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max Games per Session
            </label>
            <input
              type="number"
              value={localBotConfig.max_games}
              onChange={(e) => handleBotConfigChange('max_games', parseInt(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              min="1"
              max="1000"
            />
          </div>

          {/* Pause Between Games */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Pause Between Games (seconds)
            </label>
            <input
              type="number"
              value={localBotConfig.pause_between_games}
              onChange={(e) => handleBotConfigChange('pause_between_games', parseInt(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              min="0"
              max="300"
            />
          </div>
        </div>
      </div>

      {/* Bot Behavior */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Bot Behavior
        </h3>
        
        <div className="space-y-4">
          {/* Auto Start */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Auto Start on Launch
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Automatically start the bot when the application launches
              </p>
            </div>
            <button
              onClick={() => handleBotConfigChange('auto_start', !localBotConfig.auto_start)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localBotConfig.auto_start ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localBotConfig.auto_start ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Auto Restart */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Auto Restart on Error
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Automatically restart the bot when an error occurs
              </p>
            </div>
            <button
              onClick={() => handleBotConfigChange('auto_restart', !localBotConfig.auto_restart)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localBotConfig.auto_restart ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localBotConfig.auto_restart ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Stop on Error */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Stop on Error
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Stop the bot immediately when an error occurs
              </p>
            </div>
            <button
              onClick={() => handleBotConfigChange('stop_on_error', !localBotConfig.stop_on_error)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localBotConfig.stop_on_error ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localBotConfig.stop_on_error ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Enable Notifications */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Enable Notifications
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Show notifications for bot events and status changes
              </p>
            </div>
            <button
              onClick={() => handleBotConfigChange('enable_notifications', !localBotConfig.enable_notifications)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localBotConfig.enable_notifications ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localBotConfig.enable_notifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSystemSettings = () => (
    <div className="space-y-6">
      {/* Appearance */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Appearance
        </h3>
        
        <div className="space-y-4">
          {/* Theme */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Theme
            </label>
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Dark Mode
                </span>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Toggle between light and dark theme
                </p>
              </div>
              <button
                onClick={() => handleSystemPreferencesChange('theme', localSystemPreferences.theme === 'dark' ? 'light' : 'dark')}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  localSystemPreferences.theme === 'dark' ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    localSystemPreferences.theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Accent Color */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Accent Color
            </label>
            <div className="flex items-center space-x-3">
              <input
                type="color"
                value={localSystemPreferences.accentColor}
                onChange={(e) => handleSystemPreferencesChange('accentColor', e.target.value)}
                className="w-12 h-8 rounded border border-gray-300 dark:border-gray-600"
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {localSystemPreferences.accentColor}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Accessibility */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Accessibility
        </h3>
        
        <div className="space-y-4">
          {/* Reduced Motion */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Reduce Motion
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Minimize animations and transitions
              </p>
            </div>
            <button
              onClick={() => handleSystemPreferencesChange('reducedMotion', !localSystemPreferences.reducedMotion)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localSystemPreferences.reducedMotion ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localSystemPreferences.reducedMotion ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* High Contrast */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                High Contrast
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Increase contrast for better visibility
              </p>
            </div>
            <button
              onClick={() => handleSystemPreferencesChange('highContrast', !localSystemPreferences.highContrast)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localSystemPreferences.highContrast ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localSystemPreferences.highContrast ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Transparency */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Transparency Effects
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Enable transparency and blur effects
              </p>
            </div>
            <button
              onClick={() => handleSystemPreferencesChange('transparency', !localSystemPreferences.transparency)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localSystemPreferences.transparency ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localSystemPreferences.transparency ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      {/* Notification Preferences */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Notification Preferences
        </h3>
        
        <div className="space-y-4">
          {/* Enable Notifications */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Enable Notifications
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Allow the app to show notifications
              </p>
            </div>
            <button
              onClick={() => handleNotificationSettingsChange('enabled', !localNotificationSettings.enabled)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localNotificationSettings.enabled ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localNotificationSettings.enabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Sound */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Sound
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Play sound with notifications
              </p>
            </div>
            <button
              onClick={() => handleNotificationSettingsChange('play_sound', !localNotificationSettings.play_sound)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localNotificationSettings.play_sound ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localNotificationSettings.play_sound ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Badge */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Badge
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Show badge on app icon
              </p>
            </div>
            <button
              onClick={() => handleNotificationSettingsChange('show_badge', !localNotificationSettings.show_badge)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localNotificationSettings.show_badge ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localNotificationSettings.show_badge ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Banner */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Banner
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Show banner notifications
              </p>
            </div>
            <button
              onClick={() => handleNotificationSettingsChange('show_banner', !localNotificationSettings.show_banner)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localNotificationSettings.show_banner ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localNotificationSettings.show_banner ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Critical Alerts */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Critical Alerts
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Allow critical alerts to bypass Do Not Disturb
              </p>
            </div>
            <button
              onClick={() => handleNotificationSettingsChange('criticalAlerts', !localNotificationSettings.criticalAlerts)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                localNotificationSettings.criticalAlerts ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  localNotificationSettings.criticalAlerts ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAdvancedSettings = () => (
    <div className="space-y-6">
      {/* Performance */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Performance
        </h3>
        
        <div className="space-y-4">
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
            <div className="flex items-start">
              <Shield className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3" />
              <div>
                <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                  Advanced Settings
                </h4>
                <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                  These settings can affect app performance and stability. Change only if you know what you're doing.
                </p>
              </div>
            </div>
          </div>
          
          <div className="text-center py-8">
            <Zap className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">
              Advanced performance settings will be available in a future update.
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Settings
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Configure your bot, system preferences, and notifications
          </p>
        </div>
        
        {/* Save/Reset Buttons */}
        {hasUnsavedChanges && (
          <div className="flex items-center space-x-3">
            <button
              onClick={resetSettings}
              className="flex items-center px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Reset
            </button>
            <button
              onClick={saveSettings}
              className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </button>
          </div>
        )}
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
        {activeTab === 'bot' && renderBotSettings()}
        {activeTab === 'system' && renderSystemSettings()}
        {activeTab === 'notifications' && renderNotificationSettings()}
        {activeTab === 'advanced' && renderAdvancedSettings()}
      </div>
    </div>
  );
};

export default Settings;