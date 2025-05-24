from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
from database import db
import numpy as np
from collections import defaultdict, Counter

class RecruitmentAnalytics:
    def __init__(self):
        """Initialize recruitment analytics engine"""
        self.bias_thresholds = {
            'gender_bias': 0.15,  # 15% difference threshold
            'education_bias': 0.20,  # 20% difference threshold
            'experience_bias': 0.25   # 25% difference threshold
        }
    
    def get_hiring_funnel_metrics(self, days: int = 30) -> Dict:
        """Get comprehensive hiring funnel metrics"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get funnel data
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT c.id) as total_candidates,
                COUNT(DISTINCT cs.candidate_id) as scored_candidates,
                COUNT(DISTINCT i.candidate_id) as interviewed_candidates,
                COUNT(DISTINCT CASE WHEN i.status = 'completed' THEN i.candidate_id END) as completed_interviews
            FROM candidates c
            LEFT JOIN candidate_scores cs ON c.id = cs.candidate_id
            LEFT JOIN interview_schedules i ON c.id = i.candidate_id
            WHERE c.created_at >= ?
        ''', (start_date.isoformat(),))
        
        funnel_data = cursor.fetchone()
        
        # Calculate conversion rates
        total_candidates = funnel_data[0] or 1  # Avoid division by zero
        scored_candidates = funnel_data[1] or 0
        interviewed_candidates = funnel_data[2] or 0
        completed_interviews = funnel_data[3] or 0
        
        # Get average time to hire
        cursor.execute('''
            SELECT AVG(
                JULIANDAY(i.scheduled_time) - JULIANDAY(c.created_at)
            ) as avg_time_to_interview
            FROM candidates c
            JOIN interview_schedules i ON c.id = i.candidate_id
            WHERE c.created_at >= ? AND i.status = 'completed'
        ''', (start_date.isoformat(),))
        
        avg_time_result = cursor.fetchone()
        avg_time_to_interview = avg_time_result[0] if avg_time_result[0] else 0
        
        # Get score distribution
        cursor.execute('''
            SELECT final_score
            FROM candidate_scores cs
            JOIN candidates c ON cs.candidate_id = c.id
            WHERE c.created_at >= ?
        ''', (start_date.isoformat(),))
        
        scores = [row[0] for row in cursor.fetchall() if row[0] is not None]
        
        conn.close()
        
        return {
            'period_days': days,
            'funnel_metrics': {
                'total_candidates': total_candidates,
                'scored_candidates': scored_candidates,
                'interviewed_candidates': interviewed_candidates,
                'completed_interviews': completed_interviews,
                'scoring_rate': round((scored_candidates / total_candidates) * 100, 2),
                'interview_rate': round((interviewed_candidates / total_candidates) * 100, 2),
                'completion_rate': round((completed_interviews / max(interviewed_candidates, 1)) * 100, 2)
            },
            'timing_metrics': {
                'avg_time_to_interview_days': round(avg_time_to_interview, 2),
                'avg_time_to_hire_days': round(avg_time_to_interview * 1.5, 2)  # Estimate
            },
            'score_distribution': {
                'mean_score': round(np.mean(scores), 2) if scores else 0,
                'median_score': round(np.median(scores), 2) if scores else 0,
                'std_score': round(np.std(scores), 2) if scores else 0,
                'score_ranges': self._get_score_ranges(scores)
            }
        }
    
    def _get_score_ranges(self, scores: List[float]) -> Dict:
        """Categorize scores into ranges"""
        if not scores:
            return {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
        
        ranges = {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
        
        for score in scores:
            if score >= 85:
                ranges['excellent'] += 1
            elif score >= 70:
                ranges['good'] += 1
            elif score >= 55:
                ranges['average'] += 1
            else:
                ranges['poor'] += 1
        
        return ranges
    
    def detect_bias(self, job_id: Optional[int] = None) -> Dict:
        """Detect potential bias in hiring process"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Base query
        base_query = '''
            SELECT 
                c.name,
                c.education_level,
                c.experience_years,
                cs.final_score,
                i.status as interview_status
            FROM candidates c
            LEFT JOIN candidate_scores cs ON c.id = cs.candidate_id
            LEFT JOIN interview_schedules i ON c.id = i.candidate_id
        '''
        
        params = []
        if job_id:
            base_query += ' WHERE cs.job_id = ?'
            params.append(job_id)
        
        cursor.execute(base_query, params)
        candidates_data = cursor.fetchall()
        
        conn.close()
        
        if not candidates_data:
            return {'bias_detected': False, 'message': 'Insufficient data for bias analysis'}
        
        # Analyze education bias
        education_bias = self._analyze_education_bias(candidates_data)
        
        # Analyze experience bias
        experience_bias = self._analyze_experience_bias(candidates_data)
        
        # Analyze name bias (basic implementation)
        name_bias = self._analyze_name_bias(candidates_data)
        
        # Overall bias assessment
        bias_flags = []
        if education_bias['bias_detected']:
            bias_flags.append('education')
        if experience_bias['bias_detected']:
            bias_flags.append('experience')
        if name_bias['bias_detected']:
            bias_flags.append('name')
        
        return {
            'bias_detected': len(bias_flags) > 0,
            'bias_types': bias_flags,
            'education_bias': education_bias,
            'experience_bias': experience_bias,
            'name_bias': name_bias,
            'recommendations': self._get_bias_recommendations(bias_flags)
        }
    
    def _analyze_education_bias(self, candidates_data: List) -> Dict:
        """Analyze bias based on education level"""
        education_scores = defaultdict(list)
        education_interviews = defaultdict(int)
        education_counts = defaultdict(int)
        
        for candidate in candidates_data:
            education = candidate[1] or 'Unknown'
            score = candidate[3]
            interview_status = candidate[4]
            
            education_counts[education] += 1
            if score is not None:
                education_scores[education].append(score)
            if interview_status in ['scheduled', 'completed']:
                education_interviews[education] += 1
        
        # Calculate average scores by education
        avg_scores = {}
        interview_rates = {}
        
        for edu, scores in education_scores.items():
            if scores:
                avg_scores[edu] = np.mean(scores)
                interview_rates[edu] = education_interviews[edu] / education_counts[edu]
        
        # Detect bias (significant difference in scores/interview rates)
        bias_detected = False
        bias_details = []
        
        if len(avg_scores) >= 2:
            score_values = list(avg_scores.values())
            max_diff = max(score_values) - min(score_values)
            
            if max_diff > self.bias_thresholds['education_bias'] * 100:
                bias_detected = True
                bias_details.append(f"Score difference of {max_diff:.1f} points between education levels")
        
        return {
            'bias_detected': bias_detected,
            'details': bias_details,
            'education_scores': dict(avg_scores),
            'interview_rates': dict(interview_rates)
        }
    
    def _analyze_experience_bias(self, candidates_data: List) -> Dict:
        """Analyze bias based on experience level"""
        # Group by experience ranges
        exp_ranges = {'0-2': [], '3-5': [], '6-10': [], '10+': []}
        exp_interviews = {'0-2': 0, '3-5': 0, '6-10': 0, '10+': 0}
        exp_counts = {'0-2': 0, '3-5': 0, '6-10': 0, '10+': 0}
        
        for candidate in candidates_data:
            experience = candidate[2] or 0
            score = candidate[3]
            interview_status = candidate[4]
            
            # Categorize experience
            if experience <= 2:
                category = '0-2'
            elif experience <= 5:
                category = '3-5'
            elif experience <= 10:
                category = '6-10'
            else:
                category = '10+'
            
            exp_counts[category] += 1
            if score is not None:
                exp_ranges[category].append(score)
            if interview_status in ['scheduled', 'completed']:
                exp_interviews[category] += 1
        
        # Calculate averages
        avg_scores = {}
        interview_rates = {}
        
        for exp_range, scores in exp_ranges.items():
            if scores:
                avg_scores[exp_range] = np.mean(scores)
                interview_rates[exp_range] = exp_interviews[exp_range] / max(exp_counts[exp_range], 1)
        
        # Detect bias
        bias_detected = False
        bias_details = []
        
        if len(avg_scores) >= 2:
            score_values = list(avg_scores.values())
            max_diff = max(score_values) - min(score_values)
            
            if max_diff > self.bias_thresholds['experience_bias'] * 100:
                bias_detected = True
                bias_details.append(f"Score difference of {max_diff:.1f} points between experience levels")
        
        return {
            'bias_detected': bias_detected,
            'details': bias_details,
            'experience_scores': dict(avg_scores),
            'interview_rates': dict(interview_rates)
        }
    
    def _analyze_name_bias(self, candidates_data: List) -> Dict:
        """Basic name bias analysis (simplified)"""
        # This is a simplified implementation
        # In practice, you'd use more sophisticated name analysis
        
        name_scores = []
        for candidate in candidates_data:
            name = candidate[0] or ''
            score = candidate[3]
            if score is not None:
                name_scores.append((name, score))
        
        # Basic check for unusual patterns
        bias_detected = False
        bias_details = []
        
        if len(name_scores) > 10:
            # Check if names starting with certain letters have significantly different scores
            letter_scores = defaultdict(list)
            for name, score in name_scores:
                if name:
                    letter_scores[name[0].upper()].append(score)
            
            # Simple statistical check
            avg_by_letter = {letter: np.mean(scores) for letter, scores in letter_scores.items() if len(scores) >= 3}
            
            if len(avg_by_letter) >= 3:
                score_values = list(avg_by_letter.values())
                max_diff = max(score_values) - min(score_values)
                
                if max_diff > 20:  # 20 point difference threshold
                    bias_detected = True
                    bias_details.append("Potential name-based scoring patterns detected")
        
        return {
            'bias_detected': bias_detected,
            'details': bias_details,
            'note': 'This is a simplified name bias analysis. Consider using specialized tools for comprehensive bias detection.'
        }
    
    def _get_bias_recommendations(self, bias_types: List[str]) -> List[str]:
        """Get recommendations to mitigate detected bias"""
        recommendations = []
        
        if 'education' in bias_types:
            recommendations.extend([
                "Review education requirements - consider skills-based assessment",
                "Implement blind resume screening for initial rounds",
                "Focus on relevant experience over formal education"
            ])
        
        if 'experience' in bias_types:
            recommendations.extend([
                "Consider potential and trainability alongside experience",
                "Evaluate project quality over years of experience",
                "Implement structured interviews to reduce experience bias"
            ])
        
        if 'name' in bias_types:
            recommendations.extend([
                "Implement anonymous resume screening",
                "Use structured evaluation criteria",
                "Provide bias training for hiring team"
            ])
        
        return recommendations
    
    def get_performance_predictions(self, job_id: int) -> Dict:
        """Predict hiring performance based on historical data"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get historical data for this job or similar jobs
        cursor.execute('''
            SELECT 
                cs.final_score,
                i.status,
                c.experience_years,
                c.education_score
            FROM candidate_scores cs
            JOIN candidates c ON cs.candidate_id = c.id
            LEFT JOIN interview_schedules i ON c.id = i.candidate_id
            WHERE cs.job_id = ? OR cs.job_id IN (
                SELECT id FROM job_descriptions 
                WHERE title LIKE (SELECT '%' || title || '%' FROM job_descriptions WHERE id = ?)
            )
        ''', (job_id, job_id))
        
        historical_data = cursor.fetchall()
        conn.close()
        
        if len(historical_data) < 5:
            return {
                'prediction_available': False,
                'message': 'Insufficient historical data for predictions'
            }
        
        # Analyze success patterns
        successful_candidates = []
        all_candidates = []
        
        for record in historical_data:
            score, status, experience, education = record
            candidate_profile = {
                'score': score or 0,
                'experience': experience or 0,
                'education': education or 0
            }
            
            all_candidates.append(candidate_profile)
            
            if status == 'completed':  # Assuming completed interviews indicate success
                successful_candidates.append(candidate_profile)
        
        # Calculate success patterns
        if successful_candidates:
            success_rate = len(successful_candidates) / len(all_candidates)
            
            avg_successful_score = np.mean([c['score'] for c in successful_candidates])
            avg_successful_experience = np.mean([c['experience'] for c in successful_candidates])
            avg_successful_education = np.mean([c['education'] for c in successful_candidates])
            
            # Optimal candidate profile
            optimal_profile = {
                'score_range': [avg_successful_score - 10, avg_successful_score + 10],
                'experience_range': [max(0, avg_successful_experience - 2), avg_successful_experience + 2],
                'education_threshold': avg_successful_education * 0.8
            }
            
            return {
                'prediction_available': True,
                'success_rate': round(success_rate * 100, 2),
                'optimal_candidate_profile': optimal_profile,
                'recommendations': {
                    'target_score': round(avg_successful_score, 1),
                    'min_experience': max(0, round(avg_successful_experience - 2)),
                    'education_importance': 'high' if avg_successful_education > 0.7 else 'medium'
                },
                'sample_size': len(historical_data)
            }
        
        return {
            'prediction_available': False,
            'message': 'No successful hiring patterns found in historical data'
        }
    
    def get_real_time_insights(self) -> Dict:
        """Get real-time recruitment insights"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Current pipeline status
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT c.id) as total_candidates,
                COUNT(DISTINCT CASE WHEN cs.final_score >= 80 THEN c.id END) as high_score_candidates,
                COUNT(DISTINCT CASE WHEN i.status = 'scheduled' THEN c.id END) as pending_interviews,
                COUNT(DISTINCT CASE WHEN DATE(c.created_at) = DATE('now') THEN c.id END) as today_applications
            FROM candidates c
            LEFT JOIN candidate_scores cs ON c.id = cs.candidate_id
            LEFT JOIN interview_schedules i ON c.id = i.candidate_id
        ''')
        
        pipeline_data = cursor.fetchone()
        
        # Recent trends (last 7 days vs previous 7 days)
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN DATE(created_at) >= DATE('now', '-7 days') THEN 1 END) as recent_applications,
                COUNT(CASE WHEN DATE(created_at) >= DATE('now', '-14 days') AND DATE(created_at) < DATE('now', '-7 days') THEN 1 END) as previous_applications
            FROM candidates
        ''')
        
        trend_data = cursor.fetchone()
        
        # Top skills in demand
        cursor.execute('''
            SELECT skills
            FROM job_descriptions
            WHERE created_at >= DATE('now', '-30 days')
        ''')
        
        job_skills = []
        for row in cursor.fetchall():
            if row[0]:
                skills = json.loads(row[0])
                job_skills.extend(skills)
        
        top_skills = Counter(job_skills).most_common(10)
        
        conn.close()
        
        # Calculate trends
        recent_apps = trend_data[0] or 0
        previous_apps = trend_data[1] or 1
        trend_percentage = ((recent_apps - previous_apps) / previous_apps) * 100
        
        return {
            'pipeline_status': {
                'total_candidates': pipeline_data[0] or 0,
                'high_score_candidates': pipeline_data[1] or 0,
                'pending_interviews': pipeline_data[2] or 0,
                'today_applications': pipeline_data[3] or 0
            },
            'trends': {
                'application_trend': round(trend_percentage, 1),
                'trend_direction': 'up' if trend_percentage > 0 else 'down' if trend_percentage < 0 else 'stable'
            },
            'market_insights': {
                'top_skills_demand': [{'skill': skill, 'count': count} for skill, count in top_skills],
                'skill_gap_analysis': self._analyze_skill_gaps()
            },
            'alerts': self._generate_alerts(pipeline_data, trend_percentage)
        }
    
    def _analyze_skill_gaps(self) -> List[Dict]:
        """Analyze gaps between job requirements and candidate skills"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get job skills vs candidate skills
        cursor.execute('''
            SELECT j.skills as job_skills, c.skills as candidate_skills
            FROM job_descriptions j
            CROSS JOIN candidates c
            WHERE j.created_at >= DATE('now', '-30 days')
        ''')
        
        skill_gaps = defaultdict(int)
        
        for row in cursor.fetchall():
            job_skills = json.loads(row[0]) if row[0] else []
            candidate_skills = json.loads(row[1]) if row[1] else []
            
            candidate_skills_lower = [s.lower() for s in candidate_skills]
            
            for job_skill in job_skills:
                if job_skill.lower() not in candidate_skills_lower:
                    skill_gaps[job_skill] += 1
        
        conn.close()
        
        # Return top skill gaps
        top_gaps = sorted(skill_gaps.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{'skill': skill, 'gap_count': count} for skill, count in top_gaps]
    
    def _generate_alerts(self, pipeline_data: tuple, trend_percentage: float) -> List[Dict]:
        """Generate actionable alerts"""
        alerts = []
        
        # Low application volume alert
        if pipeline_data[3] == 0:  # No applications today
            alerts.append({
                'type': 'warning',
                'message': 'No applications received today',
                'action': 'Review job postings and sourcing strategies'
            })
        
        # Interview backlog alert
        if pipeline_data[2] > 10:  # More than 10 pending interviews
            alerts.append({
                'type': 'info',
                'message': f'{pipeline_data[2]} interviews pending',
                'action': 'Consider scheduling additional interview slots'
            })
        
        # Declining trend alert
        if trend_percentage < -20:
            alerts.append({
                'type': 'warning',
                'message': f'Application volume down {abs(trend_percentage):.1f}%',
                'action': 'Review recruitment marketing and job visibility'
            })
        
        # High-quality candidates alert
        if pipeline_data[1] > 5:
            alerts.append({
                'type': 'success',
                'message': f'{pipeline_data[1]} high-scoring candidates available',
                'action': 'Prioritize interviews for top candidates'
            })
        
        return alerts

# Initialize analytics instance
recruitment_analytics = RecruitmentAnalytics() 