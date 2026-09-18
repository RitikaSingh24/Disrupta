import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getFlights, cancelFlight } from '../api/flights';
import FlightCard from '../components/flights/FlightCard';
import CancelFlightModal from '../components/flights/CancelFlightModal';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Flights = () => {
  const navigate = useNavigate();
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);

  useEffect(() => {
    loadFlights();
  }, []);

  const loadFlights = async () => {
    try {
      setLoading(true);
      const data = await getFlights();
      setFlights(data.flights || []);
    } catch (err) {
      setError('Failed to load flights');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelClick = (flight) => {
    setSelectedFlight(flight);
    setShowCancelModal(true);
  };

  const handleCancelFlight = async (flightId, reason) => {
    await cancelFlight(flightId, reason);
    setShowCancelModal(false);
    // Navigate to the flight detail page to show the passenger rebooking dashboard
    navigate(`/flights/${flightId}`);
  };

  const handleCloseModal = () => {
    setShowCancelModal(false);
    setSelectedFlight(null);
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
      <h1 className="text-xl sm:text-2xl font-bold text-slate mb-4 sm:mb-6">Flights</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        {flights.map((flight) => (
          <FlightCard
            key={flight.flight_id}
            flight={flight}
            onCancelClick={handleCancelClick}
          />
        ))}
      </div>

      {showCancelModal && selectedFlight && (
        <CancelFlightModal
          flight={selectedFlight}
          onCancel={handleCancelFlight}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default Flights;