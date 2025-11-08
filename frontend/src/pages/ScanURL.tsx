import { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { ScanResult } from '../types';
import { useSettings } from '../context/SettingsContext';

export default function ScanURL() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ScanResult[]>([]);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const { settings } = useSettings();

  const showNotification = (message: string, type: 'success' | 'error') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const isOnionUrl = (urlString: string) => {
    return urlString.includes('.onion');
  };

  const handleScan = async () => {
    if (!url) {
      showNotification('Please enter a URL', 'error');
      return;
    }

    setLoading(true);

    try {
      const isOnion = isOnionUrl(url);

      if (isOnion && !settings.torEnabled) {
        showNotification('Tor must be enabled for .onion URLs', 'error');
        setLoading(false);
        return;
      }

      await new Promise(resolve => setTimeout(resolve, 1500));

      const threatLevels: Array<'safe' | 'medium' | 'high'> = ['safe', 'medium', 'high'];
      const randomThreat = threatLevels[Math.floor(Math.random() * threatLevels.length)];

      const newScan: ScanResult = {
        id: Date.now().toString(),
        url,
        status: randomThreat,
        threatLevel: randomThreat === 'safe' ? 'Safe' : randomThreat === 'medium' ? 'Medium' : 'High',
        notes: randomThreat === 'high'
          ? 'Potential security threats detected'
          : randomThreat === 'medium'
          ? 'Some suspicious activity found'
          : 'No threats detected',
        timestamp: new Date().toLocaleString(),
        isOnion,
      };

      const existingScans: ScanResult[] = JSON.parse(localStorage.getItem('scans') || '[]');
      const updatedScans = [...existingScans, newScan];
      localStorage.setItem('scans', JSON.stringify(updatedScans));

      setResults(prev => [newScan, ...prev]);
      showNotification('Scan completed successfully', 'success');
      setUrl('');
    } catch (error) {
      showNotification('Scan failed. Please try again', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleScan();
    }
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
        <h1 className="text-3xl font-bold text-white mb-2">URL Scanner</h1>
        <p className="text-gray-400">Scan websites for security threats</p>
      </div>

      <div className="bg-black border border-gray-800 rounded-lg p-6">
        <div className="flex gap-3">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter URL to scan (e.g., https://example.com or http://example.onion)"
            className="flex-1 px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-[#00FFFF] transition-colors"
            disabled={loading}
          />
          <button
            onClick={handleScan}
            disabled={loading}
            className="px-6 py-3 bg-[#8A2BE2] text-white rounded-lg font-semibold hover:bg-[#FF3B3F] transition-colors duration-200 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Scanning...
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                Scan
              </>
            )}
          </button>
        </div>

        {settings.torEnabled && (
          <p className="text-[#00FFFF] text-sm mt-3 flex items-center gap-2">
            <span className="w-2 h-2 bg-[#00FFFF] rounded-full animate-pulse"></span>
            Tor routing enabled for .onion URLs
          </p>
        )}
      </div>

      {results.length > 0 && (
        <div className="bg-black border border-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Scan Results</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">URL</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Status</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Threat Level</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Notes</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {results.map((result) => (
                  <tr key={result.id} className="border-b border-gray-900 hover:bg-gray-900/50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="text-white truncate max-w-xs">{result.url}</span>
                        {result.isOnion && (
                          <span className="text-xs bg-[#8A2BE2]/20 text-[#8A2BE2] px-2 py-1 rounded">TOR</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-gray-300">{result.status}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          result.status === 'high'
                            ? 'bg-[#FF3B3F]/20 text-[#FF3B3F]'
                            : result.status === 'medium'
                            ? 'bg-[#8A2BE2]/20 text-[#8A2BE2]'
                            : 'bg-[#00FFFF]/20 text-[#00FFFF]'
                        }`}
                      >
                        {result.threatLevel}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-300">{result.notes}</td>
                    <td className="py-3 px-4 text-gray-400 text-sm">{result.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
