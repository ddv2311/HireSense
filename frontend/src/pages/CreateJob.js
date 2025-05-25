import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Save, X, Briefcase, MapPin, DollarSign, Clock, Users, AlertCircle, CheckCircle } from 'lucide-react';
import api from '../api/config';
import toast from 'react-hot-toast';

const CreateJob = () => {
  const [jobData, setJobData] = useState({
    title: '',
    description: '',
    requirements: '',
    experience_level: 'mid',
    location: '',
    salary_range: '',
    employment_type: 'full-time'
  });
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setFile(acceptedFiles[0]);
        toast.success('Job description file uploaded!');
      }
    },
    onDropRejected: () => {
      toast.error('Please upload a valid file (PDF, TXT, DOC, DOCX)');
    }
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setJobData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!jobData.title || !jobData.description) {
      toast.error('Please fill in required fields');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      
      // Add job data
      Object.keys(jobData).forEach(key => {
        formData.append(key, jobData[key]);
      });

      // Add file if uploaded
      if (file) {
        formData.append('file', file);
      }

      const response = await api.post('/upload-jd', formData);

      if (response.data.success) {
        toast.success('Job description created successfully!');
        // Reset form
        setJobData({
          title: '',
          description: '',
          requirements: '',
          experience_level: 'mid',
          location: '',
          salary_range: '',
          employment_type: 'full-time'
        });
        setFile(null);
        setPreviewMode(false);
      } else {
        toast.error(response.data.message || 'Failed to create job description');
      }
    } catch (error) {
      toast.error('Failed to create job description');
    } finally {
      setLoading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    toast.success('File removed');
  };

  const isFormValid = jobData.title && jobData.description;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Create Job Description</h1>
          <p className="text-slate-600 mt-1">Set up a new job posting to attract the right candidates</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={() => setPreviewMode(!previewMode)}
            className="btn-outline"
          >
            {previewMode ? 'Edit' : 'Preview'}
          </button>
        </div>
      </div>

      {previewMode ? (
        /* Preview Mode */
        <div className="space-y-6">
          <div className="card-elevated">
            <div className="card-header border-l-4 border-sky-500">
              <h2 className="text-xl font-bold text-slate-900">Job Preview</h2>
              <p className="text-sm text-slate-600">How your job posting will appear to candidates</p>
            </div>
            <div className="card-body space-y-6">
              {/* Job Header */}
              <div className="border-b border-slate-200 pb-6">
                <h1 className="text-2xl font-bold text-slate-900 mb-2">{jobData.title || 'Job Title'}</h1>
                <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600">
                  {jobData.location && (
                    <div className="flex items-center space-x-1">
                      <MapPin className="w-4 h-4" />
                      <span>{jobData.location}</span>
                    </div>
                  )}
                  {jobData.employment_type && (
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span className="capitalize">{jobData.employment_type.replace('-', ' ')}</span>
                    </div>
                  )}
                  {jobData.experience_level && (
                    <div className="flex items-center space-x-1">
                      <Users className="w-4 h-4" />
                      <span className="capitalize">{jobData.experience_level} Level</span>
                    </div>
                  )}
                  {jobData.salary_range && (
                    <div className="flex items-center space-x-1">
                      <DollarSign className="w-4 h-4" />
                      <span>{jobData.salary_range}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Job Description */}
              {jobData.description && (
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-3">Job Description</h3>
                  <div className="prose prose-slate max-w-none">
                    <p className="whitespace-pre-wrap">{jobData.description}</p>
                  </div>
                </div>
              )}

              {/* Requirements */}
              {jobData.requirements && (
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-3">Requirements</h3>
                  <div className="prose prose-slate max-w-none">
                    <p className="whitespace-pre-wrap">{jobData.requirements}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        /* Edit Mode */
        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {/* Main Form */}
            <div className="xl:col-span-2 space-y-6">
              {/* Basic Information Section */}
              <div className="form-section">
                <div className="form-section-header">
                  <div>
                    <h2 className="form-section-title">Basic Information</h2>
                    <p className="form-section-subtitle">Essential details about the position</p>
                  </div>
                </div>
                
                <div className="form-section-body">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="md:col-span-2">
                      <label className="label">
                        Job Title *
                      </label>
                      <input
                        type="text"
                        name="title"
                        value={jobData.title}
                        onChange={handleInputChange}
                        required
                        className="input"
                        placeholder="e.g. Senior Software Engineer"
                      />
                      <p className="helper-text">
                        Enter a clear job title that candidates can easily understand
                      </p>
                    </div>

                    <div>
                      <label className="label">
                        Experience Level
                      </label>
                      <select
                        name="experience_level"
                        value={jobData.experience_level}
                        onChange={handleInputChange}
                        className="input"
                      >
                        <option value="entry">Entry Level (0-2 years)</option>
                        <option value="mid">Mid Level (2-5 years)</option>
                        <option value="senior">Senior Level (5+ years)</option>
                        <option value="lead">Lead/Principal (8+ years)</option>
                      </select>
                    </div>

                    <div>
                      <label className="label">
                        Employment Type
                      </label>
                      <select
                        name="employment_type"
                        value={jobData.employment_type}
                        onChange={handleInputChange}
                        className="input"
                      >
                        <option value="full-time">Full Time</option>
                        <option value="part-time">Part Time</option>
                        <option value="contract">Contract</option>
                        <option value="internship">Internship</option>
                      </select>
                    </div>

                    <div>
                      <label className="label">
                        Location
                      </label>
                      <input
                        type="text"
                        name="location"
                        value={jobData.location}
                        onChange={handleInputChange}
                        className="input"
                        placeholder="e.g. San Francisco, CA or Remote"
                      />
                      <p className="helper-text">
                        Specify the work location or indicate if remote work is available
                      </p>
                    </div>

                    <div>
                      <label className="label">
                        Salary Range
                      </label>
                      <input
                        type="text"
                        name="salary_range"
                        value={jobData.salary_range}
                        onChange={handleInputChange}
                        className="input"
                        placeholder="e.g. $80,000 - $120,000"
                      />
                      <p className="helper-text">
                        Optional: Include salary range to attract qualified candidates
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Job Details Section */}
              <div className="form-section">
                <div className="form-section-header">
                  <div>
                    <h2 className="form-section-title">Job Details</h2>
                    <p className="form-section-subtitle">Detailed description and requirements</p>
                  </div>
                </div>
                
                <div className="form-section-body">
                  <div className="space-y-6">
                    <div>
                      <label className="label">
                        Job Description *
                      </label>
                      <textarea
                        name="description"
                        value={jobData.description}
                        onChange={handleInputChange}
                        required
                        rows={8}
                        className="input resize-none"
                        placeholder="Describe the role, responsibilities, and what makes this position exciting..."
                      />
                      <p className="helper-text">
                        Provide a comprehensive overview of the role and day-to-day responsibilities
                      </p>
                    </div>

                    <div>
                      <label className="label">
                        Requirements & Qualifications
                      </label>
                      <textarea
                        name="requirements"
                        value={jobData.requirements}
                        onChange={handleInputChange}
                        rows={6}
                        className="input resize-none"
                        placeholder="List the required skills, experience, and qualifications..."
                      />
                      <p className="helper-text">
                        Specify must-have skills, preferred qualifications, and any certifications needed
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Upload Section */}
              <div className="form-section">
                <div className="form-section-header">
                  <div>
                    <h2 className="form-section-title">Upload Job Description</h2>
                    <p className="form-section-subtitle">Optional: Upload existing JD file</p>
                  </div>
                </div>
                
                <div className="form-section-body">
                  {!file ? (
                    <div
                      {...getRootProps()}
                      className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 ${
                        isDragActive
                          ? 'border-sky-400 bg-sky-50'
                          : 'border-slate-300 hover:border-sky-400 hover:bg-slate-50'
                      }`}
                    >
                      <input {...getInputProps()} />
                      <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                        <Upload className="w-6 h-6 text-slate-400" />
                      </div>
                      <p className="text-sm font-medium text-slate-900 mb-1">
                        {isDragActive ? 'Drop the file here' : 'Upload job description'}
                      </p>
                      <p className="text-xs text-slate-500">
                        PDF, TXT, DOC, DOCX up to 10MB
                      </p>
                    </div>
                  ) : (
                    <div className="border border-slate-200 rounded-xl p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                            <FileText className="w-5 h-5 text-emerald-600" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-slate-900 truncate">
                              {file.name}
                            </p>
                            <p className="text-xs text-slate-500">
                              {(file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={removeFile}
                          className="p-1 text-slate-400 hover:text-red-600 transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Form Status */}
              <div className="form-section">
                <div className="form-section-header">
                  <h3 className="text-sm font-semibold text-slate-900">Form Status</h3>
                </div>
                <div className="form-section-body">
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      {jobData.title ? (
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-slate-400" />
                      )}
                      <span className={`text-sm ${jobData.title ? 'text-slate-900' : 'text-slate-500'}`}>
                        Job title
                      </span>
                    </div>
                    <div className="flex items-center space-x-3">
                      {jobData.description ? (
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-slate-400" />
                      )}
                      <span className={`text-sm ${jobData.description ? 'text-slate-900' : 'text-slate-500'}`}>
                        Job description
                      </span>
                    </div>
                    <div className="flex items-center space-x-3">
                      {jobData.location ? (
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-slate-400" />
                      )}
                      <span className={`text-sm ${jobData.location ? 'text-slate-900' : 'text-slate-500'}`}>
                        Location (optional)
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  type="submit"
                  disabled={!isFormValid || loading}
                  className="btn-primary w-full flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <div className="loading-spinner w-4 h-4"></div>
                  ) : (
                    <Save className="w-4 h-4" />
                  )}
                  <span>{loading ? 'Creating...' : 'Create Job Posting'}</span>
                </button>
                
                <button
                  type="button"
                  onClick={() => setPreviewMode(true)}
                  disabled={!isFormValid}
                  className="btn-outline w-full"
                >
                  Preview Job Posting
                </button>
              </div>
            </div>
          </div>
        </form>
      )}
    </div>
  );
};

export default CreateJob; 