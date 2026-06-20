import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const api = axios.create({ baseURL: API });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('av_admin_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;

export const fetchJobs = (params = {}) => api.get('/jobs', { params }).then(r => r.data);
export const fetchJob = (id) => api.get(`/jobs/${id}`).then(r => r.data);
export const fetchStats = () => api.get('/stats').then(r => r.data);
export const submitContact = (data) => api.post('/contact', data).then(r => r.data);
export const loginAdmin = (data) => api.post('/auth/login', data).then(r => r.data);
export const verifyAdmin = () => api.get('/auth/verify').then(r => r.data);
export const createJob = (data) => api.post('/admin/jobs', data).then(r => r.data);
export const updateJob = (id, data) => api.put(`/admin/jobs/${id}`, data).then(r => r.data);
export const deleteJob = (id) => api.delete(`/admin/jobs/${id}`).then(r => r.data);
export const listContacts = () => api.get('/admin/contacts').then(r => r.data);
export const deleteContact = (id) => api.delete(`/admin/contacts/${id}`).then(r => r.data);
