import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, AlertCircle } from 'lucide-react';
import { Layout } from '../components/Layout';
import { supabase } from '../lib/supabase';
import { validateRealEmail, validatePasswordStrength } from '../utils/emailValidator';

export const Signup = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else {
      setLoading(true);
      const isValidEmail = await validateRealEmail(formData.email);
      setLoading(false);
      if (!isValidEmail) {
        newErrors.email = 'Invalid email. Please enter a real email address.';
      }
    }

    const passwordValidation = validatePasswordStrength(formData.password);
    if (!passwordValidation.valid) {
      newErrors.password = passwordValidation.error!;
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    try {
      const { error } = await supabase.auth.signUp({
        email: formData.email,
        password: formData.password,
        options: {
          data: {
            name: formData.name
          }
        }
      });

      if (error) {
        setErrors({ general: error.message });
      } else {
        navigate('/signin');
      }
    } catch (err) {
      setErrors({ general: 'An unexpected error occurred' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-full max-w-md">
          <div className="bg-gray-900 rounded-lg shadow-2xl border border-purple-500/20 p-8">
            <h1 className="text-3xl font-bold text-center mb-2 bg-gradient-to-r from-red-500 via-purple-500 to-cyan-400 bg-clip-text text-transparent">
              Create Account
            </h1>
            <p className="text-gray-400 text-center mb-8">Join us today</p>

            {errors.general && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-red-400 text-sm">{errors.general}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-cyan-400 text-sm font-medium mb-2">
                  Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={`w-full bg-gray-800 border ${
                      errors.name ? 'border-red-500' : 'border-gray-700'
                    } rounded-lg px-10 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 transition-colors`}
                    placeholder="Enter your name"
                  />
                </div>
                {errors.name && (
                  <p className="mt-2 text-red-400 text-sm flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.name}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-cyan-400 text-sm font-medium mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className={`w-full bg-gray-800 border ${
                      errors.email ? 'border-red-500' : 'border-gray-700'
                    } rounded-lg px-10 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 transition-colors`}
                    placeholder="Enter your email"
                  />
                </div>
                {errors.email && (
                  <p className="mt-2 text-red-400 text-sm flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.email}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-cyan-400 text-sm font-medium mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className={`w-full bg-gray-800 border ${
                      errors.password ? 'border-red-500' : 'border-gray-700'
                    } rounded-lg px-10 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 transition-colors`}
                    placeholder="Create a password"
                  />
                </div>
                {errors.password && (
                  <p className="mt-2 text-red-400 text-sm flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.password}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-cyan-400 text-sm font-medium mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className={`w-full bg-gray-800 border ${
                      errors.confirmPassword ? 'border-red-500' : 'border-gray-700'
                    } rounded-lg px-10 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 transition-colors`}
                    placeholder="Confirm your password"
                  />
                </div>
                {errors.confirmPassword && (
                  <p className="mt-2 text-red-400 text-sm flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.confirmPassword}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white font-semibold py-3 rounded-lg transition-all duration-200 shadow-lg hover:shadow-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating Account...' : 'Sign Up'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-400">
                Already have an account?{' '}
                <Link to="/signin" className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};
