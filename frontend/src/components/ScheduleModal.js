import React, { useState, useEffect } from 'react';
import { X, Calendar, Clock, User, Link } from 'lucide-react';
import api from '../api/config';
import toast from 'react-hot-toast';

const ScheduleModal = ({ candidate, isOpen, onClose, onSchedule, selectedJobId }) => {
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState('');
  const [interviewerName, setInterviewerName] = useState('');
  const [meetingLink, setMeetingLink] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingSlots, setLoadingSlots] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchAvailableSlots();
    }
  }, [isOpen]);

  const fetchAvailableSlots = async () => {
    setLoadingSlots(true);
    try {
      const response = await api.get('/schedule/slots');
      if (response.data.success) {
        setAvailableSlots(response.data.slots);
      }
    } catch (error) {
      toast.error('Failed to fetch available slots');
      console.error('Error fetching slots:', error);
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleSchedule = async () => {
    if (!selectedSlot || !interviewerName.trim()) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const scheduleData = {
        slot_id: parseInt(selectedSlot),
        interviewer_name: interviewerName,
        meeting_link: meetingLink,
        job_id: selectedJobId
      };
      
      await onSchedule(scheduleData);
      
      // Reset form
      setSelectedSlot('');
      setInterviewerName('');
      setMeetingLink('');
    } catch (error) {
      toast.error('Failed to schedule interview');
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isOpen || !candidate) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-amber-400 to-amber-600 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900">Schedule Interview</h2>
              <p className="text-slate-600">Schedule an interview with {candidate.name}</p>
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
          {/* Candidate Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="text-sm font-medium text-blue-900 mb-1">Candidate</div>
            <div className="text-sm text-blue-700">
              {candidate.name} ({candidate.email})
            </div>
            {candidate.phone && (
              <div className="text-sm text-blue-600 mt-1">
                Phone: {candidate.phone}
              </div>
            )}
          </div>

          {/* Available Time Slots */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              <Clock className="w-4 h-4 inline mr-2" />
              Available Time Slots
            </label>
            {loadingSlots ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-amber-600"></div>
                <span className="ml-2 text-slate-600">Loading slots...</span>
              </div>
            ) : (
              <select
                value={selectedSlot}
                onChange={(e) => setSelectedSlot(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              >
                <option value="">Select a time slot</option>
                {availableSlots.map((slot) => (
                  <option key={slot.id} value={slot.id}>
                    {formatDateTime(slot.slot_datetime)} - {slot.interviewer_name}
                  </option>
                ))}
              </select>
            )}
            {availableSlots.length === 0 && !loadingSlots && (
              <div className="text-sm text-slate-500 mt-2">
                No available slots found. Please contact admin to add time slots.
              </div>
            )}
          </div>

          {/* Interviewer Name */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              <User className="w-4 h-4 inline mr-2" />
              Interviewer Name *
            </label>
            <input
              type="text"
              value={interviewerName}
              onChange={(e) => setInterviewerName(e.target.value)}
              placeholder="Enter interviewer name"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            />
          </div>

          {/* Meeting Link */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              <Link className="w-4 h-4 inline mr-2" />
              Meeting Link (Optional)
            </label>
            <input
              type="url"
              value={meetingLink}
              onChange={(e) => setMeetingLink(e.target.value)}
              placeholder="https://zoom.us/j/... or https://meet.google.com/..."
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            />
            <div className="text-xs text-slate-500 mt-1">
              Provide a video call link for remote interviews
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
            <div className="text-sm font-medium text-slate-700 mb-2">Quick Actions</div>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setMeetingLink('https://zoom.us/j/')}
                className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
              >
                Zoom Meeting
              </button>
              <button
                onClick={() => setMeetingLink('https://meet.google.com/')}
                className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors"
              >
                Google Meet
              </button>
              <button
                onClick={() => setMeetingLink('https://teams.microsoft.com/')}
                className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition-colors"
              >
                Teams Meeting
              </button>
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
            onClick={handleSchedule}
            disabled={loading || !selectedSlot || !interviewerName.trim()}
            className="px-6 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <Calendar className="w-4 h-4" />
            )}
            <span>{loading ? 'Scheduling...' : 'Schedule Interview'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ScheduleModal; 