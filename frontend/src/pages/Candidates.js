import React, { useState, useEffect } from 'react';
import { Search, Eye, MessageSquare, Calendar, Star, Filter, Download, MoreVertical, User, Trash2 } from 'lucide-react';
import api from '../api/config';
import toast from 'react-hot-toast';
import CandidateModal from '../components/CandidateModal';

const Candidates = () => {
  const [candidates, setCandidates] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchJobs();
    fetchCandidates();
  }, []);

  useEffect(() => {
    if (selectedJob) {
      fetchCandidates(selectedJob);
    } else {
      fetchCandidates();
    }
  }, [selectedJob]);

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

  const fetchCandidates = async (jobId = null) => {
    try {
      const url = jobId ? `/candidates?job_id=${jobId}` : '/candidates';
      const response = await api.get(url);
      if (response.data.success) {
        setCandidates(response.data.candidates);
      }
    } catch (error) {
      toast.error('Failed to fetch candidates');
    } finally {
      setLoading(false);
    }
  };

  const handleViewCandidate = (candidate) => {
    setSelectedCandidate(candidate);
    setIsModalOpen(true);
  };

  const handleUpdateCandidate = (updatedCandidate) => {
    setCandidates(candidates.map(candidate => 
      candidate.id === updatedCandidate.id ? updatedCandidate : candidate
    ));
  };

  const handleDeleteCandidate = async (candidate) => {
    if (window.confirm(`Are you sure you want to delete ${candidate.name}? This action cannot be undone.`)) {
      try {
        const response = await api.delete(`/candidate/${candidate.id}`);
        if (response.data.success) {
          toast.success(response.data.message);
          setCandidates(candidates.filter(c => c.id !== candidate.id));
        }
      } catch (error) {
        toast.error('Failed to delete candidate');
        console.error('Error deleting candidate:', error);
      }
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'badge-success';
    if (score >= 0.6) return 'badge-warning';
    if (score >= 0.4) return 'badge-info';
    return 'badge-error';
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
      'from-sky-400 to-sky-600',
      'from-cyan-400 to-cyan-600',
      'from-red-400 to-red-600'
    ];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };

  const filteredCandidates = candidates.filter(candidate =>
    candidate.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    candidate.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (candidate.skills && candidate.skills.some(skill => 
      skill.toLowerCase().includes(searchTerm.toLowerCase())
    ))
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner w-8 h-8"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Candidates</h1>
          <p className="text-slate-600 mt-1">Manage and review candidate applications</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button className="btn-outline flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
          <button className="btn-outline flex items-center space-x-2">
            <Filter className="w-4 h-4" />
            <span>Filter</span>
          </button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="card">
        <div className="card-body">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search candidates by name, email, or skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10"
              />
            </div>
            
            {/* Job Filter */}
            <div className="sm:w-64">
              <select
                value={selectedJob}
                onChange={(e) => setSelectedJob(e.target.value)}
                className="input"
              >
                <option value="">All Candidates</option>
                {jobs.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.title}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Results Summary */}
          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="text-slate-600">
              Showing {filteredCandidates.length} of {candidates.length} candidates
              {selectedJob && (
                <span className="ml-2 badge badge-primary">
                  {jobs.find(job => job.id.toString() === selectedJob)?.title}
                </span>
              )}
            </span>
            {searchTerm && (
              <span className="text-slate-500">
                Filtered by: "{searchTerm}"
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Candidates Table */}
      <div className="card-elevated">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50/80">
              <tr>
                <th className="table-header">
                  <div className="flex items-center space-x-2">
                    <span>Candidate</span>
                  </div>
                </th>
                <th className="table-header">Experience</th>
                <th className="table-header">Education</th>
                {selectedJob && (
                  <th className="table-header">
                    <div className="flex items-center space-x-1">
                      <Star className="w-3 h-3" />
                      <span>Match Score</span>
                    </div>
                  </th>
                )}
                <th className="table-header">Skills</th>
                <th className="table-header">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {filteredCandidates.map((candidate, index) => (
                <tr key={candidate.id} className={`table-row group ${index % 2 === 0 ? 'bg-white' : 'bg-slate-50'}`}>
                  <td className="table-cell">
                    <div className="flex items-center space-x-4">
                      <div className={`avatar-md bg-gradient-to-br ${getAvatarColor(candidate.name)}`}>
                        <span>{getInitials(candidate.name)}</span>
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="text-sm font-semibold text-slate-900 truncate">
                          {candidate.name}
                        </div>
                        <div className="text-sm text-slate-500 truncate">
                          {candidate.email}
                        </div>
                        {candidate.phone && (
                          <div className="text-xs text-slate-400 truncate">
                            {candidate.phone}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  
                  <td className="table-cell">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-slate-900">
                        {candidate.experience_years || 0} years
                      </span>
                      {candidate.experience_years >= 5 && (
                        <span className="badge badge-success text-xs">Senior</span>
                      )}
                    </div>
                  </td>
                  
                  <td className="table-cell">
                    <span className="text-sm text-slate-900 capitalize">
                      {candidate.education_level || 'Not specified'}
                    </span>
                    {candidate.education_score && (
                      <div className="text-xs text-slate-500 mt-1">
                        Score: {(candidate.education_score * 100).toFixed(0)}%
                      </div>
                    )}
                  </td>
                  
                  {selectedJob && (
                    <td className="table-cell">
                      {candidate.final_score ? (
                        <div className="flex items-center space-x-2">
                          <span className={`badge ${getScoreColor(candidate.final_score)} flex items-center space-x-1`}>
                            <Star className="h-3 w-3" />
                            <span>{(candidate.final_score * 100).toFixed(0)}%</span>
                          </span>
                          <div className="w-16 bg-slate-200 rounded-full h-1.5">
                            <div 
                              className="bg-gradient-to-r from-sky-500 to-sky-600 h-1.5 rounded-full transition-all duration-300"
                              style={{ width: `${candidate.final_score * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      ) : (
                        <span className="badge badge-neutral">Not scored</span>
                      )}
                    </td>
                  )}
                  
                  <td className="table-cell">
                    <div className="flex flex-wrap gap-1 max-w-xs">
                      {candidate.skills?.slice(0, 3).map((skill, skillIndex) => (
                        <span
                          key={skillIndex}
                          className="badge badge-primary text-xs"
                        >
                          {skill}
                        </span>
                      ))}
                      {candidate.skills?.length > 3 && (
                        <span className="badge badge-neutral text-xs">
                          +{candidate.skills.length - 3} more
                        </span>
                      )}
                      {(!candidate.skills || candidate.skills.length === 0) && (
                        <span className="text-xs text-slate-400">No skills listed</span>
                      )}
                    </div>
                  </td>
                  
                  <td className="table-cell">
                    <div className="flex items-center space-x-2">
                      <button 
                        onClick={() => handleViewCandidate(candidate)}
                        className="p-2 text-slate-400 hover:text-sky-600 hover:bg-sky-50 rounded-lg transition-all duration-200 group-hover:scale-110"
                        title="View profile"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button 
                        className="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-all duration-200 group-hover:scale-110"
                        title="Send message"
                      >
                        <MessageSquare className="h-4 w-4" />
                      </button>
                      <button 
                        className="p-2 text-slate-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-all duration-200 group-hover:scale-110"
                        title="Schedule interview"
                      >
                        <Calendar className="h-4 w-4" />
                      </button>
                      <button 
                        onClick={() => handleDeleteCandidate(candidate)}
                        className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200 group-hover:scale-110"
                        title="Delete candidate"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Empty State */}
        {filteredCandidates.length === 0 && (
          <div className="text-center py-12">
            <div className="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <User className="w-10 h-10 text-slate-400" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              {searchTerm ? 'No candidates found' : 'No candidates yet'}
            </h3>
            <p className="text-slate-500 mb-6 max-w-sm mx-auto">
              {searchTerm 
                ? `No candidates match your search for "${searchTerm}". Try adjusting your search terms.`
                : 'Start by uploading resumes or creating job postings to attract candidates.'
              }
            </p>
            {!searchTerm && (
              <div className="flex justify-center space-x-3">
                <button className="btn-primary">
                  Upload Resume
                </button>
                <button className="btn-outline">
                  Create Job
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Pagination (if needed) */}
      {filteredCandidates.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-slate-600">
            Showing all {filteredCandidates.length} candidates
          </div>
          <div className="flex items-center space-x-2">
            <button className="btn-outline text-sm px-3 py-2" disabled>
              Previous
            </button>
            <span className="px-3 py-2 text-sm font-medium text-slate-900 bg-sky-50 border border-sky-200 rounded-lg">
              1
            </span>
            <button className="btn-outline text-sm px-3 py-2" disabled>
              Next
            </button>
          </div>
        </div>
      )}

      {/* Candidate Modal */}
      <CandidateModal
        candidate={selectedCandidate}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedCandidate(null);
        }}
        onUpdate={handleUpdateCandidate}
      />
    </div>
  );
};

export default Candidates; 