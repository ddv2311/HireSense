import fitz  # PyMuPDF
import re
from typing import Dict, List
import os

class JobDescriptionParser:
    def __init__(self):
        self.skill_keywords = [
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
            'rust', 'swift', 'kotlin', 'dart', 'flutter', 'react native', 'ionic', 'xamarin',
            'rest api', 'graphql', 'microservices', 'cloud computing', 'data analysis', 'statistics',
            'business intelligence', 'etl', 'data warehouse', 'big data', 'hadoop', 'spark',
            'kafka', 'rabbitmq', 'nginx', 'apache', 'tomcat', 'websockets', 'oauth', 'jwt',
            'testing', 'unit testing', 'integration testing', 'automation testing', 'selenium',
            'cypress', 'jest', 'mocha', 'pytest', 'junit', 'tdd', 'bdd', 'design patterns'
        ]
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF job description"""
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
    
    def extract_title(self, text: str) -> str:
        """Extract job title from job description"""
        lines = text.split('\n')
        
        # Look for common job title patterns
        title_patterns = [
            r'job title\s*:?\s*(.+)',
            r'position\s*:?\s*(.+)',
            r'role\s*:?\s*(.+)',
            r'we are looking for\s+(?:a|an)\s+(.+)',
            r'hiring\s+(?:a|an)\s+(.+)'
        ]
        
        text_lower = text.lower()
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                title = matches[0].strip()
                # Clean up the title
                title = re.sub(r'\s+', ' ', title)
                if len(title) < 100:  # Reasonable title length
                    return title.title()
        
        # If no pattern matches, try to find it in the first few lines
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 5 and len(line) < 100:
                # Check if it looks like a job title
                job_keywords = ['developer', 'engineer', 'manager', 'analyst', 'specialist', 
                               'coordinator', 'lead', 'senior', 'junior', 'intern', 'consultant']
                if any(keyword in line.lower() for keyword in job_keywords):
                    return line
        
        return "Software Developer"  # Default title
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract required skills from job description"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        # Look for skills in specific sections
        skills_sections = [
            r'required skills?\s*:?\s*(.+?)(?:\n\n|\n[A-Z])',
            r'technical skills?\s*:?\s*(.+?)(?:\n\n|\n[A-Z])',
            r'qualifications?\s*:?\s*(.+?)(?:\n\n|\n[A-Z])',
            r'requirements?\s*:?\s*(.+?)(?:\n\n|\n[A-Z])',
            r'must have\s*:?\s*(.+?)(?:\n\n|\n[A-Z])',
            r'technologies?\s*:?\s*(.+?)(?:\n\n|\n[A-Z])'
        ]
        
        for pattern in skills_sections:
            matches = re.findall(pattern, text_lower, re.DOTALL)
            for match in matches:
                # Extract skills from bullet points or comma-separated lists
                skill_items = re.split(r'[,\n•\-\*]', match)
                for item in skill_items:
                    item = item.strip()
                    if len(item) > 2 and len(item) < 50:
                        # Check if it's a known skill
                        for skill in self.skill_keywords:
                            if skill.lower() in item.lower():
                                found_skills.append(skill.title())
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def extract_experience_requirements(self, text: str) -> int:
        """Extract required years of experience"""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'(\d+)\+?\s*years?\s*experience',
            r'minimum\s*(\d+)\+?\s*years?',
            r'at least\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s*experience'
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
        
        return max_years
    
    def extract_education_requirements(self, text: str) -> str:
        """Extract education requirements"""
        education_patterns = [
            r'(phd|ph\.d|doctorate|doctoral)',
            r'(masters?|master\'s|mba|ms|ma|mtech)',
            r'(bachelors?|bachelor\'s|bs|ba|btech|be)',
            r'(diploma|certificate)',
            r'(high school|secondary)'
        ]
        
        text_lower = text.lower()
        
        for pattern in education_patterns:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower).group(1)
                return match.title()
        
        return "Bachelor's"  # Default requirement
    
    def extract_requirements(self, text: str) -> List[str]:
        """Extract general requirements from job description"""
        requirements = []
        
        # Look for requirements sections
        req_patterns = [
            r'requirements?\s*:?\s*(.+?)(?:\n\n|\n[A-Z])',
            r'qualifications?\s*:?\s*(.+?)(?:\n\n|\n[A-Z])',
            r'must have\s*:?\s*(.+?)(?:\n\n|\n[A-Z])',
            r'essential\s*:?\s*(.+?)(?:\n\n|\n[A-Z])',
            r'mandatory\s*:?\s*(.+?)(?:\n\n|\n[A-Z])'
        ]
        
        text_lower = text.lower()
        
        for pattern in req_patterns:
            matches = re.findall(pattern, text_lower, re.DOTALL)
            for match in matches:
                # Split by bullet points or new lines
                req_items = re.split(r'[•\-\*\n]', match)
                for item in req_items:
                    item = item.strip()
                    if len(item) > 10 and len(item) < 200:
                        requirements.append(item.capitalize())
        
        return requirements[:10]  # Limit to top 10 requirements
    
    def parse_job_description(self, text: str = None, pdf_path: str = None) -> Dict:
        """Parse job description and extract all relevant information"""
        if pdf_path:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"Job description file not found: {pdf_path}")
            text = self.extract_text_from_pdf(pdf_path)
        
        if not text or not text.strip():
            raise ValueError("No text provided or could not extract text from PDF")
        
        title = self.extract_title(text)
        skills = self.extract_skills(text)
        experience_years = self.extract_experience_requirements(text)
        education_requirement = self.extract_education_requirements(text)
        requirements = self.extract_requirements(text)
        
        return {
            'title': title,
            'description': text,
            'skills': skills,
            'experience_years': experience_years,
            'education_requirement': education_requirement,
            'requirements': requirements
        }

# Initialize parser instance
jd_parser = JobDescriptionParser() 