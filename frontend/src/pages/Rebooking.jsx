import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getFlights } from '../api/flights';
import { getFlightRecommendations, analyzeRebooking, approveRecommendation, rejectRecommendation } from '../api/rebooking';
import PassengerTable from '../components/passengers/PassengerTable';

const Rebooking = () => {
  const navigate = useNavigate();
  const [cancelledFlights, setCancelledFlights] = useState([]);
  const [selectedFlightId, setSelectedFlightId] = useState(null);
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loadingFlights, setLoadingFlights] = useState(true);
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [analyzeError, setAnalyzeError] = useState('');
  const autoAnalyzedRef = useRef({}); // track auto-analyzed flight IDs

  // Fetch all cancelled flights on mount
  useEffect(() => {
    const fetchCancelledFlights = async () => {
      try {
        setLoadingFlights(true);
        setError('');
        const response = await getFlights();
        const flights = Array.isArray(response) ? response : (response.flights ?? []);
        const cancelled = flights.filter(f => f.status === 'CANCELLED');
        setCancelledFlights(cancelled);
        
        if (cancelled.length > 0) {
          setSelectedFlightId(cancelled[0].flight_id);
          setSelectedFlight(cancelled[0]);
        }
      } catch (err) {
        console.error('Failed to fetch flights:', err);
        setError('Failed to load cancelled flights list');
      } finally {
        setLoadingFlights(false);
      }
    };

    fetchCancelledFlights();
  }, []);

  // When selected flight changes, fetch its recommendations & auto-analyze if needed
  useEffect(() => {
    if (!selectedFlightId) return;

    const currentFlight = cancelledFlights.find(f => f.flight_id === selectedFlightId);
    setSelectedFlight(currentFlight || null);

    const loadRecs = async () => {
      try {
        setLoadingRecs(true);
        setAnalyzeError('');
        const recsData = await getFlightRecommendations(selectedFlightId);
        const fetchedRecs = recsData.recommendations ?? [];
        setRecommendations(fetchedRecs);

        // Auto-analyze if 0 recommendations & not yet auto-analyzed for this flight
        if (fetchedRecs.length === 0 && !autoAnalyzedRef.current[selectedFlightId]) {
          autoAnalyzedRef.current[selectedFlightId] = true;
          setAnalyzing(true);
          try {
            const result = await analyzeRebooking(selectedFlightId);
            setRecommendations(result.recommendations ?? []);
          } catch (autoErr) {
            console.error('Auto-analyze failed:', autoErr);
            setAnalyzeError('Could not auto-generate recommendations. Try "Re-analyze" manually.');
          } finally {
            setAnalyzing(false);
          }
        }
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
        setAnalyzeError('Failed to load passenger recommendations.');
      } finally {
        setLoadingRecs(false);
      }
    };

    loadRecs();
  }, [selectedFlightId, cancelledFlights]);

  const handleAnalyze = async () => {
    if (!selectedFlightId) return;
    setAnalyzeError('');
    try {
      setAnalyzing(true);
      const result = await analyzeRebooking(selectedFlightId);
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
      const refreshed = await getFlightRecommendations(selectedFlightId);
      setRecommendations(refreshed.recommendations ?? []);
    } catch (err) {
      console.error('Failed to approve recommendation:', err);
    }
  };

  const handleReject = async (recommendationId) => {
    try {
      await rejectRecommendation(recommendationId);
      const refreshed = await getFlightRecommendations(selectedFlightId);
      setRecommendations(refreshed.recommendations ?? []);
    } catch (err) {
      console.error('Failed to reject recommendation:', err);
    }
  };

  if (loadingFlights) {
    return (
      <div className="p-6 flex items-center gap-3 text-slate-500">
        <svg className="animate-spin h-5 w-5 text-orange-500" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
        Loading cancelled flights...
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-4 sm:mb-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 sm:gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Passenger Rebooking Copilot</h1>
          <p className="text-slate-500 text-xs sm:text-sm mt-0.5">
            Prioritized passenger rebooking engine for cancelled flights
          </p>
        </div>
        <button
          onClick={() => navigate('/flights')}
          className="self-start sm:self-auto px-4 py-2 text-white text-xs sm:text-sm font-medium rounded-lg transition-colors whitespace-nowrap"
          style={{ backgroundColor: '#1D312A' }}
          onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#2A423A'; }}
          onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#1D312A'; }}
        >
          Manage All Flights →
        </button>
      </div>

      {error && (
        <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-red-50 text-red-700 text-xs sm:text-sm rounded-lg">{error}</div>
      )}

      {/* No Cancelled Flights Banner */}
      {cancelledFlights.length === 0 && !loadingFlights && (
        <div className="rounded-lg shadow p-6 sm:p-8 text-center border border-slate-200" style={{ backgroundColor: '#FDFCF9' }}>
          <div className="text-3xl sm:text-4xl mb-3">✈️</div>
          <h3 className="text-base sm:text-lg font-semibold text-slate-800 mb-2">No Cancelled Flights</h3>
          <p className="text-slate-500 text-xs sm:text-sm max-w-md mx-auto mb-6">
            There are currently no cancelled flights requiring passenger rebooking.
            You can cancel an active flight from the Flights view to initiate auto-rebooking.
          </p>
          <button
            onClick={() => navigate('/flights')}
            className="px-5 py-2.5 bg-orange-500 text-white font-medium rounded-lg hover:bg-orange-600 transition-colors text-xs sm:text-sm"
          >
            Go to Flights List
          </button>
        </div>
      )}

      {/* Main Content with Flight Selector & Passenger Priority Table */}
      {cancelledFlights.length > 0 && (
        <div className="space-y-4 sm:space-y-6">
          {/* Flight Selector Bar */}
          <div className="rounded-lg shadow p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4 border border-slate-200" style={{ backgroundColor: '#FDFCF9' }}>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-3 w-full sm:w-auto">
              <span className="text-xs sm:text-sm font-semibold text-slate-700 whitespace-nowrap">Select Cancelled Flight:</span>
              <select
                value={selectedFlightId || ''}
                onChange={(e) => setSelectedFlightId(e.target.value)}
                className="w-full sm:w-auto border text-xs sm:text-sm rounded-lg p-2.5 font-medium focus:ring-orange-500 focus:border-orange-500 max-w-full"
                style={{ backgroundColor: '#F4F1EA', borderColor: '#D6D0C6', color: '#2A423A' }}
              >
                {cancelledFlights.map((f) => (
                  <option key={f.flight_id} value={f.flight_id}>
                    {f.flight_number} ({f.origin} → {f.destination})
                  </option>
                ))}
              </select>
            </div>

            {selectedFlight && (
              <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                <span className="bg-red-100 text-red-800 font-semibold px-2.5 py-1 rounded-full whitespace-nowrap">
                  STATUS: {selectedFlight.status}
                </span>
                <span className="truncate">Reason: <strong className="text-slate-700">{selectedFlight.cancellation_reason || 'Disruption'}</strong></span>
              </div>
            )}
          </div>

          {/* Passenger Priorities Table Container */}
          <div className="rounded-lg shadow p-4 sm:p-6 border border-slate-200" style={{ backgroundColor: '#FDFCF9' }}>
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 gap-3">
              <div>
                <h2 className="text-lg sm:text-xl font-bold text-slate-900">
                  Priority Passenger Queue {selectedFlight ? `— ${selectedFlight.flight_number}` : ''}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Ordered by AI priority: 🔴 HIGH (Special Needs/Urgent) → 🟠 MEDIUM (Connecting ≤18h) → 🟢 NORMAL
                </p>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzing || loadingRecs}
                className="self-start sm:self-auto px-4 py-2 bg-orange-500 text-white text-xs sm:text-sm rounded-lg hover:bg-orange-600 disabled:opacity-50 flex items-center gap-2 font-medium transition-colors whitespace-nowrap"
              >
                {analyzing && (
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                )}
                {analyzing ? 'Analyzing Passengers…' : '↻ Re-analyze Queue'}
              </button>
            </div>

            {analyzeError && (
              <div className="mb-4 p-3 bg-red-50 text-red-600 text-xs sm:text-sm rounded-lg">{analyzeError}</div>
            )}

            {(loadingRecs || analyzing) && recommendations.length === 0 ? (
              <div className="flex items-center gap-3 text-slate-500 py-10 justify-center text-xs sm:text-sm">
                <svg className="animate-spin h-5 w-5 sm:h-6 sm:w-6 text-orange-500 flex-shrink-0" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Analyzing affected passengers and calculating rebooking priorities...
              </div>
            ) : recommendations.length > 0 ? (
              <PassengerTable
                recommendations={recommendations}
                onApprove={handleApprove}
                onReject={handleReject}
              />
            ) : (
              <div className="text-slate-500 py-8 text-center rounded-lg text-xs sm:text-sm" style={{ border: '1px dashed #D6D0C6' }}>
                No rebooking recommendations found for this flight.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Rebooking;
