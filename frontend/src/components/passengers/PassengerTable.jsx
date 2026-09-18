import PriorityBadge from './PriorityBadge';

// Priority sort order for client-side safety net (backend also sorts)
const PRIORITY_ORDER = { HIGH: 0, MEDIUM: 1, NORMAL: 2, REVIEW_REQUIRED: 3 };

// Left border color by priority for quick visual scanning
const ROW_BORDER = {
  HIGH: 'border-l-4 border-l-red-500',
  MEDIUM: 'border-l-4 border-l-orange-400',
  NORMAL: 'border-l-4 border-l-green-500',
  REVIEW_REQUIRED: 'border-l-4 border-l-gray-400',
};

const PassengerTable = ({ recommendations, onApprove, onReject }) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="text-slate-600 py-4">No affected passengers found for this flight.</div>
    );
  }

  // Sort client-side as a safety net (backend also orders by priority)
  const sorted = [...recommendations].sort(
    (a, b) => (PRIORITY_ORDER[a.priority] ?? 99) - (PRIORITY_ORDER[b.priority] ?? 99)
  );

  return (
    <div className="overflow-x-auto -mx-2 sm:mx-0">
      <table className="w-full min-w-[650px] border-collapse">
        <thead>
          <tr className="border-b-2" style={{ backgroundColor: '#EAE6DF', borderBottomColor: '#D6D0C6' }}>
            <th className="text-left py-3 px-3 sm:px-4 text-xs font-semibold uppercase tracking-wider" style={{ color: '#3D5247' }}>#</th>
            <th className="text-left py-3 px-3 sm:px-4 text-xs font-semibold uppercase tracking-wider" style={{ color: '#3D5247' }}>Passenger</th>
            <th className="text-left py-3 px-3 sm:px-4 text-xs font-semibold uppercase tracking-wider" style={{ color: '#3D5247' }}>Need / Reason</th>
            <th className="text-left py-3 px-3 sm:px-4 text-xs font-semibold uppercase tracking-wider" style={{ color: '#3D5247' }}>Priority</th>
            <th className="text-left py-3 px-3 sm:px-4 text-xs font-semibold uppercase tracking-wider" style={{ color: '#3D5247' }}>Suggested Flight</th>
            <th className="text-left py-3 px-3 sm:px-4 text-xs font-semibold uppercase tracking-wider" style={{ color: '#3D5247' }}>Status</th>
            <th className="text-left py-3 px-3 sm:px-4 text-xs font-semibold uppercase tracking-wider" style={{ color: '#3D5247' }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((rec, index) => (
            <tr
              key={rec.recommendation_id}
              className={`${ROW_BORDER[rec.priority] || 'border-l-4 border-l-transparent'} transition-colors`}
              style={{ borderBottom: '1px solid #E8E4DC' }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#F0EDE6'; }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = ''; }}
            >
              {/* Rank */}
              <td className="py-3 px-3 sm:px-4">
                <span className="text-xs sm:text-sm font-bold" style={{ color: '#A8B5AF' }}>#{index + 1}</span>
              </td>

              {/* Passenger name */}
              <td className="py-3 px-3 sm:px-4">
                <div className="text-xs sm:text-sm font-semibold" style={{ color: '#2A423A' }}>
                  {rec.passenger_name || `Passenger ${rec.passenger_id.toString().slice(0, 8)}…`}
                </div>
              </td>

              {/* Reason */}
              <td className="py-3 px-3 sm:px-4 max-w-xs">
                <div className="text-xs sm:text-sm leading-snug" style={{ color: '#3D5247' }}>{rec.reason || '—'}</div>
              </td>

              {/* Priority badge */}
              <td className="py-3 px-3 sm:px-4 whitespace-nowrap">
                <PriorityBadge priority={rec.priority} />
              </td>

              {/* Suggested flight */}
              <td className="py-3 px-3 sm:px-4 whitespace-nowrap">
                {rec.recommended_flight_number ? (
                  <span className="text-xs sm:text-sm font-medium text-blue-700 bg-blue-50 px-2 py-1 rounded">
                    {rec.recommended_flight_number}
                  </span>
                ) : rec.recommended_flight_id ? (
                  <span className="text-xs sm:text-sm text-slate-500">
                    ID: {rec.recommended_flight_id.toString().slice(0, 8)}…
                  </span>
                ) : (
                  <span className="text-xs sm:text-sm text-red-500 italic">No suitable flight</span>
                )}
              </td>

              {/* Status */}
              <td className="py-3 px-3 sm:px-4 whitespace-nowrap">
                <span className={`text-xs sm:text-sm font-semibold ${
                  rec.status === 'APPROVED'  ? 'text-green-600'  :
                  rec.status === 'REJECTED'  ? 'text-red-600'    :
                  rec.status === 'ESCALATED' ? 'text-purple-600' :
                  rec.status === 'PENDING'   ? 'text-orange-600' :
                  'text-slate-500'
                }`}>
                  {rec.status}
                </span>
              </td>

              {/* Actions */}
              <td className="py-3 px-3 sm:px-4 whitespace-nowrap">
                {rec.status === 'PENDING' ? (
                  <div className="flex gap-2">
                    <button
                      onClick={() => onApprove(rec.recommendation_id)}
                      className="px-2.5 py-1 bg-green-500 text-white text-xs font-semibold rounded hover:bg-green-600 transition-colors"
                    >
                      ✓ Approve
                    </button>
                    <button
                      onClick={() => onReject(rec.recommendation_id)}
                      className="px-2.5 py-1 bg-red-500 text-white text-xs font-semibold rounded hover:bg-red-600 transition-colors"
                    >
                      ✗ Reject
                    </button>
                  </div>
                ) : (
                  <span className="text-xs text-slate-400 italic">Completed</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PassengerTable;