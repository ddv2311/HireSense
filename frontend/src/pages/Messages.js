import React, { useState, useEffect } from 'react';
import { Send, Search, Filter, MessageSquare, Clock } from 'lucide-react';
import api from '../api/config';
import toast from 'react-hot-toast';

const Messages = () => {
  const [messages, setMessages] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState('');
  const [messageType, setMessageType] = useState('shortlisted');
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchMessages();
    fetchCandidates();
  }, []);

  const fetchMessages = async () => {
    try {
      const response = await api.get('/messages');
      if (response.data.success) {
        setMessages(response.data.messages);
      }
    } catch (error) {
      toast.error('Failed to fetch messages');
    } finally {
      setLoading(false);
    }
  };

  const fetchCandidates = async () => {
    try {
      const response = await api.get('/candidates');
      if (response.data.success) {
        setCandidates(response.data.candidates);
      }
    } catch (error) {
      toast.error('Failed to fetch candidates');
    }
  };

  const sendMessage = async () => {
    if (!selectedCandidate || !messageType) {
      toast.error('Please select a candidate and message type');
      return;
    }

    try {
      const response = await api.post('/send-message', {
        candidate_id: selectedCandidate,
        message_type: messageType,
      });

      if (response.data.success) {
        toast.success('Message sent successfully!');
        fetchMessages();
      } else {
        toast.error(response.data.message || 'Failed to send message');
      }
    } catch (error) {
      toast.error('Failed to send message');
    }
  };

  const getMessageTypeColor = (type) => {
    switch (type) {
      case 'shortlisted':
        return 'bg-green-100 text-green-800';
      case 'interview_confirmation':
        return 'bg-blue-100 text-blue-800';
      case 'interview_reminder':
        return 'bg-yellow-100 text-yellow-800';
      case 'rejection':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredMessages = messages.filter(message =>
    message.candidate_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    message.message_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center space-x-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <input
                    type="text"
                    placeholder="Search messages..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                  <Filter className="h-4 w-4" />
                  <span>Filter</span>
                </button>
              </div>
            </div>

            <div className="divide-y divide-gray-200">
              {filteredMessages.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  No messages found
                </div>
              ) : (
                filteredMessages.map((message) => (
                  <div key={message.id} className="p-6 hover:bg-gray-50">
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 bg-blue-600 rounded-full flex items-center justify-center">
                          <MessageSquare className="h-5 w-5 text-white" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <h3 className="text-sm font-medium text-gray-900">
                              {message.candidate_name}
                            </h3>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getMessageTypeColor(message.message_type)}`}>
                              {message.message_type.replace('_', ' ')}
                            </span>
                          </div>
                          <div className="flex items-center text-sm text-gray-500">
                            <Clock className="h-4 w-4 mr-1" />
                            {new Date(message.sent_at).toLocaleDateString()}
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                          {message.content}
                        </p>
                        <div className="flex items-center space-x-4 mt-2">
                          <span className="text-xs text-gray-500">
                            To: {message.candidate_email}
                          </span>
                          <span className={`text-xs ${message.status === 'sent' ? 'text-green-600' : 'text-red-600'}`}>
                            {message.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Send Message</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Candidate
                </label>
                <select
                  value={selectedCandidate}
                  onChange={(e) => setSelectedCandidate(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Choose a candidate...</option>
                  {candidates.map((candidate) => (
                    <option key={candidate.id} value={candidate.id}>
                      {candidate.name} - {candidate.email}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message Type
                </label>
                <select
                  value={messageType}
                  onChange={(e) => setMessageType(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="shortlisted">Shortlisted</option>
                  <option value="interview_confirmation">Interview Confirmation</option>
                  <option value="interview_reminder">Interview Reminder</option>
                  <option value="rejection">Rejection</option>
                </select>
              </div>

              <button
                onClick={sendMessage}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
              >
                <Send className="h-4 w-4" />
                Send Message
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Message Stats</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Sent</span>
                <span className="text-sm font-medium text-gray-900">
                  {messages.length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Shortlisted</span>
                <span className="text-sm font-medium text-gray-900">
                  {messages.filter(m => m.message_type === 'shortlisted').length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Interview Confirmations</span>
                <span className="text-sm font-medium text-gray-900">
                  {messages.filter(m => m.message_type === 'interview_confirmation').length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Reminders</span>
                <span className="text-sm font-medium text-gray-900">
                  {messages.filter(m => m.message_type === 'interview_reminder').length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Rejections</span>
                <span className="text-sm font-medium text-gray-900">
                  {messages.filter(m => m.message_type === 'rejection').length}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-3">
              {messages.slice(0, 5).map((message) => (
                <div key={message.id} className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 bg-blue-400 rounded-full"></div>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">
                      {message.message_type.replace('_', ' ')} sent to {message.candidate_name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(message.sent_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Messages; 