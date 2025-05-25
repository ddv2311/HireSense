import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import ErrorBoundary from './components/ErrorBoundary';
import { 
  Home, 
  Users, 
  FileText, 
  Calendar, 
  MessageSquare, 
  BarChart3, 
  Upload,
  Briefcase,
  Play
} from 'lucide-react';

// Import pages
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import Candidates from './pages/Candidates';
import CandidateProfile from './pages/CandidateProfile';
import Schedule from './pages/Schedule';
import Messages from './pages/Messages';
import UploadResume from './pages/UploadResume';
import CreateJob from './pages/CreateJob';
import Analytics from './pages/Analytics';
import Demo from './pages/Demo';

function Layout({ children }) {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Demo', href: '/demo', icon: Play },
    { name: 'Jobs', href: '/jobs', icon: Briefcase },
    { name: 'Candidates', href: '/candidates', icon: Users },
    { name: 'Upload Resume', href: '/upload-resume', icon: Upload },
    { name: 'Schedule', href: '/schedule', icon: Calendar },
    { name: 'Messages', href: '/messages', icon: MessageSquare },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-16 items-center justify-center border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">HireSense AI</h1>
        </div>
        <nav className="mt-8 px-4">
          <ul className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      isActive
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    <Icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="py-8">
          {children}
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="App">
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                style: {
                  background: '#22c55e',
                  color: '#fff',
                },
              },
              error: {
                duration: 5000,
                style: {
                  background: '#ef4444',
                  color: '#fff',
                },
              },
            }}
          />
          
          <Routes>
            <Route path="/*" element={
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/demo" element={<Demo />} />
                  <Route path="/jobs" element={<Jobs />} />
                  <Route path="/jobs/create" element={<CreateJob />} />
                  <Route path="/candidates" element={<Candidates />} />
                  <Route path="/candidate/:id" element={<CandidateProfile />} />
                  <Route path="/upload-resume" element={<UploadResume />} />
                  <Route path="/schedule" element={<Schedule />} />
                  <Route path="/messages" element={<Messages />} />
                  <Route path="/analytics" element={<Analytics />} />
                </Routes>
              </Layout>
            } />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App; 