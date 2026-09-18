import apiClient from './client';

export const getDashboardOverview = async () => {
  const response = await apiClient.get('/dashboard/overview');
  return response.data;
};