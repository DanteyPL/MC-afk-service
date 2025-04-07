import { NextPage } from 'next';
import Link from 'next/link';
import Head from 'next/head';

const HomePage: NextPage = () => {
  return (
    <>
      <Head>
        <title>Minecraft AFK Client</title>
        <meta name="description" content="Minecraft AFK Service Dashboard" />
      </Head>

      <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
        <main className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
          <h1 className="text-2xl font-bold text-center mb-6">Welcome to Minecraft AFK Client</h1>
          
          <div className="flex flex-col space-y-4">
            <div className="flex border-b border-gray-200">
              <Link
                href="/login"
                className="flex-1 py-2 px-4 text-center border-b-2 font-medium text-sm border-blue-500 text-blue-600"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="flex-1 py-2 px-4 text-center border-b-2 font-medium text-sm border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              >
                Register
              </Link>
              <Link
                href="/dashboard"
                className="flex-1 py-2 px-4 text-center border-b-2 font-medium text-sm border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              >
                Dashboard
              </Link>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h2 className="text-lg font-semibold mb-2">Welcome to Minecraft AFK Client</h2>
              <p className="text-gray-600">
                Manage your Minecraft AFK sessions and whitelist status from one place.
              </p>
            </div>
          </div>
        </main>
      </div>
    </>
  );
};

export default HomePage;
