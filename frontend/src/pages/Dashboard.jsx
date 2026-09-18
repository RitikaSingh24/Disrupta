import { useState, useEffect } from 'react';
import { getDashboardOverview } from '../api/dashboard';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Dashboard = () => {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await getDashboardOverview();
      setOverview(data);
    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="p-4 sm:p-6">
        <div className="bg-red-50 text-danger p-4 rounded-lg">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto">
      <h1 className="text-xl sm:text-2xl font-bold text-slate mb-4 sm:mb-6">Dashboard Overview</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="border border-slate rounded-lg p-4 sm:p-6 shadow-sm" style={{ backgroundColor: '#FDFCF9' }}>
          <div className="text-xs sm:text-sm mb-1 sm:mb-2 font-medium" style={{ color: '#3D5247' }}>Total Flights</div>
          <div className="text-2xl sm:text-3xl font-bold text-navy">{overview.total_flights}</div>
        </div>

        <div className="border border-slate rounded-lg p-4 sm:p-6 shadow-sm" style={{ backgroundColor: '#FDFCF9' }}>
          <div className="text-xs sm:text-sm mb-1 sm:mb-2 font-medium" style={{ color: '#3D5247' }}>Cancelled Flights</div>
          <div className="text-2xl sm:text-3xl font-bold text-danger">{overview.cancelled_flights}</div>
        </div>

        <div className="border border-slate rounded-lg p-4 sm:p-6 shadow-sm" style={{ backgroundColor: '#FDFCF9' }}>
          <div className="text-xs sm:text-sm mb-1 sm:mb-2 font-medium" style={{ color: '#3D5247' }}>Affected Passengers</div>
          <div className="text-2xl sm:text-3xl font-bold text-warning">{overview.affected_passengers}</div>
        </div>

        <div className="border border-slate rounded-lg p-4 sm:p-6 shadow-sm" style={{ backgroundColor: '#FDFCF9' }}>
          <div className="text-xs sm:text-sm mb-1 sm:mb-2 font-medium" style={{ color: '#3D5247' }}>Pending Recommendations</div>
          <div className="text-2xl sm:text-3xl font-bold text-orange">{overview.pending_recommendations}</div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;