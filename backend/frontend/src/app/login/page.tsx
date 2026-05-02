'use client';
import { useState } from 'react';
import Link from 'next/link';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password }),
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('token', data.access_token);
        window.location.href = '/dashboard';
      } else {
        alert(data.detail || "Login failed");
      }
    } catch(err) {
      alert("Network Error");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-zinc-950">
      <div className="w-full max-w-md p-8 space-y-8 bg-zinc-900 rounded-xl border border-zinc-800">
        <h1 className="text-3xl font-bold text-center text-white">Login</h1>
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300">Email</label>
            <input type="email" value={email} onChange={e=>setEmail(e.target.value)} required className="w-full px-4 py-2 mt-2 bg-zinc-800 border border-zinc-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300">Password</label>
            <input type="password" value={password} onChange={e=>setPassword(e.target.value)} required className="w-full px-4 py-2 mt-2 bg-zinc-800 border border-zinc-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500" />
          </div>
          <button type="submit" className="w-full py-3 font-semibold text-white bg-red-600 rounded-lg hover:bg-red-500 transition">
            Continue to Dashboard
          </button>
        </form>
        <p className="text-center text-gray-400">
          Don&apos;t have an account? <Link href="/register" className="text-red-500 hover:text-red-400">Sign Up</Link>
        </p>
      </div>
    </div>
  );
}
