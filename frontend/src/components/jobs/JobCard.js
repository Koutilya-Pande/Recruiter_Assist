import React from 'react';
import { Calendar, MapPin, DollarSign, Building, Clock, Users } from 'lucide-react';

const JobCard = ({ job, onEdit, onDelete, onViewApplications, onViewDetails }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'published':
        return 'bg-green-100 text-green-800';
      case 'closed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'draft':
        return 'Draft';
      case 'published':
        return 'Published';
      case 'closed':
        return 'Closed';
      default:
        return status;
    }
  };

  // Debug: Log the job object to see its structure
  console.log('Job object:', job);
  console.log('Job ID:', job.id, 'Job _id:', job._id);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">{job.title}</h3>
          <div className="flex items-center text-gray-600 mb-2">
            <Building className="w-4 h-4 mr-2" />
            <span>{job.company}</span>
          </div>
          {job.location && (
            <div className="flex items-center text-gray-600 mb-2">
              <MapPin className="w-4 h-4 mr-2" />
              <span>{job.location}</span>
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
            {getStatusText(job.status)}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="flex items-center text-gray-600">
          <DollarSign className="w-4 h-4 mr-2" />
          <span>${job.salary_min?.toLocaleString()} - ${job.salary_max?.toLocaleString()}</span>
        </div>
        <div className="flex items-center text-gray-600">
          <Clock className="w-4 h-4 mr-2" />
          <span className="capitalize">{job.type}</span>
        </div>
      </div>

      {job.description && (
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {job.description.length > 150 
            ? `${job.description.substring(0, 150)}...` 
            : job.description
          }
        </p>
      )}

      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
        <div className="flex items-center">
          <Calendar className="w-4 h-4 mr-2" />
          <span>Created {formatDate(job.created_at)}</span>
        </div>
        {job.application_deadline && (
          <div className="flex items-center">
            <span>Deadline: {formatDate(job.application_deadline)}</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center text-gray-600">
          <Users className="w-4 h-4 mr-2" />
          <span className="text-sm">0 applications</span>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => onViewDetails(job.id || job._id)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium px-3 py-1 rounded hover:bg-blue-50 transition-colors"
          >
            View Details
          </button>
          <button
            onClick={() => onViewApplications(job.id || job._id)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium px-3 py-1 rounded hover:bg-blue-50 transition-colors"
          >
            View Applications
          </button>
          <button
            onClick={() => onEdit(job)}
            className="text-gray-600 hover:text-gray-700 text-sm font-medium px-3 py-1 rounded hover:bg-gray-50 transition-colors"
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(job.id || job._id)}
            className="text-red-600 hover:text-red-700 text-sm font-medium px-3 py-1 rounded hover:bg-red-50 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobCard; 