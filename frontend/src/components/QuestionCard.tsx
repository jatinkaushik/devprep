import React, { useState } from 'react';
import { GroupedCompanyQuestion, TIME_PERIOD_LABELS } from '../types';
import { getDifficultyBadgeClass, formatAcceptanceRate, formatFrequency, parseTopics } from '../utils';
import { ExternalLink, Building, Clock, Hash, ChevronDown, ChevronUp } from 'lucide-react';

interface QuestionCardProps {
  groupedQuestion: GroupedCompanyQuestion;
  selectedCompanies?: string[];
  selectedTimePeriods?: string[];
}

export const QuestionCard: React.FC<QuestionCardProps> = ({ 
  groupedQuestion, 
  selectedCompanies = [],
  selectedTimePeriods = []
}) => {
  const [showAllCompanies, setShowAllCompanies] = useState(false);
  const [showAllTimePeriods, setShowAllTimePeriods] = useState(false);
  
  const { question, companies } = groupedQuestion;
  const topics = parseTopics(question.topics);
  
  // Filter companies based on selection
  const companyEntries = Object.entries(companies);
  const hasSelectedCompanies = selectedCompanies.length > 0;
  const hasSelectedTimePeriods = selectedTimePeriods.length > 0;
  
  // Show only selected companies if any are selected, otherwise show all
  const filteredCompanies = hasSelectedCompanies 
    ? companyEntries.filter(([name]) => selectedCompanies.includes(name))
    : companyEntries;
  
  // Limit companies shown initially
  const companiesToShow = showAllCompanies ? filteredCompanies : filteredCompanies.slice(0, 3);
  const hasMoreCompanies = filteredCompanies.length > 3;

  return (
    <div className="card p-6 hover:shadow-md transition-shadow animate-fade-in">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-semibold text-lg text-gray-900">
              {question.title}
            </h3>
            <span className={`badge ${getDifficultyBadgeClass(question.difficulty)}`}>
              {question.difficulty}
            </span>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
            {showCompany && (
              <div className="flex items-center gap-1">
                <Building size={16} />
                <span>{company_name}</span>
              </div>
            )}
            
            <div className="flex items-center gap-1">
              <Clock size={16} />
              <span>{TIME_PERIOD_LABELS[time_period] || time_period}</span>
            </div>
            
            {frequency && (
              <div className="flex items-center gap-1">
                <Hash size={16} />
                <span>Frequency: {formatFrequency(frequency)}</span>
              </div>
            )}
            
            {question.acceptance_rate && (
              <div className="text-gray-500">
                Acceptance: {formatAcceptanceRate(question.acceptance_rate)}
              </div>
            )}
          </div>
          
          {topics.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {topics.map((topic, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-md"
                >
                  {topic}
                </span>
              ))}
            </div>
          )}
        </div>
        
        <a
          href={question.link}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary px-4 py-2 text-sm flex items-center gap-2 ml-4"
        >
          <ExternalLink size={16} />
          Solve
        </a>
      </div>
    </div>
  );
};
