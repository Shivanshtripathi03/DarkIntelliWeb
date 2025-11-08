import { useEffect, useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Activity } from 'lucide-react';
import { Layout } from '../components/Layout';
import { ScanResult, AIQuery, DashboardStats } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://uripadress:5000/api';
console.log('API =', API);


export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalScans: 0,
    highThreat: 0,
    mediumThreat: 0,
    safeThreat: 0,
  });
  const [recentScans, setRecentScans] = useState<ScanResult[]>([]);
  const [recentQueries, setRecentQueries] = useState<AIQuery[]>([]);
  const [urlToScan, setUrlToScan] = useState('');
  const [aiQuery, setAiQuery] = useState('');
  const [loadingScan, setLoadingScan] = useState(false);
  const [loadingAI, setLoadingAI] = useState(false);

  useEffect(() => {
    const scans: ScanResult[] = JSON.parse(localStorage.getItem('scans') || '[]');
    const queries: AIQuery[] = JSON.parse(localStorage.getItem('queries') || '[]');

    const newStats: DashboardStats = {
      totalScans: scans.length,
      highThreat: scans.filter(s => s.status === 'high').length,
      mediumThreat: scans.filter(s => s.status === 'medium').length,
      safeThreat: scans.filter(s => s.status === 'safe').length,
    };

    setStats(newStats);
    setRecentScans(scans.slice(-5).reverse());
    setRecentQueries(queries.slice(-3).reverse());
  }, []);

const handleScanURL = async () => {
  if (!urlToScan.trim()) return;
  setLoadingScan(true);

  try {
    const status = urlToScan.includes('onion') ? 'high' : 'safe';
    const threatLevel = status === 'high' ? 'High' : 'Safe';

    const reqUrl = `${API}/scan`;
    console.log('SCAN →', reqUrl, { url: urlToScan, status, threatLevel });

    const response = await fetch(reqUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: urlToScan, status, threatLevel }),
    });

    console.log('SCAN ← status:', response.status, response.statusText);

    const ct = response.headers.get('content-type') || '';
    const raw = await (ct.includes('application/json') ? response.json() : response.text());
    console.log('SCAN ← body:', raw);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status} ${response.statusText}`);
    }

    const result: any = raw;

    const newScan: ScanResult = {
      id: result?.id ?? Date.now(),
      url: result?.url ?? urlToScan,
      status: result?.status ?? status,
      threatLevel: result?.threatLevel ?? threatLevel,
      timestamp: new Date().toLocaleString(),
    };

    const updatedScans = [newScan, ...recentScans].slice(0, 20);
    localStorage.setItem('scans', JSON.stringify(updatedScans));
    setRecentScans(updatedScans);

    setStats({
      totalScans: updatedScans.length,
      highThreat: updatedScans.filter(s => s.status === 'high').length,
      mediumThreat: updatedScans.filter(s => s.status === 'medium').length,
      safeThreat: updatedScans.filter(s => s.status === 'safe').length,
    });
    setUrlToScan('');
  } catch (err) {
    console.error('SCAN ✖ error:', err);
    alert('Scan failed. Check console for details.');
  } finally {
    setLoadingScan(false);
  }
};


  const handleAIQuery = async () => {
    if (!aiQuery.trim()) return;
    setLoadingAI(true);

    try {
      const response = await fetch(`${API}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: aiQuery }),
      });

      const result = await response.json();

      const newQuery: AIQuery = {
        id: Date.now(),
        query: aiQuery,
        answer: result.answer,
        timestamp: new Date().toLocaleString(),
      };

      const updatedQueries = [newQuery, ...recentQueries].slice(0, 20);
      localStorage.setItem('queries', JSON.stringify(updatedQueries));
      setRecentQueries(updatedQueries);
      setAiQuery('');
    } catch (err) {
      alert('AI query failed. Try again.');
      console.error(err);
    } finally {
      setLoadingAI(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, color }: { title: string; value: number; icon: any; color: string }) => (
    <div className="bg-black border border-gray-800 rounded-lg p-6 hover:border-[#00FFFF] transition-all duration-200 hover:shadow-lg hover:shadow-[#8A2BE2]/20">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
        </div>
        <Icon className={`w-12 h-12 ${color}`} />
      </div>
    </div>
  );

  return (
    <Layout>
      <div className="space-y-6 p-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-gray-400">Overview of your security intelligence</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard title="Total Scans" value={stats.totalScans} icon={Activity} color="text-white" />
          <StatCard title="High Threat" value={stats.highThreat} icon={AlertTriangle} color="text-[#FF3B3F]" />
          <StatCard title="Medium Threat" value={stats.mediumThreat} icon={Shield} color="text-[#8A2BE2]" />
          <StatCard title="Safe" value={stats.safeThreat} icon={CheckCircle} color="text-[#00FFFF]" />
        </div>

        {/* Scan URL Section */}
        <div className="bg-black border border-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Scan a URL</h2>
          <div className="flex gap-3">
            <input
              type="text"
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400"
              placeholder="Enter website URL"
              value={urlToScan}
              onChange={e => setUrlToScan(e.target.value)}
            />
            <button
              onClick={handleScanURL}
              disabled={loadingScan}
              className="bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white font-semibold px-4 py-2 rounded-lg shadow-lg hover:shadow-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loadingScan ? 'Scanning...' : 'Scan'}
            </button>
          </div>
        </div>

        {/* AI Query Section */}
        <div className="bg-black border border-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Ask AI</h2>
          <div className="flex gap-3">
            <input
              type="text"
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400"
              placeholder="Enter your query"
              value={aiQuery}
              onChange={e => setAiQuery(e.target.value)}
            />
            <button
              onClick={handleAIQuery}
              disabled={loadingAI}
              className="bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 text-white font-semibold px-4 py-2 rounded-lg shadow-lg hover:shadow-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loadingAI ? 'Querying...' : 'Ask'}
            </button>
          </div>
        </div>

        {/* Recent Scans & AI Queries */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-black border border-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4">Recent Scans</h2>
            {recentScans.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No scans yet</p>
            ) : (
              <div className="space-y-3">
                {recentScans.map(scan => (
                  <div key={scan.id} className="bg-gray-900 rounded-lg p-4 border border-gray-800 hover:border-[#8A2BE2] transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-white truncate text-sm">{scan.url}</p>
                        <p className="text-gray-400 text-xs mt-1">{scan.timestamp}</p>
                      </div>
                      <span
                        className={`ml-4 px-3 py-1 rounded-full text-xs font-semibold ${
                          scan.status === 'high'
                            ? 'bg-[#FF3B3F]/20 text-[#FF3B3F]'
                            : scan.status === 'medium'
                            ? 'bg-[#8A2BE2]/20 text-[#8A2BE2]'
                            : 'bg-[#00FFFF]/20 text-[#00FFFF]'
                        }`}
                      >
                        {scan.threatLevel}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-black border border-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4">Recent AI Queries</h2>
            {recentQueries.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No queries yet</p>
            ) : (
              <div className="space-y-3">
                {recentQueries.map(query => (
                  <div key={query.id} className="bg-gray-900 rounded-lg p-4 border border-gray-800 hover:border-[#8A2BE2] transition-colors">
                    <p className="text-[#00FFFF] text-sm font-medium mb-2">{query.query}</p>
                    <p className="text-gray-300 text-sm line-clamp-2">{query.answer}</p>
                    <p className="text-gray-400 text-xs mt-2">{query.timestamp}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
