import React, { useState } from 'react';
import { X, Send, MessageSquare } from 'lucide-react';
import toast from 'react-hot-toast';

const MessageModal = ({ candidate, isOpen, onClose, onSend, selectedJobId }) => {
  const [messageType, setMessageType] = useState('interview_invitation');
  const [customMessage, setCustomMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const messageTemplates = {
    interview_invitation: {
      subject: 'Interview Invitation',
      template: `Dear ${candidate?.name || '[Name]'},\n\nWe are pleased to invite you for an interview for the position you applied for. We were impressed by your qualifications and would like to discuss your candidacy further.\n\nPlease let us know your availability for the coming week.\n\nBest regards,\nHiring Team`
    },
    application_received: {
      subject: 'Application Received',
      template: `Dear ${candidate?.name || '[Name]'},\n\nThank you for your interest in our company and for submitting your application. We have received your resume and will review it carefully.\n\nWe will contact you within the next few days regarding the next steps.\n\nBest regards,\nHiring Team`
    },
    follow_up: {
      subject: 'Follow-up on Your Application',
      template: `Dear ${candidate?.name || '[Name]'},\n\nI hope this message finds you well. I wanted to follow up on your recent application and see if you have any questions about the position or our company.\n\nPlease feel free to reach out if you need any additional information.\n\nBest regards,\nHiring Team`
    },
    rejection: {
      subject: 'Update on Your Application',
      template: `Dear ${candidate?.name || '[Name]'},\n\nThank you for your interest in our company and for taking the time to apply for the position.\n\nAfter careful consideration, we have decided to move forward with other candidates whose qualifications more closely match our current needs.\n\nWe appreciate your interest and wish you the best in your job search.\n\nBest regards,\nHiring Team`
    },
    custom: {
      subject: 'Message from Hiring Team',
      template: ''
    }
  };

  const handleSend = async () => {
    setLoading(true);
    try {
      const messageData = {
        candidate_id: candidate.id,
        job_id: selectedJobId ? parseInt(selectedJobId) : null,
        message_type: messageType,
        additional_context: {
          subject: messageTemplates[messageType].subject,
          content: messageType === 'custom' ? customMessage : messageTemplates[messageType].template,
          candidate_name: candidate.name,
          candidate_email: candidate.email
        }
      };
      
      console.log('Sending message data:', messageData);
      await onSend(messageData);
      setCustomMessage('');
      setMessageType('interview_invitation');
    } catch (error) {
      console.error('Error in MessageModal:', error);
      toast.error('Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !candidate) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900">Send Message</h2>
              <p className="text-slate-600">Send a message to {candidate.name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Message Type */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Message Type
            </label>
            <select
              value={messageType}
              onChange={(e) => setMessageType(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option value="interview_invitation">Interview Invitation</option>
              <option value="application_received">Application Received</option>
              <option value="follow_up">Follow-up</option>
              <option value="rejection">Application Update</option>
              <option value="custom">Custom Message</option>
            </select>
          </div>

          {/* Message Preview/Editor */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Message Content
            </label>
            {messageType === 'custom' ? (
              <textarea
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                placeholder="Enter your custom message..."
                rows="8"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            ) : (
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                <div className="text-sm font-medium text-slate-700 mb-2">
                  Subject: {messageTemplates[messageType].subject}
                </div>
                <div className="text-sm text-slate-600 whitespace-pre-wrap">
                  {messageTemplates[messageType].template}
                </div>
              </div>
            )}
          </div>

          {/* Candidate Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="text-sm font-medium text-blue-900 mb-1">Recipient</div>
            <div className="text-sm text-blue-700">
              {candidate.name} ({candidate.email})
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-slate-200 bg-slate-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-slate-600 hover:text-slate-800 font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSend}
            disabled={loading || (messageType === 'custom' && !customMessage.trim())}
            className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span>{loading ? 'Sending...' : 'Send Message'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default MessageModal; 