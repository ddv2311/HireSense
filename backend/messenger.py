import os
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
from datetime import datetime
import requests
from database import db
from config import config

class LLMMessenger:
    def __init__(self):
        """Initialize the LLM Messenger for automated communication"""
        
        # Email configuration from centralized config
        self.email_config = config.get_email_config()
        self.email_enabled = self.email_config['enabled']
        
        if not self.email_enabled:
            print("⚠️  Email credentials not configured. Messages will be logged only.")
            print("   Set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables to enable email sending.")
        
        # Message templates
        self.message_templates = {
            'welcome': {
                'subject': 'Welcome to {company_name} - Application Received',
                'template': '''Dear {candidate_name},

Thank you for your interest in the {job_title} position at {company_name}. We have received your application and are excited to review your qualifications.

Our team will carefully review your resume and experience. If your background aligns with our requirements, we will contact you within the next few days to discuss next steps.

In the meantime, feel free to explore our company culture and values on our website.

Best regards,
{company_name} Hiring Team'''
            },
            'shortlisted': {
                'subject': 'Great News! You\'ve been shortlisted for {job_title}',
                'template': '''Dear {candidate_name},

We are pleased to inform you that you have been shortlisted for the {job_title} position at {company_name}!

After reviewing your application and {relevant_experience}, we are impressed by your background in {key_skills} and believe you could be an excellent fit for our team.

Next Steps:
- Our hiring team will review your profile in detail
- We will contact you within the next 2-3 business days to schedule an interview
- Please keep an eye on your email for further communication

We are excited about the possibility of you joining our team and look forward to learning more about your experience and goals.

Best regards,
{company_name} Hiring Team'''
            },
            'interview_invitation': {
                'subject': 'Interview Invitation - {job_title} Position',
                'template': '''Dear {candidate_name},

We are pleased to invite you for an interview for the {job_title} position at {company_name}.

Based on your {relevant_experience} and skills in {key_skills}, we believe you could be a great fit for our team.

Please reply to this email with your availability for the coming week, and we will schedule a convenient time for both parties.

The interview will cover:
- Your technical background and experience
- Discussion about the role and responsibilities
- Questions about our company and culture
- Opportunity for you to ask questions

We look forward to meeting you!

Best regards,
{company_name} Hiring Team'''
            },
            'interview_confirmation': {
                'subject': 'Interview Confirmed - {job_title} on {interview_time}',
                'template': '''Dear {candidate_name},

Your interview for the {job_title} position has been confirmed.

Interview Details:
- Date & Time: {interview_datetime}
- Interviewer: {interviewer_name}
- Meeting Link: {meeting_link}
- Duration: Approximately 45-60 minutes

Please ensure you:
- Join the meeting 5 minutes early
- Test your audio and video beforehand
- Have your resume and portfolio ready
- Prepare examples of your {key_skills} experience
- Come with questions about the role and company

If you need to reschedule, please contact us at least 24 hours in advance.

Looking forward to our conversation!

Best regards,
{interviewer_name}
{company_name}'''
            },
            'rejection': {
                'subject': 'Application Update - {job_title}',
                'template': '''Dear {candidate_name},

Thank you for your interest in the {job_title} position and for taking the time to apply to {company_name}.

After careful consideration of all applications, we have decided to move forward with other candidates whose experience more closely matches our current requirements.

This decision was not easy, as we received many qualified applications. We were impressed by your background and encourage you to apply for future positions that match your skills and experience.

We will keep your resume on file and may reach out if suitable opportunities arise.

We wish you the best in your job search and future endeavors.

Best regards,
{company_name} Hiring Team'''
            },
            'interview_reminder': {
                'subject': 'Interview Reminder - Tomorrow at {interview_time}',
                'template': '''Dear {candidate_name},

This is a friendly reminder about your interview tomorrow for the {job_title} position at {company_name}.

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
{interviewer_name}
{company_name}'''
            }
        }
        
        # Initialize local LLM (placeholder for actual implementation)
        self.llm_available = self._check_llm_availability()
    
    def _check_llm_availability(self) -> bool:
        """Check if local LLM is available"""
        # Check for free alternatives first
        if config.HUGGINGFACE_API_KEY or self._check_local_ollama() or config.GROQ_API_KEY or config.GEMINI_API_KEY:
            return True
        
        # Check for affordable alternatives
        if config.MISTRAL_API_KEY:
            return True
        
        # Check for OpenAI API key (paid)
        if config.OPENAI_API_KEY:
            return True
        
        # Check for local transformers
        if self._check_local_transformers():
            return True
        
        return False
    
    def _check_local_ollama(self) -> bool:
        """Check if Ollama is running locally"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _check_local_transformers(self) -> bool:
        """Check if local transformers are available"""
        try:
            from transformers import pipeline
            return True
        except ImportError:
            return False
    
    def _generate_with_llm(self, prompt: str, context: Dict) -> str:
        """Generate message using LLM (free alternatives first)"""
        if not self.llm_available:
            return f"Generated message based on: {prompt[:100]}..."
        
        # Try free alternatives first (in order of speed/quality)
        if config.GROQ_API_KEY:
            return self._generate_with_groq(prompt, context)
        
        if config.GEMINI_API_KEY:
            return self._generate_with_gemini(prompt, context)
        
        if self._check_local_ollama():
            return self._generate_with_ollama(prompt, context)
        
        if config.HUGGINGFACE_API_KEY:
            return self._generate_with_huggingface(prompt, context)
        
        if self._check_local_transformers():
            return self._generate_with_local_transformers(prompt, context)
        
        # Try affordable alternatives
        if config.MISTRAL_API_KEY:
            return self._generate_with_mistral(prompt, context)
        
        # Fallback to OpenAI if configured
        if config.OPENAI_API_KEY:
            return self._generate_with_openai(prompt, context)
        
        # Final fallback
        return f"AI-generated message for {context.get('candidate_name', 'candidate')}"
    
    def _generate_with_groq(self, prompt: str, context: Dict) -> str:
        """Generate message using Groq API (Free tier available)"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": [
                    {"role": "system", "content": "You are a professional HR assistant writing personalized messages to job candidates."},
                    {"role": "user", "content": prompt}
                ],
                "model": "mixtral-8x7b-32768",  # Free model
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"⚠️  Groq API error: {response.status_code}")
                return f"Template-based message for {context.get('candidate_name', 'candidate')}"
                
        except ImportError:
            print("⚠️  Requests library required for Groq API")
            return f"Template-based message for {context.get('candidate_name', 'candidate')}"
        except Exception as e:
            print(f"⚠️  Groq API error: {e}")
            return f"Template-based message for {context.get('candidate_name', 'candidate')}"
    
    def _generate_with_ollama(self, prompt: str, context: Dict) -> str:
        """Generate message using local Ollama"""
        try:
            import requests
            
            data = {
                "model": "llama2",  # or "mistral", "codellama"
                "prompt": f"System: You are a professional HR assistant writing personalized messages to job candidates.\n\nUser: {prompt}",
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["response"].strip()
            else:
                print(f"⚠️  Ollama error: {response.status_code}")
                return f"Template-based message for {context.get('candidate_name', 'candidate')}"
                
        except Exception as e:
            print(f"⚠️  Ollama error: {e}")
            return f"Template-based message for {context.get('candidate_name', 'candidate')}"
    
    def _generate_with_huggingface(self, prompt: str, context: Dict) -> str:
        """Generate message using Hugging Face API"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {config.HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Use a free model like microsoft/DialoGPT-medium
            data = {
                "inputs": f"HR Assistant: {prompt}",
                "parameters": {
                    "max_length": 500,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                return f"Template-based message for {context.get('candidate_name', 'candidate')}"
            else:
                print(f"⚠️  Hugging Face API error: {response.status_code}")
                return f"Template-based message for {context.get('candidate_name', 'candidate')}"
                
        except Exception as e:
            print(f"⚠️  Hugging Face API error: {e}")
            return f"Template-based message for {context.get('candidate_name', 'candidate')}"
    
    def _generate_with_local_transformers(self, prompt: str, context: Dict) -> str:
        """Generate message using local transformers"""
        try:
            from transformers import pipeline
            
            # Use a small, free model that can run locally
            if not hasattr(self, '_local_generator'):
                print("🤖 Loading local AI model (first time may take a moment)...")
                self._local_generator = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-small",  # Small, fast model
                    device=-1  # Use CPU
                )
            
            # Generate response
            full_prompt = f"HR Assistant writing to {context.get('candidate_name', 'candidate')}: {prompt}"
            
            result = self._local_generator(
                full_prompt,
                max_length=200,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=50256
            )
            
            generated_text = result[0]["generated_text"]
            # Extract just the generated part
            if full_prompt in generated_text:
                generated_text = generated_text.replace(full_prompt, "").strip()
            
            return generated_text if generated_text else f"Template-based message for {context.get('candidate_name', 'candidate')}"
            
        except ImportError:
            print("⚠️  Transformers library not installed. Install with: pip install transformers torch")
            return f"Template-based message for {context.get('candidate_name', 'candidate')}"
        except Exception as e:
            print(f"⚠️  Local transformers error: {e}")
            return f"Template-based message for {context.get('candidate_name', 'candidate')}"
    
    def _generate_with_openai(self, prompt: str, context: Dict) -> str:
        """Generate message using OpenAI API"""
        try:
            import openai
            openai.api_key = config.OPENAI_API_KEY
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional HR assistant writing personalized messages to job candidates."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except ImportError:
            print("⚠️  OpenAI library not installed. Install with: pip install openai")
            return f"Template-based message for {context.get('candidate_name', 'candidate')}"
        except Exception as e:
            print(f"⚠️  OpenAI API error: {e}")
            return f"Template-based message for {context.get('candidate_name', 'candidate')}"
    
    def _generate_with_gemini(self, prompt: str, context: Dict) -> str:
        """Generate message using Google Gemini API (Free tier available)"""
        try:
            import requests
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"You are a professional HR assistant writing personalized messages to job candidates. {prompt}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500
                }
            }
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={config.GEMINI_API_KEY}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    return content.strip()
                return f"Template-based message for {context.get('candidate_name', 'candidate')}"
            else:
                print(f"⚠️  Gemini API error: {response.status_code}")
                return f"Template-based message for {context.get('candidate_name', 'candidate')}"
                
        except Exception as e:
            print(f"⚠️  Gemini API error: {e}")
            return f"Template-based message for {context.get('candidate_name', 'candidate')}"
    
    def _generate_with_mistral(self, prompt: str, context: Dict) -> str:
        """Generate message using Mistral API (Affordable pricing)"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {config.MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "mistral-tiny",  # Most affordable model
                "messages": [
                    {"role": "system", "content": "You are a professional HR assistant writing personalized messages to job candidates."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"⚠️  Mistral API error: {response.status_code}")
                return f"Template-based message for {context.get('candidate_name', 'candidate')}"
                
        except Exception as e:
            print(f"⚠️  Mistral API error: {e}")
            return f"Template-based message for {context.get('candidate_name', 'candidate')}"
    
    def _send_email(self, to_email: str, subject: str, content: str) -> Dict:
        """Send email using SMTP"""
        if not self.email_enabled:
            print(f"📧 Email would be sent to {to_email}:")
            print(f"   Subject: {subject}")
            print(f"   Content: {content[:100]}...")
            return {
                'success': True,
                'method': 'logged',
                'message': 'Email logged (SMTP not configured)'
            }
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['address']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(content, 'plain'))
            
            # Create SMTP session
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.email_config['server'], self.email_config['port']) as server:
                server.starttls(context=context)
                server.login(self.email_config['address'], self.email_config['password'])
                
                # Send email
                text = msg.as_string()
                server.sendmail(self.email_config['address'], to_email, text)
            
            return {
                'success': True,
                'method': 'smtp',
                'message': f'Email sent successfully to {to_email}'
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'error': 'SMTP authentication failed. Check email credentials.'
            }
        except smtplib.SMTPRecipientsRefused:
            return {
                'success': False,
                'error': f'Recipient email address rejected: {to_email}'
            }
        except smtplib.SMTPServerDisconnected:
            return {
                'success': False,
                'error': 'SMTP server disconnected unexpectedly'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to send email: {str(e)}'
            }
    
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
            'company_name': config.COMPANY_NAME
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
            # Get candidate email
            candidate_data = db.get_candidate_by_id(candidate_id)
            if not candidate_data:
                return {
                    'success': False,
                    'error': 'Candidate not found'
                }
            
            candidate_email = candidate_data.get('email')
            if not candidate_email:
                return {
                    'success': False,
                    'error': 'Candidate email not available'
                }
            
            # Send email
            email_result = self._send_email(candidate_email, subject, content)
            
            # Store message in database regardless of email success
            message_id = db.insert_message(candidate_id, message_type, subject, content)
            
            # Update message status based on email result
            status = 'sent' if email_result['success'] else 'failed'
            
            return {
                'success': True,
                'message_id': message_id,
                'email_sent': email_result['success'],
                'email_method': email_result.get('method', 'unknown'),
                'email_message': email_result.get('message', email_result.get('error', '')),
                'sent_at': datetime.now().isoformat(),
                'status': status
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