from typing import Dict, List
import json
from datetime import datetime

class MCPScorer:
    def __init__(self):
        """Initialize MCP (Multi-Criteria Preference) Scorer"""
        # Default weights for scoring criteria
        self.default_weights = {
            'match_score': 0.6,      # RAG matching score weight
            'experience': 0.3,       # Years of experience weight
            'education': 0.1         # Education level weight
        }
        
        # Context-aware weight adjustments based on job type
        self.job_type_weights = {
            'senior': {
                'match_score': 0.5,
                'experience': 0.4,
                'education': 0.1
            },
            'junior': {
                'match_score': 0.7,
                'experience': 0.1,
                'education': 0.2
            },
            'lead': {
                'match_score': 0.4,
                'experience': 0.5,
                'education': 0.1
            },
            'manager': {
                'match_score': 0.3,
                'experience': 0.5,
                'education': 0.2
            },
            'intern': {
                'match_score': 0.8,
                'experience': 0.0,
                'education': 0.2
            }
        }
        
        # Industry-specific weight adjustments
        self.industry_weights = {
            'research': {
                'match_score': 0.4,
                'experience': 0.3,
                'education': 0.3
            },
            'startup': {
                'match_score': 0.7,
                'experience': 0.2,
                'education': 0.1
            },
            'enterprise': {
                'match_score': 0.5,
                'experience': 0.4,
                'education': 0.1
            }
        }
    
    def get_context_weights(self, job_title: str, job_description: str) -> Dict[str, float]:
        """Get context-aware weights based on job characteristics"""
        weights = self.default_weights.copy()
        
        job_title_lower = job_title.lower()
        job_desc_lower = job_description.lower()
        
        # Adjust weights based on seniority level
        for level, level_weights in self.job_type_weights.items():
            if level in job_title_lower:
                weights.update(level_weights)
                break
        
        # Adjust weights based on industry context
        for industry, industry_weights in self.industry_weights.items():
            if industry in job_desc_lower:
                # Blend with existing weights
                for key in weights:
                    weights[key] = (weights[key] + industry_weights.get(key, weights[key])) / 2
                break
        
        # Special adjustments for specific keywords
        if any(keyword in job_desc_lower for keyword in ['phd', 'research', 'academic']):
            weights['education'] = min(weights['education'] + 0.1, 0.4)
            weights['match_score'] = max(weights['match_score'] - 0.05, 0.3)
        
        if any(keyword in job_desc_lower for keyword in ['startup', 'fast-paced', 'agile']):
            weights['match_score'] = min(weights['match_score'] + 0.1, 0.8)
            weights['experience'] = max(weights['experience'] - 0.05, 0.1)
        
        # Ensure weights sum to 1.0
        total_weight = sum(weights.values())
        if total_weight != 1.0:
            for key in weights:
                weights[key] = weights[key] / total_weight
        
        return weights
    
    def normalize_experience_score(self, candidate_experience: int, required_experience: int) -> float:
        """Normalize experience score to 0-100 scale"""
        if required_experience == 0:
            return 100.0
        
        if candidate_experience >= required_experience:
            # Bonus for extra experience, but diminishing returns
            extra_years = candidate_experience - required_experience
            bonus = min(extra_years * 2, 20)  # Max 20% bonus
            return min(100.0 + bonus, 100.0)
        else:
            # Linear penalty for missing experience
            ratio = candidate_experience / required_experience
            return ratio * 100.0
    
    def normalize_education_score(self, education_score: float) -> float:
        """Normalize education score to 0-100 scale"""
        # Education score is already normalized (0.0 to 1.0)
        return education_score * 100.0
    
    def compute_mcp_score(self, candidate_data: Dict, job_data: Dict, 
                         match_score: float) -> Dict:
        """Compute MCP score using context-aware weights"""
        
        # Get context-aware weights
        job_title = job_data.get('title', '')
        job_description = job_data.get('description', '')
        weights = self.get_context_weights(job_title, job_description)
        
        # Extract candidate information
        candidate_experience = candidate_data.get('experience_years', 0)
        candidate_education_score = candidate_data.get('education_score', 0.0)
        
        # Extract job requirements
        required_experience = job_data.get('experience_years', 0)
        
        # Normalize scores
        normalized_match_score = max(0, min(100, match_score))
        normalized_experience_score = self.normalize_experience_score(
            candidate_experience, required_experience
        )
        normalized_education_score = self.normalize_education_score(candidate_education_score)
        
        # Calculate weighted final score
        final_score = (
            normalized_match_score * weights['match_score'] +
            normalized_experience_score * weights['experience'] +
            normalized_education_score * weights['education']
        )
        
        # Apply contextual adjustments
        final_score = self.apply_contextual_adjustments(
            final_score, candidate_data, job_data
        )
        
        return {
            'final_score': round(final_score, 2),
            'component_scores': {
                'match_score': round(normalized_match_score, 2),
                'experience_score': round(normalized_experience_score, 2),
                'education_score': round(normalized_education_score, 2)
            },
            'weights_used': weights,
            'score_breakdown': {
                'match_contribution': round(normalized_match_score * weights['match_score'], 2),
                'experience_contribution': round(normalized_experience_score * weights['experience'], 2),
                'education_contribution': round(normalized_education_score * weights['education'], 2)
            }
        }
    
    def apply_contextual_adjustments(self, base_score: float, candidate_data: Dict, 
                                   job_data: Dict) -> float:
        """Apply contextual adjustments to the base score"""
        adjusted_score = base_score
        
        # Bonus for relevant skills beyond requirements
        candidate_skills = set(skill.lower() for skill in candidate_data.get('skills', []))
        job_skills = set(skill.lower() for skill in job_data.get('skills', []))
        
        if job_skills:
            extra_relevant_skills = len(candidate_skills - job_skills)
            if extra_relevant_skills > 0:
                # Small bonus for additional relevant skills
                skill_bonus = min(extra_relevant_skills * 1, 5)  # Max 5% bonus
                adjusted_score += skill_bonus
        
        # Penalty for significant skill gaps
        if job_skills:
            missing_skills = len(job_skills - candidate_skills)
            skill_gap_ratio = missing_skills / len(job_skills)
            if skill_gap_ratio > 0.5:  # Missing more than 50% of required skills
                penalty = skill_gap_ratio * 10  # Up to 10% penalty
                adjusted_score -= penalty
        
        # Experience level adjustments
        job_title_lower = job_data.get('title', '').lower()
        candidate_experience = candidate_data.get('experience_years', 0)
        
        if 'senior' in job_title_lower and candidate_experience < 5:
            adjusted_score *= 0.9  # 10% penalty for senior roles with low experience
        elif 'lead' in job_title_lower and candidate_experience < 7:
            adjusted_score *= 0.85  # 15% penalty for lead roles with low experience
        elif 'junior' in job_title_lower and candidate_experience > 8:
            adjusted_score *= 1.05  # 5% bonus for overqualified junior candidates
        
        # Education relevance adjustments
        job_desc_lower = job_data.get('description', '').lower()
        candidate_education = candidate_data.get('education_level', '').lower()
        
        if 'computer science' in job_desc_lower or 'software' in job_desc_lower:
            if any(term in candidate_education for term in ['computer', 'software', 'engineering']):
                adjusted_score *= 1.02  # 2% bonus for relevant education
        
        # Ensure score stays within bounds
        return max(0, min(100, adjusted_score))
    
    def get_score_explanation(self, score_data: Dict, candidate_data: Dict, 
                            job_data: Dict) -> Dict:
        """Generate explanation for the MCP score"""
        explanation = {
            'final_score': score_data['final_score'],
            'grade': self.get_score_grade(score_data['final_score']),
            'components': [],
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # Component explanations
        components = score_data['component_scores']
        weights = score_data['weights_used']
        
        explanation['components'] = [
            {
                'name': 'Skills Match',
                'score': components['match_score'],
                'weight': f"{weights['match_score']*100:.0f}%",
                'contribution': score_data['score_breakdown']['match_contribution']
            },
            {
                'name': 'Experience',
                'score': components['experience_score'],
                'weight': f"{weights['experience']*100:.0f}%",
                'contribution': score_data['score_breakdown']['experience_contribution']
            },
            {
                'name': 'Education',
                'score': components['education_score'],
                'weight': f"{weights['education']*100:.0f}%",
                'contribution': score_data['score_breakdown']['education_contribution']
            }
        ]
        
        # Identify strengths and weaknesses
        if components['match_score'] >= 80:
            explanation['strengths'].append("Excellent skills alignment")
        elif components['match_score'] < 50:
            explanation['weaknesses'].append("Significant skills gap")
            explanation['recommendations'].append("Consider skills training or alternative candidates")
        
        if components['experience_score'] >= 90:
            explanation['strengths'].append("Strong experience background")
        elif components['experience_score'] < 60:
            explanation['weaknesses'].append("Limited relevant experience")
            explanation['recommendations'].append("May require mentoring or extended onboarding")
        
        if components['education_score'] >= 80:
            explanation['strengths'].append("Meets education requirements")
        elif components['education_score'] < 60:
            explanation['weaknesses'].append("Education level below preference")
        
        return explanation
    
    def get_score_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        else:
            return "D"
    
    def batch_score_candidates(self, candidates: List[Dict], job_data: Dict, 
                             match_scores: List[float]) -> List[Dict]:
        """Score multiple candidates efficiently"""
        scored_candidates = []
        
        for i, candidate in enumerate(candidates):
            match_score = match_scores[i] if i < len(match_scores) else 0.0
            
            score_data = self.compute_mcp_score(candidate, job_data, match_score)
            explanation = self.get_score_explanation(score_data, candidate, job_data)
            
            scored_candidate = candidate.copy()
            scored_candidate.update({
                'mcp_score': score_data['final_score'],
                'score_data': score_data,
                'score_explanation': explanation
            })
            
            scored_candidates.append(scored_candidate)
        
        # Sort by MCP score
        scored_candidates.sort(key=lambda x: x['mcp_score'], reverse=True)
        
        return scored_candidates
    
    def update_weights_from_feedback(self, job_type: str, feedback_data: Dict):
        """Update weights based on recruiter feedback (for future ML learning)"""
        # This is a placeholder for future machine learning integration
        # where we can learn from recruiter decisions to improve scoring
        pass

# Initialize scorer instance
mcp_scorer = MCPScorer() 