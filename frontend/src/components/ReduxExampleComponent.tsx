import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { 
  fetchCompanies, 
  fetchTopics, 
  fetchQuestions,
  setPage 
} from '../store/slices/questionsSlice';
import {
  toggleCompany,
  setCompanyLogic,
  toggleTimePeriod,
  setTimePeriodLogic,
  setSearchQuery,
  clearAllFilters
} from '../store/slices/filtersSlice';
import {
  addToast,
  toggleSidebar
} from '../store/slices/uiSlice';

export const ReduxExampleComponent: React.FC = () => {
  const dispatch = useAppDispatch();
  
  // Select data from store
  const { 
    questions, 
    companies, 
    loading, 
    currentPage, 
    totalPages,
    error 
  } = useAppSelector(state => state.questions);
  
  const { 
    selectedCompanies, 
    companyLogic,
    selectedTimePeriods,
    timePeriodLogic,
    searchQuery 
  } = useAppSelector(state => state.filters);
  
  const { sidebarCollapsed, theme } = useAppSelector(state => state.ui);

  // Load initial data
  useEffect(() => {
    dispatch(fetchCompanies());
    dispatch(fetchTopics());
  }, [dispatch]);

  // Load questions when filters change
  useEffect(() => {
    const params = {
      companies: selectedCompanies.join(','),
      company_logic: companyLogic,
      time_periods: selectedTimePeriods.join(','),
      time_period_logic: timePeriodLogic,
      search: searchQuery,
      page: currentPage,
    };

    // Only fetch if we have some filters or it's the initial load
    if (selectedCompanies.length > 0 || selectedTimePeriods.length > 0 || searchQuery) {
      dispatch(fetchQuestions(params));
    }
  }, [
    dispatch, 
    selectedCompanies, 
    companyLogic, 
    selectedTimePeriods, 
    timePeriodLogic, 
    searchQuery, 
    currentPage
  ]);

  const handleCompanyToggle = (company: string) => {
    dispatch(toggleCompany(company));
    dispatch(addToast({
      type: 'info',
      title: 'Filter Updated',
      message: `Company ${company} ${selectedCompanies.includes(company) ? 'removed' : 'added'}`,
      duration: 2000
    }));
  };

  const handleClearFilters = () => {
    dispatch(clearAllFilters());
    dispatch(addToast({
      type: 'success',
      title: 'Filters Cleared',
      message: 'All filters have been reset',
      duration: 3000
    }));
  };

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <h3 className="text-red-800 font-medium">Error</h3>
        <p className="text-red-600">{error}</p>
        <button 
          onClick={() => dispatch(fetchQuestions({}))}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className={`redux-example ${theme === 'dark' ? 'dark' : 'light'}`}>
      <div className="flex items-center justify-between p-4 bg-blue-50 border-b">
        <h2 className="text-xl font-bold text-blue-900">Redux Integration Example</h2>
        <button 
          onClick={() => dispatch(toggleSidebar())}
          className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {sidebarCollapsed ? 'Show' : 'Hide'} Sidebar
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Search Questions
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => dispatch(setSearchQuery(e.target.value))}
            placeholder="Enter search term..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Company Logic */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Company Logic
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                checked={companyLogic === 'OR'}
                onChange={() => dispatch(setCompanyLogic('OR'))}
                className="mr-1"
              />
              OR
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                checked={companyLogic === 'AND'}
                onChange={() => dispatch(setCompanyLogic('AND'))}
                className="mr-1"
              />
              AND
            </label>
          </div>
        </div>

        {/* Time Period Logic */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Time Period Logic
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                checked={timePeriodLogic === 'OR'}
                onChange={() => dispatch(setTimePeriodLogic('OR'))}
                className="mr-1"
              />
              OR
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                checked={timePeriodLogic === 'AND'}
                onChange={() => dispatch(setTimePeriodLogic('AND'))}
                className="mr-1"
              />
              AND
            </label>
          </div>
        </div>

        {/* Companies */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Selected Companies ({selectedCompanies.length})
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {companies.slice(0, 10).map(company => (
              <button
                key={company.id}
                onClick={() => handleCompanyToggle(company.name)}
                className={`px-3 py-1 rounded text-sm ${
                  selectedCompanies.includes(company.name)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {company.name}
              </button>
            ))}
          </div>
        </div>

        {/* Time Periods */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Selected Time Periods ({selectedTimePeriods.length})
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {['30_days', '3_months', '6_months', 'more_than_6_months', 'all_time'].map(period => (
              <button
                key={period}
                onClick={() => dispatch(toggleTimePeriod(period))}
                className={`px-3 py-1 rounded text-sm ${
                  selectedTimePeriods.includes(period)
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {period.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Clear Filters */}
        <button
          onClick={handleClearFilters}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Clear All Filters
        </button>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-4">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading questions...</p>
          </div>
        )}

        {/* Questions Display */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Questions ({questions.length})
          </h3>
          <div className="space-y-2">
            {questions.slice(0, 5).map(q => (
              <div key={q.question.id} className="p-3 bg-gray-50 rounded border">
                <h4 className="font-medium text-gray-900">{q.question.title}</h4>
                <p className="text-sm text-gray-600">
                  Difficulty: <span className="font-medium">{q.question.difficulty}</span>
                </p>
                <p className="text-sm text-gray-600">
                  Companies: {Object.keys(q.companies).join(', ')}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => dispatch(setPage(Math.max(1, currentPage - 1)))}
            disabled={currentPage <= 1}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-gray-400"
          >
            Previous
          </button>
          <span className="text-gray-600">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => dispatch(setPage(Math.min(totalPages, currentPage + 1)))}
            disabled={currentPage >= totalPages}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-gray-400"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};
