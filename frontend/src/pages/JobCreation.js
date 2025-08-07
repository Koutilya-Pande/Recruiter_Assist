import React, { useState } from 'react';
import { useAuth } from '../App';
import { ArrowLeft, Edit3, Sparkles } from 'lucide-react';
import apiService from '../services/api';

const JobCreation = () => {
  const { user, logout } = useAuth();
  const [activeMode, setActiveMode] = useState('manual'); // 'manual' or 'ai'
  const [isLoading, setIsLoading] = useState(false);
  const [jobData, setJobData] = useState({
    title: '',
    company: '',
    location: '',
    type: 'full-time', // full-time, part-time, contract, internship
    salary_min: '',
    salary_max: '',
    description: '',
    requirements: '',
    responsibilities: '',
    benefits: '',
    contact_email: '',
    application_deadline: ''
  });
  const [aiText, setAiText] = useState('');

  const handleInputChange = (field, value) => {
    setJobData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAiParse = async () => {
    if (!aiText.trim()) {
      alert('Please enter a job description to parse.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiService.request('/jobs/parse', {
        method: 'POST',
        body: JSON.stringify({ job_description: aiText }),
      });

      setJobData(response);
      setActiveMode('manual'); // Switch to manual mode to review/edit
      alert('Job description parsed successfully! Please review and edit the extracted information.');
    } catch (error) {
      console.error('AI parsing error:', error);
      alert('Failed to parse job description. Please try again or fill in manually.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate salary fields
    if (!jobData.salary_min || !jobData.salary_max) {
      alert('Please fill in both minimum and maximum salary fields.');
      return;
    }
    
    const minSalary = parseInt(jobData.salary_min);
    const maxSalary = parseInt(jobData.salary_max);
    
    if (isNaN(minSalary) || isNaN(maxSalary)) {
      alert('Please enter valid numbers for salary fields.');
      return;
    }
    
    if (minSalary > maxSalary) {
      alert('Minimum salary cannot be greater than maximum salary.');
      return;
    }
    
    // Convert salary strings to integers for the API
    const submitData = {
      ...jobData,
      salary_min: minSalary,
      salary_max: maxSalary
    };
    
    setIsLoading(true);

    try {
      await apiService.createJob(submitData);
      alert('Job created successfully!');
      window.location.href = '/jobs';
    } catch (error) {
      console.error('Job creation error:', error);
      alert(`Failed to create job: ${error.message || 'Please try again.'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <div className="text-2xl font-bold text-gray-900">Recruiter Assist</div>
              <nav className="flex space-x-4">
                <a
                  href="/dashboard"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Dashboard
                </a>
                <a
                  href="/candidates"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Candidates
                </a>
                <a
                  href="/jobs"
                  className="text-blue-600 hover:text-blue-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Jobs
                </a>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user?.full_name || user?.email}
              </span>
              <button
                onClick={logout}
                className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <div className="mb-6">
          <a
            href="/jobs"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Jobs
          </a>
        </div>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create New Job</h1>
          <p className="mt-2 text-gray-600">Add a new job posting.</p>
        </div>

        {/* Mode Selection */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Choose Input Method</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => setActiveMode('manual')}
              className={`p-4 rounded-lg border-2 transition-all ${
                activeMode === 'manual'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center mb-2">
                <Edit3 className="w-5 h-5 mr-2 text-blue-600" />
                <span className="font-medium">Manual Entry</span>
              </div>
              <p className="text-sm text-gray-600">Fill in each field manually for complete control</p>
            </button>

            <button
              onClick={() => setActiveMode('ai')}
              className={`p-4 rounded-lg border-2 transition-all ${
                activeMode === 'ai'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center mb-2">
                <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
                <span className="font-medium">AI-Powered Parsing</span>
              </div>
              <p className="text-sm text-gray-600">Paste job description and let AI extract the details</p>
            </button>
          </div>
        </div>

        {/* AI Text Input */}
        {activeMode === 'ai' && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              <Sparkles className="w-5 h-5 inline mr-2 text-blue-600" />
              AI-Powered Job Parsing
            </h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Paste Job Description
              </label>
              <textarea
                value={aiText}
                onChange={(e) => setAiText(e.target.value)}
                placeholder="Paste the complete job description here. Our AI will extract job title, requirements, responsibilities, and other details automatically."
                className="w-full h-48 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              />
            </div>
            <button
              onClick={handleAiParse}
              disabled={isLoading || !aiText.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              {isLoading ? 'Parsing...' : 'Parse with AI'}
            </button>
          </div>
        )}

        {/* Manual Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            <Edit3 className="w-5 h-5 inline mr-2 text-blue-600" />
            Job Details
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Title *
                </label>
                <input
                  type="text"
                  value={jobData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  required
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Senior Software Engineer"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company *
                </label>
                <input
                  type="text"
                  value={jobData.company}
                  onChange={(e) => handleInputChange('company', e.target.value)}
                  required
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Tech Corp"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  value={jobData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., New York, NY or Remote"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Type
                </label>
                <select
                  value={jobData.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="full-time">Full-time</option>
                  <option value="part-time">Part-time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Min Salary *
                  </label>
                  <input
                    type="number"
                    value={jobData.salary_min}
                    onChange={(e) => handleInputChange('salary_min', e.target.value)}
                    required
                    min="0"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="50000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Max Salary *
                  </label>
                  <input
                    type="number"
                    value={jobData.salary_max}
                    onChange={(e) => handleInputChange('salary_max', e.target.value)}
                    required
                    min="0"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="80000"
                  />
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Email
                </label>
                <input
                  type="email"
                  value={jobData.contact_email}
                  onChange={(e) => handleInputChange('contact_email', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="hr@company.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Application Deadline
                </label>
                <input
                  type="date"
                  value={jobData.application_deadline}
                  onChange={(e) => handleInputChange('application_deadline', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Detailed Information */}
          <div className="mt-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Description *
              </label>
              <textarea
                value={jobData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                required
                rows={4}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Provide a comprehensive overview of the role..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Requirements
              </label>
              <textarea
                value={jobData.requirements}
                onChange={(e) => handleInputChange('requirements', e.target.value)}
                rows={4}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="List the required skills, experience, and qualifications..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Responsibilities
              </label>
              <textarea
                value={jobData.responsibilities}
                onChange={(e) => handleInputChange('responsibilities', e.target.value)}
                rows={4}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Describe the key responsibilities and duties..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Benefits
              </label>
              <textarea
                value={jobData.benefits}
                onChange={(e) => handleInputChange('benefits', e.target.value)}
                rows={3}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="List the benefits and perks offered..."
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="mt-8 flex justify-end space-x-4">
            <a
              href="/jobs"
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md text-sm font-medium transition-colors"
            >
              Cancel
            </a>
            <button
              type="submit"
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-md text-sm font-medium transition-colors"
            >
              {isLoading ? 'Creating...' : 'Create Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default JobCreation; 