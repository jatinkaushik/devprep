import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UiState {
  // Theme
  theme: 'light' | 'dark' | 'system';
  
  // Layout
  sidebarCollapsed: boolean;
  sidebarWidth: number;
  
  // Modals and dialogs
  isQuestionDetailModalOpen: boolean;
  selectedQuestionId: number | null;
  
  // Toast notifications
  toasts: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message?: string;
    duration?: number;
    timestamp: number;
  }>;
  
  // Progress tracking (for future features)
  progressTracking: {
    enabled: boolean;
    completedQuestions: number[];
    favoriteQuestions: number[];
    studyPlans: Array<{
      id: string;
      name: string;
      questionIds: number[];
      completed: number[];
      createdAt: number;
    }>;
  };
  
  // View preferences
  viewPreferences: {
    questionsPerPage: number;
    showCompanyFrequency: boolean;
    showAcceptanceRate: boolean;
    showTopics: boolean;
    compactView: boolean;
    groupByDifficulty: boolean;
  };
  
  // Recent activity
  recentActivity: Array<{
    id: string;
    type: 'question_viewed' | 'filter_applied' | 'search_performed';
    data: any;
    timestamp: number;
  }>;
}

const initialState: UiState = {
  theme: 'light',
  
  sidebarCollapsed: false,
  sidebarWidth: 320,
  
  isQuestionDetailModalOpen: false,
  selectedQuestionId: null,
  
  toasts: [],
  
  progressTracking: {
    enabled: false,
    completedQuestions: [],
    favoriteQuestions: [],
    studyPlans: [],
  },
  
  viewPreferences: {
    questionsPerPage: 20,
    showCompanyFrequency: true,
    showAcceptanceRate: true,
    showTopics: true,
    compactView: false,
    groupByDifficulty: false,
  },
  
  recentActivity: [],
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Theme
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'system'>) => {
      state.theme = action.payload;
    },
    
    // Layout
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    setSidebarWidth: (state, action: PayloadAction<number>) => {
      state.sidebarWidth = Math.max(250, Math.min(500, action.payload));
    },
    
    // Question detail modal
    openQuestionDetail: (state, action: PayloadAction<number>) => {
      state.isQuestionDetailModalOpen = true;
      state.selectedQuestionId = action.payload;
    },
    closeQuestionDetail: (state) => {
      state.isQuestionDetailModalOpen = false;
      state.selectedQuestionId = null;
    },
    
    // Toast notifications
    addToast: (state, action: PayloadAction<{
      type: 'success' | 'error' | 'warning' | 'info';
      title: string;
      message?: string;
      duration?: number;
    }>) => {
      const toast = {
        id: `toast-${Date.now()}-${Math.random()}`,
        ...action.payload,
        timestamp: Date.now(),
      };
      state.toasts.push(toast);
      
      // Keep only last 10 toasts
      if (state.toasts.length > 10) {
        state.toasts = state.toasts.slice(-10);
      }
    },
    removeToast: (state, action: PayloadAction<string>) => {
      state.toasts = state.toasts.filter(toast => toast.id !== action.payload);
    },
    clearAllToasts: (state) => {
      state.toasts = [];
    },
    
    // Progress tracking
    setProgressTrackingEnabled: (state, action: PayloadAction<boolean>) => {
      state.progressTracking.enabled = action.payload;
    },
    markQuestionCompleted: (state, action: PayloadAction<number>) => {
      const questionId = action.payload;
      if (!state.progressTracking.completedQuestions.includes(questionId)) {
        state.progressTracking.completedQuestions.push(questionId);
      }
    },
    markQuestionIncomplete: (state, action: PayloadAction<number>) => {
      const questionId = action.payload;
      state.progressTracking.completedQuestions = state.progressTracking.completedQuestions
        .filter(id => id !== questionId);
    },
    toggleQuestionFavorite: (state, action: PayloadAction<number>) => {
      const questionId = action.payload;
      if (state.progressTracking.favoriteQuestions.includes(questionId)) {
        state.progressTracking.favoriteQuestions = state.progressTracking.favoriteQuestions
          .filter(id => id !== questionId);
      } else {
        state.progressTracking.favoriteQuestions.push(questionId);
      }
    },
    addStudyPlan: (state, action: PayloadAction<{ name: string; questionIds: number[] }>) => {
      const studyPlan = {
        id: `plan-${Date.now()}`,
        name: action.payload.name,
        questionIds: action.payload.questionIds,
        completed: [],
        createdAt: Date.now(),
      };
      state.progressTracking.studyPlans.push(studyPlan);
    },
    deleteStudyPlan: (state, action: PayloadAction<string>) => {
      state.progressTracking.studyPlans = state.progressTracking.studyPlans
        .filter(plan => plan.id !== action.payload);
    },
    
    // View preferences
    setViewPreferences: (state, action: PayloadAction<Partial<UiState['viewPreferences']>>) => {
      state.viewPreferences = { ...state.viewPreferences, ...action.payload };
    },
    setQuestionsPerPage: (state, action: PayloadAction<number>) => {
      state.viewPreferences.questionsPerPage = action.payload;
    },
    toggleCompactView: (state) => {
      state.viewPreferences.compactView = !state.viewPreferences.compactView;
    },
    
    // Recent activity
    addRecentActivity: (state, action: PayloadAction<{
      type: 'question_viewed' | 'filter_applied' | 'search_performed';
      data: any;
    }>) => {
      const activity = {
        id: `activity-${Date.now()}`,
        ...action.payload,
        timestamp: Date.now(),
      };
      state.recentActivity.unshift(activity);
      
      // Keep only last 50 activities
      if (state.recentActivity.length > 50) {
        state.recentActivity = state.recentActivity.slice(0, 50);
      }
    },
    clearRecentActivity: (state) => {
      state.recentActivity = [];
    },
  },
});

export const {
  setTheme,
  setSidebarCollapsed,
  toggleSidebar,
  setSidebarWidth,
  openQuestionDetail,
  closeQuestionDetail,
  addToast,
  removeToast,
  clearAllToasts,
  setProgressTrackingEnabled,
  markQuestionCompleted,
  markQuestionIncomplete,
  toggleQuestionFavorite,
  addStudyPlan,
  deleteStudyPlan,
  setViewPreferences,
  setQuestionsPerPage,
  toggleCompactView,
  addRecentActivity,
  clearRecentActivity,
} = uiSlice.actions;

export default uiSlice.reducer;
