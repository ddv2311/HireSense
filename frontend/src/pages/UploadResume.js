import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import api from '../api/config';
import { Upload, FileText, Github, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const UploadResume = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [githubUrl, setGithubUrl] = useState('');
  const [videoFile, setVideoFile] = useState(null);
  const [parsedData, setParsedData] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file && file.type === 'application/pdf') {
      setUploadedFile(file);
    } else {
      toast.error('Please upload a PDF file');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!uploadedFile) {
      toast.error('Please upload a resume PDF');
      return;
    }

    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      
      if (githubUrl) {
        formData.append('github_url', githubUrl);
      }
      
      if (videoFile) {
        formData.append('video_intro', videoFile);
      }

      const response = await api.post('/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setParsedData(response.data.parsed_data);
        toast.success('Resume uploaded and parsed successfully!');
      } else {
        toast.error('Failed to upload resume');
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload resume');
    } finally {
      setUploading(false);
    }
  };

  const resetForm = () => {
    setUploadedFile(null);
    setVideoFile(null);
    setGithubUrl('');
    setParsedData(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Resume</h1>
        <p className="text-gray-600">
          Upload a candidate's resume to automatically extract and analyze their information
        </p>
      </div>

      {!parsedData ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Resume (PDF)
              </h3>
              <p className="text-sm text-gray-600">Upload a PDF resume for parsing</p>
            </div>
            <div className="card-body">
              <div
                {...getRootProps()}
                className={`
                  border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
                  ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'}
                  ${uploadedFile ? 'border-success-500 bg-success-50' : ''}
                `}
              >
                <input {...getInputProps()} />
                {uploadedFile ? (
                  <div className="space-y-2">
                    <CheckCircle className="w-12 h-12 text-success-500 mx-auto" />
                    <p className="text-success-700 font-medium">{uploadedFile.name}</p>
                    <p className="text-sm text-success-600">
                      {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                    <p className="text-gray-600">
                      {isDragActive ? 'Drop the PDF here' : 'Drag & drop a PDF resume, or click to select'}
                    </p>
                    <p className="text-sm text-gray-500">PDF files only, max 10MB</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold flex items-center">
                <Github className="w-5 h-5 mr-2" />
                GitHub Profile (Optional)
              </h3>
            </div>
            <div className="card-body">
              <input
                type="url"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                placeholder="https://github.com/username"
                className="input"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <button type="button" onClick={resetForm} className="btn-outline" disabled={uploading}>
              Reset
            </button>
            <button type="submit" className="btn-primary" disabled={uploading || !uploadedFile}>
              {uploading ? 'Processing...' : 'Upload & Parse Resume'}
            </button>
          </div>
        </form>
      ) : (
        <div className="space-y-6">
          <div className="card border-success-200 bg-success-50">
            <div className="card-body">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-success-600" />
                <div>
                  <h3 className="text-lg font-semibold text-success-800">Resume Parsed Successfully!</h3>
                  <p className="text-success-700">The candidate information has been extracted and stored.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold">Basic Information</h3>
              </div>
              <div className="card-body space-y-3">
                <div>
                  <label className="label">Name</label>
                  <p className="text-gray-900 font-medium">{parsedData.name}</p>
                </div>
                <div>
                  <label className="label">Email</label>
                  <p className="text-gray-900">{parsedData.email || 'Not provided'}</p>
                </div>
                <div>
                  <label className="label">Experience</label>
                  <p className="text-gray-900">{parsedData.experience_years} years</p>
                </div>
                <div>
                  <label className="label">Education</label>
                  <p className="text-gray-900">{parsedData.education_level}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold">Skills Detected</h3>
              </div>
              <div className="card-body">
                {parsedData.skills && parsedData.skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {parsedData.skills.map((skill, index) => (
                      <span key={index} className="badge-primary">
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No skills detected</p>
                )}
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <button onClick={resetForm} className="btn-outline">
              Upload Another Resume
            </button>
            <button onClick={() => window.location.href = '/candidates'} className="btn-primary">
              View All Candidates
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadResume; 