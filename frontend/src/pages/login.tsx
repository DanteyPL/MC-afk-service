import { useState } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [microsoftEmail, setMicrosoftEmail] = useState('');
  const [microsoftPassword, setMicrosoftPassword] = useState('');
  const [storeCredentials, setStoreCredentials] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/auth/login', {
        username: email,
        password,
        microsoftEmail,
        microsoftPassword,
        storeCredentials
      });
      localStorage.setItem('token', response.data.access_token);
      router.push('/dashboard');
    } catch (err) {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Minecraft AFK Client</h1>
        {error && <div className="mb-4 text-red-500">{error}</div>}
        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="w-full px-3 py-2 border rounded-lg"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 mb-2" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="w-full px-3 py-2 border rounded-lg"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <div className="mb-6 border-t pt-4">
            <h3 className="text-lg font-medium mb-4">Microsoft Account (Optional)</h3>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2" htmlFor="microsoftEmail">
                Microsoft Email
              </label>
              <input
                id="microsoftEmail"
                type="email"
                className="w-full px-3 py-2 border rounded-lg"
                value={microsoftEmail}
                onChange={(e) => setMicrosoftEmail(e.target.value)}
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2" htmlFor="microsoftPassword">
                Microsoft Password
              </label>
              <input
                id="microsoftPassword"
                type="password"
                className="w-full px-3 py-2 border rounded-lg"
                value={microsoftPassword}
                onChange={(e) => setMicrosoftPassword(e.target.value)}
              />
            </div>
            <div className="flex items-center mb-4">
              <input
                id="storeCredentials"
                type="checkbox"
                className="mr-2"
                checked={storeCredentials}
                onChange={(e) => setStoreCredentials(e.target.checked)}
              />
              <label htmlFor="storeCredentials" className="text-gray-700">
                Store my Microsoft credentials securely
              </label>
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
}
