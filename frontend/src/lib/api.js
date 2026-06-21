import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const api = axios.create({ baseURL: API });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('av_admin_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      const isAuthCall = err.config?.url?.includes('/auth/');
      if (!isAuthCall) {
        localStorage.removeItem('av_admin_token');
        if (window.location.pathname.startsWith('/admin') && window.location.pathname !== '/admin/login') {
          window.location.href = '/admin/login?expired=1';
        }
      }
    }
    return Promise.reject(err);
  }
);

export default api;

export const fetchNotices = (params = {}) => api.get('/notices', { params }).then(r => r.data);
export const fetchNotice = (id) => api.get(`/notices/${id}`).then(r => r.data);
export const fetchStats = () => api.get('/stats').then(r => r.data);
export const fetchDistricts = () => api.get('/districts').then(r => r.data);
export const submitContact = (data) => api.post('/contact', data).then(r => r.data);
export const loginAdmin = (data) => api.post('/auth/login', data).then(r => r.data);
export const verifyAdmin = () => api.get('/auth/verify').then(r => r.data);
export const refreshAdmin = () => api.post('/auth/refresh').then(r => r.data);
export const changePassword = (data) => api.post('/auth/change-password', data).then(r => r.data);
export const createNotice = (data) => api.post('/admin/notices', data).then(r => r.data);
export const updateNotice = (id, data) => api.put(`/admin/notices/${id}`, data).then(r => r.data);
export const deleteNotice = (id) => api.delete(`/admin/notices/${id}`).then(r => r.data);
export const listContacts = () => api.get('/admin/contacts').then(r => r.data);
export const deleteContact = (id) => api.delete(`/admin/contacts/${id}`).then(r => r.data);
export const fetchActivity = () => api.get('/admin/activity').then(r => r.data);

// Aggregator
export const aggSources = () => api.get('/admin/aggregator/sources').then(r => r.data);
export const aggCreateSource = (data) => api.post('/admin/aggregator/sources', data).then(r => r.data);
export const aggUpdateSource = (id, data) => api.put(`/admin/aggregator/sources/${id}`, data).then(r => r.data);
export const aggDeleteSource = (id) => api.delete(`/admin/aggregator/sources/${id}`).then(r => r.data);
export const aggRunSource = (id) => api.post(`/admin/aggregator/sources/${id}/run`).then(r => r.data);
export const aggRunAll = () => api.post('/admin/aggregator/run-all').then(r => r.data);
export const aggRuns = (limit = 50) => api.get('/admin/aggregator/runs', { params: { limit } }).then(r => r.data);
export const aggDrafts = (params = {}) => api.get('/admin/aggregator/drafts', { params }).then(r => r.data);
export const aggApproveDraft = (id) => api.post(`/admin/aggregator/drafts/${id}/approve`).then(r => r.data);
export const aggRejectDraft = (id) => api.post(`/admin/aggregator/drafts/${id}/reject`).then(r => r.data);
export const aggBulkDrafts = (data) => api.post('/admin/aggregator/drafts/bulk', data).then(r => r.data);
export const aggGetSettings = () => api.get('/admin/aggregator/settings').then(r => r.data);
export const aggUpdateSettings = (data) => api.put('/admin/aggregator/settings', data).then(r => r.data);
