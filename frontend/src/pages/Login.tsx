import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield } from 'lucide-react';

interface LoginProps {
  onLogin: () => void;
}

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }

    const success = await login(username, password, remember);
    if (success) {
      onLogin();
    } else {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Shield className="w-16 h-16 text-[#00FFFF]" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">DarkIntelliWeb</h1>
          <p className="text-gray-400">Cybersecurity Intelligence Dashboard</p>
        </div>

        <div className="bg-black border border-[#8A2BE2] rounded-lg p-8 shadow-lg shadow-[#8A2BE2]/20">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-white mb-2 text-sm font-medium">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-[#00FFFF] transition-colors"
                placeholder="Enter username"
              />
            </div>

            <div>
              <label className="block text-white mb-2 text-sm font-medium">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-[#00FFFF] transition-colors"
                placeholder="Enter password"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="remember"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="w-4 h-4 border-gray-700 rounded bg-gray-900 text-[#8A2BE2] focus:ring-[#8A2BE2]"
              />
              <label htmlFor="remember" className="ml-2 text-sm text-gray-400">
                Remember me
              </label>
            </div>

            {error && (
              <div className="bg-[#FF3B3F]/10 border border-[#FF3B3F] text-[#FF3B3F] px-4 py-2 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="w-full bg-[#8A2BE2] text-white py-3 rounded-lg font-semibold hover:bg-[#FF3B3F] transition-colors duration-200"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
