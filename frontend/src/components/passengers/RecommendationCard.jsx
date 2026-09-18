const RecommendationCard = ({ recommendation, onApprove, onReject }) => {
  return (
    <div className="border border-slate-200 rounded-lg p-4">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h4 className="font-medium text-slate-900">Recommendation #{recommendation.recommendation_id.toString().slice(0, 8)}...</h4>
          <p className="text-sm text-slate-600">{recommendation.reason}</p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          recommendation.status === 'APPROVED' ? 'bg-green-100 text-green-700' :
          recommendation.status === 'REJECTED' ? 'bg-red-100 text-red-700' :
          recommendation.status === 'PENDING' ? 'bg-orange-100 text-orange-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {recommendation.status}
        </span>
      </div>
      
      <div className="mb-3">
        <p className="text-sm text-slate-600">
          <span className="font-medium">Suggested Flight:</span> {recommendation.recommended_flight_id ? recommendation.recommended_flight_id.toString().slice(0, 8) + '...' : 'No suitable flight'}
        </p>
      </div>

      {recommendation.status === 'PENDING' && (
        <div className="flex gap-2">
          <button
            onClick={() => onApprove(recommendation.recommendation_id)}
            className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600"
          >
            Approve
          </button>
          <button
            onClick={() => onReject(recommendation.recommendation_id)}
            className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600"
          >
            Reject
          </button>
        </div>
      )}
    </div>
  );
};

export default RecommendationCard;