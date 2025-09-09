export interface Question {
  id: number;
  title: string;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  acceptance_rate?: number;
  link: string;
  topics?: string;
}

// Type aliases
export type QuestionDifficulty = 'Easy' | 'Medium' | 'Hard';

// User Management Types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: string;
}

// User Question Types
export interface UserQuestion {
  id: number;
  title: string;
  description?: string;
  difficulty: QuestionDifficulty;
  topics?: string[];
  solution?: string;
  link?: string;
  is_public: boolean;
  is_approved: boolean;
  created_by: number;
  creator_username?: string;
  approved_by?: number;
  approver_username?: string;
  created_at: string;
  updated_at: string;
  approved_at?: string;
  references?: QuestionReference[];
  companies?: UserQuestionCompany[];
  is_favorited?: boolean;
}

export interface UserQuestionCreate {
  title: string;
  description?: string;
  difficulty: QuestionDifficulty;
  topics?: string[];
  solution?: string;
  link?: string;
  is_public?: boolean;
  request_public?: boolean;  // For admin approval request
}

export interface UserQuestionUpdate {
  title?: string;
  description?: string;
  difficulty?: 'Easy' | 'Medium' | 'Hard';
  topics?: string[];
  solution?: string;
  link?: string;
}

// Question Reference Types
export interface QuestionReference {
  id: number;
  url: string;
  title?: string;
  description?: string;
  is_approved: boolean;
  created_by: number;
  creator_username?: string;
  approved_by?: number;
  approver_username?: string;
  created_at: string;
  approved_at?: string;
}

export interface QuestionReferenceCreate {
  url: string;
  title?: string;
  description?: string;
  question_id?: number;
  user_question_id?: number;
}

// Company Association Types
export interface UserQuestionCompany {
  id: number;
  company_id: number;
  company_name?: string;
  time_period: string;
  frequency: number;
  is_approved: boolean;
  created_by: number;
  creator_username?: string;
  approved_by?: number;
  approver_username?: string;
  created_at: string;
  approved_at?: string;
}

// Approval Request Types
export interface ApprovalRequest {
  id: number;
  request_type: 'question_public' | 'reference' | 'company_association';
  entity_id: number;
  entity_type: string;
  requested_by: number;
  requester_username?: string;
  status: 'pending' | 'approved' | 'rejected';
  admin_notes?: string;
  processed_by?: number;
  processor_username?: string;
  created_at: string;
  processed_at?: string;
  entity_details?: any;
}

// Response Types
export interface UserQuestionListResponse {
  questions: UserQuestion[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface AdminStats {
  total_users: number;
  total_user_questions: number;
  pending_question_approvals: number;
  pending_reference_approvals: number;
  pending_company_associations: number;
  questions_approved_today: number;
  references_approved_today: number;
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
