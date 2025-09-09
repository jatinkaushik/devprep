import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { ApprovalRequest, AdminStats } from '../types';
import { 
  Users, MessageSquare, CheckCircle, XCircle, Clock, 
  TrendingUp, Database, Link as LinkIcon 
} from 'lucide-react';

export const AdminDashboardPage: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [pendingApprovals, setPendingApprovals] = useState<{
    question_public: ApprovalRequest[];
    reference: ApprovalRequest[];
    company_association: ApprovalRequest[];
  }>({
    question_public: [],
    reference: [],
    company_association: [],
  });
  const [questionDetails, setQuestionDetails] = useState<{[key: number]: any}>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');

      // Fetch admin stats
      const statsResponse = await fetch('http://localhost:8000/api/admin/stats', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Fetch pending approvals
      const approvalsResponse = await fetch('http://localhost:8000/api/admin/pending-approvals', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (approvalsResponse.ok) {
        const approvalsData = await approvalsResponse.json();
        setPendingApprovals(approvalsData);
        
        // Fetch question details for pending approvals
        const details: {[key: number]: any} = {};
        for (const request of approvalsData.question_public) {
          try {
            const questionResponse = await fetch(`http://localhost:8000/api/user-questions/${request.entity_id}`, {
              headers: { 'Authorization': `Bearer ${token}` },
            });
            if (questionResponse.ok) {
              const questionData = await questionResponse.json();
              details[request.entity_id] = questionData;
            }
          } catch (error) {
            console.error(`Failed to fetch details for question ${request.entity_id}:`, error);
          }
        }
        setQuestionDetails(details);
      }

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleApproveQuestion = async (questionId: number, approve: boolean, notes?: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/admin/approve-question/${questionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: approve ? 'approved' : 'rejected',
          admin_notes: notes,
        }),
      });

      if (response.ok) {
        // Remove from pending list
        setPendingApprovals(prev => ({
          ...prev,
          question_public: prev.question_public.filter(req => req.entity_id !== questionId),
        }));
      } else {
        throw new Error('Failed to process approval');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process approval');
    }
  };

  const handleApproveReference = async (referenceId: number, notes?: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/admin/approve-reference/${referenceId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: 'approved',
          admin_notes: notes,
        }),
      });

      if (response.ok) {
        // Remove from pending list
        setPendingApprovals(prev => ({
          ...prev,
          reference: prev.reference.filter(req => req.entity_id !== referenceId),
        }));
      } else {
        throw new Error('Failed to approve reference');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve reference');
    }
  };

  if (user?.role !== 'admin') {
    return (
      <div className="h-full bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <XCircle size={48} className="mx-auto text-red-500 mb-4" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Access Denied</h2>
          <p className="text-gray-600 dark:text-gray-400">You need admin privileges to access this page.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="h-full bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-gray-50 dark:bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400">Manage user content and approvals</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {error && (
            <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
              <p className="text-red-700 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <Users className="h-8 w-8 text-blue-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Users</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_users}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <MessageSquare className="h-8 w-8 text-green-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">User Questions</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_user_questions}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <Clock className="h-8 w-8 text-yellow-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Pending Approvals</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {stats.pending_question_approvals + stats.pending_reference_approvals}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <TrendingUp className="h-8 w-8 text-purple-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Approved Today</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {stats.questions_approved_today + stats.references_approved_today}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Pending Approvals */}
          <div className="space-y-6">
            {/* Question Approvals */}
            {pendingApprovals.question_public.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <Database className="mr-2" size={20} />
                    Pending Question Approvals ({pendingApprovals.question_public.length})
                  </h2>
                </div>
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {pendingApprovals.question_public.map((request) => {
                    const questionDetail = questionDetails[request.entity_id];
                    return (
                      <div key={request.id} className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="mb-4">
                              <p className="text-sm text-gray-500 dark:text-gray-400">
                                Request from <span className="font-medium">{request.requester_username}</span>
                              </p>
                              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                                {new Date(request.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            
                            {questionDetail && (
                              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mt-3">
                                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                                  {questionDetail.title}
                                </h4>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                  <div>
                                    <span className="text-gray-500 dark:text-gray-400">Difficulty:</span>
                                    <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                                      questionDetail.difficulty === 'Easy' ? 'bg-green-100 text-green-800' :
                                      questionDetail.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                      'bg-red-100 text-red-800'
                                    }`}>
                                      {questionDetail.difficulty}
                                    </span>
                                  </div>
                                  <div>
                                    <span className="text-gray-500 dark:text-gray-400">Created:</span>
                                    <span className="ml-2 text-gray-900 dark:text-white">
                                      {new Date(questionDetail.created_at).toLocaleDateString()}
                                    </span>
                                  </div>
                                </div>
                                
                                {questionDetail.description && (
                                  <div className="mt-3">
                                    <span className="text-gray-500 dark:text-gray-400 text-sm">Description:</span>
                                    <p className="text-gray-900 dark:text-white mt-1 text-sm">
                                      {questionDetail.description}
                                    </p>
                                  </div>
                                )}
                                
                                {questionDetail.topics && questionDetail.topics.length > 0 && (
                                  <div className="mt-3">
                                    <span className="text-gray-500 dark:text-gray-400 text-sm">Topics:</span>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {questionDetail.topics.map((topic: string, index: number) => (
                                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                                          {topic}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                
                                {questionDetail.link && (
                                  <div className="mt-3">
                                    <span className="text-gray-500 dark:text-gray-400 text-sm">Link:</span>
                                    <a 
                                      href={questionDetail.link} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                      className="ml-2 text-blue-600 hover:text-blue-800 text-sm underline"
                                    >
                                      {questionDetail.link}
                                    </a>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                          <div className="flex space-x-2 ml-4">
                            <button
                              onClick={() => handleApproveQuestion(request.entity_id, true)}
                              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 transition-colors"
                            >
                              <CheckCircle size={14} className="mr-1" />
                              Approve
                            </button>
                            <button
                              onClick={() => handleApproveQuestion(request.entity_id, false)}
                              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 transition-colors"
                            >
                              <XCircle size={14} className="mr-1" />
                              Reject
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Reference Approvals */}
            {pendingApprovals.reference.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <LinkIcon className="mr-2" size={20} />
                    Pending Reference Approvals ({pendingApprovals.reference.length})
                  </h2>
                </div>
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {pendingApprovals.reference.map((request) => (
                    <div key={request.id} className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Reference from <span className="font-medium">{request.requester_username}</span>
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            {new Date(request.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex space-x-2 ml-4">
                          <button
                            onClick={() => handleApproveReference(request.entity_id)}
                            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 transition-colors"
                          >
                            <CheckCircle size={14} className="mr-1" />
                            Approve
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No Pending Approvals */}
            {pendingApprovals.question_public.length === 0 && 
             pendingApprovals.reference.length === 0 && 
             pendingApprovals.company_association.length === 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-12 text-center">
                <CheckCircle size={48} className="mx-auto text-green-500 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">All Caught Up!</h3>
                <p className="text-gray-500 dark:text-gray-400">
                  There are no pending approval requests at the moment.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
