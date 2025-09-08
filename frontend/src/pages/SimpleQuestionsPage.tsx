import React, { useState, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { setLoading } from '../store/slices/simpleQuestionsSlice';

export const SimpleQuestionsPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { loading } = useAppSelector(state => state.questions);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'error'>('checking');

  // Test backend connection
  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/companies');
        if (response.ok) {
          setBackendStatus('connected');
        } else {
          setBackendStatus('error');
        }
      } catch (error) {
        setBackendStatus('error');
      }
    };

    testConnection();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-gray-900">
            DevPrep Questions Browser
          </h1>
          <p className="text-gray-600 mt-1">
            Scalable architecture with Redux & class-based backend
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* System Status */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🚀 System Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Frontend Status */}
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <h3 className="font-medium text-green-900">Frontend</h3>
              </div>
              <p className="text-green-700 text-sm mt-1">
                ✅ React + Redux + TypeScript
              </p>
            </div>

            {/* Backend Status */}
            <div className={`p-4 border rounded-lg ${
              backendStatus === 'connected' ? 'bg-green-50 border-green-200' :
              backendStatus === 'error' ? 'bg-red-50 border-red-200' :
              'bg-yellow-50 border-yellow-200'
            }`}>
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-3 ${
                  backendStatus === 'connected' ? 'bg-green-500' :
                  backendStatus === 'error' ? 'bg-red-500' :
                  'bg-yellow-500'
                }`}></div>
                <h3 className={`font-medium ${
                  backendStatus === 'connected' ? 'text-green-900' :
                  backendStatus === 'error' ? 'text-red-900' :
                  'text-yellow-900'
                }`}>Backend</h3>
              </div>
              <p className={`text-sm mt-1 ${
                backendStatus === 'connected' ? 'text-green-700' :
                backendStatus === 'error' ? 'text-red-700' :
                'text-yellow-700'
              }`}>
                {backendStatus === 'connected' ? '✅ FastAPI Class-based' :
                 backendStatus === 'error' ? '❌ Connection failed' :
                 '⏳ Checking connection...'}
              </p>
            </div>

            {/* Redux Status */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                <h3 className="font-medium text-blue-900">Redux Store</h3>
              </div>
              <p className="text-blue-700 text-sm mt-1">
                ✅ State Management Active
              </p>
            </div>
          </div>
        </div>

        {/* Redux Demo */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🎛️ Redux Demo</h2>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Loading State:</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                loading ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
              }`}>
                {loading ? 'Loading...' : 'Ready'}
              </span>
              <button
                onClick={() => dispatch(setLoading(!loading))}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Toggle Loading
              </button>
            </div>
          </div>
        </div>

        {/* Architecture Features */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🏗️ Architecture Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Backend Features */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Backend (Class-based)</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Repository-Service-Controller Pattern
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Time Period AND/OR Logic
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Company AND/OR Logic
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Pydantic Schemas & Validation
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Database Connection Management
                </li>
              </ul>
            </div>

            {/* Frontend Features */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Frontend (Redux)</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  Redux Toolkit State Management
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  TypeScript Type Safety
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  Async Actions & Loading States
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  Filter History & Undo/Redo Ready
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  Progress Tracking Foundation
                </li>
              </ul>
            </div>
          </div>

          {/* API Test */}
          {backendStatus === 'connected' && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">🔌 API Connection Test</h4>
              <p className="text-sm text-gray-600">
                Backend is accessible at <code className="bg-gray-200 px-1 rounded">http://localhost:8000</code>
              </p>
              <div className="mt-2 flex space-x-2">
                <a 
                  href="http://localhost:8000/api/companies" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  Test Companies API
                </a>
                <span className="text-gray-400">|</span>
                <a 
                  href="http://localhost:8000/api/stats" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  Test Stats API
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
