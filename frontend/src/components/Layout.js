import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Briefcase, 
  Users, 
  Calendar, 
  MessageSquare, 
  Upload,
  Menu,
  X,
  Bot,
  Settings,
  Bell,
  BarChart3,
  Zap,
  User,
  LogOut,
  HelpCircle,
  Plus
} from 'lucide-react';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navigationSections = [
    {
      title: 'Overview',
      items: [
        { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, description: 'Main overview' },
        { name: 'Analytics', href: '/analytics', icon: BarChart3, description: 'Insights & reports' },
      ]
    },
    {
      title: 'Recruitment',
      items: [
        { name: 'Jobs', href: '/jobs', icon: Briefcase, description: 'Manage job postings' },
        { name: 'Candidates', href: '/candidates', icon: Users, description: 'View all candidates' },
        { name: 'Upload Resume', href: '/upload-resume', icon: Upload, description: 'Add new candidates' },
      ]
    },
    {
      title: 'Operations',
      items: [
        { name: 'Schedule', href: '/schedule', icon: Calendar, description: 'Interview scheduling' },
        { name: 'Messages', href: '/messages', icon: MessageSquare, description: 'Communication hub' },
      ]
    }
  ];

  const isActive = (href) => {
    return location.pathname === href || 
           (href !== '/dashboard' && location.pathname.startsWith(href));
  };

  const getPageTitle = () => {
    for (const section of navigationSections) {
      const item = section.items.find(item => isActive(item.href));
      if (item) return item.name;
    }
    return 'Dashboard';
  };

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm" />
        </div>
      )}

      {/* Sidebar */}
      <aside className={`
        w-72 h-screen bg-white shadow-large border-r border-slate-200/60 flex flex-col transform transition-all duration-300 ease-in-out lg:translate-x-0 fixed lg:relative z-50 lg:z-auto
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-slate-200/60 bg-gradient-to-r from-sky-600 to-sky-700 flex-shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold text-white">
                HireSense
              </span>
              <div className="text-xs text-sky-100 font-medium">
                AI Assistant
              </div>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-colors"
            title="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-8 overflow-y-auto scrollbar-hide">
          {navigationSections.map((section, sectionIndex) => (
            <div key={sectionIndex} className="sidebar-nav-section">
              <div className="sidebar-nav-section-title">
                {section.title}
              </div>
              <div className="sidebar-nav">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.href);
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`sidebar-nav-item group ${active ? 'active' : ''}`}
                      onClick={() => setSidebarOpen(false)}
                      title={item.description}
                    >
                      <Icon className="w-5 h-5 mr-3 transition-transform duration-200 group-hover:scale-110" />
                      <div className="flex-1">
                        <div className="font-medium">{item.name}</div>
                        {!active && (
                          <div className="text-xs text-slate-500 group-hover:text-slate-600 transition-colors">
                            {item.description}
                          </div>
                        )}
                      </div>
                      {active && (
                        <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Sidebar Footer */}
        <div className="border-t border-slate-200/60 p-4 flex-shrink-0">
          {/* User Profile */}
          <div className="flex items-center space-x-3 p-3 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer group">
            <div className="avatar-md">
              <span>HR</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-900 truncate">
                HR Manager
              </p>
              <p className="text-xs text-slate-500 truncate">
                hr@company.com
              </p>
            </div>
            <Settings className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" />
          </div>

          {/* Quick Actions */}
          <div className="mt-3 flex space-x-2">
            <button 
              className="flex-1 flex items-center justify-center p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
              title="Help & Support"
            >
              <HelpCircle className="w-4 h-4" />
            </button>
            <button 
              className="flex-1 flex items-center justify-center p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
            <button 
              className="flex-1 flex items-center justify-center p-2 text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Sign out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top header */}
        <header className="bg-white/80 backdrop-blur-sm shadow-soft border-b border-slate-200/60 flex-shrink-0 z-30">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all duration-200"
                title="Open sidebar"
              >
                <Menu className="w-5 h-5" />
              </button>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-sky-500 to-sky-600 rounded-lg flex items-center justify-center">
                  <Zap className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-slate-900">
                    {getPageTitle()}
                  </h1>
                  <div className="text-xs text-slate-500 font-medium">
                    AI-Powered Recruitment
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <button className="relative p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-all duration-200 group">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                <span className="sr-only">Notifications</span>
              </button>

              {/* Quick Actions */}
              <div className="hidden md:flex items-center space-x-2">
                <Link 
                  to="/upload-resume"
                  className="btn-ghost text-xs px-3 py-2"
                  title="Quick upload"
                >
                  <Upload className="w-4 h-4 mr-1" />
                  Upload
                </Link>
                <Link 
                  to="/jobs/create"
                  className="btn-primary text-xs px-3 py-2"
                  title="Create new job"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  New Job
                </Link>
              </div>

              {/* System Status */}
              <div className="status-indicator">
                <div className="status-dot online"></div>
                <span className="text-sm font-medium text-slate-600 hidden sm:block">
                  System Active
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <div className="py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="animate-fade-in">
                {children}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;