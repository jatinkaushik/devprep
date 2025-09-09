import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { Plus, X, Link as LinkIcon, Save, ArrowLeft } from 'lucide-react';

interface Company {
  id: number;
  name: string;
}

interface CompanyAssociation {
  company_id: number;
  time_period: string;
  frequency: number;
}

export const CreateQuestionPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams<{ id: string }>();
  
  const isEditMode = !!id;
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    difficulty: 'Medium',
    link: '',
    is_public: false
  });
  
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [availableTopics, setAvailableTopics] = useState<string[]>([]);
  const [availableCompanies, setAvailableCompanies] = useState<Company[]>([]);
  const [availableTimePeriods, setAvailableTimePeriods] = useState<string[]>([]);
  const [availableDifficulties, setAvailableDifficulties] = useState<string[]>([]);
  
  const [companyAssociations, setCompanyAssociations] = useState<CompanyAssociation[]>([]);
  const [showAddCompany, setShowAddCompany] = useState(false);
  const [newCompanyAssociation, setNewCompanyAssociation] = useState<CompanyAssociation>({
    company_id: 0,
    time_period: '',
    frequency: 1.0
  });
  
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchMetadata();
    if (isEditMode && id) {
      fetchExistingQuestion(id);
    }
  }, [isEditMode, id]);

  const fetchMetadata = async () => {
    try {
      const [topicsRes, companiesRes, timePeriodsRes, difficultiesRes] = await Promise.all([
        fetch('http://localhost:8000/api/questions/meta/topics'),
        fetch('http://localhost:8000/api/questions/meta/companies'),
        fetch('http://localhost:8000/api/questions/meta/time-periods'),
        fetch('http://localhost:8000/api/questions/meta/difficulties')
      ]);

      if (topicsRes.ok) {
        const topics = await topicsRes.json();
        setAvailableTopics(topics);
      }

      if (companiesRes.ok) {
        const companies = await companiesRes.json();
        setAvailableCompanies(companies);
      }

      if (timePeriodsRes.ok) {
        const timePeriods = await timePeriodsRes.json();
        setAvailableTimePeriods(timePeriods);
      }

      if (difficultiesRes.ok) {
        const difficulties = await difficultiesRes.json();
        setAvailableDifficulties(difficulties);
      }
    } catch (error) {
      console.error('Error fetching metadata:', error);
    }
  };

  const fetchExistingQuestion = async (questionId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/questions/${questionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const question = await response.json();
        setFormData({
          title: question.title,
          description: question.description || '',
          difficulty: question.difficulty,
          link: question.link || '',
          is_public: question.is_public
        });
        setSelectedTopics(question.topics || []);
        
        // Load existing company associations
        if (question.companies && question.companies.length > 0) {
          const existingAssociations: CompanyAssociation[] = question.companies.map((company: any) => ({
            company_id: company.company_id,
            time_period: company.time_period,
            frequency: company.frequency
          }));
          setCompanyAssociations(existingAssociations);
        }
      }
    } catch (error) {
      console.error('Error fetching existing question:', error);
    }
  };

  const addTopic = (topic: string) => {
    if (!selectedTopics.includes(topic)) {
      setSelectedTopics([...selectedTopics, topic]);
    }
  };

  const removeTopic = (topic: string) => {
    setSelectedTopics(selectedTopics.filter(t => t !== topic));
  };

  const addCompanyAssociation = () => {
    if (newCompanyAssociation.company_id && newCompanyAssociation.time_period) {
      setCompanyAssociations([...companyAssociations, { ...newCompanyAssociation }]);
      setNewCompanyAssociation({ company_id: 0, time_period: '', frequency: 1.0 });
      setShowAddCompany(false);
    }
  };

  const removeCompanyAssociation = (index: number) => {
    setCompanyAssociations(companyAssociations.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      alert('Please enter a question title');
      return;
    }

    setIsLoading(true);
    
    try {
      const questionData = {
        ...formData,
        topics: selectedTopics,
        companies: companyAssociations
      };

      let response;
      if (isEditMode && id) {
        response = await fetch(`http://localhost:8000/api/questions/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(questionData)
        });
      } else {
        response = await fetch('http://localhost:8000/api/questions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(questionData)
        });
      }

      if (!response.ok) {
        throw new Error(`Failed to ${isEditMode ? 'update' : 'create'} question`);
      }

      const result = await response.json();
      alert(result.message || `Question ${isEditMode ? 'updated' : 'created'} successfully!`);
      navigate('/questions/user');
    } catch (error) {
      console.error('Error saving question:', error);
      alert('Failed to save question. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    const state = location.state as any;
    if (state?.from) {
      navigate(state.from);
    } else {
      navigate('/questions/user');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white mb-4"
          >
            <ArrowLeft size={20} />
            Back to Questions
          </button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {isEditMode ? 'Edit Question' : 'Create New Question'}
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            {isEditMode 
              ? 'Update your programming question details' 
              : 'Add your own programming question with company associations'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Question Details */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Question Details</h2>
            
            <div className="space-y-6">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Question Title *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-transparent"
                  placeholder="Enter question title..."
                  required
                />
              </div>
              
              {/* Link */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  External Link
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <LinkIcon size={18} className="text-gray-500 dark:text-gray-400" />
                  </div>
                  <input
                    type="url"
                    value={formData.link}
                    onChange={(e) => setFormData({ ...formData, link: e.target.value })}
                    className="w-full pl-10 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-transparent"
                    placeholder="https://example.com/problem/123"
                  />
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Question Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={6}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-transparent"
                  placeholder="Describe the problem in detail..."
                />
              </div>

              {/* Difficulty */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Difficulty *
                </label>
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-transparent"
                  required
                >
                  {availableDifficulties.map((difficulty) => (
                    <option key={difficulty} value={difficulty}>
                      {difficulty}
                    </option>
                  ))}
                </select>
              </div>

              {/* Topics */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Topics
                </label>
                <div className="space-y-3">
                  <select
                    onChange={(e) => {
                      if (e.target.value) {
                        addTopic(e.target.value);
                        e.target.value = '';
                      }
                    }}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-transparent"
                  >
                    <option value="">Select a topic to add</option>
                    {availableTopics
                      .filter(topic => !selectedTopics.includes(topic))
                      .map((topic) => (
                        <option key={topic} value={topic}>
                          {topic}
                        </option>
                      ))}
                  </select>
                  
                  {/* Selected Topics */}
                  {selectedTopics.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {selectedTopics.map((topic) => (
                        <span
                          key={topic}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-800 dark:text-indigo-300 rounded-full text-sm"
                        >
                          {topic}
                          <button
                            type="button"
                            onClick={() => removeTopic(topic)}
                            className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200"
                          >
                            <X size={14} />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Company Associations */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Company Associations</h2>
              <button
                type="button"
                onClick={() => setShowAddCompany(true)}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <Plus size={16} />
                Add Company
              </button>
            </div>

            {/* Add Company Form */}
            {showAddCompany && (
              <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <select
                    value={newCompanyAssociation.company_id}
                    onChange={(e) => setNewCompanyAssociation({ 
                      ...newCompanyAssociation, 
                      company_id: parseInt(e.target.value) 
                    })}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    required
                  >
                    <option value={0}>Select Company</option>
                    {availableCompanies.map((company) => (
                      <option key={company.id} value={company.id}>
                        {company.name}
                      </option>
                    ))}
                  </select>
                  <select
                    value={newCompanyAssociation.time_period}
                    onChange={(e) => setNewCompanyAssociation({ 
                      ...newCompanyAssociation, 
                      time_period: e.target.value 
                    })}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    required
                  >
                    <option value="">Select Time Period</option>
                    {availableTimePeriods.map((period) => (
                      <option key={period} value={period}>
                        {period}
                      </option>
                    ))}
                  </select>
                  <input
                    type="number"
                    min="0.1"
                    max="10"
                    step="0.1"
                    value={newCompanyAssociation.frequency}
                    onChange={(e) => setNewCompanyAssociation({ 
                      ...newCompanyAssociation, 
                      frequency: parseFloat(e.target.value) 
                    })}
                    placeholder="Frequency"
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <div className="flex gap-2 mt-4">
                  <button
                    type="button"
                    onClick={addCompanyAssociation}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Add
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddCompany(false)}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Company Associations List */}
            {companyAssociations.length > 0 && (
              <div className="space-y-3">
                {companyAssociations.map((association, index) => {
                  const company = availableCompanies.find(c => c.id === association.company_id);
                  return (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {company?.name || 'Unknown Company'}
                        </span>
                        <span className="text-gray-500 dark:text-gray-400 ml-2">
                          • {association.time_period} • Frequency: {association.frequency}
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeCompanyAssociation(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Submission Options */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Submission Options</h2>
            
            <div className="space-y-4">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={formData.is_public}
                  onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <div>
                  <span className="font-medium text-gray-900 dark:text-white">Request Public Approval</span>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Submit this question for admin review to make it visible to all users
                  </p>
                </div>
              </label>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => navigate('/questions/user')}
              className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  {isEditMode ? 'Updating...' : 'Creating...'}
                </>
              ) : (
                <>
                  <Save size={16} />
                  {isEditMode ? 'Update Question' : 'Create Question'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
