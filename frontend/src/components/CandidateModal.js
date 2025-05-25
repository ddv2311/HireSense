import React, { useState, useEffect } from 'react';
import { X, User, Mail, Phone, MapPin, Calendar, Star, Edit2, Save } from 'lucide-react';
import api from '../api/config';
import toast from 'react-hot-toast';

const CandidateModal = ({ candidate, isOpen, onClose, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (candidate) {
      setEditData({
        name: candidate.name || '',
        email: candidate.email || '',
        phone: candidate.phone || '',
        skills: candidate.skills || [],
        experience_years: candidate.experience_years || 0,
        education_level: candidate.education_level || '',
        github_url: candidate.github_url || ''
      });
    }
  }, [candidate]);

  const handleSave = async () => {
    setLoading(true);
    try {
      const response = await api.put(`/candidate/${candidate.id}`, editData);
      if (response.data.success) {
        toast.success('Candidate updated successfully');
        setIsEditing(false);
        onUpdate(response.data.candidate);
      }
    } catch (error) {
      toast.error('Failed to update candidate');
      console.error('Error updating candidate:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    // Reset edit data
    setEditData({
      name: candidate.name || '',
      email: candidate.email || '',
      phone: candidate.phone || '',
      skills: candidate.skills || [],
      experience_years: candidate.experience_years || 0,
      education_level: candidate.education_level || '',
      github_url: candidate.github_url || ''
    });
  };

  const handleSkillsChange = (skillsText) => {
    const skillsArray = skillsText.split(',').map(skill => skill.trim()).filter(skill => skill);
    setEditData({ ...editData, skills: skillsArray });
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getAvatarColor = (name) => {
    const colors = [
      'from-blue-400 to-blue-600',
      'from-emerald-400 to-emerald-600',
      'from-sky-400 to-sky-600',
      'from-amber-400 to-amber-600',
      'from-pink-400 to-pink-600',
      'from-cyan-400 to-cyan-600',
      'from-red-400 to-red-600'
    ];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };

  if (!isOpen || !candidate) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center space-x-4">
            <div className={`w-16 h-16 bg-gradient-to-br ${getAvatarColor(candidate.name)} rounded-xl flex items-center justify-center`}>
              <span className="text-white text-xl font-bold">{getInitials(candidate.name)}</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900">
                {isEditing ? 'Edit Candidate' : 'Candidate Profile'}
              </h2>
              <p className="text-slate-600">View and manage candidate information</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Edit candidate"
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
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <User className="w-4 h-4 inline mr-2" />
                Full Name
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={editData.name}
                  onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              ) : (
                <p className="text-slate-900 font-medium">{candidate.name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <Mail className="w-4 h-4 inline mr-2" />
                Email Address
              </label>
              {isEditing ? (
                <input
                  type="email"
                  value={editData.email}
                  onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              ) : (
                <p className="text-slate-900">{candidate.email}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <Phone className="w-4 h-4 inline mr-2" />
                Phone Number
              </label>
              {isEditing ? (
                <input
                  type="tel"
                  value={editData.phone}
                  onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              ) : (
                <p className="text-slate-900">{candidate.phone || 'Not provided'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-2" />
                Experience
              </label>
              {isEditing ? (
                <input
                  type="number"
                  min="0"
                  value={editData.experience_years}
                  onChange={(e) => setEditData({ ...editData, experience_years: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              ) : (
                <p className="text-slate-900">{candidate.experience_years || 0} years</p>
              )}
            </div>
          </div>

          {/* Education */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Education Level
            </label>
            {isEditing ? (
              <select
                value={editData.education_level}
                onChange={(e) => setEditData({ ...editData, education_level: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select education level</option>
                <option value="high_school">High School</option>
                <option value="associate">Associate Degree</option>
                <option value="bachelor">Bachelor's Degree</option>
                <option value="master">Master's Degree</option>
                <option value="phd">PhD</option>
              </select>
            ) : (
              <p className="text-slate-900 capitalize">{candidate.education_level || 'Not specified'}</p>
            )}
          </div>

          {/* Skills */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Skills
            </label>
            {isEditing ? (
              <textarea
                value={editData.skills.join(', ')}
                onChange={(e) => handleSkillsChange(e.target.value)}
                placeholder="Enter skills separated by commas"
                rows="3"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            ) : (
              <div className="flex flex-wrap gap-2">
                {candidate.skills && candidate.skills.length > 0 ? (
                  candidate.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="text-slate-500">No skills listed</p>
                )}
              </div>
            )}
          </div>

          {/* GitHub URL */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              GitHub Profile
            </label>
            {isEditing ? (
              <input
                type="url"
                value={editData.github_url}
                onChange={(e) => setEditData({ ...editData, github_url: e.target.value })}
                placeholder="https://github.com/username"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            ) : (
              candidate.github_url ? (
                <a
                  href={candidate.github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  {candidate.github_url}
                </a>
              ) : (
                <p className="text-slate-500">Not provided</p>
              )
            )}
          </div>

          {/* Scores */}
          {candidate.final_score && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <Star className="w-4 h-4 inline mr-2" />
                Match Score
              </label>
              <div className="flex items-center space-x-4">
                <div className="flex-1 bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${candidate.final_score * 100}%` }}
                  ></div>
                </div>
                <span className="text-lg font-bold text-slate-900">
                  {(candidate.final_score * 100).toFixed(0)}%
                </span>
              </div>
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

export default CandidateModal; 