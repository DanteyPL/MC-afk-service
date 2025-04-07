import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import Head from 'next/head';

export default function Dashboard() {
  const [afkStatus, setAfkStatus] = useState('inactive');
  const [stats, setStats] = useState<any>({});
  const router = useRouter();

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Load initial status
    checkAfkStatus();
    loadStats();
  }, []);

  const checkAfkStatus = async () => {
    try {
      const response = await axios.get('/api/minecraft/status', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setAfkStatus(response.data.status);
    } catch (error) {
      console.error('Failed to check AFK status:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get('/api/minecraft/stats', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = response.data;
      setStats({
        itemsCollected: data.items_collected,
        shinyItems: data.shiny_items,
        sessionTime: formatSessionTime(data.session_time),
        cpuUsage: `${(data.cpu_usage / 1e9).toFixed(2)}%`,
        memoryUsage: `${(data.memory_usage / (1024 * 1024)).toFixed(2)} MB`
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
      setStats({
        itemsCollected: 0,
        shinyItems: 0,
        sessionTime: '0h 0m',
        cpuUsage: '0%',
        memoryUsage: '0 MB'
      });
    }
  };

  const formatSessionTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const toggleAfk = async () => {
    try {
      if (afkStatus === 'active') {
        await axios.post('/api/minecraft/stop', {}, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
      } else {
        await axios.post('/api/minecraft/start', {}, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
      }
      checkAfkStatus();
    } catch (error) {
      console.error('Failed to toggle AFK:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Head>
        <title>Minecraft AFK Dashboard</title>
      </Head>

      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">AFK Dashboard</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">AFK Status</h2>
              <button
                onClick={toggleAfk}
                className={`px-4 py-2 rounded-md text-white ${
                  afkStatus === 'active' 
                    ? 'bg-red-500 hover:bg-red-600' 
                    : 'bg-green-500 hover:bg-green-600'
                }`}
              >
                {afkStatus === 'active' ? 'Stop AFK' : 'Start AFK'}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-700">Items Collected</h3>
                <p className="text-2xl font-bold">{stats.itemsCollected || 0}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-700">Shiny Items</h3>
                <p className="text-2xl font-bold">{stats.shinyItems || 0}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-700">Session Time</h3>
                <p className="text-2xl font-bold">{stats.sessionTime || '0h 0m'}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-700">CPU Usage</h3>
                <p className="text-2xl font-bold">{stats.cpuUsage || '0%'}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-700">Memory Usage</h3>
                <p className="text-2xl font-bold">{stats.memoryUsage || '0 MB'}</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
