from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from database import db
import numpy as np
from dataclasses import dataclass
from enum import Enum

class MCPMessageType(Enum):
    """MCP Message Types"""
    INITIALIZE = "initialize"
    SCORE_REQUEST = "score_request"
    FEEDBACK = "feedback"
    MODEL_UPDATE = "model_update"
    CONTEXT_UPDATE = "context_update"

@dataclass
class MCPContext:
    """Model Context Protocol Context"""
    job_id: int
    job_type: str
    industry: str
    seniority_level: str
    required_skills: List[str]
    historical_performance: Dict
    market_conditions: Dict

@dataclass
class MCPRequest:
    """MCP Request Structure"""
    message_type: MCPMessageType
    context: MCPContext
    candidate_data: Dict
    timestamp: datetime
    request_id: str

@dataclass
class MCPResponse:
    """MCP Response Structure"""
    request_id: str
    score: float
    confidence: float
    reasoning: List[str]
    context_factors: Dict
    model_version: str
    timestamp: datetime

class ModelContextProtocol:
    """
    Model Context Protocol for continuous model improvement
    and context-aware candidate scoring
    """
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.context_weights = {
            'skills_match': 0.4,
            'experience_relevance': 0.3,
            'cultural_fit': 0.15,
            'growth_potential': 0.15
        }
        self.feedback_history = []
        self.performance_metrics = {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0
        }
    
    def initialize_context(self, job_id: int) -> MCPContext:
        """Initialize context for a specific job"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get job details
        cursor.execute('SELECT * FROM job_descriptions WHERE id = ?', (job_id,))
        job_data = cursor.fetchone()
        
        if not job_data:
            raise ValueError(f"Job {job_id} not found")
        
        # Extract job characteristics
        job_title = job_data[1].lower()
        job_description = job_data[2].lower()
        skills = json.loads(job_data[4]) if job_data[4] else []
        
        # Determine job type and seniority
        job_type = self._classify_job_type(job_title, job_description)
        seniority_level = self._determine_seniority(job_title)
        industry = self._classify_industry(job_description)
        
        # Get historical performance for similar jobs
        cursor.execute('''
            SELECT 
                cs.final_score,
                i.status,
                c.experience_years
            FROM candidate_scores cs
            JOIN candidates c ON cs.candidate_id = c.id
            LEFT JOIN interview_schedules i ON c.id = i.candidate_id
            JOIN job_descriptions j ON cs.job_id = j.id
            WHERE j.title LIKE ? OR j.id = ?
        ''', (f'%{job_type}%', job_id))
        
        historical_data = cursor.fetchall()
        
        # Calculate historical performance metrics
        historical_performance = self._calculate_historical_performance(historical_data)
        
        # Get market conditions (simplified)
        market_conditions = self._get_market_conditions(skills)
        
        conn.close()
        
        return MCPContext(
            job_id=job_id,
            job_type=job_type,
            industry=industry,
            seniority_level=seniority_level,
            required_skills=skills,
            historical_performance=historical_performance,
            market_conditions=market_conditions
        )
    
    def process_score_request(self, request: MCPRequest) -> MCPResponse:
        """Process a scoring request using MCP"""
        
        # Extract candidate and context data
        candidate = request.candidate_data
        context = request.context
        
        # Calculate context-aware scores
        scores = self._calculate_contextual_scores(candidate, context)
        
        # Apply context weights
        weighted_score = self._apply_context_weights(scores, context)
        
        # Calculate confidence based on data quality and historical performance
        confidence = self._calculate_confidence(candidate, context, scores)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(scores, context, candidate)
        
        # Context factors that influenced the score
        context_factors = {
            'job_type_influence': self._get_job_type_influence(context),
            'market_demand': context.market_conditions.get('demand_score', 0.5),
            'historical_success_rate': context.historical_performance.get('success_rate', 0.0),
            'skill_rarity': self._calculate_skill_rarity(candidate.get('skills', []), context.required_skills)
        }
        
        return MCPResponse(
            request_id=request.request_id,
            score=round(weighted_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            context_factors=context_factors,
            model_version=self.model_version,
            timestamp=datetime.now()
        )
    
    def _classify_job_type(self, title: str, description: str) -> str:
        """Classify job type based on title and description"""
        tech_keywords = ['software', 'developer', 'engineer', 'programmer', 'technical']
        management_keywords = ['manager', 'lead', 'director', 'head', 'chief']
        sales_keywords = ['sales', 'business development', 'account', 'revenue']
        design_keywords = ['design', 'ui', 'ux', 'creative', 'visual']
        
        text = f"{title} {description}".lower()
        
        if any(keyword in text for keyword in management_keywords):
            return 'management'
        elif any(keyword in text for keyword in tech_keywords):
            return 'technical'
        elif any(keyword in text for keyword in sales_keywords):
            return 'sales'
        elif any(keyword in text for keyword in design_keywords):
            return 'design'
        else:
            return 'general'
    
    def _determine_seniority(self, title: str) -> str:
        """Determine seniority level from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['senior', 'sr', 'lead', 'principal']):
            return 'senior'
        elif any(word in title_lower for word in ['junior', 'jr', 'entry', 'associate']):
            return 'junior'
        elif any(word in title_lower for word in ['manager', 'director', 'head', 'vp']):
            return 'management'
        else:
            return 'mid'
    
    def _classify_industry(self, description: str) -> str:
        """Classify industry based on job description"""
        fintech_keywords = ['fintech', 'financial', 'banking', 'payment', 'trading']
        healthcare_keywords = ['healthcare', 'medical', 'hospital', 'patient', 'clinical']
        ecommerce_keywords = ['ecommerce', 'retail', 'marketplace', 'shopping', 'commerce']
        
        desc_lower = description.lower()
        
        if any(keyword in desc_lower for keyword in fintech_keywords):
            return 'fintech'
        elif any(keyword in desc_lower for keyword in healthcare_keywords):
            return 'healthcare'
        elif any(keyword in desc_lower for keyword in ecommerce_keywords):
            return 'ecommerce'
        else:
            return 'technology'
    
    def _calculate_historical_performance(self, historical_data: List) -> Dict:
        """Calculate historical performance metrics"""
        if not historical_data:
            return {'success_rate': 0.0, 'avg_score': 0.0, 'sample_size': 0}
        
        total_candidates = len(historical_data)
        successful_interviews = sum(1 for record in historical_data if record[1] == 'completed')
        scores = [record[0] for record in historical_data if record[0] is not None]
        
        return {
            'success_rate': successful_interviews / total_candidates if total_candidates > 0 else 0.0,
            'avg_score': np.mean(scores) if scores else 0.0,
            'sample_size': total_candidates
        }
    
    def _get_market_conditions(self, required_skills: List[str]) -> Dict:
        """Get market conditions for required skills"""
        # Simplified market analysis
        high_demand_skills = ['python', 'react', 'aws', 'kubernetes', 'machine learning', 'ai']
        
        demand_score = 0.0
        if required_skills:
            matching_skills = [skill for skill in required_skills 
                             if any(hd_skill in skill.lower() for hd_skill in high_demand_skills)]
            demand_score = len(matching_skills) / len(required_skills)
        
        return {
            'demand_score': demand_score,
            'market_trend': 'growing' if demand_score > 0.5 else 'stable',
            'competition_level': 'high' if demand_score > 0.7 else 'medium'
        }
    
    def _calculate_contextual_scores(self, candidate: Dict, context: MCPContext) -> Dict:
        """Calculate context-aware scores"""
        scores = {}
        
        # Skills match score with context
        scores['skills_match'] = self._calculate_skills_match_score(
            candidate.get('skills', []), 
            context.required_skills,
            context.market_conditions
        )
        
        # Experience relevance score
        scores['experience_relevance'] = self._calculate_experience_relevance(
            candidate.get('experience_years', 0),
            context.seniority_level,
            context.job_type
        )
        
        # Cultural fit score (simplified)
        scores['cultural_fit'] = self._calculate_cultural_fit(
            candidate,
            context.industry,
            context.job_type
        )
        
        # Growth potential score
        scores['growth_potential'] = self._calculate_growth_potential(
            candidate,
            context.seniority_level,
            context.historical_performance
        )
        
        return scores
    
    def _calculate_skills_match_score(self, candidate_skills: List[str], 
                                    required_skills: List[str], 
                                    market_conditions: Dict) -> float:
        """Calculate skills match with market context"""
        if not required_skills:
            return 100.0
        
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        # Basic match
        matched_skills = [skill for skill in required_skills_lower 
                         if skill in candidate_skills_lower]
        base_score = (len(matched_skills) / len(required_skills)) * 100
        
        # Market demand bonus
        demand_bonus = market_conditions.get('demand_score', 0) * 10
        
        return min(100.0, base_score + demand_bonus)
    
    def _calculate_experience_relevance(self, candidate_experience: int, 
                                      seniority_level: str, job_type: str) -> float:
        """Calculate experience relevance score"""
        # Expected experience by seniority
        expected_experience = {
            'junior': 2,
            'mid': 5,
            'senior': 8,
            'management': 10
        }
        
        expected = expected_experience.get(seniority_level, 5)
        
        if candidate_experience >= expected:
            # Bonus for extra experience, but diminishing returns
            extra_years = candidate_experience - expected
            bonus = min(extra_years * 3, 15)  # Max 15% bonus
            return min(100.0, 100.0 + bonus)
        else:
            # Penalty for insufficient experience
            ratio = candidate_experience / expected
            return ratio * 100
    
    def _calculate_cultural_fit(self, candidate: Dict, industry: str, job_type: str) -> float:
        """Calculate cultural fit score (simplified)"""
        # This is a simplified implementation
        # In practice, this would use more sophisticated analysis
        
        base_score = 75.0  # Default cultural fit
        
        # Education alignment
        education = candidate.get('education_level', '').lower()
        if 'computer' in education or 'engineering' in education:
            if job_type == 'technical':
                base_score += 10
        
        # Experience diversity bonus
        experience_years = candidate.get('experience_years', 0)
        if 3 <= experience_years <= 15:  # Sweet spot for adaptability
            base_score += 5
        
        return min(100.0, base_score)
    
    def _calculate_growth_potential(self, candidate: Dict, seniority_level: str, 
                                  historical_performance: Dict) -> float:
        """Calculate growth potential score"""
        base_score = 70.0
        
        # Age and experience balance
        experience = candidate.get('experience_years', 0)
        
        if seniority_level == 'junior' and experience <= 3:
            base_score += 20  # High growth potential for juniors
        elif seniority_level == 'mid' and 3 <= experience <= 7:
            base_score += 15  # Good growth potential for mid-level
        elif seniority_level == 'senior' and experience >= 5:
            base_score += 10  # Proven track record
        
        # Education factor
        education_score = candidate.get('education_score', 0.5)
        base_score += education_score * 10
        
        return min(100.0, base_score)
    
    def _apply_context_weights(self, scores: Dict, context: MCPContext) -> float:
        """Apply context-specific weights to scores"""
        # Adjust weights based on context
        weights = self.context_weights.copy()
        
        # Adjust weights based on job type
        if context.job_type == 'technical':
            weights['skills_match'] = 0.5
            weights['experience_relevance'] = 0.3
        elif context.job_type == 'management':
            weights['experience_relevance'] = 0.4
            weights['cultural_fit'] = 0.25
        
        # Adjust weights based on seniority
        if context.seniority_level == 'junior':
            weights['growth_potential'] = 0.25
            weights['skills_match'] = 0.35
        elif context.seniority_level == 'senior':
            weights['experience_relevance'] = 0.4
            weights['skills_match'] = 0.35
        
        # Calculate weighted score
        weighted_score = sum(scores[key] * weights[key] for key in scores.keys())
        
        return weighted_score
    
    def _calculate_confidence(self, candidate: Dict, context: MCPContext, scores: Dict) -> float:
        """Calculate confidence in the score"""
        confidence_factors = []
        
        # Data completeness
        required_fields = ['skills', 'experience_years', 'education_level']
        completeness = sum(1 for field in required_fields if candidate.get(field)) / len(required_fields)
        confidence_factors.append(completeness * 0.3)
        
        # Historical data availability
        sample_size = context.historical_performance.get('sample_size', 0)
        historical_confidence = min(sample_size / 20, 1.0) * 0.3  # Max confidence at 20+ samples
        confidence_factors.append(historical_confidence)
        
        # Score consistency
        score_variance = np.var(list(scores.values()))
        consistency = max(0, 1 - (score_variance / 1000)) * 0.2  # Lower variance = higher confidence
        confidence_factors.append(consistency)
        
        # Market data quality
        market_confidence = 0.2  # Fixed for now
        confidence_factors.append(market_confidence)
        
        return sum(confidence_factors) * 100
    
    def _generate_reasoning(self, scores: Dict, context: MCPContext, candidate: Dict) -> List[str]:
        """Generate human-readable reasoning for the score"""
        reasoning = []
        
        # Skills analysis
        skills_score = scores.get('skills_match', 0)
        if skills_score >= 80:
            reasoning.append(f"Strong skills alignment ({skills_score:.1f}%) with {context.job_type} requirements")
        elif skills_score < 50:
            reasoning.append(f"Skills gap identified ({skills_score:.1f}%) - may require training")
        
        # Experience analysis
        exp_score = scores.get('experience_relevance', 0)
        if exp_score >= 90:
            reasoning.append(f"Excellent experience match for {context.seniority_level} level")
        elif exp_score < 60:
            reasoning.append(f"Experience below expectations for {context.seniority_level} role")
        
        # Market context
        if context.market_conditions.get('demand_score', 0) > 0.7:
            reasoning.append("High market demand for candidate's skill set")
        
        # Historical context
        if context.historical_performance.get('success_rate', 0) > 0.8:
            reasoning.append("Similar candidates have shown high success rate in this role")
        
        return reasoning
    
    def _get_job_type_influence(self, context: MCPContext) -> float:
        """Calculate how much job type influenced the scoring"""
        # This would be more sophisticated in practice
        job_type_weights = {
            'technical': 0.8,
            'management': 0.6,
            'sales': 0.7,
            'design': 0.75,
            'general': 0.5
        }
        
        return job_type_weights.get(context.job_type, 0.5)
    
    def _calculate_skill_rarity(self, candidate_skills: List[str], required_skills: List[str]) -> float:
        """Calculate rarity score for candidate skills"""
        # Simplified rarity calculation
        rare_skills = ['machine learning', 'ai', 'blockchain', 'quantum computing']
        
        candidate_rare_skills = [skill for skill in candidate_skills 
                               if any(rare in skill.lower() for rare in rare_skills)]
        
        return len(candidate_rare_skills) / max(len(candidate_skills), 1)
    
    def record_feedback(self, request_id: str, actual_outcome: str, feedback_score: float):
        """Record feedback for continuous learning"""
        feedback = {
            'request_id': request_id,
            'actual_outcome': actual_outcome,
            'feedback_score': feedback_score,
            'timestamp': datetime.now().isoformat()
        }
        
        self.feedback_history.append(feedback)
        
        # Update performance metrics
        self._update_performance_metrics()
    
    def _update_performance_metrics(self):
        """Update model performance metrics based on feedback"""
        if len(self.feedback_history) < 10:
            return  # Need minimum feedback for meaningful metrics
        
        # Calculate accuracy, precision, recall, etc.
        # This is a simplified implementation
        recent_feedback = self.feedback_history[-50:]  # Last 50 feedback items
        
        accurate_predictions = sum(1 for fb in recent_feedback if fb['feedback_score'] >= 0.8)
        self.performance_metrics['accuracy'] = accurate_predictions / len(recent_feedback)
        
        # Update model version if performance improves significantly
        if self.performance_metrics['accuracy'] > 0.85:
            self.model_version = f"1.{len(self.feedback_history) // 100}.0"
    
    def get_model_stats(self) -> Dict:
        """Get current model statistics"""
        return {
            'model_version': self.model_version,
            'performance_metrics': self.performance_metrics,
            'feedback_count': len(self.feedback_history),
            'context_weights': self.context_weights,
            'last_updated': datetime.now().isoformat()
        }

# Initialize MCP instance
mcp = ModelContextProtocol() 