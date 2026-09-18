import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Sidebar = ({ mobileMenuOpen, setMobileMenuOpen }) => {
  const { logout, user } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/flights', label: 'Flights' },
    { path: '/rebooking', label: 'Rebooking' },
  ];

  const handleNavClick = () => {
    if (setMobileMenuOpen) {
      setMobileMenuOpen(false);
    }
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm transition-opacity"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar Container: Fixed width on Desktop, Sliding Drawer on Mobile */}
      <div 
        className={`fixed inset-y-0 left-0 z-50 w-64 flex flex-col transition-transform duration-300 ease-in-out md:static md:translate-x-0 md:min-h-screen ${
          mobileMenuOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'
        }`}
        style={{ backgroundColor: '#2A423A' }}
      >
        <div className="p-6 flex items-center justify-between" style={{ borderBottom: '1px solid #1D312A' }}>
          <div className="flex items-center space-x-3">
            <div 
              className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: '#1D312A', border: '1px solid rgba(255, 255, 255, 0.1)' }}
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C12 7.5 7.5 12 2 12C7.5 12 12 16.5 12 22C12 16.5 16.5 12 22 12C16.5 12 12 7.5 12 2Z" fill="#EFECE6"/>
                <path d="M19 2C19 4 17.5 5.5 15.5 5.5C17.5 5.5 19 7 19 9C19 7 20.5 5.5 22.5 5.5C20.5 5.5 19 4 19 2Z" fill="#EFECE6"/>
              </svg>
            </div>
            <div>
              <h1 className="text-base font-semibold leading-tight" style={{ color: '#EFECE6' }}>IROP Rebooking</h1>
              <p className="text-xs mt-0.5" style={{ color: '#EFECE6', opacity: 0.6 }}>Passenger Copilot</p>
            </div>
          </div>

          {/* Close button on mobile drawer */}
          <button 
            onClick={() => setMobileMenuOpen(false)}
            className="md:hidden p-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-[#1D312A] focus:outline-none"
            aria-label="Close menu"
          >
            ✕
          </button>
        </div>
        
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  onClick={handleNavClick}
                  className={({ isActive }) =>
                    `block px-4 py-2.5 rounded-lg transition-colors font-medium text-sm ${
                      isActive ? '' : ''
                    }`
                  }
                  style={({ isActive }) => 
                    isActive 
                      ? { backgroundColor: '#1D312A', color: '#FDFCF9', borderLeft: '3px solid #EFECE6' } 
                      : { color: '#EFECE6', opacity: 0.8 }
                  }
                  onMouseEnter={(e) => { 
                    if (!location.pathname.startsWith(item.path)) { 
                      e.currentTarget.style.backgroundColor = '#1D312A'; 
                      e.currentTarget.style.opacity = '1';
                    } 
                  }}
                  onMouseLeave={(e) => { 
                    if (!location.pathname.startsWith(item.path)) { 
                      e.currentTarget.style.backgroundColor = 'transparent'; 
                      e.currentTarget.style.opacity = '0.8';
                    } 
                  }}
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4" style={{ borderTop: '1px solid #1D312A' }}>
          <div className="text-sm mb-2 truncate" style={{ color: '#EFECE6', opacity: 0.6 }}>
            {user?.email}
          </div>
          <button
            onClick={() => {
              handleNavClick();
              logout();
            }}
            className="w-full px-4 py-2 text-white rounded-lg transition-colors font-medium text-sm"
            style={{ backgroundColor: '#1D312A' }}
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#DC2626'; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#1D312A'; }}
          >
            Logout
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;