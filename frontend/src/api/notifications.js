import apiClient from './client';

export const sendNotification = async (notificationId) => {
  const response = await apiClient.post(`/notifications/${notificationId}/send`);
  return response.data;
};

export const updateNotification = async (notificationId, message) => {
  const response = await apiClient.patch(`/notifications/${notificationId}`, {
    message,
  });
  return response.data;
};