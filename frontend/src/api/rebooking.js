import apiClient from './client';

export const getFlightRecommendations = async (flightId) => {
  const response = await apiClient.get(`/rebooking/flight/${flightId}`);
  return response.data;
};

export const analyzeRebooking = async (flightId) => {
  const response = await apiClient.post('/rebooking/analyze', {
    flight_id: flightId,
  });
  return response.data;
};

export const approveRecommendation = async (recommendationId) => {
  const response = await apiClient.post(`/rebooking/${recommendationId}/approve`);
  return response.data;
};

export const editRecommendation = async (recommendationId, recommendedFlightId) => {
  const response = await apiClient.post(`/rebooking/${recommendationId}/edit`, {
    recommended_flight_id: recommendedFlightId,
  });
  return response.data;
};

export const rejectRecommendation = async (recommendationId) => {
  const response = await apiClient.post(`/rebooking/${recommendationId}/reject`);
  return response.data;
};