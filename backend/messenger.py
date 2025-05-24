import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import requests
from database import db

class LLMMessenger:
    def __init__(self):
        """Initialize the LLM Messenger for automated communication"""
        self.message_templates = {
            'shortlisting': {
                'subject': 'Application Update - {job_title}',
                'template': '''Dear {candidate_name},

Thank you for your interest in the {job_title} position at our company. 

After reviewing your application, we are pleased to inform you that you have been shortlisted for the next stage of our hiring process. Your background in {key_skills} aligns well with our requirements.

Next Steps:
- We will be scheduling an interview in the coming days
- You will receive a separate email with available time slots
- Please prepare to discuss your experience with {relevant_experience}

We look forward to speaking with you soon.

Best regards,
Hiring Team'''
            },
            'interview_confirmation': {
                'subject': 'Interview Scheduled - {job_title}',
                'template': '''Dear {candidate_name},

Your interview for the {job_title} position has been scheduled.

Interview Details:
- Date & Time: {interview_datetime}
- Interviewer: {interviewer_name}
- Duration: Approximately 60 minutes
- Meeting Link: {meeting_link}

Please join the meeting 5 minutes early and ensure you have a stable internet connection.

What to Prepare:
- Review your resume and be ready to discuss your experience
- Prepare questions about the role and company
- Have examples ready of your work with {key_skills}

If you need to reschedule, please contact us at least 24 hours in advance.

Best regards,
{interviewer_name}
Hiring Team'''
            },
            'rejection': {
                'subject': 'Application Update - {job_title}',
                'template': '''Dear {candidate_name},

Thank you for your interest in the {job_title} position and for taking the time to apply.

After careful consideration of all applications, we have decided to move forward with other candidates whose experience more closely matches our current requirements.

This decision was not easy, as we received many qualified applications. We encourage you to apply for future positions that match your skills and experience.

We wish you the best in your job search and future endeavors.

Best regards,
Hiring Team'''
            },
            'interview_reminder': {
                'subject': 'Interview Reminder - Tomorrow at {interview_time}',
                'template': '''Dear {candidate_name},

This is a friendly reminder about your interview tomorrow for the {job_title} position.

Interview Details:
- Date & Time: {interview_datetime}
- Interviewer: {interviewer_name}
- Meeting Link: {meeting_link}

Please ensure you:
- Join 5 minutes early
- Test your audio/video beforehand
- Have your resume and questions ready
- Prepare examples of your {key_skills} experience

Looking forward to our conversation!

Best regards,
{interviewer_name}'''
            }
        }
        
        # Initialize local LLM (placeholder for actual implementation)
        self.llm_available = self._check_llm_availability()
    
    def _check_llm_availability(self) -> bool:
        """Check if local LLM is available"""
        # This would check for actual LLM installation
        # For demo purposes, we'll use template-based generation
        return False
    
    def _generate_with_llm(self, prompt: str, context: Dict) -> str:
        """Generate message using local LLM"""
        # Placeholder for actual LLM integration
        # In a real implementation, this would use llama-cpp-python or similar
        
        # For now, return a simple generated message
        return f"Generated message based on: {prompt[:100]}..."
    
    def generate_message(self, message_type: str, candidate_data: Dict, 
                        job_data: Dict, additional_context: Dict = None) -> Dict:
        """Generate personalized message using templates or LLM"""
        
        if message_type not in self.message_templates:
            return {
                'success': False,
                'error': f'Unknown message type: {message_type}'
            }
        
        template_data = self.message_templates[message_type]
        
        # Prepare context for message generation
        context = {
            'candidate_name': candidate_data.get('name', 'Candidate'),
            'job_title': job_data.get('title', 'Position'),
            'key_skills': ', '.join(candidate_data.get('skills', [])[:3]),
            'relevant_experience': f"{candidate_data.get('experience_years', 0)} years of experience",
            'company_name': 'Our Company'
        }
        
        # Add additional context if provided
        if additional_context:
            context.update(additional_context)
        
        # Generate message content
        if self.llm_available and message_type in ['shortlisting', 'rejection']:
            # Use LLM for more personalized messages
            prompt = self._create_llm_prompt(message_type, context, candidate_data, job_data)
            content = self._generate_with_llm(prompt, context)
            subject = template_data['subject'].format(**context)
        else:
            # Use template-based generation
            try:
                subject = template_data['subject'].format(**context)
                content = template_data['template'].format(**context)
            except KeyError as e:
                return {
                    'success': False,
                    'error': f'Missing template variable: {e}'
                }
        
        return {
            'success': True,
            'subject': subject,
            'content': content,
            'message_type': message_type,
            'generated_at': datetime.now().isoformat()
        }
    
    def _create_llm_prompt(self, message_type: str, context: Dict, 
                          candidate_data: Dict, job_data: Dict) -> str:
        """Create prompt for LLM message generation"""
        
        base_prompt = f"""You are an AI recruiter assistant. Write a professional {message_type} email for the following context:

Candidate: {context['candidate_name']}
Position: {context['job_title']}
Candidate Skills: {context['key_skills']}
Experience: {context['relevant_experience']}

Job Requirements: {', '.join(job_data.get('skills', []))}
"""
        
        if message_type == 'shortlisting':
            base_prompt += """
Write a positive, encouraging email informing the candidate they've been shortlisted. 
Highlight their relevant skills and mention next steps.
Keep it professional but warm.
"""
        elif message_type == 'rejection':
            base_prompt += """
Write a polite, respectful rejection email. 
Be encouraging and suggest they apply for future positions.
Keep it brief but empathetic.
"""
        
        return base_prompt
    
    def send_message(self, candidate_id: int, message_type: str, 
                    subject: str, content: str) -> Dict:
        """Send message and store in database"""
        
        try:
            # Store message in database
            message_id = db.insert_message(candidate_id, message_type, subject, content)
            
            # In a real implementation, this would integrate with email service
            # For demo purposes, we'll just log the message
            print(f"Message sent to candidate {candidate_id}:")
            print(f"Subject: {subject}")
            print(f"Content: {content[:100]}...")
            
            return {
                'success': True,
                'message_id': message_id,
                'sent_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to send message: {str(e)}'
            }
    
    def generate_and_send_message(self, candidate_id: int, message_type: str, 
                                 job_id: int, additional_context: Dict = None) -> Dict:
        """Generate and send message in one step"""
        
        # Get candidate and job data
        candidate_data = db.get_candidate_by_id(candidate_id)
        job_data = db.get_job_description(job_id)
        
        if not candidate_data:
            return {
                'success': False,
                'error': 'Candidate not found'
            }
        
        if not job_data:
            return {
                'success': False,
                'error': 'Job description not found'
            }
        
        # Generate message
        message_result = self.generate_message(
            message_type, candidate_data, job_data, additional_context
        )
        
        if not message_result['success']:
            return message_result
        
        # Send message
        send_result = self.send_message(
            candidate_id, 
            message_type,
            message_result['subject'],
            message_result['content']
        )
        
        return {
            'success': send_result['success'],
            'message_id': send_result.get('message_id'),
            'subject': message_result['subject'],
            'content': message_result['content'],
            'error': send_result.get('error')
        }
    
    def send_bulk_messages(self, candidate_ids: List[int], message_type: str, 
                          job_id: int, additional_context: Dict = None) -> List[Dict]:
        """Send messages to multiple candidates"""
        
        results = []
        
        for candidate_id in candidate_ids:
            result = self.generate_and_send_message(
                candidate_id, message_type, job_id, additional_context
            )
            result['candidate_id'] = candidate_id
            results.append(result)
        
        return results
    
    def get_message_history(self, candidate_id: int) -> List[Dict]:
        """Get message history for a candidate"""
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM messages 
            WHERE candidate_id = ? 
            ORDER BY sent_at DESC
        ''', (candidate_id,))
        
        messages = cursor.fetchall()
        conn.close()
        
        message_history = []
        for message in messages:
            message_history.append({
                'message_id': message[0],
                'candidate_id': message[1],
                'message_type': message[2],
                'subject': message[3],
                'content': message[4],
                'sent_at': message[5]
            })
        
        return message_history
    
    def get_all_messages(self) -> List[Dict]:
        """Get all messages with candidate information"""
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.*, c.name as candidate_name, c.email as candidate_email
            FROM messages m
            LEFT JOIN candidates c ON m.candidate_id = c.id
            ORDER BY m.sent_at DESC
        ''')
        
        messages = cursor.fetchall()
        conn.close()
        
        all_messages = []
        for message in messages:
            all_messages.append({
                'id': message[0],
                'candidate_id': message[1],
                'message_type': message[2],
                'subject': message[3],
                'content': message[4],
                'sent_at': message[5],
                'status': 'sent',  # Default status
                'candidate_name': message[6] if len(message) > 6 else 'Unknown',
                'candidate_email': message[7] if len(message) > 7 else 'Unknown'
            })
        
        return all_messages
    
    def create_interview_confirmation_message(self, candidate_id: int, job_id: int, 
                                            interview_details: Dict) -> Dict:
        """Create interview confirmation message with specific details"""
        
        additional_context = {
            'interview_datetime': interview_details.get('scheduled_time', ''),
            'interviewer_name': interview_details.get('interviewer_name', ''),
            'meeting_link': interview_details.get('meeting_link', 'Will be provided separately'),
            'interview_time': interview_details.get('scheduled_time', '').split('T')[1][:5] if 'T' in interview_details.get('scheduled_time', '') else ''
        }
        
        return self.generate_and_send_message(
            candidate_id, 'interview_confirmation', job_id, additional_context
        )
    
    def create_interview_reminder(self, candidate_id: int, job_id: int, 
                                interview_details: Dict) -> Dict:
        """Create interview reminder message"""
        
        additional_context = {
            'interview_datetime': interview_details.get('scheduled_time', ''),
            'interviewer_name': interview_details.get('interviewer_name', ''),
            'meeting_link': interview_details.get('meeting_link', ''),
            'interview_time': interview_details.get('scheduled_time', '').split('T')[1][:5] if 'T' in interview_details.get('scheduled_time', '') else ''
        }
        
        return self.generate_and_send_message(
            candidate_id, 'interview_reminder', job_id, additional_context
        )
    
    def get_message_templates(self) -> Dict:
        """Get all available message templates"""
        return {
            template_type: {
                'subject': template_data['subject'],
                'variables': self._extract_template_variables(template_data['template'])
            }
            for template_type, template_data in self.message_templates.items()
        }
    
    def _extract_template_variables(self, template: str) -> List[str]:
        """Extract variables from template string"""
        import re
        variables = re.findall(r'\{([^}]+)\}', template)
        return list(set(variables))

# Initialize messenger instance
llm_messenger = LLMMessenger() 