import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { RootState } from '../store';
import { UserQuestion, UserQuestionListResponse } from '../types';
import { Plus, Heart, MessageSquare, Users, Calendar, Edit, Trash2, Eye, Lock, CheckCircle, XCircle, Link as LinkIcon } from 'lucide-react';

export const UserQuestionsPage: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [questions, setQuestions] = useState<UserQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'public' | 'private'>('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      let url = `/api/user-questions?page=${page}&per_page=20`;
      
      if (filter === 'public') {
        url += '&is_public_only=true&is_approved_only=true';
      } else if (filter === 'private') {
        url += `&created_by=${user?.id}`;
      }

      const response = await fetch(`http://localhost:8000${url}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch questions');
      }

      const data: UserQuestionListResponse = await response.json();
      setQuestions(data.questions);
      setTotalPages(data.total_pages);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch questions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, [filter, page, user?.id]);

  const toggleFavorite = async (questionId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/favorites/toggle?user_question_id=${questionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Update the question's favorite status locally
        setQuestions(prev => prev.map(q => 
          q.id === questionId ? { ...q, is_favorited: !q.is_favorited } : q
        ));
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  const deleteQuestion = async (questionId: number) => {
    if (!confirm('Are you sure you want to delete this question?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/user-questions/${questionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setQuestions(prev => prev.filter(q => q.id !== questionId));
      } else {
        throw new Error('Failed to delete question');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete question');
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'text-green-600 dark:text-green-400';
      case 'Medium': return 'text-yellow-600 dark:text-yellow-400';
      case 'Hard': return 'text-red-600 dark:text-red-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getDifficultyBadge = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300';
      case 'Medium': return 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-300';
      case 'Hard': return 'bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-300';
      default: return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="h-full bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading questions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-gray-50 dark:bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">User Questions</h1>
              <p className="text-gray-600 dark:text-gray-400">Create and manage your own questions</p>
            </div>
            <Link
              to="/questions/create"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 transition-colors"
            >
              <Plus size={16} className="mr-2" />
              Create Question
            </Link>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex space-x-4">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              All Questions
            </button>
            <button
              onClick={() => setFilter('public')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                filter === 'public'
                  ? 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              Public Questions
            </button>
            <button
              onClick={() => setFilter('private')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                filter === 'private'
                  ? 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              My Questions
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {error && (
            <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
              <p className="text-red-700 dark:text-red-400">{error}</p>
            </div>
          )}

          {questions.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare size={48} className="mx-auto text-gray-400 dark:text-gray-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {filter === 'private' ? 'No questions created yet' : 'No questions found'}
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                {filter === 'private' 
                  ? 'Start creating your own questions to build your collection.'
                  : 'Try adjusting your filters or check back later.'}
              </p>
              {filter === 'private' && (
                <Link
                  to="/questions/create"
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 transition-colors"
                >
                  <Plus size={16} className="mr-2" />
                  Create Your First Question
                </Link>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {questions.map((question) => (
                <div
                  key={question.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                          {question.title}
                        </h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyBadge(question.difficulty)}`}>
                          {question.difficulty}
                        </span>
                        {question.is_public ? (
                          <div className="flex items-center space-x-1">
                            <Eye size={14} className="text-green-500" />
                            {question.is_approved ? (
                              <CheckCircle size={14} className="text-green-500" />
                            ) : (
                              <XCircle size={14} className="text-yellow-500" />
                            )}
                          </div>
                        ) : (
                          <Lock size={14} className="text-gray-400" />
                        )}
                      </div>
                      
                      {question.description && (
                        <p className="text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                          {question.description}
                        </p>
                      )}

                      {question.link && (
                        <div className="mb-3">
                          <a 
                            href={question.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300"
                          >
                            <LinkIcon size={14} className="mr-1" />
                            <span className="text-sm underline">{question.link}</span>
                          </a>
                        </div>
                      )}

                      {question.topics && question.topics.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-3">
                          {question.topics.map((topic, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs"
                            >
                              {topic}
                            </span>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                        <div className="flex items-center space-x-1">
                          <Users size={14} />
                          <span>{question.creator_username}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar size={14} />
                          <span>{new Date(question.created_at).toLocaleDateString()}</span>
                        </div>
                        {question.references && question.references.length > 0 && (
                          <div className="flex items-center space-x-1">
                            <MessageSquare size={14} />
                            <span>{question.references.length} references</span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => toggleFavorite(question.id)}
                        className={`p-2 rounded-full transition-colors ${
                          question.is_favorited
                            ? 'text-red-500 hover:text-red-600'
                            : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
                        }`}
                      >
                        <Heart size={16} fill={question.is_favorited ? 'currentColor' : 'none'} />
                      </button>
                      
                      {question.created_by === user?.id && (
                        <>
                          <Link
                            to={`/questions/edit/${question.id}`}
                            state={{ from: '/questions/user' }}
                            className="p-2 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 rounded-full transition-colors"
                          >
                            <Edit size={16} />
                          </Link>
                          <button
                            onClick={() => deleteQuestion(question.id)}
                            className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded-full transition-colors"
                          >
                            <Trash2 size={16} />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-center space-x-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-2 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="px-3 py-2 text-sm text-gray-700 dark:text-gray-300">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-2 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
