import React, { useState, useEffect } from 'react';
import { Clock, Plus, User, Video, X, Edit, Trash2 } from 'lucide-react';
import api from '../api/config';
import toast from 'react-hot-toast';

const Schedule = () => {
  const [interviews, setInterviews] = useState([]);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingInterview, setEditingInterview] = useState(null);
  const [scheduleForm, setScheduleForm] = useState({
    candidate_id: '',
    job_id: '',
    slot_id: '',
    interviewer_name: '',
    meeting_link: ''
  });

  const fetchInterviews = async () => {
    try {
      const response = await api.get(`/schedule?date=${selectedDate}`);
      if (response.data.success) {
        setInterviews(response.data.schedule);
      }
    } catch (error) {
      toast.error('Failed to fetch interviews');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableSlots = async () => {
    try {
      const response = await api.get('/schedule/slots');
      if (response.data.success) {
        setAvailableSlots(response.data.slots);
      }
    } catch (error) {
      toast.error('Failed to fetch available slots');
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

  const fetchJobs = async () => {
    try {
      const response = await api.get('/jobs');
      if (response.data.success) {
        setJobs(response.data.jobs);
      }
    } catch (error) {
      toast.error('Failed to fetch jobs');
    }
  };

  useEffect(() => {
    fetchInterviews();
    fetchAvailableSlots();
    fetchCandidates();
    fetchJobs();
  }, [selectedDate]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleScheduleInterview = async (e) => {
    e.preventDefault();
    
    if (!scheduleForm.candidate_id || !scheduleForm.job_id || !scheduleForm.slot_id) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const response = await api.post('/schedule', scheduleForm);
      if (response.data.success) {
        toast.success('Interview scheduled successfully!');
        setShowScheduleModal(false);
        setScheduleForm({
          candidate_id: '',
          job_id: '',
          slot_id: '',
          interviewer_name: '',
          meeting_link: ''
        });
        fetchInterviews();
        fetchAvailableSlots();
      } else {
        toast.error(response.data.error || 'Failed to schedule interview');
      }
    } catch (error) {
      toast.error('Failed to schedule interview');
    }
  };

  const handleEditInterview = (interview) => {
    setEditingInterview(interview);
    setScheduleForm({
      candidate_id: interview.candidate_id,
      job_id: interview.job_id || '',
      slot_id: '',
      interviewer_name: interview.interviewer_name,
      meeting_link: interview.meeting_link || ''
    });
    setShowEditModal(true);
  };

  const handleUpdateInterview = async (e) => {
    e.preventDefault();
    
    if (!scheduleForm.slot_id) {
      toast.error('Please select a new time slot');
      return;
    }

    try {
      const response = await api.put(`/schedule/${editingInterview.id}`, {
        new_slot_id: parseInt(scheduleForm.slot_id),
        interviewer_name: scheduleForm.interviewer_name,
        meeting_link: scheduleForm.meeting_link
      });
      
      if (response.data.success) {
        toast.success('Interview updated successfully!');
        setShowEditModal(false);
        setEditingInterview(null);
        setScheduleForm({
          candidate_id: '',
          job_id: '',
          slot_id: '',
          interviewer_name: '',
          meeting_link: ''
        });
        fetchInterviews();
        fetchAvailableSlots();
      } else {
        toast.error(response.data.error || 'Failed to update interview');
      }
    } catch (error) {
      toast.error('Failed to update interview');
      console.error('Error updating interview:', error);
    }
  };

  const handleCancelInterview = async (interview) => {
    if (window.confirm(`Are you sure you want to cancel the interview with ${interview.candidate_name}? This action cannot be undone.`)) {
      try {
        const response = await api.delete(`/schedule/${interview.id}`);
        if (response.data.success) {
          toast.success('Interview cancelled successfully');
          fetchInterviews();
          fetchAvailableSlots();
        } else {
          toast.error(response.data.error || 'Failed to cancel interview');
        }
      } catch (error) {
        toast.error('Failed to cancel interview');
        console.error('Error cancelling interview:', error);
      }
    }
  };

  const handleQuickBook = async (slot) => {
    if (candidates.length === 0 || jobs.length === 0) {
      toast.error('No candidates or jobs available');
      return;
    }

    // Pre-fill the form with the selected slot
    setScheduleForm({
      candidate_id: candidates[0]?.id || '',
      job_id: jobs[0]?.id || '',
      slot_id: slot.id,
      interviewer_name: slot.interviewer_name,
      meeting_link: ''
    });
    setShowScheduleModal(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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
        <h1 className="text-2xl font-bold text-gray-900">Interview Schedule</h1>
        <div className="flex space-x-4">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button 
            onClick={() => setShowScheduleModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Schedule Interview
          </button>
        </div>
      </div>

      {/* Schedule Interview Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Schedule Interview</h2>
              <button 
                onClick={() => setShowScheduleModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <form onSubmit={handleScheduleInterview} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Candidate *
                </label>
                <select
                  value={scheduleForm.candidate_id}
                  onChange={(e) => setScheduleForm({...scheduleForm, candidate_id: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Select a candidate</option>
                  {candidates.map(candidate => (
                    <option key={candidate.id} value={candidate.id}>
                      {candidate.name} - {candidate.email}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Position *
                </label>
                <select
                  value={scheduleForm.job_id}
                  onChange={(e) => setScheduleForm({...scheduleForm, job_id: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Select a job</option>
                  {jobs.map(job => (
                    <option key={job.id} value={job.id}>
                      {job.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Time Slot *
                </label>
                <select
                  value={scheduleForm.slot_id}
                  onChange={(e) => {
                    const selectedSlot = availableSlots.find(slot => slot.id.toString() === e.target.value);
                    setScheduleForm({
                      ...scheduleForm, 
                      slot_id: e.target.value,
                      interviewer_name: selectedSlot?.interviewer_name || ''
                    });
                  }}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Select a time slot</option>
                  {availableSlots.filter(slot => !slot.is_booked).map(slot => (
                    <option key={slot.id} value={slot.id}>
                      {new Date(slot.start_time).toLocaleString()} - {slot.interviewer_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Interviewer Name
                </label>
                <input
                  type="text"
                  value={scheduleForm.interviewer_name}
                  onChange={(e) => setScheduleForm({...scheduleForm, interviewer_name: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter interviewer name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Meeting Link
                </label>
                <input
                  type="url"
                  value={scheduleForm.meeting_link}
                  onChange={(e) => setScheduleForm({...scheduleForm, meeting_link: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="https://meet.google.com/..."
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowScheduleModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Interview Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Edit Interview</h2>
              <button 
                onClick={() => setShowEditModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <form onSubmit={handleUpdateInterview} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Time Slot *
                </label>
                <select
                  value={scheduleForm.slot_id}
                  onChange={(e) => setScheduleForm({...scheduleForm, slot_id: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Select a new time slot</option>
                  {availableSlots.filter(slot => !slot.is_booked).map(slot => (
                    <option key={slot.id} value={slot.id}>
                      {new Date(slot.start_time).toLocaleString()} - {slot.interviewer_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Interviewer Name
                </label>
                <input
                  type="text"
                  value={scheduleForm.interviewer_name}
                  onChange={(e) => setScheduleForm({...scheduleForm, interviewer_name: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter new interviewer name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Meeting Link
                </label>
                <input
                  type="url"
                  value={scheduleForm.meeting_link}
                  onChange={(e) => setScheduleForm({...scheduleForm, meeting_link: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="https://meet.google.com/..."
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Update
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Interviews for {new Date(selectedDate).toLocaleDateString()}
              </h2>
            </div>
            
            <div className="divide-y divide-gray-200">
              {interviews.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  No interviews scheduled for this date
                </div>
              ) : (
                interviews.map((interview) => (
                  <div key={interview.id} className="p-6 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 bg-blue-600 rounded-full flex items-center justify-center">
                            <User className="h-5 w-5 text-white" />
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <h3 className="text-sm font-medium text-gray-900">
                              {interview.candidate_name}
                            </h3>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(interview.status)}`}>
                              {interview.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mt-1">
                            {interview.job_title}
                          </p>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                            <div className="flex items-center">
                              <Clock className="h-4 w-4 mr-1" />
                              {new Date(interview.scheduled_time).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </div>
                            <div className="flex items-center">
                              <User className="h-4 w-4 mr-1" />
                              {interview.interviewer_name}
                            </div>
                            {interview.meeting_link && (
                              <div className="flex items-center">
                                <Video className="h-4 w-4 mr-1" />
                                <a 
                                  href={interview.meeting_link}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-600 hover:underline"
                                >
                                  Join Meeting
                                </a>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button 
                          onClick={() => handleEditInterview(interview)}
                          className="text-blue-600 hover:text-blue-900 text-sm"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => handleCancelInterview(interview)}
                          className="text-red-600 hover:text-red-900 text-sm"
                        >
                          Cancel
                        </button>
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
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Time Slots</h2>
            <div className="space-y-2">
              {availableSlots.filter(slot => !slot.is_booked).slice(0, 8).map((slot) => (
                <div key={slot.id} className="flex items-center justify-between p-2 border border-gray-200 rounded">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {new Date(slot.start_time).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                    <div className="text-xs text-gray-500">
                      {slot.interviewer_name}
                    </div>
                  </div>
                  <button 
                    onClick={() => handleQuickBook(slot)}
                    className="text-blue-600 hover:text-blue-900 text-sm"
                  >
                    Book
                  </button>
                </div>
              ))}
            </div>
            <button className="w-full mt-4 text-blue-600 hover:text-blue-900 text-sm font-medium">
              View All Slots
            </button>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Today's Interviews</span>
                <span className="text-sm font-medium text-gray-900">
                  {interviews.filter(i => i.status === 'scheduled').length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">This Week</span>
                <span className="text-sm font-medium text-gray-900">12</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Completed</span>
                <span className="text-sm font-medium text-gray-900">
                  {interviews.filter(i => i.status === 'completed').length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Available Slots</span>
                <span className="text-sm font-medium text-gray-900">
                  {availableSlots.filter(slot => !slot.is_booked).length}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming</h2>
            <div className="space-y-3">
              {interviews.slice(0, 3).map((interview) => (
                <div key={interview.id} className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 bg-blue-400 rounded-full"></div>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{interview.candidate_name}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(interview.scheduled_time).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
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

export default Schedule; 