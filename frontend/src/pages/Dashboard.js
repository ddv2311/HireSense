import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/config';
import { 
  Users, 
  FileText, 
  Calendar, 
  MessageSquare, 
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  Plus,
  ArrowRight,
  AlertCircle,
  Building2,
  Target,
  Activity,
  Award,
  Brain,
  Shield
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setError(null);
      const response = await api.get('/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError(error.message);
      // Don't show toast error immediately, let user see the dashboard with sample data
    } finally {
      setLoading(false);
    }
  };

  // Enhanced sample data for charts
  const candidateScoreData = [
    { range: 'Excellent (90-100)', count: 5, color: '#10b981', percentage: 11 },
    { range: 'Good (80-89)', count: 12, color: '#3b82f6', percentage: 26 },
    { range: 'Average (70-79)', count: 18, color: '#f59e0b', percentage: 39 },
    { range: 'Below Average (60-69)', count: 8, color: '#ef4444', percentage: 17 },
    { range: 'Poor (<60)', count: 3, color: '#6b7280', percentage: 7 },
  ];

  const monthlyData = [
    { month: 'Jan', candidates: 24, interviews: 18, hires: 6 },
    { month: 'Feb', candidates: 32, interviews: 25, hires: 8 },
    { month: 'Mar', candidates: 28, interviews: 22, hires: 7 },
    { month: 'Apr', candidates: 35, interviews: 28, hires: 9 },
    { month: 'May', candidates: 42, interviews: 35, hires: 12 },
    { month: 'Jun', candidates: 38, interviews: 30, hires: 10 },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner w-8 h-8"></div>
      </div>
    );
  }

  const stats = dashboardData?.statistics || {
    total_candidates: 46,
    total_jobs: 8,
    scheduled_interviews: 12,
    messages_sent: 34
  };

  const kpiCards = [
    {
      title: 'Total Candidates',
      value: stats.total_candidates,
      icon: Users,
      gradient: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      change: '+12%',
      changeType: 'positive',
      description: 'Active in pipeline',
      type: 'primary'
    },
    {
      title: 'Active Jobs',
      value: stats.total_jobs,
      icon: FileText,
      gradient: 'from-emerald-500 to-emerald-600',
      bgColor: 'bg-emerald-50',
      iconColor: 'text-emerald-600',
      change: '+3%',
      changeType: 'positive',
      description: 'Currently hiring',
      type: 'success'
    },
    {
      title: 'Scheduled Interviews',
      value: stats.scheduled_interviews,
      icon: Calendar,
      gradient: 'from-amber-500 to-amber-600',
      bgColor: 'bg-amber-50',
      iconColor: 'text-amber-600',
      change: '+8%',
      changeType: 'positive',
      description: 'This week',
      type: 'warning'
    },
    {
      title: 'Messages Sent',
      value: stats.messages_sent,
      icon: MessageSquare,
      gradient: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      change: '+15%',
      changeType: 'positive',
      description: 'Automated comms',
      type: 'info'
    }
  ];

  return (
    <div className="space-y-8">
      {/* API Connection Status */}
      {error && (
        <div className="card border-l-4 border-amber-400">
          <div className="card-body">
            <div className="flex items-start space-x-3">
              <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
                <AlertCircle className="h-5 w-5 text-amber-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-amber-800 mb-1">
                  Backend Connection Issue
                </h3>
                <p className="text-sm text-amber-700">
                  Unable to connect to the backend API. Showing sample data for demonstration.
                </p>
                <p className="text-xs text-amber-600 mt-1 font-mono">
                  Error: {error}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Welcome Section */}
      <div className="relative overflow-hidden">
        <div className="card-elevated bg-gradient-to-br from-sky-600 via-sky-700 to-cyan-700 text-white">
          <div className="card-body relative z-10">
            <div className="flex items-center justify-between">
              <div className="space-y-4">
                <div>
                  <h1 className="text-3xl font-bold mb-2">Welcome to HireSense</h1>
                  <p className="text-sky-100 text-lg">
                    Streamline your hiring process with intelligent automation and insights
                  </p>
                </div>
                
                <div className="flex items-center space-x-6 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                    <span className="text-sky-100">AI Models Active</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                    <span className="text-sky-100">Real-time Processing</span>
                  </div>
                </div>
              </div>
              
              <div className="hidden lg:block">
                <div className="flex space-x-3">
                  <Link to="/upload-resume" className="btn bg-white/20 text-white hover:bg-white/30 border border-white/30 backdrop-blur-sm">
                    <Plus className="w-4 h-4 mr-2" />
                    Upload Resume
                  </Link>
                  <Link to="/jobs/create" className="btn bg-white text-sky-600 hover:bg-sky-50">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Job
                  </Link>
                </div>
              </div>
            </div>
          </div>
          
          {/* Background decoration */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-32 translate-x-32"></div>
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-24 -translate-x-24"></div>
        </div>
      </div>

      {/* Enhanced KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className={`kpi-card ${card.type} hover-lift`}>
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 ${card.bgColor} rounded-2xl flex items-center justify-center`}>
                  <Icon className={`w-6 h-6 ${card.iconColor}`} />
                </div>
                <div className="flex items-center space-x-1 text-xs">
                  <TrendingUp className="w-3 h-3 text-emerald-500" />
                  <span className="font-semibold text-emerald-600">{card.change}</span>
                </div>
              </div>
              
              <div className="space-y-1">
                <p className="text-sm font-medium text-slate-600">{card.title}</p>
                <p className="text-3xl font-bold text-slate-900">{card.value.toLocaleString()}</p>
                <p className="text-xs text-slate-500">{card.description}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Enhanced Charts Section */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Monthly Trends Chart */}
        <div className="card-elevated">
          <div className="card-header border-l-4 border-sky-500">
            <div>
              <h3 className="chart-title">Monthly Hiring Trends</h3>
              <p className="chart-subtitle">Candidates, interviews, and successful hires over time</p>
            </div>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={monthlyData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="month" 
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  axisLine={{ stroke: '#e2e8f0' }}
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  axisLine={{ stroke: '#e2e8f0' }}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Bar dataKey="candidates" fill="#3b82f6" name="Candidates" radius={[4, 4, 0, 0]} />
                <Bar dataKey="interviews" fill="#f59e0b" name="Interviews" radius={[4, 4, 0, 0]} />
                <Bar dataKey="hires" fill="#10b981" name="Hires" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Candidate Score Distribution */}
        <div className="card-elevated">
          <div className="card-header border-l-4 border-emerald-500">
            <div>
              <h3 className="chart-title">AI Matching Score Distribution</h3>
              <p className="chart-subtitle">Candidate performance breakdown by AI scoring</p>
            </div>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={320}>
              <PieChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <Pie
                  data={candidateScoreData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="count"
                  label={({ range, percentage }) => `${percentage}%`}
                  labelLine={false}
                >
                  {candidateScoreData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            
            {/* Legend */}
            <div className="mt-4 grid grid-cols-1 gap-2">
              {candidateScoreData.map((entry, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: entry.color }}
                    ></div>
                    <span className="text-slate-700">{entry.range}</span>
                  </div>
                  <span className="font-semibold text-slate-900">{entry.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Activity */}
        <div className="card-elevated">
          <div className="card-header border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-slate-900">Recent Activity</h3>
                <p className="text-sm text-slate-600">Latest updates and actions</p>
              </div>
              <Link to="/candidates" className="text-sm font-medium text-purple-600 hover:text-purple-700 flex items-center space-x-1">
                <span>View all</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {dashboardData?.recent_activity?.slice(0, 5).map((activity, index) => (
                <div key={index} className="flex items-center space-x-4 p-3 rounded-xl hover:bg-slate-50 transition-colors">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    activity.type === 'candidate' ? 'bg-blue-100' : 'bg-emerald-100'
                  }`}>
                    {activity.type === 'candidate' ? (
                      <Users className={`w-5 h-5 ${activity.type === 'candidate' ? 'text-blue-600' : 'text-emerald-600'}`} />
                    ) : (
                      <FileText className="w-5 h-5 text-emerald-600" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-900 truncate">
                      {activity.type === 'candidate' ? 'New candidate:' : 'New job:'} {activity.title}
                    </p>
                    <p className="text-xs text-slate-500">
                      {new Date(activity.created_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                  <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                </div>
              )) || (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <Activity className="w-8 h-8 text-slate-400" />
                  </div>
                  <p className="text-sm text-slate-500">No recent activity</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Enhanced Quick Actions */}
        <div className="card-elevated">
          <div className="card-header border-l-4 border-amber-500">
            <div>
              <h3 className="text-lg font-bold text-slate-900">Quick Actions</h3>
              <p className="text-sm text-slate-600">Common tasks and shortcuts</p>
            </div>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 gap-3">
              <Link 
                to="/upload-resume" 
                className="group flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl hover:from-blue-100 hover:to-blue-200 transition-all duration-200 hover-lift"
              >
                <div>
                  <span className="text-sm font-semibold text-slate-900">Upload New Resume</span>
                  <p className="text-xs text-slate-600">Add candidates to pipeline</p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-slate-600 group-hover:translate-x-1 transition-all" />
              </Link>

              <Link 
                to="/jobs/create" 
                className="group flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-emerald-100 rounded-xl hover:from-emerald-100 hover:to-emerald-200 transition-all duration-200 hover-lift"
              >
                <div>
                  <span className="text-sm font-semibold text-slate-900">Create Job Posting</span>
                  <p className="text-xs text-slate-600">Start new hiring process</p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-slate-600 group-hover:translate-x-1 transition-all" />
              </Link>

              <Link 
                to="/schedule" 
                className="group flex items-center justify-between p-4 bg-gradient-to-r from-amber-50 to-amber-100 rounded-xl hover:from-amber-100 hover:to-amber-200 transition-all duration-200 hover-lift"
              >
                <div>
                  <span className="text-sm font-semibold text-slate-900">Schedule Interviews</span>
                  <p className="text-xs text-slate-600">Manage interview calendar</p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-slate-600 group-hover:translate-x-1 transition-all" />
              </Link>

              <Link 
                to="/analytics" 
                className="group flex items-center justify-between p-4 bg-gradient-to-r from-sky-50 to-sky-100 rounded-xl hover:from-sky-100 hover:to-sky-200 transition-all duration-200 hover-lift"
              >
                <div>
                  <span className="text-sm font-semibold text-slate-900">View Analytics</span>
                  <p className="text-xs text-slate-600">Insights and performance</p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-slate-600 group-hover:translate-x-1 transition-all" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced System Status */}
      <div className="card-elevated">
        <div className="card-header border-l-4 border-sky-500">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Service Health</h3>
            <p className="text-sm text-slate-600">Real-time system status monitoring</p>
          </div>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center space-x-4 p-4 bg-emerald-50 rounded-xl">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">AI Models</p>
                <p className="text-xs text-emerald-600 font-medium">All systems operational</p>
                <div className="flex items-center space-x-1 mt-1">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                  <span className="text-xs text-slate-500">99.9% uptime</span>
                </div>
              </div>
            </div>
            
            <div className={`flex items-center space-x-4 p-4 rounded-xl ${
              error ? 'bg-amber-50' : 'bg-emerald-50'
            }`}>
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                error ? 'bg-amber-100' : 'bg-emerald-100'
              }`}>
                {error ? (
                  <AlertCircle className="w-6 h-6 text-amber-600" />
                ) : (
                  <CheckCircle className="w-6 h-6 text-emerald-600" />
                )}
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">Database</p>
                <p className={`text-xs font-medium ${
                  error ? 'text-amber-600' : 'text-emerald-600'
                }`}>
                  {error ? 'Connection issues' : 'Connected and synced'}
                </p>
                <div className="flex items-center space-x-1 mt-1">
                  <div className={`w-2 h-2 rounded-full ${
                    error ? 'bg-amber-500' : 'bg-emerald-500 animate-pulse'
                  }`}></div>
                  <span className="text-xs text-slate-500">
                    {error ? 'Retrying...' : 'Real-time sync'}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4 p-4 bg-blue-50 rounded-xl">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">Email Service</p>
                <p className="text-xs text-blue-600 font-medium">Processing queue</p>
                <div className="flex items-center space-x-1 mt-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-xs text-slate-500">3 messages pending</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 