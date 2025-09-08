import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Provider, useDispatch, useSelector } from 'react-redux';
import { store, RootState, AppDispatch } from './store';
import { getCurrentUser } from './store/authSlice';
import { ThemeProvider } from './contexts/ThemeContext';
import { QuestionsPage } from './pages/QuestionsPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { TestPage } from './pages/TestPage';
import { LandingPage } from './pages/LandingPage';
import { Navbar } from './components/Navbar';
import { ProtectedRoute } from './components/ProtectedRoute';

const AppContent: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { token, isAuthenticated } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    // Try to get current user if token exists
    if (token && !isAuthenticated) {
      dispatch(getCurrentUser());
    }
  }, [dispatch, token, isAuthenticated]);

  return (
    <div className="App h-screen bg-gray-50 dark:bg-gray-900 transition-colors overflow-hidden flex flex-col">
      <Navbar />
      <div className="flex-1 min-h-0">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/test" element={<TestPage />} />
          <Route
            path="/questions"
            element={
              <ProtectedRoute>
                <QuestionsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              isAuthenticated ? <Navigate to="/questions" replace /> : <LandingPage />
            }
          />
        </Routes>
      </div>
    </div>
  );
};

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </Provider>
  );
}

export default App;