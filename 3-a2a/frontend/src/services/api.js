import axios from 'axios';

const API = process.env.REACT_APP_API_URL || '';

const client = axios.create({
  baseURL: API,
  withCredentials: true,
});

export const login = (username, password) =>
  client.post('/api/login', { username, password });

export const logout = () =>
  client.post('/api/logout');

export const checkAuth = () =>
  client.get('/api/me');

export const analyse = (query) =>
  client.post('/api/analyse', { query });

export const chartUrl = (filename) =>
  `${API}/api/charts/${filename}`;
