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
import { UserQuestionsPage } from './pages/UserQuestionsPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { Navbar } from './components/Navbar';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AdminRoute } from './components/AdminRoute';

const AppContent: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { token, isAuthenticated, user } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    // Try to get current user if token exists but user data is not loaded
    if (token && !user) {
      dispatch(getCurrentUser());
    }
  }, [dispatch, token, user]);

  return (
    <div className="App min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <Navbar />
      <main>
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
            path="/questions/user"
            element={
              <ProtectedRoute>
                <UserQuestionsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <AdminRoute>
                <AdminDashboardPage />
              </AdminRoute>
            }
          />
          <Route
            path="/"
            element={
              isAuthenticated ? <Navigate to="/questions" replace /> : <LandingPage />
            }
          />
        </Routes>
      </main>
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