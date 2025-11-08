import { useState } from 'react';
import { Settings as SettingsIcon, Save, RotateCcw } from 'lucide-react';
import { useSettings } from '../context/SettingsContext';

export default function Settings() {
  const { settings, updateSettings, resetSettings } = useSettings();
  const [apiKey, setApiKey] = useState(settings.apiKey);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const showNotification = (message: string, type: 'success' | 'error') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const handleSave = () => {
    updateSettings({ apiKey });
    showNotification('Settings saved successfully', 'success');
  };

  const handleReset = () => {
    resetSettings();
    setApiKey('');
    showNotification('Settings reset to defaults', 'success');
  };

  const handleThemeToggle = () => {
    updateSettings({ theme: settings.theme === 'dark' ? 'light' : 'dark' });
  };

  const handleTorToggle = () => {
    updateSettings({ torEnabled: !settings.torEnabled });
    showNotification(
      settings.torEnabled ? 'Tor routing disabled' : 'Tor routing enabled',
      'success'
    );
  };

  return (
    <div className="space-y-6">
      {notification && (
        <div
          className={`fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
            notification.type === 'success'
              ? 'bg-[#00FFFF]/20 border border-[#00FFFF] text-[#00FFFF]'
              : 'bg-[#FF3B3F]/20 border border-[#FF3B3F] text-[#FF3B3F]'
          }`}
        >
          {notification.message}
        </div>
      )}

      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">Configure your dashboard preferences</p>
      </div>

      <div className="bg-black border border-gray-800 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-6">
          <SettingsIcon className="w-6 h-6 text-[#00FFFF]" />
          <h2 className="text-xl font-bold text-white">Appearance</h2>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-900 rounded-lg">
            <div>
              <h3 className="text-white font-medium">Theme</h3>
              <p className="text-gray-400 text-sm">Switch between dark and light mode</p>
            </div>
            <button
              onClick={handleThemeToggle}
              className={`relative w-14 h-7 rounded-full transition-colors ${
                settings.theme === 'dark' ? 'bg-[#8A2BE2]' : 'bg-gray-600'
              }`}
            >
              <span
                className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full transition-transform ${
                  settings.theme === 'dark' ? 'translate-x-7' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      <div className="bg-black border border-gray-800 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-6">
          <SettingsIcon className="w-6 h-6 text-[#00FFFF]" />
          <h2 className="text-xl font-bold text-white">Network Configuration</h2>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-900 rounded-lg">
            <div>
              <h3 className="text-white font-medium">Tor Routing</h3>
              <p className="text-gray-400 text-sm">Enable Tor SOCKS5 proxy for .onion URLs</p>
            </div>
            <button
              onClick={handleTorToggle}
              className={`relative w-14 h-7 rounded-full transition-colors ${
                settings.torEnabled ? 'bg-[#00FFFF]' : 'bg-gray-600'
              }`}
            >
              <span
                className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full transition-transform ${
                  settings.torEnabled ? 'translate-x-7' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {settings.torEnabled && (
            <div className="p-4 bg-[#00FFFF]/10 border border-[#00FFFF] rounded-lg">
              <p className="text-[#00FFFF] text-sm flex items-center gap-2">
                <span className="w-2 h-2 bg-[#00FFFF] rounded-full animate-pulse"></span>
                Tor routing is active. .onion URLs will be routed through Tor SOCKS5 proxy.
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-black border border-gray-800 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-6">
          <SettingsIcon className="w-6 h-6 text-[#00FFFF]" />
          <h2 className="text-xl font-bold text-white">API Configuration</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-white mb-2 font-medium">AI API Key</label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your AI API key"
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-[#00FFFF] transition-colors"
            />
            <p className="text-gray-400 text-sm mt-2">
              Your API key is stored locally and used for AI query integration
            </p>
          </div>
        </div>
      </div>

      <div className="flex gap-4">
        <button
          onClick={handleSave}
          className="flex-1 px-6 py-3 bg-[#8A2BE2] text-white rounded-lg font-semibold hover:bg-[#FF3B3F] transition-colors duration-200 flex items-center justify-center gap-2"
        >
          <Save className="w-5 h-5" />
          Save Settings
        </button>

        <button
          onClick={handleReset}
          className="px-6 py-3 bg-gray-800 text-white rounded-lg font-semibold hover:bg-gray-700 transition-colors duration-200 flex items-center justify-center gap-2"
        >
          <RotateCcw className="w-5 h-5" />
          Reset
        </button>
      </div>
    </div>
  );
}
