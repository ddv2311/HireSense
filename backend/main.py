from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import shutil
from datetime import datetime, timedelta
import json

# Import our modules
from database import db
from resume_parser import resume_parser
from jd_parser import jd_parser
from matcher import rag_matcher
from scorer import mcp_scorer
from scheduler import interview_scheduler
from messenger import llm_messenger
from analytics import recruitment_analytics
from mcp_protocol import mcp, MCPRequest, MCPMessageType
from video_analyzer import video_analyzer
from code_analyzer import code_analyzer
import uuid
from config import config

# Create FastAPI app
app = FastAPI(
    title="Agentic AI Hiring Assistant",
    description="AI-powered hiring system with RAG matching, MCP scoring, and automated communication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router
api_router = APIRouter(prefix="/api")

# Create upload directories
os.makedirs("uploads/resumes", exist_ok=True)
os.makedirs("uploads/job_descriptions", exist_ok=True)
os.makedirs("uploads/videos", exist_ok=True)
os.makedirs("uploads/code_samples", exist_ok=True)

# Pydantic models
class JobDescriptionCreate(BaseModel):
    title: str
    description: str
    requirements: Optional[str] = ""
    skills: Optional[str] = ""

class ScheduleRequest(BaseModel):
    candidate_id: int
    job_id: int
    slot_id: int
    interviewer_name: str
    meeting_link: Optional[str] = ""

class MessageRequest(BaseModel):
    candidate_id: int
    job_id: int
    message_type: str
    additional_context: Optional[Dict] = None

class BulkMessageRequest(BaseModel):
    candidate_ids: List[int]
    job_id: int
    message_type: str
    additional_context: Optional[Dict] = None

class TimeSlotCreate(BaseModel):
    start_date: str
    end_date: str
    interviewer_name: str

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Agentic AI Hiring Assistant API",
        "version": "1.0.0",
        "status": "active"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "services": {
            "resume_parser": "active",
            "job_matcher": "active",
            "scheduler": "active",
            "messenger": "active"
        }
    }

# Job Description endpoints
@api_router.post("/upload-jd")
async def upload_job_description(
    file: Optional[UploadFile] = File(None),
    title: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Upload job description (PDF file or text input)"""
    try:
        if file and file.filename.endswith('.pdf'):
            # Save uploaded file
            file_path = f"uploads/job_descriptions/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Parse PDF job description
            jd_data = jd_parser.parse_job_description(pdf_path=file_path)
        elif description:
            # Parse text job description
            jd_data = jd_parser.parse_job_description(text=description)
            jd_data['title'] = title
        else:
            raise HTTPException(status_code=400, detail="Either PDF file or description text is required")
        
        # Store in database
        job_id = db.insert_job_description(
            title=jd_data['title'],
            description=jd_data['description'],
            requirements=json.dumps(jd_data.get('requirements', [])),
            skills=json.dumps(jd_data['skills'])
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "parsed_data": jd_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing job description: {str(e)}")

@api_router.get("/jobs")
async def get_all_jobs():
    """Get all job descriptions"""
    try:
        jobs = db.get_all_job_descriptions()
        return {
            "success": True,
            "jobs": jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

@api_router.get("/jobs/{job_id}")
async def get_job_description(job_id: int):
    """Get specific job description"""
    try:
        job = db.get_job_description(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "success": True,
            "job": job
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job: {str(e)}")

# Resume upload and candidate management
@api_router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    github_url: Optional[str] = Form(None),
    video_intro: Optional[UploadFile] = File(None),
    coding_sample: Optional[UploadFile] = File(None)
):
    """Upload and parse resume with optional GitHub, video intro, and coding sample"""
    try:
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.pdf', '.txt', '.text']:
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads/resumes", exist_ok=True)
        
        # Save resume file
        resume_path = f"uploads/resumes/{file.filename}"
        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse resume
        candidate_data = resume_parser.parse_resume(resume_path)
        
        # Handle video intro if provided
        video_analysis = None
        video_path = None
        if video_intro:
            os.makedirs("uploads/videos", exist_ok=True)
            video_path = f"uploads/videos/{video_intro.filename}"
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(video_intro.file, buffer)
            
            # Analyze video introduction
            try:
                video_analysis = video_analyzer.analyze_video_introduction(video_path)
                candidate_data['video_analysis'] = video_analysis
                
                # Add communication score from video analysis
                if 'overall_score' in video_analysis:
                    candidate_data['communication_score'] = video_analysis['overall_score'].get('final_score', 0)
                    
            except Exception as e:
                print(f"Video analysis failed: {e}")
                candidate_data['video_analysis'] = {'error': str(e)}
        
        # Handle coding sample if provided
        code_analysis = None
        code_path = None
        if coding_sample:
            os.makedirs("uploads/code_samples", exist_ok=True)
            code_path = f"uploads/code_samples/{coding_sample.filename}"
            with open(code_path, "wb") as buffer:
                shutil.copyfileobj(coding_sample.file, buffer)
            
            # Analyze coding sample
            try:
                code_analysis = code_analyzer.analyze_code_sample(code_path)
                candidate_data['code_analysis'] = code_analysis
                
                # Add coding skills to candidate skills if detected
                if code_analysis.get('language') and code_analysis['language'] != 'unknown':
                    if 'skills' not in candidate_data:
                        candidate_data['skills'] = []
                    candidate_data['skills'].append(code_analysis['language'])
                
                # Add technical score from code analysis
                if 'overall_score' in code_analysis:
                    candidate_data['technical_score'] = code_analysis['overall_score'].get('final_score', 0)
                    
            except Exception as e:
                print(f"Code analysis failed: {e}")
                candidate_data['code_analysis'] = {'error': str(e)}
        
        # Add additional data
        candidate_data['github_url'] = github_url
        candidate_data['video_intro_path'] = video_path
        candidate_data['coding_sample_path'] = code_path
        
        # Calculate enhanced score including multi-modal data
        enhanced_score = calculate_enhanced_candidate_score(candidate_data)
        candidate_data['enhanced_score'] = enhanced_score
        
        # Store in database
        candidate_id = db.insert_candidate(candidate_data)
        
        return {
            "success": True,
            "candidate_id": candidate_id,
            "parsed_data": candidate_data,
            "multi_modal_analysis": {
                "video_analysis": video_analysis,
                "code_analysis": code_analysis,
                "enhanced_score": enhanced_score
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

# Candidate ranking and matching
@api_router.get("/candidates")
async def get_candidates(job_id: Optional[int] = None):
    """Get ranked candidates for a specific job or all candidates"""
    try:
        if job_id:
            # Get candidates with scores for specific job
            candidates = db.get_candidates_with_scores(job_id)
            job_data = db.get_job_description(job_id)
            
            if not job_data:
                raise HTTPException(status_code=404, detail="Job not found")
            
            # If candidates don't have scores, compute them
            unscored_candidates = [c for c in candidates if c['final_score'] is None]
            
            if unscored_candidates:
                # Compute RAG matching and MCP scores
                for candidate in unscored_candidates:
                    # Compute RAG match
                    match_result = rag_matcher.compute_overall_match(candidate, job_data)
                    
                    # Compute MCP score
                    mcp_result = mcp_scorer.compute_mcp_score(
                        candidate, job_data, match_result['final_score']
                    )
                    
                    # Store scores in database
                    score_data = {
                        'candidate_id': candidate['id'],
                        'job_id': job_id,
                        'match_score': match_result['final_score'],
                        'experience_score': mcp_result['component_scores']['experience_score'],
                        'education_score': mcp_result['component_scores']['education_score'],
                        'final_score': mcp_result['final_score'],
                        'matched_skills': match_result['skills_match']['matched_skills'],
                        'missing_skills': match_result['skills_match']['missing_skills']
                    }
                    
                    db.insert_candidate_score(score_data)
                
                # Refresh candidates list
                candidates = db.get_candidates_with_scores(job_id)
            
            return {
                "success": True,
                "candidates": candidates,
                "job": job_data
            }
        else:
            # Get all candidates without specific job matching
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM candidates ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            
            candidates = []
            for row in rows:
                candidates.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'skills': json.loads(row[4]) if row[4] else [],
                    'experience_years': row[5],
                    'education_level': row[6],
                    'education_score': row[7],
                    'resume_path': row[8],
                    'github_url': row[9],
                    'video_intro_path': row[10],
                    'created_at': row[11]
                })
            
            return {
                "success": True,
                "candidates": candidates
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candidates: {str(e)}")

@api_router.get("/candidate/{candidate_id}")
async def get_candidate_profile(candidate_id: int, job_id: Optional[int] = None):
    """Get detailed candidate profile with optional job matching insights"""
    try:
        candidate = db.get_candidate_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        profile = {
            "candidate": candidate,
            "message_history": llm_messenger.get_message_history(candidate_id)
        }
        
        if job_id:
            job_data = db.get_job_description(job_id)
            if job_data:
                # Get matching insights
                match_insights = rag_matcher.get_match_insights(candidate, job_data)
                profile["match_insights"] = match_insights
                profile["job"] = job_data
        
        return {
            "success": True,
            "profile": profile
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candidate profile: {str(e)}")

# Interview scheduling endpoints
@api_router.post("/schedule/slots")
async def create_time_slots(slot_request: TimeSlotCreate):
    """Create available time slots for interviews"""
    try:
        start_date = datetime.fromisoformat(slot_request.start_date)
        end_date = datetime.fromisoformat(slot_request.end_date)
        
        # Generate slots
        slots = interview_scheduler.generate_available_slots(
            start_date, end_date, slot_request.interviewer_name
        )
        
        # Add to database
        slot_ids = interview_scheduler.add_available_slots(slots)
        
        return {
            "success": True,
            "slots_created": len(slot_ids),
            "slot_ids": slot_ids
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating time slots: {str(e)}")

@api_router.get("/schedule/slots")
async def get_available_slots(interviewer_name: Optional[str] = None):
    """Get available time slots"""
    try:
        slots = interview_scheduler.get_available_slots(interviewer_name)
        return {
            "success": True,
            "slots": slots
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching slots: {str(e)}")

@api_router.post("/schedule")
async def schedule_interview(schedule_request: ScheduleRequest):
    """Schedule an interview"""
    try:
        result = interview_scheduler.schedule_interview(
            schedule_request.candidate_id,
            schedule_request.job_id,
            schedule_request.slot_id,
            schedule_request.interviewer_name,
            schedule_request.meeting_link
        )
        
        if result['success']:
            # Send interview confirmation message
            interview_details = {
                'scheduled_time': result['scheduled_time'],
                'interviewer_name': result['interviewer'],
                'meeting_link': result['meeting_link']
            }
            
            message_result = llm_messenger.create_interview_confirmation_message(
                schedule_request.candidate_id,
                schedule_request.job_id,
                interview_details
            )
            
            result['message_sent'] = message_result['success']
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling interview: {str(e)}")

@api_router.get("/schedule")
async def get_interview_schedule(
    interviewer_name: Optional[str] = None,
    date: Optional[str] = None
):
    """Get interview schedule"""
    try:
        date_obj = datetime.fromisoformat(date) if date else None
        schedule = interview_scheduler.get_interview_schedule(date=date_obj, interviewer_name=interviewer_name)
        
        return {
            "success": True,
            "schedule": schedule
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {str(e)}")

# Messaging endpoints
@api_router.post("/send-message")
async def send_message(message_request: MessageRequest):
    """Generate and send a message to a candidate"""
    try:
        result = llm_messenger.generate_and_send_message(
            message_request.candidate_id,
            message_request.message_type,
            message_request.job_id,
            message_request.additional_context
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@api_router.post("/message/bulk")
async def send_bulk_messages(bulk_request: BulkMessageRequest):
    """Send messages to multiple candidates"""
    try:
        results = llm_messenger.send_bulk_messages(
            bulk_request.candidate_ids,
            bulk_request.message_type,
            bulk_request.job_id,
            bulk_request.additional_context
        )
        
        return {
            "success": True,
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending bulk messages: {str(e)}")

@api_router.get("/message/templates")
async def get_message_templates():
    """Get available message templates"""
    try:
        templates = llm_messenger.get_message_templates()
        return {
            "success": True,
            "templates": templates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")

@api_router.get("/message/history/{candidate_id}")
async def get_message_history(candidate_id: int):
    """Get message history for a candidate"""
    try:
        history = llm_messenger.get_message_history(candidate_id)
        return {
            "success": True,
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching message history: {str(e)}")

# Add missing messages endpoint
@api_router.get("/messages")
async def get_all_messages():
    """Get all messages"""
    try:
        messages = llm_messenger.get_all_messages()
        return {
            "success": True,
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")

# Dashboard and analytics endpoints
@api_router.get("/dashboard")
async def get_dashboard_data():
    """Get dashboard data with insights"""
    try:
        # Get basic statistics
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Count candidates
        cursor.execute('SELECT COUNT(*) FROM candidates')
        total_candidates = cursor.fetchone()[0]
        
        # Count jobs
        cursor.execute('SELECT COUNT(*) FROM job_descriptions')
        total_jobs = cursor.fetchone()[0]
        
        # Count scheduled interviews
        cursor.execute('SELECT COUNT(*) FROM interview_schedules WHERE status = "scheduled"')
        scheduled_interviews = cursor.fetchone()[0]
        
        # Count messages sent
        cursor.execute('SELECT COUNT(*) FROM messages')
        messages_sent = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute('''
            SELECT 'candidate' as type, name as title, created_at 
            FROM candidates 
            UNION ALL
            SELECT 'job' as type, title, created_at 
            FROM job_descriptions 
            ORDER BY created_at DESC LIMIT 10
        ''')
        recent_activity = cursor.fetchall()
        
        conn.close()
        
        return {
            "success": True,
            "statistics": {
                "total_candidates": total_candidates,
                "total_jobs": total_jobs,
                "scheduled_interviews": scheduled_interviews,
                "messages_sent": messages_sent
            },
            "recent_activity": [
                {
                    "type": activity[0],
                    "title": activity[1],
                    "created_at": activity[2]
                }
                for activity in recent_activity
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

# Advanced Analytics endpoints
@api_router.get("/analytics/funnel")
async def get_hiring_funnel_metrics(days: int = 30):
    """Get comprehensive hiring funnel metrics"""
    try:
        metrics = recruitment_analytics.get_hiring_funnel_metrics(days)
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching funnel metrics: {str(e)}")

@api_router.get("/analytics/bias")
async def detect_bias(job_id: Optional[int] = None):
    """Detect potential bias in hiring process"""
    try:
        bias_analysis = recruitment_analytics.detect_bias(job_id)
        return {
            "success": True,
            "bias_analysis": bias_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting bias: {str(e)}")

@api_router.get("/analytics/predictions/{job_id}")
async def get_performance_predictions(job_id: int):
    """Get hiring performance predictions for a job"""
    try:
        predictions = recruitment_analytics.get_performance_predictions(job_id)
        return {
            "success": True,
            "predictions": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")

@api_router.get("/analytics/insights")
async def get_real_time_insights():
    """Get real-time recruitment insights"""
    try:
        insights = recruitment_analytics.get_real_time_insights()
        return {
            "success": True,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching insights: {str(e)}")

# Model Context Protocol endpoints
@api_router.post("/mcp/score")
async def mcp_score_candidate(candidate_id: int, job_id: int):
    """Score candidate using Model Context Protocol"""
    try:
        # Get candidate and job data
        candidate_data = db.get_candidate_by_id(candidate_id)
        if not candidate_data:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Initialize MCP context
        context = mcp.initialize_context(job_id)
        
        # Create MCP request
        request = MCPRequest(
            message_type=MCPMessageType.SCORE_REQUEST,
            context=context,
            candidate_data=candidate_data,
            timestamp=datetime.now(),
            request_id=str(uuid.uuid4())
        )
        
        # Process request
        response = mcp.process_score_request(request)
        
        return {
            "success": True,
            "mcp_response": {
                "request_id": response.request_id,
                "score": response.score,
                "confidence": response.confidence,
                "reasoning": response.reasoning,
                "context_factors": response.context_factors,
                "model_version": response.model_version,
                "timestamp": response.timestamp.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing MCP score: {str(e)}")

@api_router.post("/mcp/feedback")
async def record_mcp_feedback(request_id: str, actual_outcome: str, feedback_score: float):
    """Record feedback for MCP continuous learning"""
    try:
        mcp.record_feedback(request_id, actual_outcome, feedback_score)
        return {
            "success": True,
            "message": "Feedback recorded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")

@api_router.get("/mcp/stats")
async def get_mcp_stats():
    """Get MCP model statistics"""
    try:
        stats = mcp.get_model_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MCP stats: {str(e)}")

# Include the API router
app.include_router(api_router)

# Initialize some sample data on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the application with sample data"""
    print("🚀 Starting Agentic AI Hiring Assistant...")
    config.print_config_status()
    print("📊 Database initialized")
    print("🤖 AI models loaded")
    print("✅ Application ready!")

def calculate_enhanced_candidate_score(candidate_data: Dict) -> Dict:
    """Calculate enhanced candidate score including multi-modal analysis"""
    scores = {
        'resume_score': candidate_data.get('education_score', 0) * 100,  # Convert to 0-100 scale
        'communication_score': candidate_data.get('communication_score', 0),
        'technical_score': candidate_data.get('technical_score', 0),
        'experience_score': min(candidate_data.get('experience_years', 0) * 10, 100)  # Cap at 100
    }
    
    # Calculate weights based on available data
    weights = {
        'resume': 0.4,
        'communication': 0.2 if scores['communication_score'] > 0 else 0,
        'technical': 0.3 if scores['technical_score'] > 0 else 0,
        'experience': 0.1
    }
    
    # Redistribute weights if some components are missing
    total_weight = sum(weights.values())
    if total_weight < 1.0:
        # Redistribute missing weight to resume and experience
        missing_weight = 1.0 - total_weight
        weights['resume'] += missing_weight * 0.7
        weights['experience'] += missing_weight * 0.3
    
    # Calculate final score
    final_score = (
        scores['resume_score'] * weights['resume'] +
        scores['communication_score'] * weights['communication'] +
        scores['technical_score'] * weights['technical'] +
        scores['experience_score'] * weights['experience']
    )
    
    return {
        'final_score': round(final_score, 1),
        'component_scores': scores,
        'weights_used': weights,
        'grade': 'A' if final_score >= 90 else 'B' if final_score >= 80 else 'C' if final_score >= 70 else 'D' if final_score >= 60 else 'F'
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 