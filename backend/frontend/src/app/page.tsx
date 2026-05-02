import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white flex flex-col items-center justify-center p-8">
      <div className="max-w-4xl text-center space-y-8">
        <h1 className="text-6xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-purple-600">
          Never Watch a Youtube Video ever again.
        </h1>
        <p className="text-xl text-gray-300 max-w-2xl mx-auto">
          AI-powered transcript summarization and active-recall chat. Turn hours of tutorials into high-density, structured study guides instantly.
        </p>
        
        <div className="flex justify-center gap-4 pt-8">
          <Link href="/login" className="px-8 py-3 rounded-lg font-semibold bg-gray-800 hover:bg-gray-700 transition">
            Login
          </Link>
          <Link href="/register" className="px-8 py-3 rounded-lg font-semibold bg-red-600 hover:bg-red-500 transition shadow-lg shadow-red-500/30">
            Get Started Free
          </Link>
        </div>
      </div>
      
      <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl text-center">
        <div className="bg-zinc-900 p-8 rounded-xl border border-zinc-800">
          <h3 className="text-2xl font-bold mb-4">Paste the Link</h3>
          <p className="text-gray-400">Just drop any YouTube video URL. Our engine bypasses captions and rips the raw transcript directly.</p>
        </div>
        <div className="bg-zinc-900 p-8 rounded-xl border border-zinc-800">
          <h3 className="text-2xl font-bold mb-4">AI Note Generation</h3>
          <p className="text-gray-400">Gemini 1.5 Flash structures your video into detailed markdown chapters, code snippets, and quizzes.</p>
        </div>
        <div className="bg-zinc-900 p-8 rounded-xl border border-zinc-800">
          <h3 className="text-2xl font-bold mb-4">Chat with the Video</h3>
          <p className="text-gray-400">Ask highly specific questions about the content. The AI remembers exactly what the video discussed.</p>
        </div>
      </div>
    </div>
  );
}
