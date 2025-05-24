from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple
import json

class RAGMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the RAG matcher with sentence transformer model"""
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            # Fallback to a smaller model if the main one fails
            self.model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    
    def compute_text_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts"""
        try:
            # Generate embeddings
            embeddings = self.model.encode([text1, text2])
            
            # Compute cosine similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            # Convert to percentage (0-100)
            return float(similarity * 100)
        except Exception as e:
            print(f"Error computing text similarity: {e}")
            return 0.0
    
    def compute_skills_match(self, candidate_skills: List[str], job_skills: List[str]) -> Dict:
        """Compute skills matching between candidate and job requirements"""
        if not candidate_skills or not job_skills:
            return {
                'match_score': 0.0,
                'matched_skills': [],
                'missing_skills': job_skills if job_skills else [],
                'extra_skills': candidate_skills if candidate_skills else []
            }
        
        # Normalize skills to lowercase for comparison
        candidate_skills_lower = [skill.lower().strip() for skill in candidate_skills]
        job_skills_lower = [skill.lower().strip() for skill in job_skills]
        
        matched_skills = []
        missing_skills = []
        
        # Direct matching first
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower().strip()
            if job_skill_lower in candidate_skills_lower:
                matched_skills.append(job_skill)
            else:
                # Try semantic matching for similar skills
                best_match_score = 0.0
                best_match = None
                
                for candidate_skill in candidate_skills:
                    similarity = self.compute_text_similarity(job_skill, candidate_skill)
                    if similarity > best_match_score and similarity > 70:  # 70% threshold
                        best_match_score = similarity
                        best_match = job_skill
                
                if best_match:
                    matched_skills.append(best_match)
                else:
                    missing_skills.append(job_skill)
        
        # Find extra skills that candidate has but job doesn't require
        extra_skills = []
        for candidate_skill in candidate_skills:
            candidate_skill_lower = candidate_skill.lower().strip()
            if candidate_skill_lower not in job_skills_lower:
                # Check if it's semantically similar to any job skill
                is_similar = False
                for job_skill in job_skills:
                    similarity = self.compute_text_similarity(candidate_skill, job_skill)
                    if similarity > 70:
                        is_similar = True
                        break
                
                if not is_similar:
                    extra_skills.append(candidate_skill)
        
        # Calculate match score
        if len(job_skills) > 0:
            match_score = (len(matched_skills) / len(job_skills)) * 100
        else:
            match_score = 100.0  # If no skills required, perfect match
        
        return {
            'match_score': round(match_score, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'extra_skills': extra_skills
        }
    
    def compute_experience_match(self, candidate_experience: int, required_experience: int) -> Dict:
        """Compute experience matching score"""
        if required_experience == 0:
            return {
                'experience_score': 100.0,
                'experience_gap': 0,
                'meets_requirement': True
            }
        
        if candidate_experience >= required_experience:
            # Bonus for extra experience, but cap at 100%
            bonus = min((candidate_experience - required_experience) * 5, 20)
            score = min(100.0 + bonus, 100.0)
            return {
                'experience_score': score,
                'experience_gap': 0,
                'meets_requirement': True
            }
        else:
            # Penalty for lack of experience
            gap = required_experience - candidate_experience
            score = max(0, (candidate_experience / required_experience) * 100)
            return {
                'experience_score': round(score, 2),
                'experience_gap': gap,
                'meets_requirement': False
            }
    
    def compute_education_match(self, candidate_education: str, candidate_education_score: float, 
                               required_education: str) -> Dict:
        """Compute education matching score"""
        education_hierarchy = {
            'high school': 0.1,
            'secondary': 0.1,
            'certificate': 0.2,
            'diploma': 0.4,
            'bachelor': 0.6,
            'bachelors': 0.6,
            'bs': 0.6,
            'ba': 0.6,
            'btech': 0.6,
            'be': 0.6,
            'master': 0.8,
            'masters': 0.8,
            'mba': 0.8,
            'ms': 0.8,
            'ma': 0.8,
            'mtech': 0.8,
            'phd': 1.0,
            'ph.d': 1.0,
            'doctorate': 1.0,
            'doctoral': 1.0
        }
        
        required_score = education_hierarchy.get(required_education.lower(), 0.6)
        
        if candidate_education_score >= required_score:
            score = 100.0
            meets_requirement = True
        else:
            score = (candidate_education_score / required_score) * 100
            meets_requirement = False
        
        return {
            'education_score': round(score, 2),
            'meets_requirement': meets_requirement,
            'education_gap': max(0, required_score - candidate_education_score)
        }
    
    def compute_overall_match(self, candidate_data: Dict, job_data: Dict) -> Dict:
        """Compute overall matching score between candidate and job"""
        # Extract candidate information
        candidate_skills = candidate_data.get('skills', [])
        candidate_experience = candidate_data.get('experience_years', 0)
        candidate_education = candidate_data.get('education_level', '')
        candidate_education_score = candidate_data.get('education_score', 0.0)
        
        # Extract job requirements
        job_skills = job_data.get('skills', [])
        required_experience = job_data.get('experience_years', 0)
        required_education = job_data.get('education_requirement', 'Bachelor')
        
        # Compute individual matches
        skills_match = self.compute_skills_match(candidate_skills, job_skills)
        experience_match = self.compute_experience_match(candidate_experience, required_experience)
        education_match = self.compute_education_match(
            candidate_education, candidate_education_score, required_education
        )
        
        # Compute semantic similarity between resume and job description
        candidate_text = f"{' '.join(candidate_skills)} {candidate_education}"
        job_text = job_data.get('description', '')
        semantic_similarity = self.compute_text_similarity(candidate_text, job_text)
        
        # Weighted final score calculation
        # Skills: 40%, Experience: 30%, Education: 10%, Semantic: 20%
        final_score = (
            skills_match['match_score'] * 0.4 +
            experience_match['experience_score'] * 0.3 +
            education_match['education_score'] * 0.1 +
            semantic_similarity * 0.2
        )
        
        return {
            'final_score': round(final_score, 2),
            'skills_match': skills_match,
            'experience_match': experience_match,
            'education_match': education_match,
            'semantic_similarity': round(semantic_similarity, 2),
            'breakdown': {
                'skills_weight': 40,
                'experience_weight': 30,
                'education_weight': 10,
                'semantic_weight': 20
            }
        }
    
    def rank_candidates(self, candidates: List[Dict], job_data: Dict) -> List[Dict]:
        """Rank candidates based on their match scores with the job"""
        ranked_candidates = []
        
        for candidate in candidates:
            match_result = self.compute_overall_match(candidate, job_data)
            
            candidate_with_score = candidate.copy()
            candidate_with_score.update({
                'match_score': match_result['final_score'],
                'skills_match': match_result['skills_match'],
                'experience_match': match_result['experience_match'],
                'education_match': match_result['education_match'],
                'semantic_similarity': match_result['semantic_similarity'],
                'score_breakdown': match_result['breakdown']
            })
            
            ranked_candidates.append(candidate_with_score)
        
        # Sort by final score in descending order
        ranked_candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        return ranked_candidates
    
    def get_match_insights(self, candidate_data: Dict, job_data: Dict) -> Dict:
        """Get detailed insights about the match"""
        match_result = self.compute_overall_match(candidate_data, job_data)
        
        insights = {
            'overall_score': match_result['final_score'],
            'recommendation': self._get_recommendation(match_result['final_score']),
            'strengths': [],
            'weaknesses': [],
            'suggestions': []
        }
        
        # Analyze strengths and weaknesses
        skills_match = match_result['skills_match']
        experience_match = match_result['experience_match']
        education_match = match_result['education_match']
        
        if skills_match['match_score'] >= 80:
            insights['strengths'].append(f"Strong skills match ({skills_match['match_score']:.1f}%)")
        elif skills_match['match_score'] < 50:
            insights['weaknesses'].append(f"Skills gap ({skills_match['match_score']:.1f}% match)")
            insights['suggestions'].append(f"Consider developing: {', '.join(skills_match['missing_skills'][:3])}")
        
        if experience_match['meets_requirement']:
            insights['strengths'].append("Meets experience requirements")
        else:
            insights['weaknesses'].append(f"Experience gap: {experience_match['experience_gap']} years")
            insights['suggestions'].append("Consider candidates with relevant project experience")
        
        if education_match['meets_requirement']:
            insights['strengths'].append("Meets education requirements")
        else:
            insights['weaknesses'].append("Education level below requirement")
        
        return insights
    
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on match score"""
        if score >= 85:
            return "Highly Recommended - Excellent match"
        elif score >= 70:
            return "Recommended - Good match with minor gaps"
        elif score >= 55:
            return "Consider - Moderate match, may need training"
        elif score >= 40:
            return "Weak Match - Significant gaps present"
        else:
            return "Not Recommended - Poor match"

# Initialize matcher instance
rag_matcher = RAGMatcher() 