from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from database import db

class InterviewScheduler:
    def __init__(self):
        """Initialize the Interview Scheduler with A2A conflict resolution"""
        self.business_hours = {
            'start': 9,  # 9 AM
            'end': 17,   # 5 PM
            'timezone': 'UTC'
        }
        self.interview_duration = 60  # minutes
        self.buffer_time = 15  # minutes between interviews
    
    def generate_available_slots(self, start_date: datetime, end_date: datetime, 
                                interviewer_name: str) -> List[Dict]:
        """Generate available time slots for interviews"""
        slots = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                # Generate slots for business hours
                for hour in range(self.business_hours['start'], self.business_hours['end']):
                    slot_datetime = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
                    
                    # Check if slot is not already booked
                    if not self.is_slot_booked(slot_datetime, interviewer_name):
                        slots.append({
                            'datetime': slot_datetime.isoformat(),
                            'interviewer': interviewer_name,
                            'duration': self.interview_duration,
                            'available': True
                        })
            
            current_date += timedelta(days=1)
        
        return slots
    
    def is_slot_booked(self, slot_datetime: datetime, interviewer_name: str) -> bool:
        """Check if a time slot is already booked"""
        # Check in database for existing bookings
        existing_slots = db.get_available_slots()
        
        for slot in existing_slots:
            slot_dt = datetime.fromisoformat(slot['slot_datetime'])
            if (slot_dt == slot_datetime and 
                slot['interviewer_name'] == interviewer_name and 
                slot['is_booked']):
                return True
        
        return False
    
    def add_available_slots(self, slots: List[Dict]) -> List[int]:
        """Add available time slots to the database"""
        slot_ids = []
        
        for slot in slots:
            slot_id = db.insert_available_slot(
                slot['datetime'],
                slot['interviewer']
            )
            slot_ids.append(slot_id)
        
        return slot_ids
    
    def get_available_slots(self, interviewer_name: str = None, 
                           start_date: datetime = None) -> List[Dict]:
        """Get available time slots with optional filtering"""
        slots = db.get_available_slots()
        
        filtered_slots = []
        for slot in slots:
            # Filter by interviewer if specified
            if interviewer_name and slot['interviewer_name'] != interviewer_name:
                continue
            
            # Filter by start date if specified
            if start_date:
                slot_dt = datetime.fromisoformat(slot['slot_datetime'])
                if slot_dt < start_date:
                    continue
            
            # Transform the slot data to match frontend expectations
            filtered_slot = {
                'id': slot['id'],
                'start_time': slot['slot_datetime'],  # Frontend expects 'start_time'
                'interviewer_name': slot['interviewer_name'],
                'is_booked': slot['is_booked'],
                'created_at': slot.get('created_at', '')
            }
            filtered_slots.append(filtered_slot)
        
        return filtered_slots
    
    def check_conflicts(self, requested_datetime: datetime, 
                       interviewer_name: str, candidate_id: int) -> Dict:
        """Check for scheduling conflicts using A2A logic"""
        conflicts = {
            'has_conflicts': False,
            'conflict_types': [],
            'alternative_suggestions': []
        }
        
        # Check interviewer availability
        if self.is_slot_booked(requested_datetime, interviewer_name):
            conflicts['has_conflicts'] = True
            conflicts['conflict_types'].append('interviewer_busy')
        
        # Check if candidate already has an interview scheduled
        candidate_conflicts = self.get_candidate_conflicts(candidate_id, requested_datetime)
        if candidate_conflicts:
            conflicts['has_conflicts'] = True
            conflicts['conflict_types'].append('candidate_busy')
        
        # Check business hours
        if not self.is_business_hours(requested_datetime):
            conflicts['has_conflicts'] = True
            conflicts['conflict_types'].append('outside_business_hours')
        
        # Generate alternative suggestions if conflicts exist
        if conflicts['has_conflicts']:
            conflicts['alternative_suggestions'] = self.suggest_alternatives(
                requested_datetime, interviewer_name, candidate_id
            )
        
        return conflicts
    
    def get_candidate_conflicts(self, candidate_id: int, 
                               requested_datetime: datetime) -> List[Dict]:
        """Check if candidate has conflicting interviews"""
        # This would typically check an external calendar or database
        # For now, we'll implement a simple check
        
        # Get existing interviews for the candidate
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM interview_schedules 
            WHERE candidate_id = ? AND status = 'scheduled'
        ''', (candidate_id,))
        
        existing_interviews = cursor.fetchall()
        conn.close()
        
        conflicts = []
        for interview in existing_interviews:
            interview_dt = datetime.fromisoformat(interview[3])  # scheduled_time
            
            # Check if interviews overlap (considering duration + buffer)
            time_diff = abs((interview_dt - requested_datetime).total_seconds() / 60)
            if time_diff < (self.interview_duration + self.buffer_time):
                conflicts.append({
                    'interview_id': interview[0],
                    'scheduled_time': interview[3],
                    'interviewer': interview[5]
                })
        
        return conflicts
    
    def is_business_hours(self, dt: datetime) -> bool:
        """Check if datetime falls within business hours"""
        # Check if it's a weekday
        if dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check if it's within business hours
        hour = dt.hour
        return self.business_hours['start'] <= hour < self.business_hours['end']
    
    def suggest_alternatives(self, requested_datetime: datetime, 
                           interviewer_name: str, candidate_id: int, 
                           num_suggestions: int = 5) -> List[Dict]:
        """Suggest alternative time slots using A2A conflict resolution"""
        suggestions = []
        
        # Get available slots around the requested time
        search_start = requested_datetime - timedelta(days=3)
        search_end = requested_datetime + timedelta(days=7)
        
        available_slots = self.get_available_slots(interviewer_name, search_start)
        
        for slot in available_slots:
            slot_dt = datetime.fromisoformat(slot['slot_datetime'])
            
            # Skip if outside search range
            if slot_dt < search_start or slot_dt > search_end:
                continue
            
            # Check if this slot has no conflicts
            conflicts = self.check_conflicts(slot_dt, interviewer_name, candidate_id)
            if not conflicts['has_conflicts']:
                # Calculate preference score based on proximity to requested time
                time_diff = abs((slot_dt - requested_datetime).total_seconds() / 3600)  # hours
                preference_score = max(0, 100 - (time_diff * 5))  # Decrease by 5 points per hour
                
                suggestions.append({
                    'slot_id': slot['id'],
                    'datetime': slot['slot_datetime'],
                    'interviewer': slot['interviewer_name'],
                    'preference_score': round(preference_score, 1),
                    'time_difference_hours': round(time_diff, 1)
                })
        
        # Sort by preference score and return top suggestions
        suggestions.sort(key=lambda x: x['preference_score'], reverse=True)
        return suggestions[:num_suggestions]
    
    def schedule_interview(self, candidate_id: int, job_id: int, 
                          slot_id: int, interviewer_name: str, 
                          meeting_link: str = "") -> Dict:
        """Schedule an interview with conflict resolution"""
        
        # Get slot details
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM available_slots WHERE id = ?', (slot_id,))
        slot = cursor.fetchone()
        conn.close()
        
        if not slot:
            return {
                'success': False,
                'error': 'Slot not found',
                'interview_id': None
            }
        
        slot_datetime = datetime.fromisoformat(slot[1])
        
        # Check for conflicts
        conflicts = self.check_conflicts(slot_datetime, interviewer_name, candidate_id)
        
        if conflicts['has_conflicts']:
            return {
                'success': False,
                'error': 'Scheduling conflicts detected',
                'conflicts': conflicts,
                'interview_id': None
            }
        
        # Schedule the interview
        try:
            interview_id = db.schedule_interview(
                candidate_id, job_id, slot_id, interviewer_name, meeting_link
            )
            
            return {
                'success': True,
                'interview_id': interview_id,
                'scheduled_time': slot[1],
                'interviewer': interviewer_name,
                'meeting_link': meeting_link
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}',
                'interview_id': None
            }
    
    def reschedule_interview(self, interview_id: int, new_slot_id: int) -> Dict:
        """Reschedule an existing interview"""
        
        # Get current interview details
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM interview_schedules WHERE id = ?', (interview_id,))
        interview = cursor.fetchone()
        
        if not interview:
            conn.close()
            return {
                'success': False,
                'error': 'Interview not found'
            }
        
        candidate_id = interview[1]
        job_id = interview[2]
        interviewer_name = interview[5]
        
        # Get new slot details
        cursor.execute('SELECT * FROM available_slots WHERE id = ?', (new_slot_id,))
        new_slot = cursor.fetchone()
        
        if not new_slot:
            conn.close()
            return {
                'success': False,
                'error': 'New slot not found'
            }
        
        new_datetime = datetime.fromisoformat(new_slot[1])
        
        # Check for conflicts
        conflicts = self.check_conflicts(new_datetime, interviewer_name, candidate_id)
        
        if conflicts['has_conflicts']:
            conn.close()
            return {
                'success': False,
                'error': 'Conflicts with new time slot',
                'conflicts': conflicts
            }
        
        # Update the interview
        try:
            # Free up the old slot
            old_slot_datetime = interview[3]
            cursor.execute('''
                UPDATE available_slots SET is_booked = FALSE 
                WHERE slot_datetime = ? AND interviewer_name = ?
            ''', (old_slot_datetime, interviewer_name))
            
            # Update interview with new time
            cursor.execute('''
                UPDATE interview_schedules 
                SET scheduled_time = ? 
                WHERE id = ?
            ''', (new_slot[1], interview_id))
            
            # Mark new slot as booked
            cursor.execute('''
                UPDATE available_slots SET is_booked = TRUE 
                WHERE id = ?
            ''', (new_slot_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'interview_id': interview_id,
                'old_time': old_slot_datetime,
                'new_time': new_slot[1]
            }
        
        except Exception as e:
            conn.rollback()
            conn.close()
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def cancel_interview(self, interview_id: int) -> Dict:
        """Cancel an interview and free up the time slot"""
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get interview details
        cursor.execute('SELECT * FROM interview_schedules WHERE id = ?', (interview_id,))
        interview = cursor.fetchone()
        
        if not interview:
            conn.close()
            return {
                'success': False,
                'error': 'Interview not found'
            }
        
        try:
            # Update interview status
            cursor.execute('''
                UPDATE interview_schedules 
                SET status = 'cancelled' 
                WHERE id = ?
            ''', (interview_id,))
            
            # Free up the time slot
            scheduled_time = interview[3]
            interviewer_name = interview[5]
            
            cursor.execute('''
                UPDATE available_slots 
                SET is_booked = FALSE 
                WHERE slot_datetime = ? AND interviewer_name = ?
            ''', (scheduled_time, interviewer_name))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'interview_id': interview_id,
                'freed_slot': scheduled_time
            }
        
        except Exception as e:
            conn.rollback()
            conn.close()
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def get_interview_schedule(self, interviewer_name: str = None, 
                             date: datetime = None) -> List[Dict]:
        """Get interview schedule with optional filtering"""
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Join with candidates and job_descriptions to get names and titles
        query = '''
            SELECT 
                i.id,
                i.candidate_id,
                i.job_id,
                i.scheduled_time,
                i.status,
                i.interviewer_name,
                i.meeting_link,
                i.notes,
                i.created_at,
                c.name as candidate_name,
                j.title as job_title
            FROM interview_schedules i
            LEFT JOIN candidates c ON i.candidate_id = c.id
            LEFT JOIN job_descriptions j ON i.job_id = j.id
            WHERE i.status = "scheduled"
        '''
        params = []
        
        if interviewer_name:
            query += ' AND i.interviewer_name = ?'
            params.append(interviewer_name)
        
        if date:
            date_str = date.date().isoformat()
            query += ' AND DATE(i.scheduled_time) = ?'
            params.append(date_str)
        
        query += ' ORDER BY i.scheduled_time'
        
        cursor.execute(query, params)
        interviews = cursor.fetchall()
        conn.close()
        
        schedule = []
        for interview in interviews:
            schedule.append({
                'id': interview[0],  # Frontend expects 'id' not 'interview_id'
                'candidate_id': interview[1],
                'job_id': interview[2],
                'scheduled_time': interview[3],
                'status': interview[4],
                'interviewer_name': interview[5],
                'meeting_link': interview[6],
                'notes': interview[7],
                'created_at': interview[8],
                'candidate_name': interview[9] or 'Unknown Candidate',
                'job_title': interview[10] or 'Unknown Position'
            })
        
        return schedule

# Initialize scheduler instance
interview_scheduler = InterviewScheduler() 