import { useEffect, useState } from 'react';
import { FileText, Search, Brain, Trash2 } from 'lucide-react';
import { ScanResult, AIQuery } from '../types';

export default function Logs() {
  const [scans, setScans] = useState<ScanResult[]>([]);
  const [queries, setQueries] = useState<AIQuery[]>([]);
  const [activeTab, setActiveTab] = useState<'scans' | 'queries'>('scans');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    const savedScans: ScanResult[] = JSON.parse(localStorage.getItem('scans') || '[]');
    const savedQueries: AIQuery[] = JSON.parse(localStorage.getItem('queries') || '[]');
    setScans(savedScans.reverse());
    setQueries(savedQueries.reverse());
  };

  const clearScans = () => {
    localStorage.setItem('scans', '[]');
    setScans([]);
  };

  const clearQueries = () => {
    localStorage.setItem('queries', '[]');
    setQueries([]);
  };

  const filteredScans = scans.filter(scan =>
    scan.url.toLowerCase().includes(searchTerm.toLowerCase()) ||
    scan.notes.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredQueries = queries.filter(query =>
    query.query.toLowerCase().includes(searchTerm.toLowerCase()) ||
    query.answer.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">History & Logs</h1>
        <p className="text-gray-400">View all your scans and AI queries</p>
      </div>

      <div className="bg-black border border-gray-800 rounded-lg p-6">
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search logs..."
              className="w-full pl-10 pr-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-[#00FFFF] transition-colors"
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('scans')}
              className={`px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                activeTab === 'scans'
                  ? 'bg-[#8A2BE2] text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              <FileText className="w-5 h-5 inline mr-2" />
              Scans
            </button>
            <button
              onClick={() => setActiveTab('queries')}
              className={`px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                activeTab === 'queries'
                  ? 'bg-[#8A2BE2] text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              <Brain className="w-5 h-5 inline mr-2" />
              Queries
            </button>
          </div>
        </div>

        {activeTab === 'scans' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-white">URL Scan History</h2>
              {scans.length > 0 && (
                <button
                  onClick={clearScans}
                  className="px-4 py-2 bg-[#FF3B3F] text-white rounded-lg text-sm font-semibold hover:bg-[#FF3B3F]/80 transition-colors flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Clear All
                </button>
              )}
            </div>

            {filteredScans.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                <p className="text-gray-400">
                  {scans.length === 0 ? 'No scan history yet' : 'No results found'}
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-800">
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Timestamp</th>
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">URL</th>
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Threat Level</th>
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredScans.map((scan) => (
                      <tr key={scan.id} className="border-b border-gray-900 hover:bg-gray-900/50">
                        <td className="py-3 px-4 text-gray-400 text-sm">{scan.timestamp}</td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <span className="text-white truncate max-w-xs">{scan.url}</span>
                            {scan.isOnion && (
                              <span className="text-xs bg-[#8A2BE2]/20 text-[#8A2BE2] px-2 py-1 rounded">TOR</span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              scan.status === 'high'
                                ? 'bg-[#FF3B3F]/20 text-[#FF3B3F]'
                                : scan.status === 'medium'
                                ? 'bg-[#8A2BE2]/20 text-[#8A2BE2]'
                                : 'bg-[#00FFFF]/20 text-[#00FFFF]'
                            }`}
                          >
                            {scan.threatLevel}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-gray-300">{scan.notes}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'queries' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-white">AI Query History</h2>
              {queries.length > 0 && (
                <button
                  onClick={clearQueries}
                  className="px-4 py-2 bg-[#FF3B3F] text-white rounded-lg text-sm font-semibold hover:bg-[#FF3B3F]/80 transition-colors flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Clear All
                </button>
              )}
            </div>

            {filteredQueries.length === 0 ? (
              <div className="text-center py-12">
                <Brain className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                <p className="text-gray-400">
                  {queries.length === 0 ? 'No query history yet' : 'No results found'}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredQueries.map((query) => (
                  <div
                    key={query.id}
                    className="bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-[#8A2BE2] transition-colors"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center gap-2">
                        <Brain className="w-4 h-4 text-[#00FFFF]" />
                        <span className="text-[#00FFFF] font-semibold text-sm">QUERY</span>
                      </div>
                      <span className="text-gray-400 text-xs">{query.timestamp}</span>
                    </div>
                    <p className="text-white mb-3 pl-6">{query.query}</p>
                    <div className="border-t border-gray-800 pt-3">
                      <span className="text-gray-400 text-sm font-medium">Response:</span>
                      <p className="text-gray-300 mt-2 text-sm leading-relaxed">{query.answer}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
