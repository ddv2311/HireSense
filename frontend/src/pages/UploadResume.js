import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import api from '../api/config';
import { Upload, FileText, Github, CheckCircle, Video, Code, Brain, Target } from 'lucide-react';
import toast from 'react-hot-toast';

const UploadResume = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [codeFile, setCodeFile] = useState(null);
  const [githubUrl, setGithubUrl] = useState('');
  const [parsedData, setParsedData] = useState(null);
  const [multiModalAnalysis, setMultiModalAnalysis] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file && (file.type === 'application/pdf' || file.type === 'text/plain')) {
      setUploadedFile(file);
    } else {
      toast.error('Please upload a PDF or TXT file');
    }
  }, []);

  const onVideoDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file && file.type.startsWith('video/')) {
      setVideoFile(file);
      toast.success('Video introduction added!');
    } else {
      toast.error('Please upload a video file');
    }
  }, []);

  const onCodeDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    const validExtensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php', '.rb'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.'));
    
    if (validExtensions.includes(fileExtension.toLowerCase())) {
      setCodeFile(file);
      toast.success('Coding sample added!');
    } else {
      toast.error('Please upload a valid code file (.py, .js, .java, etc.)');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt']
    },
    multiple: false
  });

  const { getRootProps: getVideoRootProps, getInputProps: getVideoInputProps, isDragActive: isVideoDragActive } = useDropzone({
    onDrop: onVideoDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    },
    multiple: false
  });

  const { getRootProps: getCodeRootProps, getInputProps: getCodeInputProps, isDragActive: isCodeDragActive } = useDropzone({
    onDrop: onCodeDrop,
    accept: {
      'text/*': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php', '.rb']
    },
    multiple: false
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!uploadedFile) {
      toast.error('Please upload a resume');
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

      if (codeFile) {
        formData.append('coding_sample', codeFile);
      }

      const response = await api.post('/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setParsedData(response.data.parsed_data);
        setMultiModalAnalysis(response.data.multi_modal_analysis);
        toast.success('Resume uploaded and analyzed successfully!');
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
    setCodeFile(null);
    setGithubUrl('');
    setParsedData(null);
    setMultiModalAnalysis(null);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Multi-Modal Resume Upload</h1>
        <p className="mt-2 text-gray-600">
          Upload resumes, video introductions, and coding samples for comprehensive AI analysis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <div className="space-y-6">
          {/* Resume Upload */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <FileText className="w-5 h-5 mr-2 text-blue-600" />
              Resume Upload (Required)
            </h2>
            
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-blue-400 bg-blue-50'
                  : uploadedFile
                  ? 'border-green-400 bg-green-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <input {...getInputProps()} />
              {uploadedFile ? (
                <div className="space-y-2">
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto" />
                  <p className="text-green-700 font-medium">{uploadedFile.name}</p>
                  <p className="text-sm text-green-600">Ready to upload</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                  <p className="text-gray-600">
                    {isDragActive ? 'Drop the resume here' : 'Drag & drop resume or click to browse'}
                  </p>
                  <p className="text-sm text-gray-500">PDF or TXT files only</p>
                </div>
              )}
            </div>
          </div>

          {/* Video Introduction Upload */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Video className="w-5 h-5 mr-2 text-purple-600" />
              Video Introduction (Optional)
            </h2>
            
            <div
              {...getVideoRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isVideoDragActive
                  ? 'border-purple-400 bg-purple-50'
                  : videoFile
                  ? 'border-green-400 bg-green-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <input {...getVideoInputProps()} />
              {videoFile ? (
                <div className="space-y-2">
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto" />
                  <p className="text-green-700 font-medium">{videoFile.name}</p>
                  <p className="text-sm text-green-600">Video ready for analysis</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <Video className="w-12 h-12 text-gray-400 mx-auto" />
                  <p className="text-gray-600">
                    {isVideoDragActive ? 'Drop the video here' : 'Upload video introduction'}
                  </p>
                  <p className="text-sm text-gray-500">MP4, AVI, MOV, MKV, WebM</p>
                </div>
              )}
            </div>
          </div>

          {/* Coding Sample Upload */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Code className="w-5 h-5 mr-2 text-green-600" />
              Coding Sample (Optional)
            </h2>
            
            <div
              {...getCodeRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isCodeDragActive
                  ? 'border-green-400 bg-green-50'
                  : codeFile
                  ? 'border-green-400 bg-green-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <input {...getCodeInputProps()} />
              {codeFile ? (
                <div className="space-y-2">
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto" />
                  <p className="text-green-700 font-medium">{codeFile.name}</p>
                  <p className="text-sm text-green-600">Code ready for analysis</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <Code className="w-12 h-12 text-gray-400 mx-auto" />
                  <p className="text-gray-600">
                    {isCodeDragActive ? 'Drop the code file here' : 'Upload coding sample'}
                  </p>
                  <p className="text-sm text-gray-500">Python, JavaScript, Java, C++, etc.</p>
                </div>
              )}
            </div>
          </div>

          {/* GitHub URL */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Github className="w-5 h-5 mr-2 text-gray-800" />
              GitHub Profile (Optional)
            </h2>
            
            <input
              type="url"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder="https://github.com/username"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={!uploadedFile || uploading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Processing...
              </>
            ) : (
              <>
                <Brain className="w-5 h-5 mr-2" />
                Analyze with AI
              </>
            )}
          </button>

          {parsedData && (
            <button
              onClick={resetForm}
              className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Upload Another Resume
            </button>
          )}
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          {parsedData && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Target className="w-5 h-5 mr-2 text-green-600" />
                Analysis Results
              </h2>
              
              <div className="space-y-4">
                {/* Basic Info */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">Candidate Profile</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div><span className="font-medium">Name:</span> {parsedData.name}</div>
                    <div><span className="font-medium">Email:</span> {parsedData.email}</div>
                    <div><span className="font-medium">Experience:</span> {parsedData.experience_years} years</div>
                    <div><span className="font-medium">Education:</span> {(parsedData.education_score * 100).toFixed(0)}%</div>
                  </div>
                </div>

                {/* Skills */}
                {parsedData.skills && parsedData.skills.length > 0 && (
                  <div className="bg-green-50 rounded-lg p-4">
                    <h3 className="font-semibold text-green-900 mb-2">Detected Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {parsedData.skills.map((skill, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Enhanced Score */}
                {parsedData.enhanced_score && (
                  <div className="bg-purple-50 rounded-lg p-4">
                    <h3 className="font-semibold text-purple-900 mb-2">Enhanced AI Score</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Overall Score:</span>
                        <span className="font-bold text-lg">{parsedData.enhanced_score.final_score}/100</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Grade:</span>
                        <span className="font-bold">{parsedData.enhanced_score.grade}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Multi-Modal Analysis */}
                {multiModalAnalysis && (
                  <div className="space-y-3">
                    {multiModalAnalysis.video_analysis && !multiModalAnalysis.video_analysis.error && (
                      <div className="bg-purple-50 rounded-lg p-4">
                        <h3 className="font-semibold text-purple-900 mb-2">Video Analysis</h3>
                        <div className="text-sm space-y-1">
                          {multiModalAnalysis.video_analysis.overall_score && (
                            <div className="flex justify-between">
                              <span>Communication Score:</span>
                              <span className="font-medium">{multiModalAnalysis.video_analysis.overall_score.final_score}/100</span>
                            </div>
                          )}
                          {multiModalAnalysis.video_analysis.audio_analysis && (
                            <div className="flex justify-between">
                              <span>Word Count:</span>
                              <span className="font-medium">{multiModalAnalysis.video_analysis.audio_analysis.word_count}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {multiModalAnalysis.code_analysis && !multiModalAnalysis.code_analysis.error && (
                      <div className="bg-green-50 rounded-lg p-4">
                        <h3 className="font-semibold text-green-900 mb-2">Code Analysis</h3>
                        <div className="text-sm space-y-1">
                          <div className="flex justify-between">
                            <span>Language:</span>
                            <span className="font-medium">{multiModalAnalysis.code_analysis.language}</span>
                          </div>
                          {multiModalAnalysis.code_analysis.overall_score && (
                            <div className="flex justify-between">
                              <span>Code Quality:</span>
                              <span className="font-medium">{multiModalAnalysis.code_analysis.overall_score.final_score}/100</span>
                            </div>
                          )}
                          {multiModalAnalysis.code_analysis.overall_score && (
                            <div className="flex justify-between">
                              <span>Grade:</span>
                              <span className="font-medium">{multiModalAnalysis.code_analysis.overall_score.grade}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {!parsedData && (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">AI Analysis Ready</h3>
              <p className="text-gray-600">
                Upload a resume to see comprehensive AI analysis including skills extraction, 
                video communication assessment, and code quality evaluation.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadResume; 