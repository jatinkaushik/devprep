import axios from 'axios';
import { Company, QuestionResponse, OverallStats } from '../types';

// In Docker, the API will be proxied through nginx, so we use relative paths
const API_BASE_URL = window.location.hostname === 'localhost' && window.location.port === '3000' 
  ? 'http://localhost:8000/api'  // Development mode
  : '/api';  // Production mode (proxied through nginx)

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const apiService = {
  // Get all companies
  getCompanies: async (): Promise<Company[]> => {
    const response = await api.get('/companies');
    return response.data;
  },

  // Get all difficulties
  getDifficulties: async (): Promise<string[]> => {
    const response = await api.get('/difficulties');
    return response.data;
  },

  // Get all time periods
  getTimePeriods: async (): Promise<string[]> => {
    const response = await api.get('/time-periods');
    return response.data;
  },

  // Get all topics
  getTopics: async (): Promise<string[]> => {
    const response = await api.get('/topics');
    return response.data;
  },

  // Get questions with filters
  getQuestions: async (params: {
    companies?: string;
    company_logic?: 'AND' | 'OR';
    difficulties?: string;
    time_periods?: string;
    time_period_logic?: 'AND' | 'OR';
    topics?: string;
    search?: string;
    page?: number;
    per_page?: number;
    sort_by?: string;
    sort_order?: string;
  }): Promise<QuestionResponse> => {
    const response = await api.get('/questions', { params });
    return response.data;
  },

  // Get overall statistics
  getStats: async (): Promise<OverallStats> => {
    const response = await api.get('/stats');
    return response.data;
  },
};
