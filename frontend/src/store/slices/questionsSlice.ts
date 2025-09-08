import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

// Types
export interface Company {
  id: number;
  name: string;
}

export interface Question {
  id: number;
  title: string;
  difficulty: string;
  acceptance_rate?: number;
  link: string;
  topics?: string;
}

export interface CompanyData {
  frequency?: number;
  time_periods: string[];
}

export interface GroupedCompanyQuestion {
  question: Question;
  companies: Record<string, CompanyData>;
}

export interface FilterStats {
  total_questions: number;
  easy_count: number;
  medium_count: number;
  hard_count: number;
  companies_count: number;
  time_periods: string[];
  topics: string[];
}

export interface QuestionResponse {
  questions: GroupedCompanyQuestion[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  stats: FilterStats;
}

export interface OverallStats {
  total_questions: number;
  total_companies: number;
  total_relationships: number;
  difficulty_distribution: Record<string, number>;
  top_companies: Array<{ name: string; count: number }>;
  popular_questions: Array<{ title: string; difficulty: string; count: number }>;
}

interface QuestionsState {
  // Data
  questions: GroupedCompanyQuestion[];
  companies: Company[];
  topics: string[];
  difficulties: string[];
  timePeriods: string[];
  
  // Pagination
  currentPage: number;
  totalPages: number;
  totalQuestions: number;
  perPage: number;
  
  // Statistics
  stats: FilterStats | null;
  overallStats: OverallStats | null;
  
  // Loading states
  loading: boolean;
  companiesLoading: boolean;
  topicsLoading: boolean;
  statsLoading: boolean;
  
  // Error states
  error: string | null;
  companiesError: string | null;
  topicsError: string | null;
  statsError: string | null;
}

const initialState: QuestionsState = {
  questions: [],
  companies: [],
  topics: [],
  difficulties: ['EASY', 'MEDIUM', 'HARD'],
  timePeriods: ['30_days', '3_months', '6_months', 'more_than_6_months', 'all_time'],
  
  currentPage: 1,
  totalPages: 0,
  totalQuestions: 0,
  perPage: 20,
  
  stats: null,
  overallStats: null,
  
  loading: false,
  companiesLoading: false,
  topicsLoading: false,
  statsLoading: false,
  
  error: null,
  companiesError: null,
  topicsError: null,
  statsError: null,
};

// Async thunks
export const fetchQuestions = createAsyncThunk(
  'questions/fetchQuestions',
  async (params: {
    companies?: string;
    company_logic?: string;
    difficulties?: string;
    time_periods?: string;
    time_period_logic?: string;
    topics?: string;
    search?: string;
    page?: number;
    per_page?: number;
    sort_by?: string;
    sort_order?: string;
  }) => {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, value.toString());
      }
    });
    
    const response = await axios.get(`http://localhost:8000/api/questions?${searchParams}`);
    return response.data;
  }
);

export const fetchCompanies = createAsyncThunk(
  'questions/fetchCompanies',
  async () => {
    const response = await axios.get('http://localhost:8000/api/companies');
    return response.data;
  }
);

export const fetchTopics = createAsyncThunk(
  'questions/fetchTopics',
  async () => {
    const response = await axios.get('http://localhost:8000/api/topics');
    return response.data;
  }
);

export const fetchOverallStats = createAsyncThunk(
  'questions/fetchOverallStats',
  async () => {
    const response = await axios.get('http://localhost:8000/api/stats');
    return response.data;
  }
);

// Slice
const questionsSlice = createSlice({
  name: 'questions',
  initialState,
  reducers: {
    setPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    setPerPage: (state, action: PayloadAction<number>) => {
      state.perPage = action.payload;
      state.currentPage = 1; // Reset to first page when changing per page
    },
    clearError: (state) => {
      state.error = null;
      state.companiesError = null;
      state.topicsError = null;
      state.statsError = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch questions
    builder
      .addCase(fetchQuestions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQuestions.fulfilled, (state, action: PayloadAction<QuestionResponse>) => {
        state.loading = false;
        state.questions = action.payload.questions;
        state.totalQuestions = action.payload.total;
        state.currentPage = action.payload.page;
        state.totalPages = action.payload.total_pages;
        state.perPage = action.payload.per_page;
        state.stats = action.payload.stats;
      })
      .addCase(fetchQuestions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch questions';
      });

    // Fetch companies
    builder
      .addCase(fetchCompanies.pending, (state) => {
        state.companiesLoading = true;
        state.companiesError = null;
      })
      .addCase(fetchCompanies.fulfilled, (state, action: PayloadAction<Company[]>) => {
        state.companiesLoading = false;
        state.companies = action.payload;
      })
      .addCase(fetchCompanies.rejected, (state, action) => {
        state.companiesLoading = false;
        state.companiesError = action.error.message || 'Failed to fetch companies';
      });

    // Fetch topics
    builder
      .addCase(fetchTopics.pending, (state) => {
        state.topicsLoading = true;
        state.topicsError = null;
      })
      .addCase(fetchTopics.fulfilled, (state, action: PayloadAction<string[]>) => {
        state.topicsLoading = false;
        state.topics = action.payload;
      })
      .addCase(fetchTopics.rejected, (state, action) => {
        state.topicsLoading = false;
        state.topicsError = action.error.message || 'Failed to fetch topics';
      });

    // Fetch overall stats
    builder
      .addCase(fetchOverallStats.pending, (state) => {
        state.statsLoading = true;
        state.statsError = null;
      })
      .addCase(fetchOverallStats.fulfilled, (state, action: PayloadAction<OverallStats>) => {
        state.statsLoading = false;
        state.overallStats = action.payload;
      })
      .addCase(fetchOverallStats.rejected, (state, action) => {
        state.statsLoading = false;
        state.statsError = action.error.message || 'Failed to fetch overall stats';
      });
  },
});

export const { setPage, setPerPage, clearError } = questionsSlice.actions;
export default questionsSlice.reducer;
