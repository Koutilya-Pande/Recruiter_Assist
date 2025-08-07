// MongoDB initialization script
db = db.getSiblingDB('recruiter_assist');

// Create collections
db.createCollection('candidates');
db.createCollection('users');
db.createCollection('jobs');

// Create indexes for better performance
db.candidates.createIndex({ "filename": 1 }, { unique: true });
db.candidates.createIndex({ "email": 1 });
db.candidates.createIndex({ "full_name": 1 });
db.candidates.createIndex({ "uploaded_by": 1 });
db.candidates.createIndex({ "created_at": 1 });

db.users.createIndex({ "email": 1 }, { unique: true });

db.jobs.createIndex({ "title": 1 });
db.jobs.createIndex({ "company": 1 });
db.jobs.createIndex({ "created_at": 1 });

print('Database initialized successfully!'); 