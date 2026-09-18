const FlightCard = ({ flight, onCancelClick }) => {
  const isCancelled = flight.status === 'CANCELLED';

  return (
    <div
      className="rounded-lg p-4 hover:shadow-md transition-shadow flex flex-col justify-between"
      style={{
        backgroundColor: '#EAE6DF',
        border: isCancelled ? '1.5px solid #DC2626' : '1px solid #D6D0C6',
      }}
    >
      <div>
        <div className="flex justify-between items-start mb-3 gap-2 flex-wrap">
          <div>
            <h3 className="font-semibold text-base sm:text-lg" style={{ color: '#2A423A' }}>{flight.flight_number}</h3>
            <p className="text-xs sm:text-sm" style={{ color: '#3D5247' }}>{flight.airline}</p>
          </div>
          <span className={`px-2.5 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${
            isCancelled 
              ? 'bg-red-100 text-red-600' 
              : 'bg-green-100 text-green-600'
          }`}>
            {flight.status}
          </span>
        </div>

        <div className="space-y-2 text-xs sm:text-sm">
          <div className="flex justify-between gap-2">
            <span style={{ color: '#3D5247' }}>Origin:</span>
            <span className="font-medium truncate" style={{ color: '#2A423A' }}>{flight.origin}</span>
          </div>
          <div className="flex justify-between gap-2">
            <span style={{ color: '#3D5247' }}>Destination:</span>
            <span className="font-medium truncate" style={{ color: '#2A423A' }}>{flight.destination}</span>
          </div>
          <div className="flex justify-between gap-2">
            <span style={{ color: '#3D5247' }}>Departure:</span>
            <span className="font-medium text-right text-xs sm:text-sm" style={{ color: '#2A423A' }}>{new Date(flight.departure_time).toLocaleString()}</span>
          </div>
          <div className="flex justify-between gap-2">
            <span style={{ color: '#3D5247' }}>Arrival:</span>
            <span className="font-medium text-right text-xs sm:text-sm" style={{ color: '#2A423A' }}>{new Date(flight.arrival_time).toLocaleString()}</span>
          </div>
          <div className="flex justify-between gap-2">
            <span style={{ color: '#3D5247' }}>Seats:</span>
            <span className="font-medium" style={{ color: '#2A423A' }}>{flight.total_seats}</span>
          </div>
        </div>
      </div>

      {!isCancelled && (
        <button
          onClick={() => onCancelClick(flight)}
          className="mt-4 w-full px-4 py-2.5 bg-red-600 text-white text-sm font-semibold rounded-lg hover:bg-red-700 transition-colors active:scale-98"
        >
          Cancel Flight
        </button>
      )}
    </div>
  );
};

export default FlightCard;