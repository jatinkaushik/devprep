export interface Question {
  id: number;
  title: string;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  acceptance_rate?: number;
  link: string;
  topics?: string;
}

export interface Company {
  id: number;
  name: string;
}

export interface CompanyQuestion {
  question: Question;
  frequency?: number;
  time_period: string;
  company_name: string;
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

export interface Filters {
  companies: string[];
  difficulties: string[];
  time_periods: string[];
  topics: string[];
  search: string;
  sort_by?: 'frequency' | 'title' | 'difficulty';
  sort_order?: 'asc' | 'desc';
}

export const TIME_PERIOD_LABELS: Record<string, string> = {
  '30_days': '30 Days',
  '3_months': '3 Months',
  '6_months': '6 Months',
  'more_than_6_months': 'More than 6 Months',
  'all_time': 'All Time'
};

export const DIFFICULTY_COLORS: Record<string, string> = {
  'EASY': 'text-green-600',
  'MEDIUM': 'text-yellow-600', 
  'HARD': 'text-red-600'
};

export const DIFFICULTY_BADGE_COLORS: Record<string, string> = {
  'EASY': 'bg-green-100 text-green-800',
  'MEDIUM': 'bg-yellow-100 text-yellow-800',
  'HARD': 'bg-red-100 text-red-800'
};

export const TIME_PERIOD_OPTIONS = [
  { value: '30_days', label: '30 Days' },
  { value: '3_months', label: '3 Months' },
  { value: '6_months', label: '6 Months' },
  { value: 'more_than_6_months', label: 'More than 6 Months' },
  { value: 'all_time', label: 'All Time' }
];
