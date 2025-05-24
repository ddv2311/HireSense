import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Users, 
  Target,
  Brain,
  BarChart3,
  PieChart,
  Activity,
  Zap,
  Shield,
  Eye
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';
import api from '../api/config';
import toast from 'react-hot-toast';

const Analytics = () => {
  const [funnelMetrics, setFunnelMetrics] = useState(null);
  const [biasAnalysis, setBiasAnalysis] = useState(null);
  const [realTimeInsights, setRealTimeInsights] = useState(null);
  const [mcpStats, setMcpStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState(30);

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedTimeframe]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Fetch all analytics data
      const [funnelResponse, biasResponse, insightsResponse, mcpResponse] = await Promise.all([
        api.get(`/analytics/funnel?days=${selectedTimeframe}`),
        api.get('/analytics/bias'),
        api.get('/analytics/insights'),
        api.get('/mcp/stats')
      ]);

      if (funnelResponse.data.success) {
        setFunnelMetrics(funnelResponse.data.metrics);
      }

      if (biasResponse.data.success) {
        setBiasAnalysis(biasResponse.data.bias_analysis);
      }

      if (insightsResponse.data.success) {
        setRealTimeInsights(insightsResponse.data.insights);
      }

      if (mcpResponse.data.success) {
        setMcpStats(mcpResponse.data.stats);
      }

    } catch (error) {
      console.error('Error fetching analytics:', error);
      toast.error('Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case 'success': return 'bg-green-50 border-green-200 text-green-800';
      case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'info': return 'bg-blue-50 border-blue-200 text-blue-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getAlertIcon = (type) => {
    switch (type) {
      case 'success': return CheckCircle;
      case 'warning': return AlertTriangle;
      case 'info': return Eye;
      default: return Activity;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Prepare funnel chart data
  const funnelChartData = funnelMetrics ? [
    { stage: 'Applications', count: funnelMetrics.funnel_metrics.total_candidates, color: '#3b82f6' },
    { stage: 'Scored', count: funnelMetrics.funnel_metrics.scored_candidates, color: '#10b981' },
    { stage: 'Interviewed', count: funnelMetrics.funnel_metrics.interviewed_candidates, color: '#f59e0b' },
    { stage: 'Completed', count: funnelMetrics.funnel_metrics.completed_interviews, color: '#ef4444' }
  ] : [];

  // Prepare score distribution data
  const scoreDistributionData = funnelMetrics?.score_distribution?.score_ranges ? [
    { range: 'Excellent (85+)', count: funnelMetrics.score_distribution.score_ranges.excellent, color: '#22c55e' },
    { range: 'Good (70-84)', count: funnelMetrics.score_distribution.score_ranges.good, color: '#3b82f6' },
    { range: 'Average (55-69)', count: funnelMetrics.score_distribution.score_ranges.average, color: '#f59e0b' },
    { range: 'Poor (<55)', count: funnelMetrics.score_distribution.score_ranges.poor, color: '#ef4444' }
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Recruitment Analytics</h1>
          <p className="text-gray-600">Advanced insights and bias detection for data-driven hiring</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(Number(e.target.value))}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button
            onClick={fetchAnalyticsData}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Activity className="h-4 w-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Real-time Alerts */}
      {realTimeInsights?.alerts && realTimeInsights.alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-500" />
            Real-time Alerts
          </h2>
          <div className="space-y-3">
            {realTimeInsights.alerts.map((alert, index) => {
              const AlertIcon = getAlertIcon(alert.type);
              return (
                <div key={index} className={`border rounded-lg p-4 ${getAlertColor(alert.type)}`}>
                  <div className="flex items-start gap-3">
                    <AlertIcon className="h-5 w-5 mt-0.5" />
                    <div className="flex-1">
                      <p className="font-medium">{alert.message}</p>
                      <p className="text-sm mt-1 opacity-80">{alert.action}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Pipeline Status */}
        {realTimeInsights?.pipeline_status && (
          <>
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Candidates</p>
                  <p className="text-2xl font-bold text-gray-900">{realTimeInsights.pipeline_status.total_candidates}</p>
                  <div className="flex items-center mt-2">
                    <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                    <span className="text-sm text-green-600">{realTimeInsights.trends?.application_trend || 0}%</span>
                  </div>
                </div>
                <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
                  <Users className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">High-Score Candidates</p>
                  <p className="text-2xl font-bold text-gray-900">{realTimeInsights.pipeline_status.high_score_candidates}</p>
                  <p className="text-sm text-gray-500 mt-2">Score ≥ 80</p>
                </div>
                <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
                  <Target className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Pending Interviews</p>
                  <p className="text-2xl font-bold text-gray-900">{realTimeInsights.pipeline_status.pending_interviews}</p>
                  <p className="text-sm text-gray-500 mt-2">Scheduled</p>
                </div>
                <div className="w-12 h-12 bg-yellow-500 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Today's Applications</p>
                  <p className="text-2xl font-bold text-gray-900">{realTimeInsights.pipeline_status.today_applications}</p>
                  <p className="text-sm text-gray-500 mt-2">New today</p>
                </div>
                <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
                  <Activity className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hiring Funnel */}
        {funnelMetrics && (
          <div className="bg-white rounded-lg shadow border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Hiring Funnel</h3>
              <p className="text-sm text-gray-600">Conversion rates through hiring stages</p>
            </div>
            <div className="p-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={funnelChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="stage" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Scoring Rate:</span>
                  <span className="font-medium ml-2">{funnelMetrics.funnel_metrics.scoring_rate}%</span>
                </div>
                <div>
                  <span className="text-gray-600">Interview Rate:</span>
                  <span className="font-medium ml-2">{funnelMetrics.funnel_metrics.interview_rate}%</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Score Distribution */}
        {scoreDistributionData.length > 0 && (
          <div className="bg-white rounded-lg shadow border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Score Distribution</h3>
              <p className="text-sm text-gray-600">Candidate scoring breakdown</p>
            </div>
            <div className="p-6">
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={scoreDistributionData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="count"
                    label={({ range, count }) => `${range}: ${count}`}
                  >
                    {scoreDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
              {funnelMetrics?.score_distribution && (
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Mean Score:</span>
                    <span className="font-medium ml-2">{funnelMetrics.score_distribution.mean_score}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Median Score:</span>
                    <span className="font-medium ml-2">{funnelMetrics.score_distribution.median_score}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Bias Detection */}
      {biasAnalysis && (
        <div className="bg-white rounded-lg shadow border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-500" />
              Bias Detection Analysis
            </h3>
            <p className="text-sm text-gray-600">Automated bias detection in hiring process</p>
          </div>
          <div className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className={`flex items-center gap-2 px-3 py-2 rounded-full ${
                biasAnalysis.bias_detected 
                  ? 'bg-red-100 text-red-800' 
                  : 'bg-green-100 text-green-800'
              }`}>
                {biasAnalysis.bias_detected ? (
                  <AlertTriangle className="h-4 w-4" />
                ) : (
                  <CheckCircle className="h-4 w-4" />
                )}
                <span className="font-medium">
                  {biasAnalysis.bias_detected ? 'Bias Detected' : 'No Bias Detected'}
                </span>
              </div>
              {biasAnalysis.bias_types && biasAnalysis.bias_types.length > 0 && (
                <div className="flex gap-2">
                  {biasAnalysis.bias_types.map((type, index) => (
                    <span key={index} className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">
                      {type}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {biasAnalysis.recommendations && biasAnalysis.recommendations.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">Recommendations:</h4>
                <ul className="space-y-1 text-sm text-blue-800">
                  {biasAnalysis.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-blue-500 mt-1">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Market Insights & MCP Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Market Insights */}
        {realTimeInsights?.market_insights && (
          <div className="bg-white rounded-lg shadow border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Market Insights</h3>
              <p className="text-sm text-gray-600">Skills demand and market trends</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Top Skills in Demand</h4>
                  <div className="space-y-2">
                    {realTimeInsights.market_insights.top_skills_demand?.slice(0, 5).map((skill, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-700">{skill.skill}</span>
                        <span className="text-sm font-medium text-gray-900">{skill.count} jobs</span>
                      </div>
                    ))}
                  </div>
                </div>

                {realTimeInsights.market_insights.skill_gap_analysis?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Skill Gaps</h4>
                    <div className="space-y-2">
                      {realTimeInsights.market_insights.skill_gap_analysis.slice(0, 3).map((gap, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-sm text-gray-700">{gap.skill}</span>
                          <span className="text-sm font-medium text-red-600">{gap.gap_count} gaps</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* MCP Model Stats */}
        {mcpStats && (
          <div className="bg-white rounded-lg shadow border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-500" />
                Model Context Protocol
              </h3>
              <p className="text-sm text-gray-600">AI model performance and learning</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Model Version</span>
                    <p className="font-medium text-gray-900">{mcpStats.model_version}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Feedback Count</span>
                    <p className="font-medium text-gray-900">{mcpStats.feedback_count}</p>
                  </div>
                </div>

                <div>
                  <span className="text-sm text-gray-600">Model Accuracy</span>
                  <div className="mt-1">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{ width: `${(mcpStats.performance_metrics?.accuracy || 0) * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      {((mcpStats.performance_metrics?.accuracy || 0) * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>

                <div>
                  <span className="text-sm text-gray-600">Context Weights</span>
                  <div className="mt-2 space-y-1">
                    {Object.entries(mcpStats.context_weights || {}).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-700 capitalize">{key.replace('_', ' ')}</span>
                        <span className="font-medium">{(value * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics; 