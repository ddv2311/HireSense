# 📚 HireSense AI - API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
Currently, the API does not require authentication. In production, implement JWT or API key authentication.

## Response Format
All API responses follow this standard format:
```json
{
  "success": true,
  "data": {},
  "message": "Optional message",
  "error": "Error details if success is false"
}
```

---

## 📄 **Resume Management**

### Upload Resume (Multi-Modal)
Upload and analyze resumes with optional video introductions and coding samples.

**Endpoint:** `POST /upload-resume`

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Resume file (PDF or TXT)
- `github_url` (optional): GitHub profile URL
- `video_intro` (optional): Video introduction file
- `coding_sample` (optional): Code file for analysis

**Response:**
```json
{
  "success": true,
  "candidate_id": 123,
  "parsed_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "skills": ["Python", "React", "AWS"],
    "experience_years": 5,
    "education_level": "bachelor",
    "education_score": 0.85,
    "enhanced_score": {
      "final_score": 87.5,
      "grade": "A"
    }
  },
  "multi_modal_analysis": {
    "video_analysis": {
      "overall_score": {
        "final_score": 82.3,
        "communication": 85.0,
        "presentation": 80.0
      }
    },
    "code_analysis": {
      "language": "Python",
      "complexity_score": 78.5,
      "best_practices_score": 85.2
    }
  }
}
```

### Get Candidates
Retrieve candidates with optional job-specific filtering and scoring.

**Endpoint:** `GET /candidates`

**Query Parameters:**
- `job_id` (optional): Filter candidates for specific job

**Response:**
```json
{
  "success": true,
  "candidates": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "skills": ["Python", "React"],
      "final_score": 0.875,
      "match_score": 0.92,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Update Candidate
Update candidate information.

**Endpoint:** `PUT /candidate/{candidate_id}`

**Request Body:**
```json
{
  "name": "Updated Name",
  "email": "new@example.com",
  "skills": ["Python", "React", "Node.js"],
  "experience_years": 6
}
```

### Delete Candidate
Remove candidate and all related data.

**Endpoint:** `DELETE /candidate/{candidate_id}`

**Response:**
```json
{
  "success": true,
  "message": "Candidate 'John Doe' deleted successfully"
}
```

---

## 💼 **Job Management**

### Upload Job Description
Create a new job posting with AI-powered parsing.

**Endpoint:** `POST /upload-jd`

**Content-Type:** `multipart/form-data` or `application/json`

**Form Data Parameters:**
- `file` (optional): PDF job description
- `title` (required if no file): Job title
- `description` (required if no file): Job description text

**JSON Parameters:**
```json
{
  "title": "Senior Software Engineer",
  "description": "We are looking for an experienced software engineer...",
  "requirements": "5+ years experience, Python, React",
  "skills": "Python, React, AWS, Docker"
}
```

**Response:**
```json
{
  "success": true,
  "job_id": 456,
  "parsed_data": {
    "title": "Senior Software Engineer",
    "description": "Detailed job description...",
    "skills": ["Python", "React", "AWS"],
    "requirements": ["5+ years experience", "Bachelor's degree"]
  }
}
```

### Get Jobs
Retrieve all job descriptions.

**Endpoint:** `GET /jobs`

**Response:**
```json
{
  "success": true,
  "jobs": [
    {
      "id": 1,
      "title": "Senior Software Engineer",
      "description": "Job description...",
      "skills": ["Python", "React"],
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Update Job
Update job description details.

**Endpoint:** `PUT /jobs/{job_id}`

**Request Body:**
```json
{
  "title": "Updated Job Title",
  "description": "Updated description",
  "requirements": "Updated requirements",
  "skills": "Python, React, Node.js"
}
```

### Delete Job
Remove job description and related data.

**Endpoint:** `DELETE /jobs/{job_id}`

---

## 📅 **Interview Scheduling**

### Create Time Slots
Generate available interview time slots.

**Endpoint:** `POST /schedule/slots`

**Request Body:**
```json
{
  "start_date": "2024-01-20T09:00:00",
  "end_date": "2024-01-25T17:00:00",
  "interviewer_name": "Jane Smith"
}
```

### Get Available Slots
Retrieve available interview slots.

**Endpoint:** `GET /schedule/slots`

**Query Parameters:**
- `interviewer_name` (optional): Filter by interviewer

**Response:**
```json
{
  "success": true,
  "slots": [
    {
      "id": 1,
      "start_time": "2024-01-20T10:00:00",
      "interviewer_name": "Jane Smith",
      "is_booked": false
    }
  ]
}
```

### Schedule Interview
Book an interview slot.

**Endpoint:** `POST /schedule`

**Request Body:**
```json
{
  "candidate_id": 1,
  "job_id": 1,
  "slot_id": 5,
  "interviewer_name": "Jane Smith",
  "meeting_link": "https://zoom.us/j/123456789"
}
```

**Response:**
```json
{
  "success": true,
  "interview_id": 789,
  "scheduled_time": "2024-01-20T10:00:00",
  "interviewer": "Jane Smith",
  "meeting_link": "https://zoom.us/j/123456789"
}
```

### Update Interview
Reschedule or modify interview details.

**Endpoint:** `PUT /schedule/{interview_id}`

**Request Body:**
```json
{
  "new_slot_id": 6,
  "interviewer_name": "John Doe",
  "meeting_link": "https://meet.google.com/abc-def-ghi"
}
```

### Cancel Interview
Cancel a scheduled interview.

**Endpoint:** `DELETE /schedule/{interview_id}`

**Response:**
```json
{
  "success": true,
  "interview_id": 789,
  "freed_slot": "2024-01-20T10:00:00"
}
```

### Get Interview Schedule
Retrieve interview schedule with filtering.

**Endpoint:** `GET /schedule`

**Query Parameters:**
- `interviewer_name` (optional): Filter by interviewer
- `date` (optional): Filter by specific date (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "schedule": [
    {
      "id": 1,
      "candidate_name": "John Doe",
      "job_title": "Senior Software Engineer",
      "scheduled_time": "2024-01-20T10:00:00",
      "interviewer_name": "Jane Smith",
      "meeting_link": "https://zoom.us/j/123456789",
      "status": "scheduled"
    }
  ]
}
```

---

## 💬 **Communication**

### Send Message
Send automated message to candidate.

**Endpoint:** `POST /send-message`

**Request Body:**
```json
{
  "candidate_id": 1,
  "job_id": 1,
  "message_type": "interview_invitation",
  "additional_context": {
    "interview_date": "2024-01-20T10:00:00",
    "interviewer_name": "Jane Smith"
  }
}
```

**Message Types:**
- `interview_invitation`
- `application_received`
- `follow_up`
- `rejection`
- `custom`

**Response:**
```json
{
  "success": true,
  "message_id": 123,
  "message_sent": true,
  "preview": "Dear John, We are pleased to invite you..."
}
```

### Send Bulk Messages
Send messages to multiple candidates.

**Endpoint:** `POST /message/bulk`

**Request Body:**
```json
{
  "candidate_ids": [1, 2, 3],
  "job_id": 1,
  "message_type": "application_received",
  "additional_context": {}
}
```

### Get Message Templates
Retrieve available message templates.

**Endpoint:** `GET /message/templates`

**Response:**
```json
{
  "success": true,
  "templates": [
    {
      "type": "interview_invitation",
      "name": "Interview Invitation",
      "description": "Invite candidate for interview"
    }
  ]
}
```

### Get Message History
Retrieve message history for a candidate.

**Endpoint:** `GET /message/history/{candidate_id}`

---

## 📊 **Analytics & Insights**

### Hiring Funnel Metrics
Get comprehensive hiring pipeline analytics.

**Endpoint:** `GET /analytics/funnel`

**Query Parameters:**
- `days` (optional): Time period in days (default: 30)

**Response:**
```json
{
  "success": true,
  "metrics": {
    "period_days": 30,
    "funnel_metrics": {
      "total_candidates": 150,
      "scored_candidates": 120,
      "interviewed_candidates": 45,
      "completed_interviews": 30,
      "scoring_rate": 80.0,
      "interview_rate": 30.0,
      "completion_rate": 66.7
    },
    "timing_metrics": {
      "avg_time_to_interview_days": 5.2,
      "avg_time_to_hire_days": 7.8
    },
    "score_distribution": {
      "mean_score": 72.5,
      "median_score": 75.0,
      "score_ranges": {
        "excellent": 25,
        "good": 45,
        "average": 35,
        "poor": 15
      }
    }
  }
}
```

### Bias Detection
Analyze potential hiring bias.

**Endpoint:** `GET /analytics/bias`

**Query Parameters:**
- `job_id` (optional): Analyze bias for specific job

**Response:**
```json
{
  "success": true,
  "bias_analysis": {
    "bias_detected": true,
    "bias_types": ["education", "experience"],
    "education_bias": {
      "bias_detected": true,
      "details": ["Score difference of 15.2 points between education levels"],
      "education_scores": {
        "bachelor": 75.2,
        "master": 82.1,
        "phd": 90.4
      }
    },
    "recommendations": [
      "Review scoring criteria for education bias",
      "Implement blind resume screening",
      "Diversify interview panel"
    ]
  }
}
```

### Performance Predictions
Get hiring success predictions for a job.

**Endpoint:** `GET /analytics/predictions/{job_id}`

**Response:**
```json
{
  "success": true,
  "predictions": {
    "prediction_available": true,
    "success_rate": 78.5,
    "optimal_candidate_profile": {
      "score_range": [75, 95],
      "experience_range": [3, 7],
      "education_threshold": 0.7
    },
    "recommendations": {
      "target_score": 85.2,
      "min_experience": 3,
      "education_importance": "high"
    }
  }
}
```

### Real-Time Insights
Get live recruitment insights and alerts.

**Endpoint:** `GET /analytics/insights`

**Response:**
```json
{
  "success": true,
  "insights": {
    "pipeline_status": {
      "total_candidates": 150,
      "high_score_candidates": 25,
      "pending_interviews": 12,
      "today_applications": 5
    },
    "trends": {
      "application_trend": 15.2,
      "trend_direction": "up"
    },
    "market_insights": {
      "top_skills_demand": [
        {"skill": "Python", "count": 45},
        {"skill": "React", "count": 38}
      ],
      "skill_gap_analysis": [
        {"skill": "Machine Learning", "gap_count": 15}
      ]
    },
    "alerts": [
      {
        "type": "success",
        "message": "25 high-scoring candidates available",
        "action": "Prioritize interviews for top candidates"
      }
    ]
  }
}
```

---

## 🧠 **Model Context Protocol (MCP)**

### Score Candidate
Get context-aware candidate scoring.

**Endpoint:** `POST /mcp/score`

**Request Body:**
```json
{
  "candidate_id": 1,
  "job_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "mcp_response": {
    "request_id": "uuid-123",
    "score": 87.5,
    "confidence": 0.92,
    "reasoning": "Strong technical skills match with job requirements...",
    "context_factors": {
      "job_seniority": "senior",
      "industry": "technology",
      "team_size": "large"
    },
    "model_version": "1.0.0"
  }
}
```

### Record Feedback
Provide feedback for continuous learning.

**Endpoint:** `POST /mcp/feedback`

**Query Parameters:**
- `request_id`: MCP request ID
- `actual_outcome`: Actual hiring outcome
- `feedback_score`: Feedback score (0-1)

### Get MCP Statistics
Retrieve model performance statistics.

**Endpoint:** `GET /mcp/stats`

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_requests": 1250,
    "average_confidence": 0.87,
    "accuracy_rate": 0.92,
    "model_version": "1.0.0",
    "last_updated": "2024-01-15T10:30:00"
  }
}
```

---

## 🏥 **System Health**

### Health Check
Check system health and status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "database": "connected",
  "services": {
    "resume_parser": "active",
    "job_matcher": "active",
    "scheduler": "active",
    "messenger": "active"
  }
}
```

### Dashboard Data
Get dashboard overview data.

**Endpoint:** `GET /dashboard`

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_candidates": 150,
    "total_jobs": 25,
    "scheduled_interviews": 12,
    "messages_sent": 89
  },
  "recent_activity": [
    {
      "type": "candidate",
      "title": "John Doe",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

## 🚨 **Error Handling**

### Error Response Format
```json
{
  "success": false,
  "error": "Detailed error message",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "email",
    "message": "Invalid email format"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Request validation failed
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource conflict (e.g., scheduling conflict)
- `INTERNAL_ERROR`: Server internal error
- `RATE_LIMIT`: Rate limit exceeded

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `409`: Conflict
- `422`: Unprocessable Entity
- `500`: Internal Server Error

---

## 📝 **Rate Limiting**

Current rate limits (per minute):
- Resume upload: 10 requests
- Job creation: 20 requests
- Analytics: 100 requests
- General API: 1000 requests

---

## 🔐 **Security Considerations**

### File Upload Security
- Maximum file size: 50MB
- Allowed file types: PDF, TXT, MP4, AVI, MOV, PY, JS, etc.
- Virus scanning recommended in production
- File storage isolation

### Data Privacy
- All candidate data encrypted at rest
- Secure file handling
- GDPR compliance features
- Audit trail logging

---

## 📚 **SDK Examples**

### Python SDK Example
```python
import requests

# Upload resume
files = {'file': open('resume.pdf', 'rb')}
response = requests.post('http://localhost:8000/api/upload-resume', files=files)
candidate_data = response.json()

# Get candidates for job
response = requests.get('http://localhost:8000/api/candidates?job_id=1')
candidates = response.json()['candidates']

# Schedule interview
schedule_data = {
    'candidate_id': 1,
    'job_id': 1,
    'slot_id': 5,
    'interviewer_name': 'Jane Smith'
}
response = requests.post('http://localhost:8000/api/schedule', json=schedule_data)
```

### JavaScript SDK Example
```javascript
// Upload resume with video
const formData = new FormData();
formData.append('file', resumeFile);
formData.append('video_intro', videoFile);

const response = await fetch('/api/upload-resume', {
  method: 'POST',
  body: formData
});

// Get analytics
const analytics = await fetch('/api/analytics/funnel?days=30')
  .then(res => res.json());
```

---

**For more examples and detailed integration guides, see the [Integration Examples](INTEGRATION_EXAMPLES.md) documentation.** 