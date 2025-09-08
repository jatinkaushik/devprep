import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface FilterState {
  // Selected filters
  selectedCompanies: string[];
  companyLogic: 'AND' | 'OR';
  selectedDifficulties: string[];
  selectedTimePeriods: string[];
  timePeriodLogic: 'AND' | 'OR';
  selectedTopics: string[];
  searchQuery: string;
  
  // Sort settings
  sortBy: 'frequency' | 'title' | 'difficulty';
  sortOrder: 'asc' | 'desc';
  
  // Filter history for undo/redo functionality
  filterHistory: Array<{
    selectedCompanies: string[];
    companyLogic: 'AND' | 'OR';
    selectedDifficulties: string[];
    selectedTimePeriods: string[];
    timePeriodLogic: 'AND' | 'OR';
    selectedTopics: string[];
    searchQuery: string;
    timestamp: number;
  }>;
  historyIndex: number;
  
  // UI state
  isFilterPanelOpen: boolean;
}

const initialState: FilterState = {
  selectedCompanies: [],
  companyLogic: 'OR',
  selectedDifficulties: [],
  selectedTimePeriods: [],
  timePeriodLogic: 'OR',
  selectedTopics: [],
  searchQuery: '',
  
  sortBy: 'frequency',
  sortOrder: 'desc',
  
  filterHistory: [],
  historyIndex: -1,
  
  isFilterPanelOpen: true,
};

const filtersSlice = createSlice({
  name: 'filters',
  initialState,
  reducers: {
    // Company filters
    setSelectedCompanies: (state, action: PayloadAction<string[]>) => {
      state.selectedCompanies = action.payload;
      saveToHistory(state);
    },
    toggleCompany: (state, action: PayloadAction<string>) => {
      const company = action.payload;
      if (state.selectedCompanies.includes(company)) {
        state.selectedCompanies = state.selectedCompanies.filter(c => c !== company);
      } else {
        state.selectedCompanies.push(company);
      }
      saveToHistory(state);
    },
    setCompanyLogic: (state, action: PayloadAction<'AND' | 'OR'>) => {
      state.companyLogic = action.payload;
      saveToHistory(state);
    },
    
    // Difficulty filters
    setSelectedDifficulties: (state, action: PayloadAction<string[]>) => {
      state.selectedDifficulties = action.payload;
      saveToHistory(state);
    },
    toggleDifficulty: (state, action: PayloadAction<string>) => {
      const difficulty = action.payload;
      if (state.selectedDifficulties.includes(difficulty)) {
        state.selectedDifficulties = state.selectedDifficulties.filter(d => d !== difficulty);
      } else {
        state.selectedDifficulties.push(difficulty);
      }
      saveToHistory(state);
    },
    
    // Time period filters
    setSelectedTimePeriods: (state, action: PayloadAction<string[]>) => {
      state.selectedTimePeriods = action.payload;
      saveToHistory(state);
    },
    toggleTimePeriod: (state, action: PayloadAction<string>) => {
      const timePeriod = action.payload;
      if (state.selectedTimePeriods.includes(timePeriod)) {
        state.selectedTimePeriods = state.selectedTimePeriods.filter(t => t !== timePeriod);
      } else {
        state.selectedTimePeriods.push(timePeriod);
      }
      saveToHistory(state);
    },
    setTimePeriodLogic: (state, action: PayloadAction<'AND' | 'OR'>) => {
      state.timePeriodLogic = action.payload;
      saveToHistory(state);
    },
    
    // Topic filters
    setSelectedTopics: (state, action: PayloadAction<string[]>) => {
      state.selectedTopics = action.payload;
      saveToHistory(state);
    },
    toggleTopic: (state, action: PayloadAction<string>) => {
      const topic = action.payload;
      if (state.selectedTopics.includes(topic)) {
        state.selectedTopics = state.selectedTopics.filter(t => t !== topic);
      } else {
        state.selectedTopics.push(topic);
      }
      saveToHistory(state);
    },
    
    // Search
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload;
      saveToHistory(state);
    },
    
    // Sort
    setSortBy: (state, action: PayloadAction<'frequency' | 'title' | 'difficulty'>) => {
      state.sortBy = action.payload;
    },
    setSortOrder: (state, action: PayloadAction<'asc' | 'desc'>) => {
      state.sortOrder = action.payload;
    },
    
    // Clear filters
    clearAllFilters: (state) => {
      state.selectedCompanies = [];
      state.selectedDifficulties = [];
      state.selectedTimePeriods = [];
      state.selectedTopics = [];
      state.searchQuery = '';
      state.companyLogic = 'OR';
      state.timePeriodLogic = 'OR';
      saveToHistory(state);
    },
    
    // History management
    undoFilter: (state) => {
      if (state.historyIndex > 0) {
        state.historyIndex--;
        const previousState = state.filterHistory[state.historyIndex];
        applyHistoryState(state, previousState);
      }
    },
    redoFilter: (state) => {
      if (state.historyIndex < state.filterHistory.length - 1) {
        state.historyIndex++;
        const nextState = state.filterHistory[state.historyIndex];
        applyHistoryState(state, nextState);
      }
    },
    
    // UI
    toggleFilterPanel: (state) => {
      state.isFilterPanelOpen = !state.isFilterPanelOpen;
    },
    setFilterPanelOpen: (state, action: PayloadAction<boolean>) => {
      state.isFilterPanelOpen = action.payload;
    },
  },
});

// Helper functions
function saveToHistory(state: FilterState) {
  const newHistoryItem = {
    selectedCompanies: [...state.selectedCompanies],
    companyLogic: state.companyLogic,
    selectedDifficulties: [...state.selectedDifficulties],
    selectedTimePeriods: [...state.selectedTimePeriods],
    timePeriodLogic: state.timePeriodLogic,
    selectedTopics: [...state.selectedTopics],
    searchQuery: state.searchQuery,
    timestamp: Date.now(),
  };
  
  // Remove any history after current index
  state.filterHistory = state.filterHistory.slice(0, state.historyIndex + 1);
  
  // Add new state
  state.filterHistory.push(newHistoryItem);
  state.historyIndex = state.filterHistory.length - 1;
  
  // Keep only last 50 states
  if (state.filterHistory.length > 50) {
    state.filterHistory = state.filterHistory.slice(-50);
    state.historyIndex = state.filterHistory.length - 1;
  }
}

function applyHistoryState(state: FilterState, historyState: any) {
  state.selectedCompanies = historyState.selectedCompanies;
  state.companyLogic = historyState.companyLogic;
  state.selectedDifficulties = historyState.selectedDifficulties;
  state.selectedTimePeriods = historyState.selectedTimePeriods;
  state.timePeriodLogic = historyState.timePeriodLogic;
  state.selectedTopics = historyState.selectedTopics;
  state.searchQuery = historyState.searchQuery;
}

export const {
  setSelectedCompanies,
  toggleCompany,
  setCompanyLogic,
  setSelectedDifficulties,
  toggleDifficulty,
  setSelectedTimePeriods,
  toggleTimePeriod,
  setTimePeriodLogic,
  setSelectedTopics,
  toggleTopic,
  setSearchQuery,
  setSortBy,
  setSortOrder,
  clearAllFilters,
  undoFilter,
  redoFilter,
  toggleFilterPanel,
  setFilterPanelOpen,
} = filtersSlice.actions;

export default filtersSlice.reducer;
