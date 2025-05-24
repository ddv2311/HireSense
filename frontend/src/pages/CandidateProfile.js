import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Mail, Phone, Github, Calendar, MessageSquare } from 'lucide-react';
import api from '../api/config';
import toast from 'react-hot-toast';

const CandidateProfile = () => {
  const { id } = useParams();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchCandidate = async () => {
    try {
      const response = await api.get(`/candidate/${id}`);
      if (response.data.success) {
        setCandidate(response.data.profile.candidate);
      }
    } catch (error) {
      toast.error('Failed to fetch candidate profile');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidate();
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Candidate not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <div className="h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-xl font-bold">
                {candidate.name.charAt(0)}
              </span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{candidate.name}</h1>
              <div className="flex items-center space-x-4 mt-2">
                {candidate.email && (
                  <div className="flex items-center text-gray-600">
                    <Mail className="h-4 w-4 mr-1" />
                    <span className="text-sm">{candidate.email}</span>
                  </div>
                )}
                {candidate.phone && (
                  <div className="flex items-center text-gray-600">
                    <Phone className="h-4 w-4 mr-1" />
                    <span className="text-sm">{candidate.phone}</span>
                  </div>
                )}
                {candidate.github_url && (
                  <div className="flex items-center text-gray-600">
                    <Github className="h-4 w-4 mr-1" />
                    <a 
                      href={candidate.github_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline"
                    >
                      GitHub Profile
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="flex space-x-2">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Send Message
            </button>
            <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Schedule Interview
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Experience & Education</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Experience</label>
                <p className="mt-1 text-sm text-gray-900">{candidate.experience_years} years</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Education</label>
                <p className="mt-1 text-sm text-gray-900">{candidate.education_level}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Skills</h2>
            <div className="flex flex-wrap gap-2">
              {candidate.skills?.map((skill, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Resume</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
              <div className="text-center">
                <p className="text-sm text-gray-600">Resume file: {candidate.resume_path}</p>
                <button className="mt-2 text-blue-600 hover:text-blue-800 text-sm font-medium">
                  Download Resume
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Profile Completeness</span>
                <span className="text-sm font-medium text-gray-900">85%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '85%' }}></div>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Applications</span>
                <span className="text-sm font-medium text-gray-900">3</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Interviews</span>
                <span className="text-sm font-medium text-gray-900">1</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Messages</span>
                <span className="text-sm font-medium text-gray-900">5</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-2 w-2 bg-green-400 rounded-full mt-2"></div>
                </div>
                <div>
                  <p className="text-sm text-gray-900">Resume uploaded</p>
                  <p className="text-xs text-gray-500">2 hours ago</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-2 w-2 bg-blue-400 rounded-full mt-2"></div>
                </div>
                <div>
                  <p className="text-sm text-gray-900">Profile created</p>
                  <p className="text-xs text-gray-500">1 day ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateProfile; 