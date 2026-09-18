import { useState } from 'react';

const CancelFlightModal = ({ flight, onCancel, onClose }) => {
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await onCancel(flight.flight_id, reason);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to cancel flight');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="rounded-lg p-4 sm:p-6 w-full max-w-md my-auto shadow-2xl max-h-[90vh] overflow-y-auto" style={{ backgroundColor: '#FDFCF9' }}>
        <h3 className="text-base sm:text-lg font-semibold mb-4" style={{ color: '#2A423A' }}>Cancel Flight</h3>
        
        <div className="mb-4 p-3 sm:p-4 rounded-lg" style={{ backgroundColor: '#EAE6DF' }}>
          <p className="text-xs sm:text-sm" style={{ color: '#3D5247' }}>
            <span className="font-medium">Flight:</span> {flight.flight_number}
          </p>
          <p className="text-xs sm:text-sm" style={{ color: '#3D5247' }}>
            <span className="font-medium">Route:</span> {flight.origin} → {flight.destination}
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-xs sm:text-sm font-medium mb-2" style={{ color: '#3D5247' }}>
              Cancellation Reason
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3 py-2.5 text-xs sm:text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              style={{ border: '1px solid #D6D0C6', backgroundColor: '#FDFCF9', color: '#2A423A' }}
              rows="3"
              placeholder="Enter reason for cancellation..."
              required
            />
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 text-xs sm:text-sm rounded">
              {error}
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors"
              style={{ color: '#3D5247' }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#EAE6DF'; }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = ''; }}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-red-600 text-white text-xs sm:text-sm font-semibold rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Cancelling...' : 'Confirm Cancellation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CancelFlightModal;