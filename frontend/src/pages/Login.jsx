import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  if (isAuthenticated) {
    navigate('/dashboard');
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(email, password);

    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center relative overflow-hidden px-4 select-none"
      style={{
        background: 'radial-gradient(circle at 50% 30%, rgba(42, 66, 58, 0.6) 0%, transparent 70%), linear-gradient(135deg, #0E1815 0%, #172822 50%, #0A110E 100%)'
      }}
    >
      {/* Dynamic Atmospheric CSS Animations */}
      <style>{`
        @keyframes planeHover {
          0%, 100% {
            transform: translate(-50%, -50%) translateY(0px) rotate(-1deg);
          }
          50% {
            transform: translate(-50%, -50%) translateY(-18px) rotate(1.5deg);
          }
        }

        @keyframes cloudDriftSlow {
          0% { transform: translateX(-15vw); }
          100% { transform: translateX(115vw); }
        }

        @keyframes cloudDriftFast {
          0% { transform: translateX(-25vw); }
          100% { transform: translateX(125vw); }
        }

        @keyframes strobeRed {
          0%, 92%, 100% { opacity: 0.2; transform: scale(1); }
          95% { opacity: 1; transform: scale(1.6); }
        }

        @keyframes strobeGreen {
          0%, 88%, 100% { opacity: 0.2; transform: scale(1); }
          91% { opacity: 1; transform: scale(1.6); }
        }

        @keyframes weatherPulse {
          0%, 100% { opacity: 0.15; }
          40% { opacity: 0.35; }
          70% { opacity: 0.2; }
        }

        @keyframes rainStream {
          0% { stroke-dashoffset: 600; }
          100% { stroke-dashoffset: 0; }
        }
      `}</style>

      {/* Atmospheric Weather Background Layer */}
      {/* Weather Radar Glow & Disruption Atmosphere */}
      <div
        className="absolute w-[50rem] h-[50rem] rounded-full pointer-events-none filter blur-3xl"
        style={{
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'radial-gradient(circle, rgba(61, 100, 86, 0.45) 0%, rgba(42, 66, 58, 0.15) 50%, transparent 75%)',
          animation: 'weatherPulse 10s ease-in-out infinite'
        }}
      />

      {/* Drifting Weather Clouds (Layer 1 - Deep Clouds) */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-25">
        <svg
          className="absolute top-10 w-[700px] h-[300px] text-[#A3B899] filter blur-xl"
          style={{ animation: 'cloudDriftSlow 50s linear infinite' }}
          viewBox="0 0 500 200" fill="currentColor"
        >
          <path d="M50 150 Q70 80 140 90 Q190 40 270 60 Q340 30 400 80 Q460 90 480 150 Z" />
        </svg>

        <svg
          className="absolute bottom-5 w-[850px] h-[350px] text-[#2A423A] filter blur-2xl"
          style={{ animation: 'cloudDriftFast 38s linear infinite 15s' }}
          viewBox="0 0 500 200" fill="currentColor"
        >
          <path d="M30 160 Q60 70 150 80 Q210 20 310 50 Q390 10 450 70 Q490 80 510 160 Z" />
        </svg>
      </div>

      {/* Rain & Wind Stream Particles */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20 z-0">
        <line x1="10%" y1="0%" x2="0%" y2="100%" stroke="#EFECE6" strokeWidth="1" strokeDasharray="30 120" style={{ animation: 'rainStream 2s linear infinite' }} />
        <line x1="30%" y1="0%" x2="20%" y2="100%" stroke="#EFECE6" strokeWidth="1.5" strokeDasharray="50 150" style={{ animation: 'rainStream 1.5s linear infinite 0.4s' }} />
        <line x1="60%" y1="0%" x2="50%" y2="100%" stroke="#EFECE6" strokeWidth="1" strokeDasharray="40 100" style={{ animation: 'rainStream 1.8s linear infinite 0.8s' }} />
        <line x1="85%" y1="0%" x2="75%" y2="100%" stroke="#EFECE6" strokeWidth="1.2" strokeDasharray="35 130" style={{ animation: 'rainStream 2.2s linear infinite 0.2s' }} />
      </svg>

      {/* REALISTIC LARGE JET AIRLINER (CENTERED IN BACKGROUND) */}
      <div
        className="absolute pointer-events-none z-0 transition-transform duration-700 ease-out"
        style={{
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          animation: 'planeHover 12s ease-in-out infinite'
        }}
      >
        {/* Jet Airliner Vector Graphics */}
        <div className="relative w-[750px] h-[450px] flex items-center justify-center">

          {/* Engine Exhaust Glow / Heat Trails */}
          <div className="absolute left-[260px] top-[260px] w-32 h-6 bg-gradient-to-l from-transparent to-amber-200/20 blur-md rounded-full transform -rotate-12" />
          <div className="absolute right-[260px] top-[260px] w-32 h-6 bg-gradient-to-r from-transparent to-amber-200/20 blur-md rounded-full transform rotate-12" />

          <svg
            viewBox="0 0 800 500"
            className="w-full h-full filter drop-shadow-[0_25px_35px_rgba(0,0,0,0.85)]"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient id="fuselageGrad" x1="400" y1="50" x2="400" y2="450" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stopColor="#4A6B5D" stopOpacity="0.45" />
                <stop offset="40%" stopColor="#2A423A" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#15241F" stopOpacity="0.75" />
              </linearGradient>

              <linearGradient id="wingGradLeft" x1="100" y1="250" x2="380" y2="250" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stopColor="#2A423A" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#3D5247" stopOpacity="0.55" />
              </linearGradient>

              <linearGradient id="wingGradRight" x1="420" y1="250" x2="700" y2="250" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stopColor="#3D5247" stopOpacity="0.55" />
                <stop offset="100%" stopColor="#2A423A" stopOpacity="0.25" />
              </linearGradient>

              <linearGradient id="engineGlow" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#EFECE6" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#2A423A" stopOpacity="0.2" />
              </linearGradient>
            </defs>

            {/* Main Swept Wings */}
            {/* Left Swept Wing */}
            <path d="M 380 230 L 40 300 L 70 320 L 380 270 Z" fill="url(#wingGradLeft)" stroke="rgba(239, 236, 230, 0.15)" strokeWidth="1" />
            {/* Left Winglet */}
            <path d="M 40 300 L 25 260 L 45 290 Z" fill="#EFECE6" opacity="0.4" />

            {/* Right Swept Wing */}
            <path d="M 420 230 L 760 300 L 730 320 L 420 270 Z" fill="url(#wingGradRight)" stroke="rgba(239, 236, 230, 0.15)" strokeWidth="1" />
            {/* Right Winglet */}
            <path d="M 760 300 L 775 260 L 755 290 Z" fill="#EFECE6" opacity="0.4" />

            {/* Horizontal Tail Stabilizers */}
            <path d="M 380 410 L 220 460 L 240 470 L 380 430 Z" fill="#2A423A" opacity="0.45" />
            <path d="M 420 410 L 580 460 L 560 470 L 420 430 Z" fill="#2A423A" opacity="0.45" />

            {/* Main Fuselage Body (Commercial Jetliner Outline) */}
            <path d="M 400 40 C 425 110 430 250 425 420 C 420 445 410 465 400 475 C 390 465 380 445 375 420 C 370 250 375 110 400 40 Z" fill="url(#fuselageGrad)" stroke="rgba(239, 236, 230, 0.25)" strokeWidth="1.5" />

            {/* Cockpit Windshield Nose Windows */}
            <path d="M 390 75 C 395 70 405 70 410 75 L 415 88 C 405 85 395 85 385 88 Z" fill="#EFECE6" opacity="0.75" />

            {/* Twin Turbofan Engines */}
            {/* Left Engine */}
            <rect x="250" y="270" width="28" height="60" rx="14" fill="#1D312A" stroke="rgba(239, 236, 230, 0.3)" strokeWidth="1" />
            <ellipse cx="264" cy="275" rx="12" ry="5" fill="url(#engineGlow)" />

            {/* Right Engine */}
            <rect x="522" y="270" width="28" height="60" rx="14" fill="#1D312A" stroke="rgba(239, 236, 230, 0.3)" strokeWidth="1" />
            <ellipse cx="536" cy="275" rx="12" ry="5" fill="url(#engineGlow)" />

            {/* Cabin Passenger Windows Lights */}
            <g fill="#EFECE6" opacity="0.4">
              <circle cx="392" cy="130" r="2" /><circle cx="408" cy="130" r="2" />
              <circle cx="391" cy="150" r="2" /><circle cx="409" cy="150" r="2" />
              <circle cx="390" cy="170" r="2" /><circle cx="410" cy="170" r="2" />
              <circle cx="389" cy="190" r="2" /><circle cx="411" cy="190" r="2" />
              <circle cx="388" cy="210" r="2" /><circle cx="412" cy="210" r="2" />
              <circle cx="387" cy="330" r="2" /><circle cx="413" cy="330" r="2" />
              <circle cx="387" cy="350" r="2" /><circle cx="413" cy="350" r="2" />
              <circle cx="388" cy="370" r="2" /><circle cx="412" cy="370" r="2" />
            </g>
          </svg>

          {/* Navigation Strobe Lights on Wingtips */}
          {/* Left Wing Strobe Light (Red) */}
          <div
            className="absolute left-[30px] bottom-[170px] w-4 h-4 rounded-full bg-red-500 shadow-[0_0_12px_#EF4444]"
            style={{ animation: 'strobeRed 2.5s infinite' }}
          />
          {/* Right Wing Strobe Light (Green) */}
          <div
            className="absolute right-[30px] bottom-[170px] w-4 h-4 rounded-full bg-emerald-400 shadow-[0_0_12px_#34D399]"
            style={{ animation: 'strobeGreen 2.5s infinite 0.3s' }}
          />
        </div>
      </div>

      {/* Foreground Drifting Cloud (Layer 2 - Soft Front Fog) */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-20 z-5">
        <svg
          className="absolute top-1/3 right-0 w-[600px] h-[250px] text-[#3D5247] filter blur-2xl"
          style={{ animation: 'cloudDriftSlow 42s linear infinite 5s' }}
          viewBox="0 0 500 200" fill="currentColor"
        >
          <path d="M40 140 Q80 60 160 70 Q230 20 320 50 Q380 20 440 80 Q480 90 500 140 Z" />
        </svg>
      </div>

      {/* LOGIN FORM CONTAINER */}
      <div
        className="relative z-10 rounded-2xl p-8 w-full max-w-md shadow-2xl backdrop-blur-md"
        style={{
          background: 'linear-gradient(145deg, rgba(42, 66, 58, 0.88) 0%, rgba(20, 34, 29, 0.94) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.14)',
          boxShadow: '0 30px 60px -12px rgba(0, 0, 0, 0.7), inset 0 1px 1px rgba(255, 255, 255, 0.15)'
        }}
      >
        <div className="text-center mb-8">
          <div
            className="mx-auto w-12 h-12 rounded-2xl flex items-center justify-center mb-4 shadow-inner"
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              border: '1px solid rgba(255, 255, 255, 0.15)'
            }}
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C12 7.5 7.5 12 2 12C7.5 12 12 16.5 12 22C12 16.5 16.5 12 22 12C16.5 12 12 7.5 12 2Z" fill="#EFECE6" />
              <path d="M19 2C19 4 17.5 5.5 15.5 5.5C17.5 5.5 19 7 19 9C19 7 20.5 5.5 22.5 5.5C20.5 5.5 19 4 19 2Z" fill="#EFECE6" />
            </svg>
          </div>
          <h1
            className="text-2xl font-bold tracking-tight"
            style={{
              background: 'linear-gradient(135deg, #FFFFFF 0%, #EAE6DF 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            IROP Rebooking Copilot
          </h1>
          <p className="mt-2 text-sm" style={{ color: '#A9B7B0' }}>
            Passenger Rebooking Operations
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#D6D0C6' }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl text-white placeholder-gray-400 focus:outline-none transition-all duration-200"
              style={{
                border: '1px solid rgba(255, 255, 255, 0.15)',
                backgroundColor: 'rgba(15, 26, 22, 0.65)',
                color: '#FFFFFF'
              }}
              placeholder="agent@airline.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#D6D0C6' }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl text-white placeholder-gray-400 focus:outline-none transition-all duration-200"
              style={{
                border: '1px solid rgba(255, 255, 255, 0.15)',
                backgroundColor: 'rgba(15, 26, 22, 0.65)',
                color: '#FFFFFF'
              }}
              placeholder="•••••••••"
              required
            />
          </div>

          {error && (
            <div className="p-3 bg-red-900/40 border border-red-500/40 text-red-200 text-sm rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 text-white font-semibold rounded-xl shadow-lg transition-all duration-200 disabled:opacity-50 transform active:scale-95"
            style={{
              background: 'linear-gradient(135deg, #436B5E 0%, #2A423A 100%)',
              boxShadow: '0 4px 15px rgba(42, 66, 58, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.2)',
              border: '1px solid rgba(255, 255, 255, 0.15)'
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;