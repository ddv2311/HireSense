import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class Database:
    def __init__(self, db_path: str = "hiring_assistant.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Job descriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                requirements TEXT,
                skills TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Candidates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                skills TEXT,
                experience_years INTEGER,
                education_level TEXT,
                education_score REAL,
                resume_path TEXT,
                github_url TEXT,
                video_intro_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Candidate scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidate_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                job_id INTEGER,
                match_score REAL,
                experience_score REAL,
                education_score REAL,
                final_score REAL,
                matched_skills TEXT,
                missing_skills TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id),
                FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
            )
        ''')
        
        # Interview schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                job_id INTEGER,
                scheduled_time TIMESTAMP,
                status TEXT DEFAULT 'scheduled',
                interviewer_name TEXT,
                meeting_link TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id),
                FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                message_type TEXT,
                subject TEXT,
                content TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id)
            )
        ''')
        
        # Available time slots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS available_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_datetime TIMESTAMP,
                is_booked BOOLEAN DEFAULT FALSE,
                interviewer_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def insert_job_description(self, title: str, description: str, requirements: str = "", skills: str = "") -> int:
        """Insert a new job description"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO job_descriptions (title, description, requirements, skills)
            VALUES (?, ?, ?, ?)
        ''', (title, description, requirements, skills))
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id
    
    def insert_candidate(self, candidate_data: Dict) -> int:
        """Insert a new candidate"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO candidates (name, email, phone, skills, experience_years, 
                                  education_level, education_score, resume_path, 
                                  github_url, video_intro_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            candidate_data.get('name', ''),
            candidate_data.get('email', ''),
            candidate_data.get('phone', ''),
            json.dumps(candidate_data.get('skills', [])),
            candidate_data.get('experience_years', 0),
            candidate_data.get('education_level', ''),
            candidate_data.get('education_score', 0.0),
            candidate_data.get('resume_path', ''),
            candidate_data.get('github_url', ''),
            candidate_data.get('video_intro_path', '')
        ))
        candidate_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return candidate_id
    
    def insert_candidate_score(self, score_data: Dict) -> int:
        """Insert candidate score"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO candidate_scores (candidate_id, job_id, match_score, 
                                        experience_score, education_score, final_score,
                                        matched_skills, missing_skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            score_data['candidate_id'],
            score_data['job_id'],
            score_data['match_score'],
            score_data['experience_score'],
            score_data['education_score'],
            score_data['final_score'],
            json.dumps(score_data.get('matched_skills', [])),
            json.dumps(score_data.get('missing_skills', []))
        ))
        score_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return score_id
    
    def get_candidates_with_scores(self, job_id: int) -> List[Dict]:
        """Get all candidates with their scores for a specific job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, cs.match_score, cs.experience_score, cs.education_score, 
                   cs.final_score, cs.matched_skills, cs.missing_skills
            FROM candidates c
            LEFT JOIN candidate_scores cs ON c.id = cs.candidate_id AND cs.job_id = ?
            ORDER BY cs.final_score DESC
        ''', (job_id,))
        
        candidates = []
        for row in cursor.fetchall():
            candidate = {
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
                'created_at': row[11],
                'match_score': row[12],
                'experience_score': row[13],
                'final_score': row[15],
                'matched_skills': json.loads(row[16]) if row[16] else [],
                'missing_skills': json.loads(row[17]) if row[17] else []
            }
            candidates.append(candidate)
        
        conn.close()
        return candidates
    
    def get_job_description(self, job_id: int) -> Optional[Dict]:
        """Get job description by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_descriptions WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'requirements': row[3],
                'skills': row[4],
                'created_at': row[5]
            }
        return None
    
    def get_all_job_descriptions(self) -> List[Dict]:
        """Get all job descriptions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_descriptions ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            jobs.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'requirements': row[3],
                'skills': row[4],
                'created_at': row[5]
            })
        return jobs
    
    def insert_available_slot(self, slot_datetime: str, interviewer_name: str) -> int:
        """Insert available time slot"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO available_slots (slot_datetime, interviewer_name)
            VALUES (?, ?)
        ''', (slot_datetime, interviewer_name))
        slot_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return slot_id
    
    def get_available_slots(self) -> List[Dict]:
        """Get all available time slots"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM available_slots 
            WHERE is_booked = FALSE AND slot_datetime > datetime('now')
            ORDER BY slot_datetime
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        slots = []
        for row in rows:
            slots.append({
                'id': row[0],
                'slot_datetime': row[1],
                'is_booked': row[2],
                'interviewer_name': row[3],
                'created_at': row[4]
            })
        return slots
    
    def schedule_interview(self, candidate_id: int, job_id: int, slot_id: int, 
                          interviewer_name: str, meeting_link: str = "") -> int:
        """Schedule an interview"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get slot datetime
        cursor.execute('SELECT slot_datetime FROM available_slots WHERE id = ?', (slot_id,))
        slot_datetime = cursor.fetchone()[0]
        
        # Insert interview schedule
        cursor.execute('''
            INSERT INTO interview_schedules (candidate_id, job_id, scheduled_time, 
                                           interviewer_name, meeting_link)
            VALUES (?, ?, ?, ?, ?)
        ''', (candidate_id, job_id, slot_datetime, interviewer_name, meeting_link))
        
        # Mark slot as booked
        cursor.execute('UPDATE available_slots SET is_booked = TRUE WHERE id = ?', (slot_id,))
        
        interview_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return interview_id
    
    def insert_message(self, candidate_id: int, message_type: str, subject: str, content: str) -> int:
        """Insert a message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (candidate_id, message_type, subject, content)
            VALUES (?, ?, ?, ?)
        ''', (candidate_id, message_type, subject, content))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id
    
    def get_candidate_by_id(self, candidate_id: int) -> Optional[Dict]:
        """Get candidate by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
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
            }
        return None

    def update_candidate(self, candidate_id: int, candidate_data: Dict) -> bool:
        """Update candidate information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE candidates 
                SET name = ?, email = ?, phone = ?, skills = ?, experience_years = ?, 
                    education_level = ?, education_score = ?, github_url = ?
                WHERE id = ?
            ''', (
                candidate_data.get('name', ''),
                candidate_data.get('email', ''),
                candidate_data.get('phone', ''),
                json.dumps(candidate_data.get('skills', [])),
                candidate_data.get('experience_years', 0),
                candidate_data.get('education_level', ''),
                candidate_data.get('education_score', 0.0),
                candidate_data.get('github_url', ''),
                candidate_id
            ))
            conn.commit()
            success = cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating candidate: {e}")
            success = False
        finally:
            conn.close()
        
        return success

    def delete_candidate(self, candidate_id: int) -> bool:
        """Delete candidate and all related data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete related records first
            cursor.execute('DELETE FROM candidate_scores WHERE candidate_id = ?', (candidate_id,))
            cursor.execute('DELETE FROM interview_schedules WHERE candidate_id = ?', (candidate_id,))
            cursor.execute('DELETE FROM messages WHERE candidate_id = ?', (candidate_id,))
            
            # Delete candidate
            cursor.execute('DELETE FROM candidates WHERE id = ?', (candidate_id,))
            conn.commit()
            success = cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting candidate: {e}")
            success = False
        finally:
            conn.close()
        
        return success

    def update_job_description(self, job_id: int, job_data: Dict) -> bool:
        """Update job description"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE job_descriptions 
                SET title = ?, description = ?, requirements = ?, skills = ?
                WHERE id = ?
            ''', (
                job_data.get('title', ''),
                job_data.get('description', ''),
                job_data.get('requirements', ''),
                job_data.get('skills', ''),
                job_id
            ))
            conn.commit()
            success = cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating job description: {e}")
            success = False
        finally:
            conn.close()
        
        return success

    def delete_job_description(self, job_id: int) -> bool:
        """Delete job description and all related data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete related records first
            cursor.execute('DELETE FROM candidate_scores WHERE job_id = ?', (job_id,))
            cursor.execute('DELETE FROM interview_schedules WHERE job_id = ?', (job_id,))
            
            # Delete job description
            cursor.execute('DELETE FROM job_descriptions WHERE id = ?', (job_id,))
            conn.commit()
            success = cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting job description: {e}")
            success = False
        finally:
            conn.close()
        
        return success

# Initialize database instance
db = Database() 