import apiClient from './client';

export const getFlights = async () => {
  const response = await apiClient.get('/flights');
  return response.data;
};

export const getFlight = async (flightId) => {
  const response = await apiClient.get(`/flights/${flightId}`);
  return response.data;
};

export const cancelFlight = async (flightId, reason) => {
  const response = await apiClient.post(`/flights/${flightId}/cancel`, {
    reason,
  });
  return response.data;
};