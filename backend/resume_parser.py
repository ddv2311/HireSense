import fitz  # PyMuPDF
import re
from typing import Dict, List, Optional
import os

class ResumeParser:
    def __init__(self):
        self.education_levels = {
            'phd': 1.0,
            'ph.d': 1.0,
            'doctorate': 1.0,
            'doctoral': 1.0,
            'masters': 0.8,
            'master': 0.8,
            'mba': 0.8,
            'ms': 0.8,
            'ma': 0.8,
            'mtech': 0.8,
            'bachelors': 0.6,
            'bachelor': 0.6,
            'bs': 0.6,
            'ba': 0.6,
            'btech': 0.6,
            'be': 0.6,
            'diploma': 0.4,
            'certificate': 0.2,
            'high school': 0.1,
            'secondary': 0.1
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF resume"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_name(self, text: str) -> str:
        """Extract candidate name from resume text"""
        lines = text.split('\n')
        # Usually name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 2 and len(line) < 50:
                # Check if it looks like a name (contains letters and possibly spaces)
                if re.match(r'^[A-Za-z\s\.]+$', line) and not any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum', 'phone', 'email', 'address']):
                    return line
        return "Unknown"
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from resume text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from resume text"""
        phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\+?([0-9]{1,3})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})',
            r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})',
            r'\+\d{1,3}\s?\d{3,4}\s?\d{3,4}\s?\d{3,4}'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    return ''.join(matches[0])
                return matches[0]
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        # Common technical skills
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'express',
            'django', 'flask', 'fastapi', 'spring', 'hibernate', 'sql', 'mysql', 'postgresql',
            'mongodb', 'redis', 'elasticsearch', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'git', 'github', 'gitlab', 'jenkins', 'ci/cd', 'devops', 'linux', 'unix', 'bash',
            'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind', 'material-ui', 'figma',
            'photoshop', 'illustrator', 'sketch', 'machine learning', 'deep learning', 'ai',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn',
            'r', 'matlab', 'tableau', 'power bi', 'excel', 'powerpoint', 'word', 'jira', 'confluence',
            'agile', 'scrum', 'kanban', 'project management', 'team leadership', 'communication',
            'problem solving', 'analytical thinking', 'c++', 'c#', '.net', 'php', 'ruby', 'go',
            'rust', 'swift', 'kotlin', 'dart', 'flutter', 'react native', 'ionic', 'xamarin'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from resume text"""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'(\d+)\+?\s*years?\s*experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s*experience',
            r'(\d+)\+?\s*year\s*experience'
        ]
        
        text_lower = text.lower()
        max_years = 0
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    years = int(match)
                    max_years = max(max_years, years)
                except ValueError:
                    continue
        
        # If no explicit experience mentioned, try to infer from work history
        if max_years == 0:
            # Look for date ranges in work experience
            date_patterns = [
                r'(20\d{2})\s*[-–]\s*(20\d{2}|present|current)',
                r'(19\d{2})\s*[-–]\s*(20\d{2}|present|current)',
                r'(20\d{2})\s*to\s*(20\d{2}|present|current)'
            ]
            
            current_year = 2024
            total_experience = 0
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text_lower)
                for start_year, end_year in matches:
                    try:
                        start = int(start_year)
                        if end_year in ['present', 'current']:
                            end = current_year
                        else:
                            end = int(end_year)
                        
                        experience = end - start
                        if experience > 0 and experience < 50:  # Reasonable bounds
                            total_experience += experience
                    except ValueError:
                        continue
            
            max_years = min(total_experience, 40)  # Cap at 40 years
        
        return max_years
    
    def extract_education_level(self, text: str) -> tuple:
        """Extract education level and score from resume text"""
        text_lower = text.lower()
        highest_score = 0.0
        highest_level = "High School"
        
        for level, score in self.education_levels.items():
            if level in text_lower:
                if score > highest_score:
                    highest_score = score
                    highest_level = level.title()
        
        return highest_level, highest_score
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume and extract all relevant information"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        # Check file extension to determine how to extract text
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_extension in ['.txt', '.text']:
            # Handle text files for testing
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Only PDF and TXT files are supported.")
        
        if not text.strip():
            raise ValueError("Could not extract text from file")
        
        name = self.extract_name(text)
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        skills = self.extract_skills(text)
        experience_years = self.extract_experience_years(text)
        education_level, education_score = self.extract_education_level(text)
        
        return {
            'name': name,
            'email': email,
            'phone': phone,
            'skills': skills,
            'experience_years': experience_years,
            'education_level': education_level,
            'education_score': education_score,
            'resume_path': file_path
        }

# Initialize parser instance
resume_parser = ResumeParser() 