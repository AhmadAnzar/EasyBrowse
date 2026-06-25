import axios from 'axios';

const BACKEND_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const runAgent = async (goal: string, url?: string) => {
  const response = await api.post('/agent/run', { goal, url });
  return response.data;
};

export const getAgentStatus = async (sessionId: string) => {
  const response = await api.get(`/agent/status/${sessionId}`);
  return response.data;
};

export const stopAgent = async (sessionId: string) => {
  const response = await api.post(`/agent/stop/${sessionId}`);
  return response.data;
};

export const resumeAgent = async (sessionId: string, input: string) => {
  const response = await api.post(`/agent/resume/${sessionId}`, { input });
  return response.data;
};

export const getWebSocketUrl = (sessionId: string) => {
  return `ws://localhost:8000/ws/session/${sessionId}`;
};

export const getScreenshotFullUrl = (relativeUrl: string) => {
  return `${BACKEND_URL}${relativeUrl}`;
};
