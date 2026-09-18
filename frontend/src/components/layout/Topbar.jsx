import { useAuth } from '../../context/AuthContext';

const Topbar = ({ onMenuToggle }) => {
  const { user } = useAuth();

  return (
    <div 
      className="h-16 flex items-center justify-between px-4 sm:px-6" 
      style={{ backgroundColor: '#F4F1EA', borderBottom: '1px solid #E8E4DC' }}
    >
      <div className="flex items-center space-x-3">
        {/* Hamburger Menu Toggle Button on Mobile */}
        <button
          onClick={onMenuToggle}
          className="md:hidden p-2 rounded-lg text-[#2A423A] hover:bg-black/5 focus:outline-none transition-colors"
          aria-label="Toggle Navigation Menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <h2 className="font-semibold text-base sm:text-lg truncate" style={{ color: '#2A423A' }}>
          Operations Dashboard
        </h2>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="text-xs sm:text-sm truncate max-w-[130px] sm:max-w-[220px] md:max-w-none" style={{ color: '#3D5247' }}>
          {user?.email}
        </div>
      </div>
    </div>
  );
};

export default Topbar;