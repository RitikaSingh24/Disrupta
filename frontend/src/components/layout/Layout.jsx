import { useState } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

const Layout = ({ children }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-gray-100 overflow-x-hidden">
      <Sidebar 
        mobileMenuOpen={mobileMenuOpen} 
        setMobileMenuOpen={setMobileMenuOpen} 
      />

      <div className="flex-1 flex flex-col min-w-0">
        <Topbar 
          onMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)} 
        />
        <main className="flex-1 bg-gray-100 min-w-0">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;