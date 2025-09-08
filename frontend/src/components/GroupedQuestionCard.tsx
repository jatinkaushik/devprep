import React, { useState } from 'react';
import { GroupedCompanyQuestion } from '../types';
import { getDifficultyBadgeClass, formatAcceptanceRate, formatFrequency, parseTopics } from '../utils';
import { ExternalLink, Building, Hash, ChevronDown, ChevronUp } from 'lucide-react';

interface QuestionCardProps {
  groupedQuestion: GroupedCompanyQuestion;
  selectedCompanies?: string[];
  showAllCompaniesGlobal?: boolean;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({ 
  groupedQuestion, 
  selectedCompanies = [],
  showAllCompaniesGlobal = true
}) => {
  const [showAllCompanies, setShowAllCompanies] = useState(false);
  
  const { question, companies } = groupedQuestion;
  const topics = parseTopics(question.topics);
  
  // Filter companies based on selection and global toggle
  const companyEntries = Object.entries(companies);
  const hasSelectedCompanies = selectedCompanies.length > 0;
  
  // Determine which companies to show based on global toggle and selection
  let filteredCompanies: [string, any][] = [];
  
  if (hasSelectedCompanies) {
    // If companies are selected, show based on global toggle
    filteredCompanies = showAllCompaniesGlobal 
      ? companyEntries // Show all companies
      : companyEntries.filter(([name]) => selectedCompanies.includes(name)); // Show only selected
  } else {
    // If no companies are selected, only show companies if global toggle is on
    filteredCompanies = showAllCompaniesGlobal ? companyEntries : [];
  }
  
  // Limit companies shown initially
  const companiesToShow = showAllCompanies ? filteredCompanies : filteredCompanies.slice(0, 3);
  const hasMoreCompanies = filteredCompanies.length > 3;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-6 hover:shadow-md dark:hover:shadow-lg transition-shadow animate-fade-in">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
              {question.title}
            </h3>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyBadgeClass(question.difficulty)}`}>
              {question.difficulty}
            </span>
          </div>
          
          {/* Companies Section */}
          {filteredCompanies.length > 0 && (
            <div className="mb-3">
              <div className="flex items-center gap-2 mb-2">
                <Building className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Companies:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {companiesToShow.map(([companyName, companyData]) => (
                  <div key={companyName} className="flex items-center gap-1">
                    <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-700">
                      {companyName}
                    </span>
                    {companyData.frequency && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        ({formatFrequency(companyData.frequency)})
                      </span>
                    )}
                  </div>
                ))}
                {hasMoreCompanies && !showAllCompanies && (
                  <button
                    onClick={() => setShowAllCompanies(true)}
                    className="inline-flex items-center px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
                  >
                    +{filteredCompanies.length - 3} more
                    <ChevronDown className="w-3 h-3 ml-1" />
                  </button>
                )}
                {showAllCompanies && hasMoreCompanies && (
                  <button
                    onClick={() => setShowAllCompanies(false)}
                    className="inline-flex items-center px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
                  >
                    Show less
                    <ChevronUp className="w-3 h-3 ml-1" />
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Question Details */}
          <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
            {question.acceptance_rate && (
              <span>Acceptance: {formatAcceptanceRate(question.acceptance_rate)}</span>
            )}
          </div>

          {/* Topics */}
          {topics.length > 0 && (
            <div className="flex items-center gap-2 mb-3">
              <Hash className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              <div className="flex flex-wrap gap-1">
                {topics.map((topic, index) => (
                  <span 
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-100 dark:bg-purple-900/40 text-purple-800 dark:text-purple-300 border border-purple-200 dark:border-purple-700"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <div className="ml-4">
          <a
            href={question.link}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-3 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50 border border-blue-200 dark:border-blue-700 rounded-md transition-colors"
          >
            <ExternalLink className="w-4 h-4 mr-1" />
            View
          </a>
        </div>
      </div>
    </div>
  );
};
