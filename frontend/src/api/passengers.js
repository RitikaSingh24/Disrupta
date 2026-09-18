import apiClient from './client';

export const getPassenger = async (passengerId) => {
  const response = await apiClient.get(`/passengers/${passengerId}`);
  return response.data;
};