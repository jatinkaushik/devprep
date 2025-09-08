import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { Filters, GroupedCompanyQuestion } from '../types';
import { CompanyFilter } from '../components/filters/CompanyFilter';
import { DifficultyFilter } from '../components/filters/DifficultyFilter';
import { TimePeriodFilter } from '../components/filters/TimePeriodFilter';
import { TopicFilter } from '../components/filters/TopicFilter';
import { QuestionCard } from '../components/GroupedQuestionCard';
import { 
  Search, 
  ArrowUpDown, 
  ChevronLeft, 
  ChevronRight,
  BarChart3,
  Loader2,
  Filter
} from 'lucide-react';

export const QuestionsPage: React.FC = () => {
  // Load initial state from localStorage
  const [filters, setFilters] = useState<Filters>(() => {
    const saved = localStorage.getItem('devprep-filters');
    return saved ? JSON.parse(saved) : {
      companies: [],
      difficulties: [],
      time_periods: [],
      topics: [],
      search: '',
      sort_by: 'frequency',
      sort_order: 'desc',
    };
  });

  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(() => {
    const saved = localStorage.getItem('devprep-showFilters');
    return saved ? JSON.parse(saved) : true;
  });
  const [showAllCompaniesGlobal, setShowAllCompaniesGlobal] = useState(() => {
    const saved = localStorage.getItem('devprep-showAllCompanies');
    return saved ? JSON.parse(saved) : true;
  });
  const [companyLogic, setCompanyLogic] = useState<'AND' | 'OR'>(() => {
    const saved = localStorage.getItem('devprep-companyLogic');
    return saved ? JSON.parse(saved) : 'OR';
  });
  const [timePeriodLogic, setTimePeriodLogic] = useState<'AND' | 'OR'>(() => {
    const saved = localStorage.getItem('devprep-timePeriodLogic');
    return saved ? JSON.parse(saved) : 'OR';
  });
  const perPage = 20;

  // Fetch filter options
  const { data: companies = [] } = useQuery({
    queryKey: ['companies'],
    queryFn: apiService.getCompanies,
  });

  const { data: difficulties = [] } = useQuery({
    queryKey: ['difficulties'],
    queryFn: apiService.getDifficulties,
  });

  const { data: timePeriods = [] } = useQuery({
    queryKey: ['time-periods'],
    queryFn: apiService.getTimePeriods,
  });

  const { data: topics = [] } = useQuery({
    queryKey: ['topics'],
    queryFn: apiService.getTopics,
  });

  // Save preferences to localStorage
  useEffect(() => {
    localStorage.setItem('devprep-filters', JSON.stringify(filters));
  }, [filters]);

  useEffect(() => {
    localStorage.setItem('devprep-showFilters', JSON.stringify(showFilters));
  }, [showFilters]);

  useEffect(() => {
    localStorage.setItem('devprep-showAllCompanies', JSON.stringify(showAllCompaniesGlobal));
  }, [showAllCompaniesGlobal]);

  useEffect(() => {
    localStorage.setItem('devprep-companyLogic', JSON.stringify(companyLogic));
  }, [companyLogic]);

  useEffect(() => {
    localStorage.setItem('devprep-timePeriodLogic', JSON.stringify(timePeriodLogic));
  }, [timePeriodLogic]);

  // Fetch questions
  const { 
    data: questionsData, 
    isLoading, 
    error 
  } = useQuery({
    queryKey: ['questions', filters, page, companyLogic, timePeriodLogic],
    queryFn: () => apiService.getQuestions({
      companies: filters.companies.length > 0 ? filters.companies.join(',') : undefined,
      company_logic: filters.companies.length > 1 ? companyLogic : undefined,
      difficulties: filters.difficulties.length > 0 ? filters.difficulties.join(',') : undefined,
      time_periods: filters.time_periods.length > 0 ? filters.time_periods.join(',') : undefined,
      time_period_logic: filters.time_periods.length > 1 ? timePeriodLogic : undefined,
      topics: filters.topics.length > 0 ? filters.topics.join(',') : undefined,
      search: filters.search || undefined,
      page,
      per_page: perPage,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
    })
  });

  const updateFilter = <K extends keyof Filters>(key: K, value: Filters[K]) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const clearAllFilters = () => {
    setFilters({
      companies: [],
      difficulties: [],
      time_periods: [],
      topics: [],
      search: '',
      sort_by: 'frequency',
      sort_order: 'desc',
    });
    setShowAllCompaniesGlobal(true);
    setCompanyLogic('OR');
    setTimePeriodLogic('OR');
    setPage(1);
  };

  const hasActiveFilters = 
    filters.companies.length > 0 ||
    filters.difficulties.length > 0 ||
    filters.time_periods.length > 0 ||
    filters.topics.length > 0 ||
    filters.search;

  const totalPages = questionsData?.total_pages || 0;
  const questions = questionsData?.questions || [];
  const stats = questionsData?.stats;

  return (
    <div className="h-full bg-gray-50 dark:bg-gray-900 flex flex-col overflow-hidden">
      {/* Compact Single-Row Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="w-full max-w-[98%] sm:max-w-[95%] lg:max-w-[90%] xl:max-w-[85%] mx-auto px-1 sm:px-2 lg:px-3 xl:px-4">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between py-2 gap-2">
            {/* Left: Stats */}
            <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-sm text-gray-600 dark:text-gray-300">
              {stats && (
                <>
                  <span className="flex items-center gap-1">
                    <BarChart3 size={14} />
                    <span className="font-medium text-gray-900 dark:text-white">{stats.total_questions}</span> questions
                  </span>
                  <span className="hidden sm:inline text-gray-400 dark:text-gray-500">•</span>
                  <span><span className="font-medium text-gray-900 dark:text-white">{stats.companies_count}</span> companies</span>
                  
                  {/* Inline Difficulty Stats */}
                  <div className="flex gap-2 text-xs ml-2">
                    <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300 rounded border border-green-200 dark:border-green-700">
                      E:{stats.easy_count}
                    </span>
                    <span className="px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300 rounded border border-yellow-200 dark:border-yellow-700">
                      M:{stats.medium_count}
                    </span>
                    <span className="px-2 py-0.5 bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300 rounded border border-red-200 dark:border-red-700">
                      H:{stats.hard_count}
                    </span>
                  </div>
                </>
              )}
            </div>

            {/* Center: Controls */}
            <div className="flex flex-wrap items-center gap-3">
              {/* Sort Controls */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Sort:</span>
                <select
                  value={filters.sort_by}
                  onChange={(e) => updateFilter('sort_by', e.target.value as any)}
                  className="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-1 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 text-xs"
                >
                  <option value="frequency">Frequency</option>
                  <option value="title">Title</option>
                  <option value="difficulty">Difficulty</option>
                </select>
                
                <button
                  onClick={() => updateFilter('sort_order', filters.sort_order === 'asc' ? 'desc' : 'asc')}
                  className="p-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
                  title={`Sort ${filters.sort_order === 'asc' ? 'descending' : 'ascending'}`}
                >
                  <ArrowUpDown size={14} className="text-gray-700 dark:text-gray-300" />
                </button>
              </div>

              {/* Show All Companies Toggle */}
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showAllCompaniesGlobal}
                  onChange={(e) => setShowAllCompaniesGlobal(e.target.checked)}
                  className="w-3 h-3 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500 dark:focus:ring-indigo-600 dark:ring-offset-gray-800 focus:ring-1 dark:bg-gray-700 dark:border-gray-600"
                />
                <span className="text-xs text-gray-700 dark:text-gray-300">Show all companies</span>
              </label>
            </div>

            {/* Right: Filters Toggle */}
            <div className="flex items-center">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded border transition-colors text-sm ${
                  hasActiveFilters 
                    ? 'bg-indigo-50 dark:bg-indigo-900/30 border-indigo-300 dark:border-indigo-600 text-indigo-700 dark:text-indigo-300' 
                    : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
                }`}
              >
                <Filter size={14} />
                <span>Filters</span>
                {hasActiveFilters && (
                  <span className="bg-indigo-500 dark:bg-indigo-600 text-white text-xs rounded-full px-1.5 py-0.5 min-w-[18px] text-center leading-none">
                    {[
                      filters.companies.length,
                      filters.difficulties.length,
                      filters.time_periods.length,
                      filters.topics.length,
                      filters.search ? 1 : 0
                    ].reduce((a, b) => a + b, 0)}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Fixed Height Container with Scrollable Inner Components */}
      <div className="w-full max-w-[98%] sm:max-w-[95%] lg:max-w-[90%] xl:max-w-[85%] mx-auto px-1 sm:px-2 lg:px-3 xl:px-4 flex-1 min-h-0">
        <div className="flex flex-col lg:flex-row gap-3 lg:gap-4 h-full py-3 lg:py-4">
          {/* Enhanced Filters Sidebar */}
          {showFilters && (
            <div className="w-full lg:w-72 lg:flex-shrink-0 h-full lg:h-auto">
              <div className="h-full">
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm h-full flex flex-col">
                  {/* Filters Header - Fixed */}
                  <div className="flex items-center justify-between p-4 pb-3 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Filters</h2>
                    {hasActiveFilters && (
                      <button
                        onClick={clearAllFilters}
                        className="px-3 py-1.5 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
                      >
                        Clear All
                      </button>
                    )}
                  </div>

                  {/* Filters Content - Scrollable */}
                  <div className="p-4 space-y-4 overflow-y-auto flex-1 overscroll-contain">
                    {/* Search Filter */}
                    <div className="space-y-3">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Search</label>
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500" size={16} />
                        <input
                          type="text"
                          placeholder="Search questions..."
                          value={filters.search}
                          onChange={(e) => updateFilter('search', e.target.value)}
                          className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 transition-colors"
                        />
                      </div>
                    </div>

                    {/* Company Filter */}
                    <CompanyFilter
                      companies={companies}
                      selectedCompanies={filters.companies}
                      onChange={(companies) => updateFilter('companies', companies)}
                    />
                    
                    {/* Company Logic AND/OR */}
                    {filters.companies.length > 1 && (
                      <div className="space-y-3">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Company Filter Logic
                        </label>
                        <div className="flex gap-2">
                          <button
                            onClick={() => setCompanyLogic('OR')}
                            className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
                              companyLogic === 'OR'
                                ? 'bg-indigo-500 dark:bg-indigo-600 text-white'
                                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                            }`}
                          >
                            OR (Any)
                          </button>
                          <button
                            onClick={() => setCompanyLogic('AND')}
                            className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
                              companyLogic === 'AND'
                                ? 'bg-indigo-500 dark:bg-indigo-600 text-white'
                                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                            }`}
                          >
                            AND (All)
                          </button>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {companyLogic === 'OR' 
                            ? 'Show questions from any of the selected companies'
                            : 'Show only questions that appeared in all selected companies'
                          }
                        </p>
                      </div>
                    )}

                <DifficultyFilter
                  difficulties={difficulties}
                  selectedDifficulties={filters.difficulties}
                  onChange={(difficulties) => updateFilter('difficulties', difficulties)}
                />

                <TimePeriodFilter
                  timePeriods={timePeriods}
                  selectedTimePeriods={filters.time_periods}
                  onChange={(timePeriods) => updateFilter('time_periods', timePeriods)}
                />

                {/* Time Period Logic AND/OR */}
                {filters.time_periods.length > 1 && (
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Time Period Filter Logic
                    </label>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setTimePeriodLogic('OR')}
                        className={`px-3 py-1 text-xs rounded transition-colors ${
                          timePeriodLogic === 'OR'
                            ? 'bg-indigo-500 dark:bg-indigo-600 text-white'
                            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                        }`}
                      >
                        OR (Any)
                      </button>
                      <button
                        onClick={() => setTimePeriodLogic('AND')}
                        className={`px-3 py-1 text-xs rounded transition-colors ${
                          timePeriodLogic === 'AND'
                            ? 'bg-indigo-500 dark:bg-indigo-600 text-white'
                            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                        }`}
                      >
                        AND (All)
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {timePeriodLogic === 'OR' 
                        ? 'Show questions from any of the selected time periods'
                        : 'Show only questions that appeared in all selected time periods'
                      }
                    </p>
                  </div>
                )}

                    <TopicFilter
                      topics={topics}
                      selectedTopics={filters.topics}
                      onChange={(topics) => updateFilter('topics', topics)}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Main Content - Scrollable */}
          <div className={`${showFilters ? 'flex-1' : 'w-full'} min-w-0 h-full`}>
            <div className="h-full overflow-y-auto overscroll-contain pr-2">
              {/* Loading State */}
              {isLoading && (
                <div className="flex justify-center items-center py-12">
                  <Loader2 className="animate-spin text-indigo-500 dark:text-indigo-400" size={32} />
                </div>
              )}

              {/* Error State */}
              {error && (
                <div className="text-center py-12">
                  <p className="text-red-600 dark:text-red-400">Error loading questions. Please try again.</p>
                </div>
              )}

              {/* Questions List */}
              {!isLoading && !error && (
                <div className="pb-4">
                  <div className="space-y-3 sm:space-y-4">
                    {questions.map((groupedQuestion: GroupedCompanyQuestion, index: number) => (
                      <QuestionCard
                        key={`${groupedQuestion.question.id}-${index}`}
                        groupedQuestion={groupedQuestion}
                        selectedCompanies={filters.companies}
                        showAllCompaniesGlobal={showAllCompaniesGlobal}
                      />
                    ))}
                  </div>

                  {questions.length === 0 && (
                    <div className="text-center py-12">
                      <p className="text-gray-500 dark:text-gray-400">No questions found with the current filters.</p>
                    </div>
                  )}

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="flex flex-col sm:flex-row items-center justify-between mt-8 gap-4">
                      <div className="text-sm text-gray-700 dark:text-gray-300">
                        Page {page} of {totalPages} ({questionsData?.total} total results)
                      </div>
                      
                      <div className="flex items-center gap-2 flex-wrap justify-center">
                        <button
                          onClick={() => setPage(page - 1)}
                          disabled={page === 1}
                          className="p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
                        >
                          <ChevronLeft size={16} />
                        </button>
                        
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          const pageNum = Math.max(1, Math.min(totalPages - 4, page - 2)) + i;
                          return (
                            <button
                              key={pageNum}
                              onClick={() => setPage(pageNum)}
                              className={`px-3 py-2 text-sm rounded-md transition-colors ${
                                pageNum === page
                                  ? 'bg-indigo-600 dark:bg-indigo-500 text-white'
                                  : 'bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
                              }`}
                            >
                              {pageNum}
                            </button>
                          );
                        })}
                        
                        <button
                          onClick={() => setPage(page + 1)}
                          disabled={page === totalPages}
                          className="p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
                        >
                          <ChevronRight size={16} />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
