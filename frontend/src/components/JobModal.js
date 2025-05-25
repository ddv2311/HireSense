import React, { useState, useEffect } from 'react';
import { X, Briefcase, MapPin, DollarSign, Clock, Edit2, Save, FileText } from 'lucide-react';
import api from '../api/config';
import toast from 'react-hot-toast';

const JobModal = ({ job, isOpen, onClose, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (job) {
      setEditData({
        title: job.title || '',
        description: job.description || '',
        requirements: job.requirements || '',
        skills: job.skills || ''
      });
    }
  }, [job]);

  const handleSave = async () => {
    setLoading(true);
    try {
      const response = await api.put(`/jobs/${job.id}`, editData);
      if (response.data.success) {
        toast.success('Job updated successfully');
        setIsEditing(false);
        onUpdate(response.data.job);
      }
    } catch (error) {
      toast.error('Failed to update job');
      console.error('Error updating job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    // Reset edit data
    setEditData({
      title: job.title || '',
      description: job.description || '',
      requirements: job.requirements || '',
      skills: job.skills || ''
    });
  };

  const parseSkills = (skillsString) => {
    if (!skillsString) return [];
    try {
      return JSON.parse(skillsString);
    } catch {
      return skillsString.split(',').map(skill => skill.trim()).filter(skill => skill);
    }
  };

  const parseRequirements = (requirementsString) => {
    if (!requirementsString) return [];
    try {
      return JSON.parse(requirementsString);
    } catch {
      return requirementsString.split('\n').filter(req => req.trim());
    }
  };

  if (!isOpen || !job) return null;

  const skills = parseSkills(job.skills);
  const requirements = parseRequirements(job.requirements);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
              <Briefcase className="w-8 h-8 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900">
                {isEditing ? 'Edit Job' : 'Job Details'}
              </h2>
              <p className="text-slate-600">View and manage job posting information</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Edit job"
              >
                <Edit2 className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Job Title */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              <Briefcase className="w-4 h-4 inline mr-2" />
              Job Title
            </label>
            {isEditing ? (
              <input
                type="text"
                value={editData.title}
                onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter job title"
              />
            ) : (
              <h3 className="text-xl font-bold text-slate-900">{job.title}</h3>
            )}
          </div>

          {/* Job Description */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              <FileText className="w-4 h-4 inline mr-2" />
              Job Description
            </label>
            {isEditing ? (
              <textarea
                value={editData.description}
                onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                rows="6"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter job description"
              />
            ) : (
              <div className="prose max-w-none">
                <p className="text-slate-700 whitespace-pre-wrap">{job.description}</p>
              </div>
            )}
          </div>

          {/* Requirements */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Requirements
            </label>
            {isEditing ? (
              <textarea
                value={editData.requirements}
                onChange={(e) => setEditData({ ...editData, requirements: e.target.value })}
                rows="4"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter requirements (one per line or JSON format)"
              />
            ) : (
              <div className="space-y-2">
                {requirements.length > 0 ? (
                  <ul className="list-disc list-inside space-y-1">
                    {requirements.map((requirement, index) => (
                      <li key={index} className="text-slate-700">{requirement}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-500">No requirements specified</p>
                )}
              </div>
            )}
          </div>

          {/* Skills */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Required Skills
            </label>
            {isEditing ? (
              <textarea
                value={editData.skills}
                onChange={(e) => setEditData({ ...editData, skills: e.target.value })}
                rows="3"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter skills (comma-separated or JSON format)"
              />
            ) : (
              <div className="flex flex-wrap gap-2">
                {skills.length > 0 ? (
                  skills.map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="text-slate-500">No skills specified</p>
                )}
              </div>
            )}
          </div>

          {/* Job Metadata */}
          {!isEditing && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-200">
              <div className="flex items-center space-x-2 text-slate-600">
                <Clock className="w-4 h-4" />
                <span className="text-sm">
                  Posted: {new Date(job.created_at).toLocaleDateString()}
                </span>
              </div>
              {job.location && (
                <div className="flex items-center space-x-2 text-slate-600">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm">{job.location}</span>
                </div>
              )}
              {job.salary_range && (
                <div className="flex items-center space-x-2 text-slate-600">
                  <DollarSign className="w-4 h-4" />
                  <span className="text-sm">{job.salary_range}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        {isEditing && (
          <div className="flex items-center justify-end space-x-3 p-6 border-t border-slate-200 bg-slate-50">
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-slate-600 hover:text-slate-800 font-medium transition-colors"
            >
              <X className="w-4 h-4 inline mr-2" />
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin inline mr-2"></div>
              ) : (
                <Save className="w-4 h-4 inline mr-2" />
              )}
              Save Changes
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobModal; 