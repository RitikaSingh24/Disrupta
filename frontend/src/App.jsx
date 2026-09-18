import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import Layout from './components/layout/Layout';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Flights from './pages/Flights';
import FlightDetail from './pages/FlightDetail';
import Rebooking from './pages/Rebooking';
import PassengerDetail from './pages/PassengerDetail';
import Notifications from './pages/Notifications';
import PassengerPortal from './pages/PassengerPortal';

const AppRoutes = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/flights"
        element={
          <ProtectedRoute>
            <Layout>
              <Flights />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/rebooking"
        element={
          <ProtectedRoute>
            <Layout>
              <Rebooking />
            </Layout>
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/flights/:flightId"
        element={
          <ProtectedRoute>
            <Layout>
              <FlightDetail />
            </Layout>
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/passengers/:passengerId"
        element={
          <ProtectedRoute>
            <Layout>
              <PassengerDetail />
            </Layout>
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/notifications"
        element={
          <ProtectedRoute>
            <Layout>
              <Notifications />
            </Layout>
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/portal/:token"
        element={<PassengerPortal />}
      />
    </Routes>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
};

export default App;