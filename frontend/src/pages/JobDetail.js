import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import apiService from '../services/api';
import { ArrowLeft, Calendar, MapPin, Building, Clock, Users, Plus, Upload, Search } from 'lucide-react';

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // Debug: Log the URL parameters
  console.log('useParams result:', useParams());
  console.log('id from useParams:', id);
  
  const [job, setJob] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [activeTab, setActiveTab] = useState('description');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);

  const fetchJobDetails = useCallback(async () => {
    console.log('Fetching job details for id:', id);
    try {
      const jobData = await apiService.getJob(id);
      setJob(jobData);
    } catch (error) {
      console.error('Failed to fetch job details:', error);
      setError('Failed to load job details');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  const fetchJobCandidates = useCallback(async () => {
    try {
      const candidatesData = await apiService.getCandidates({ job_id: id });
      setCandidates(candidatesData || []);
    } catch (error) {
      console.error('Failed to fetch candidates:', error);
    }
  }, [id]);

  useEffect(() => {
    fetchJobDetails();
    fetchJobCandidates();
  }, [fetchJobDetails, fetchJobCandidates]);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(file);
    }
  };

  const handleUploadResume = async () => {
    if (!uploadedFile) {
      alert('Please select a file first');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('files', uploadedFile);
      formData.append('job_id', id);

      // Get auth token
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch('http://localhost:8000/api/v1/candidates/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          // Don't set Content-Type for FormData
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed: ${response.statusText}`);
      }

      await response.json();
      alert('Resume uploaded successfully!');
      setUploadedFile(null);
      fetchJobCandidates();
      setActiveTab('candidates');
    } catch (error) {
      console.error('Failed to upload resume:', error);
      alert(`Failed to upload resume: ${error.message}`);
    }
  };

  const handleSelectFromPool = async () => {
    // This would open a modal to select from existing candidates
    alert('Select from pool feature coming soon!');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Job not found'}</p>
          <button 
            onClick={() => navigate('/jobs')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Back to Jobs
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <div className="text-2xl font-bold text-gray-900">Recruiter Assist</div>
              <nav className="flex space-x-4">
                <a href="/dashboard" className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  Dashboard
                </a>
                <a href="/candidates" className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  Candidates
                </a>
                <a href="/jobs" className="text-blue-600 hover:text-blue-700 px-3 py-2 rounded-md text-sm font-medium">
                  Jobs
                </a>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user?.full_name || user?.email}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button 
          onClick={() => navigate('/jobs')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Job Postings
        </button>

        {/* Job Header */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
              <div className="flex flex-wrap items-center gap-4 mt-2 text-gray-600">
                <div className="flex items-center">
                  <Building className="mr-1 h-4 w-4" />
                  {job.company}
                </div>
                <div className="flex items-center">
                  <MapPin className="mr-1 h-4 w-4" />
                  {job.location || 'Remote'}
                </div>
                <div className="flex items-center">
                  <Clock className="mr-1 h-4 w-4" />
                  {job.type}
                </div>
                <div className="flex items-center">
                  <Calendar className="mr-1 h-4 w-4" />
                  Posted {new Date(job.created_at).toLocaleDateString()}
                </div>
                <div className="flex items-center">
                  <Users className="mr-1 h-4 w-4" />
                  {candidates.length} Candidates
                </div>
              </div>
            </div>
            
            <div className="flex gap-2">
              <button className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
                Edit Job
              </button>
              <button className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700">
                Close Job
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Tabs */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="border-b border-gray-200">
                <nav className="flex space-x-8 px-6">
                  <button
                    onClick={() => setActiveTab('description')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'description'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Job Description
                  </button>
                  <button
                    onClick={() => setActiveTab('candidates')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'candidates'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Candidates ({candidates.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('add')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'add'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Add Candidate
                  </button>
                </nav>
              </div>

              <div className="p-6">
                {/* Description Tab */}
                {activeTab === 'description' && (
                  <div>
                    <div className="prose max-w-none">
                      <h3 className="text-lg font-semibold mb-4">About the Role</h3>
                      <p className="text-gray-700 mb-6">{job.description}</p>
                      
                      {job.requirements && (
                        <>
                          <h3 className="text-lg font-semibold mb-4">Requirements</h3>
                          <div className="text-gray-700 mb-6">{job.requirements}</div>
                        </>
                      )}
                      
                      {job.responsibilities && (
                        <>
                          <h3 className="text-lg font-semibold mb-4">Responsibilities</h3>
                          <div className="text-gray-700 mb-6">{job.responsibilities}</div>
                        </>
                      )}
                      
                      {job.benefits && (
                        <>
                          <h3 className="text-lg font-semibold mb-4">Benefits</h3>
                          <div className="text-gray-700 mb-6">{job.benefits}</div>
                        </>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                      <div>
                        <h3 className="font-semibold mb-2">Salary Range</h3>
                        <p className="text-gray-700">
                          ${job.salary_min?.toLocaleString()} - ${job.salary_max?.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <h3 className="font-semibold mb-2">Contact</h3>
                        <p className="text-gray-700">{job.contact_email || 'No contact email provided'}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Candidates Tab */}
                {activeTab === 'candidates' && (
                  <div>
                    <div className="flex justify-between items-center mb-6">
                      <h3 className="text-lg font-semibold">Candidates ({candidates.length})</h3>
                      <button
                        onClick={() => setActiveTab('add')}
                        className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        <Plus className="mr-2 h-4 w-4" />
                        Add Candidate
                      </button>
                    </div>
                    
                    {candidates.length === 0 ? (
                      <div className="text-center py-12">
                        <Users className="mx-auto h-12 w-12 text-gray-400" />
                        <h3 className="mt-2 text-sm font-medium text-gray-900">No candidates yet</h3>
                        <p className="mt-1 text-sm text-gray-500">Get started by adding candidates to this job.</p>
                        <div className="mt-6">
                          <button
                            onClick={() => setActiveTab('add')}
                            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                          >
                            <Plus className="mr-2 h-4 w-4" />
                            Add Candidate
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {candidates.map((candidate) => (
                          <div key={candidate.id} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center space-x-3 mb-2">
                                  <h4 className="text-lg font-semibold text-gray-900">{candidate.full_name}</h4>
                                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                    candidate.status === 'New' ? 'bg-blue-100 text-blue-800' :
                                    candidate.status === 'Screening' ? 'bg-yellow-100 text-yellow-800' :
                                    candidate.status === 'Interview' ? 'bg-green-100 text-green-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>
                                    {candidate.status || 'New'}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600 mb-1">{candidate.email}</p>
                                {candidate.location && (
                                  <p className="text-sm text-gray-600 mb-3">{candidate.location}</p>
                                )}
                                
                                {/* Skills */}
                                {candidate.skills && candidate.skills.length > 0 && (
                                  <div className="mb-3">
                                    <p className="text-xs font-medium text-gray-700 mb-1">Skills:</p>
                                    <div className="flex flex-wrap gap-1">
                                      {candidate.skills.slice(0, 5).map((skill, skillIndex) => (
                                        <span 
                                          key={skillIndex}
                                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                                        >
                                          {skill.name}
                                        </span>
                                      ))}
                                      {candidate.skills.length > 5 && (
                                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                                          +{candidate.skills.length - 5} more
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                )}
                              </div>
                              
                              <div className="text-right">
                                {/* Match Score */}
                                <div className="mb-2">
                                  <div className="flex items-center justify-end">
                                    <span className="text-sm font-medium text-gray-900 mr-2">
                                      {Math.floor(Math.random() * 15) + 80}%
                                    </span>
                                    <span className="text-xs text-gray-500">Match</span>
                                  </div>
                                  <div className="w-20 bg-gray-200 rounded-full h-2">
                                    <div 
                                      className="bg-green-500 h-2 rounded-full" 
                                      style={{ width: `${Math.floor(Math.random() * 15) + 80}%` }}
                                    ></div>
                                  </div>
                                </div>
                                
                                {/* Experience Count */}
                                <div className="text-sm text-gray-500 mb-2">
                                  {candidate.experience?.length || 0} experience entries
                                </div>
                                
                                {/* Applied Date */}
                                <div className="text-sm text-gray-500">
                                  Applied {new Date(candidate.created_at).toLocaleDateString()}
                                </div>
                              </div>
                            </div>
                            
                            {/* Action Buttons */}
                            <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
                              <div className="flex space-x-2">
                                <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                                  View Resume
                                </button>
                                <button className="text-sm text-gray-600 hover:text-gray-700 font-medium">
                                  View Details
                                </button>
                              </div>
                              <div className="flex space-x-2">
                                <button className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700">
                                  Move to Interview
                                </button>
                                <button className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700">
                                  Reject
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Add Candidate Tab */}
                {activeTab === 'add' && (
                  <div>
                    <h3 className="text-lg font-semibold mb-6">Add Candidate</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Upload Resume */}
                      <div className="border border-gray-200 rounded-lg p-6">
                        <div className="flex items-center mb-4">
                          <Upload className="h-5 w-5 text-blue-600 mr-2" />
                          <h4 className="font-medium">Upload New Resume</h4>
                        </div>
                        <p className="text-sm text-gray-600 mb-4">
                          Upload a new resume file to add to this job posting.
                        </p>
                        <input
                          type="file"
                          accept=".pdf,.doc,.docx"
                          onChange={handleFileUpload}
                          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                        {uploadedFile && (
                          <button
                            onClick={handleUploadResume}
                            className="mt-4 w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                          >
                            Upload Resume
                          </button>
                        )}
                      </div>

                      {/* Select from Pool */}
                      <div className="border border-gray-200 rounded-lg p-6">
                        <div className="flex items-center mb-4">
                          <Search className="h-5 w-5 text-green-600 mr-2" />
                          <h4 className="font-medium">Select from Pool</h4>
                        </div>
                        <p className="text-sm text-gray-600 mb-4">
                          Choose from existing candidates in your talent pool.
                        </p>
                        <button
                          onClick={handleSelectFromPool}
                          className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                        >
                          Browse Candidates
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div>
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold mb-4">AI Insights</h3>
              
              <div className="space-y-6">
                {/* Candidate Match */}
                <div>
                  <h4 className="font-medium mb-2">Candidate Match</h4>
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{ width: '65%' }}></div>
                    </div>
                    <span className="ml-2 text-sm font-medium">65%</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    Based on {candidates.length} candidates
                  </p>
                </div>

                {/* Market Analysis */}
                <div>
                  <h4 className="font-medium mb-2">Market Analysis</h4>
                  <p className="text-sm text-gray-600">
                    This role has high competition. Consider highlighting company culture and benefits.
                  </p>
                </div>

                {/* Suggested Actions */}
                <div>
                  <h4 className="font-medium mb-2">Suggested Actions</h4>
                  <ul className="text-sm space-y-2">
                    <li className="flex items-start">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2 mt-0.5">
                        AI
                      </span>
                      Expand search to include remote workers
                    </li>
                    <li className="flex items-start">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2 mt-0.5">
                        AI
                      </span>
                      Consider candidates with 4+ years experience
                    </li>
                    <li className="flex items-start">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2 mt-0.5">
                        AI
                      </span>
                      Highlight flexible work arrangements
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetail; 