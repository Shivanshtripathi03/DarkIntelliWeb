import { useState } from 'react';
import { Brain, Loader2, Send } from 'lucide-react';
import { AIQuery as AIQueryType } from '../types';

export default function AIQuery() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [responses, setResponses] = useState<AIQueryType[]>([]);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const showNotification = (message: string, type: 'success' | 'error') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const handleSubmit = async () => {
    if (!query.trim()) {
      showNotification('Please enter a query', 'error');
      return;
    }

    setLoading(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 2000));

      const sampleAnswers = [
        'Based on current threat intelligence, this appears to be a sophisticated phishing campaign targeting financial institutions.',
        'The malware signature indicates it belongs to the APT-29 group, commonly associated with state-sponsored attacks.',
        'Analysis shows this vulnerability has a CVSS score of 9.8 and should be patched immediately.',
        'Cross-referencing with our threat database suggests this IP address has been involved in multiple DDoS attacks.',
        'The encryption method used is AES-256, which is considered secure for protecting sensitive data.',
      ];

      const randomAnswer = sampleAnswers[Math.floor(Math.random() * sampleAnswers.length)];

      const newQuery: AIQueryType = {
        id: Date.now().toString(),
        query: query,
        answer: randomAnswer,
        timestamp: new Date().toLocaleString(),
      };

      const existingQueries: AIQueryType[] = JSON.parse(localStorage.getItem('queries') || '[]');
      const updatedQueries = [...existingQueries, newQuery];
      localStorage.setItem('queries', JSON.stringify(updatedQueries));

      setResponses(prev => [newQuery, ...prev]);
      showNotification('Query processed successfully', 'success');
      setQuery('');
    } catch (error) {
      showNotification('Failed to process query', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
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
        <h1 className="text-3xl font-bold text-white mb-2">AI Intelligence Query</h1>
        <p className="text-gray-400">Ask questions about cybersecurity threats and intelligence</p>
      </div>

      <div className="bg-black border border-gray-800 rounded-lg p-6">
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <Brain className="w-6 h-6 text-[#00FFFF] mt-2" />
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about security threats, vulnerabilities, malware analysis, or any cybersecurity topic..."
              className="flex-1 px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-[#00FFFF] transition-colors resize-none h-24"
              disabled={loading}
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full px-6 py-3 bg-[#8A2BE2] text-white rounded-lg font-semibold hover:bg-[#FF3B3F] transition-colors duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing Query...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Ask AI
              </>
            )}
          </button>
        </div>
      </div>

      {responses.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-white">Responses</h2>
          {responses.map((response) => (
            <div
              key={response.id}
              className="bg-black border border-[#8A2BE2] rounded-lg p-6 hover:shadow-lg hover:shadow-[#8A2BE2]/20 transition-all duration-200"
            >
              <div className="mb-4">
                <div className="flex items-start gap-2 mb-2">
                  <span className="text-[#00FFFF] font-semibold text-sm">QUERY:</span>
                </div>
                <p className="text-white ml-6">{response.query}</p>
              </div>

              <div className="border-t border-gray-800 pt-4">
                <div className="flex items-start gap-2 mb-2">
                  <Brain className="w-4 h-4 text-[#00FFFF] mt-1" />
                  <span className="text-[#00FFFF] font-semibold text-sm">AI RESPONSE:</span>
                </div>
                <p className="text-gray-300 ml-6 leading-relaxed">{response.answer}</p>
              </div>

              <div className="mt-4 text-right">
                <span className="text-gray-400 text-xs">{response.timestamp}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {responses.length === 0 && !loading && (
        <div className="bg-black border border-gray-800 rounded-lg p-12 text-center">
          <Brain className="w-16 h-16 text-gray-700 mx-auto mb-4" />
          <p className="text-gray-400">No queries yet. Ask your first question to get started.</p>
        </div>
      )}
    </div>
  );
}
