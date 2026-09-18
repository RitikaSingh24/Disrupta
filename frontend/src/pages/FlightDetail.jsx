import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getFlight } from '../api/flights';
import { getFlightRecommendations, analyzeRebooking, approveRecommendation, rejectRecommendation } from '../api/rebooking';
import PassengerTable from '../components/passengers/PassengerTable';

const FlightDetail = () => {
  const { flightId } = useParams();
  const navigate = useNavigate();
  const [flight, setFlight] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState('');
  const [error, setError] = useState('');
  const autoAnalyzedRef = useRef(false); // prevent double-trigger in StrictMode

  useEffect(() => {
    if (!flightId) return;
    autoAnalyzedRef.current = false; // reset on flightId change
    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');
        setAnalyzeError('');

        const [flightData, recommendationsData] = await Promise.all([
          getFlight(flightId),
          getFlightRecommendations(flightId),
        ]);

        // Backend returns FlightDetailResponse as a flat object (not { flight: ... })
        const fetchedFlight = flightData.flight_id ? flightData : (flightData.flight ?? flightData);
        const fetchedRecs = recommendationsData.recommendations ?? [];

        setFlight(fetchedFlight);
        setRecommendations(fetchedRecs);

        // Auto-analyze: if this is a CANCELLED flight with no recommendations yet,
        // immediately trigger analysis so the passenger table appears automatically.
        if (
          fetchedFlight?.status === 'CANCELLED' &&
          fetchedRecs.length === 0 &&
          !autoAnalyzedRef.current
        ) {
          autoAnalyzedRef.current = true;
          setAnalyzing(true);
          try {
            const result = await analyzeRebooking(flightId);
            setRecommendations(result.recommendations ?? []);
          } catch (analyzeErr) {
            console.error('Auto-analyze failed:', analyzeErr);
            setAnalyzeError('Could not auto-generate recommendations. Try "Analyze Passengers" manually.');
          } finally {
            setAnalyzing(false);
          }
        }
      } catch (err) {
        setError('Failed to load flight details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [flightId]);

  const handleAnalyze = async () => {
    setAnalyzeError('');
    try {
      setAnalyzing(true);
      const result = await analyzeRebooking(flightId);
      setRecommendations(result.recommendations ?? []);
    } catch (err) {
      console.error('Failed to analyze flight:', err);
      setAnalyzeError('Failed to analyze passengers. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleApprove = async (recommendationId) => {
    try {
      await approveRecommendation(recommendationId);
      const refreshed = await getFlightRecommendations(flightId);
      setRecommendations(refreshed.recommendations ?? []);
    } catch (err) {
      console.error('Failed to approve recommendation:', err);
    }
  };

  const handleReject = async (recommendationId) => {
    try {
      await rejectRecommendation(recommendationId);
      const refreshed = await getFlightRecommendations(flightId);
      setRecommendations(refreshed.recommendations ?? []);
    } catch (err) {
      console.error('Failed to reject recommendation:', err);
    }
  };

  // ── Loading state ───────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="p-6 flex items-center gap-3 text-slate-500">
        <svg className="animate-spin h-5 w-5 text-orange-500" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
        Loading flight details...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-red-600 bg-red-50 p-4 rounded-lg">{error}</div>
      </div>
    );
  }

  if (!flight) {
    return (
      <div className="p-6">
        <div className="text-slate-600">Flight not found</div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto">
      {/* Back + Title */}
      <div className="mb-4 sm:mb-6">
        <button
          onClick={() => navigate('/flights')}
          className="text-slate-500 hover:text-slate-800 mb-3 sm:mb-4 flex items-center gap-1 text-xs sm:text-sm font-medium"
        >
          ← Back to Flights
        </button>
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Flight Details</h1>
      </div>

      {/* Flight Information Card */}
      <div className="rounded-lg shadow p-4 sm:p-6 mb-4 sm:mb-6" style={{ backgroundColor: '#FDFCF9' }}>
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-4 gap-2">
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-slate-900">{flight.flight_number}</h2>
            <p className="text-sm text-slate-600">{flight.origin} → {flight.destination}</p>
          </div>
          <div className={`self-start px-3 py-1 rounded-full text-xs sm:text-sm font-semibold whitespace-nowrap ${
            flight.status === 'CANCELLED'
              ? 'bg-red-100 text-red-700'
              : 'bg-green-100 text-green-700'
          }`}>
            {flight.status}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 text-xs sm:text-sm">
          <div>
            <span className="text-slate-500">Departure:</span>
            <span className="ml-2 text-slate-900 font-medium">{new Date(flight.departure_time).toLocaleString()}</span>
          </div>
          <div>
            <span className="text-slate-500">Arrival:</span>
            <span className="ml-2 text-slate-900 font-medium">{new Date(flight.arrival_time).toLocaleString()}</span>
          </div>
          <div>
            <span className="text-slate-500">Airline:</span>
            <span className="ml-2 text-slate-900 font-medium">{flight.airline}</span>
          </div>
          <div>
            <span className="text-slate-500">Total Seats:</span>
            <span className="ml-2 text-slate-900 font-medium">{flight.total_seats}</span>
          </div>
        </div>

        {flight.cancellation_reason && (
          <div className="mt-4 p-3 bg-red-50 rounded-lg text-xs sm:text-sm">
            <span className="text-red-700 font-medium">Cancellation Reason:</span>
            <span className="ml-2 text-red-600">{flight.cancellation_reason}</span>
          </div>
        )}
      </div>

      {/* Affected Passengers & Rebooking — only for CANCELLED flights */}
      {flight.status === 'CANCELLED' && (
        <div className="rounded-lg shadow p-4 sm:p-6" style={{ backgroundColor: '#FDFCF9' }}>
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 gap-3">
            <h2 className="text-lg sm:text-xl font-bold text-slate-900">
              Affected Passengers &amp; Rebooking
            </h2>

            {/* Manual re-analyze button */}
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="self-start sm:self-auto px-4 py-2 bg-orange-500 text-white text-xs sm:text-sm font-semibold rounded hover:bg-orange-600 disabled:opacity-50 flex items-center gap-2 transition-colors"
            >
              {analyzing && (
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
              )}
              {analyzing ? 'Analyzing…' : '↻ Re-analyze'}
            </button>
          </div>

          {/* Auto-analyzing spinner */}
          {analyzing && recommendations.length === 0 && (
            <div className="flex items-center gap-3 text-slate-500 py-6 text-xs sm:text-sm">
              <svg className="animate-spin h-5 w-5 text-orange-500 flex-shrink-0" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
              Analyzing affected passengers and generating rebooking recommendations…
            </div>
          )}

          {/* Error from analyze */}
          {analyzeError && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 text-xs sm:text-sm rounded-lg">{analyzeError}</div>
          )}

          {/* Empty state — only show after analysis is done */}
          {!analyzing && recommendations.length === 0 && !analyzeError && (
            <div className="text-slate-500 py-6 text-center text-xs sm:text-sm">
              No affected passengers found for this flight.
            </div>
          )}

          {/* Passenger priority table */}
          {recommendations.length > 0 && (
            <PassengerTable
              recommendations={recommendations}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default FlightDetail;