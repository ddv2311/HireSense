import cv2
import numpy as np
from typing import Dict, List, Optional
import os
import json
from datetime import datetime
import speech_recognition as sr

# Try to import moviepy, handle gracefully if not available
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️  MoviePy not available. Video analysis will have limited functionality.")

import tempfile

class VideoAnalyzer:
    """
    Video Introduction Analyzer for candidate assessment
    Analyzes video introductions for communication skills, confidence, and professionalism
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
    def analyze_video_introduction(self, video_path: str) -> Dict:
        """
        Analyze video introduction and extract insights
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Extract basic video properties
            video_properties = self._extract_video_properties(video_path)
            
            # Extract audio and transcribe
            audio_analysis = self._analyze_audio(video_path)
            
            # Analyze visual elements
            visual_analysis = self._analyze_visual_elements(video_path)
            
            # Generate overall assessment
            overall_score = self._calculate_overall_score(audio_analysis, visual_analysis, video_properties)
            
            return {
                'video_properties': video_properties,
                'audio_analysis': audio_analysis,
                'visual_analysis': visual_analysis,
                'overall_score': overall_score,
                'recommendations': self._generate_recommendations(audio_analysis, visual_analysis),
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
    
    def _extract_video_properties(self, video_path: str) -> Dict:
        """Extract basic video properties"""
        try:
            if not MOVIEPY_AVAILABLE:
                return {'error': "MoviePy not available"}
            
            clip = VideoFileClip(video_path)
            
            return {
                'duration': round(clip.duration, 2),
                'fps': clip.fps,
                'resolution': f"{clip.w}x{clip.h}",
                'size_mb': round(os.path.getsize(video_path) / (1024 * 1024), 2)
            }
        except Exception as e:
            return {'error': f"Could not extract video properties: {str(e)}"}
    
    def _analyze_audio(self, video_path: str) -> Dict:
        """Extract and analyze audio from video"""
        try:
            if not MOVIEPY_AVAILABLE:
                return {'error': "MoviePy not available"}
            
            # Extract audio from video
            clip = VideoFileClip(video_path)
            
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                audio_path = temp_audio.name
                clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
            
            # Transcribe audio
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                try:
                    transcript = self.recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    transcript = ""
                except sr.RequestError:
                    transcript = "Speech recognition service unavailable"
            
            # Clean up temporary file
            os.unlink(audio_path)
            
            # Analyze transcript
            speech_analysis = self._analyze_speech_content(transcript)
            
            return {
                'transcript': transcript,
                'word_count': len(transcript.split()) if transcript else 0,
                'speech_analysis': speech_analysis,
                'audio_quality': self._assess_audio_quality(clip.audio)
            }
            
        except Exception as e:
            return {
                'error': f"Audio analysis failed: {str(e)}",
                'transcript': "",
                'word_count': 0
            }
    
    def _analyze_speech_content(self, transcript: str) -> Dict:
        """Analyze speech content for communication skills"""
        if not transcript:
            return {'confidence_score': 0, 'clarity_score': 0, 'professionalism_score': 0}
        
        words = transcript.lower().split()
        
        # Confidence indicators
        confidence_words = ['confident', 'experienced', 'skilled', 'accomplished', 'successful', 'proven']
        confidence_score = min(100, len([w for w in words if w in confidence_words]) * 20)
        
        # Clarity indicators (sentence structure, filler words)
        filler_words = ['um', 'uh', 'like', 'you know', 'basically', 'actually']
        filler_count = len([w for w in words if w in filler_words])
        clarity_score = max(0, 100 - (filler_count * 10))
        
        # Professionalism indicators
        professional_words = ['experience', 'skills', 'team', 'project', 'responsibility', 'achievement']
        professionalism_score = min(100, len([w for w in words if w in professional_words]) * 15)
        
        return {
            'confidence_score': confidence_score,
            'clarity_score': clarity_score,
            'professionalism_score': professionalism_score,
            'filler_word_count': filler_count
        }
    
    def _assess_audio_quality(self, audio) -> str:
        """Assess audio quality"""
        try:
            # Simple audio quality assessment
            if audio.duration > 0:
                return "Good"
            else:
                return "Poor"
        except:
            return "Unknown"
    
    def _analyze_visual_elements(self, video_path: str) -> Dict:
        """Analyze visual elements of the video"""
        try:
            if not MOVIEPY_AVAILABLE:
                return {'error': "MoviePy not available"}
            
            cap = cv2.VideoCapture(video_path)
            
            frame_count = 0
            brightness_scores = []
            
            # Sample frames for analysis
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, total_frames // 10)  # Sample 10 frames
            
            while cap.isOpened() and frame_count < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % sample_interval == 0:
                    # Analyze brightness
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    brightness = np.mean(gray)
                    brightness_scores.append(brightness)
                
                frame_count += 1
            
            cap.release()
            
            # Calculate visual quality metrics
            avg_brightness = np.mean(brightness_scores) if brightness_scores else 0
            lighting_quality = self._assess_lighting_quality(avg_brightness)
            
            return {
                'lighting_quality': lighting_quality,
                'avg_brightness': round(avg_brightness, 2),
                'frames_analyzed': len(brightness_scores)
            }
            
        except Exception as e:
            return {
                'error': f"Visual analysis failed: {str(e)}",
                'lighting_quality': 'Unknown'
            }
    
    def _assess_lighting_quality(self, brightness: float) -> str:
        """Assess lighting quality based on brightness"""
        if brightness < 50:
            return "Too Dark"
        elif brightness > 200:
            return "Too Bright"
        elif 80 <= brightness <= 180:
            return "Good"
        else:
            return "Fair"
    
    def _calculate_overall_score(self, audio_analysis: Dict, visual_analysis: Dict, video_properties: Dict) -> Dict:
        """Calculate overall video introduction score"""
        try:
            # Audio scores (60% weight)
            speech_scores = audio_analysis.get('speech_analysis', {})
            audio_score = (
                speech_scores.get('confidence_score', 0) * 0.4 +
                speech_scores.get('clarity_score', 0) * 0.4 +
                speech_scores.get('professionalism_score', 0) * 0.2
            )
            
            # Visual scores (25% weight)
            lighting_quality = visual_analysis.get('lighting_quality', 'Unknown')
            visual_score = 80 if lighting_quality == 'Good' else 60 if lighting_quality == 'Fair' else 40
            
            # Technical scores (15% weight)
            duration = video_properties.get('duration', 0)
            duration_score = 100 if 30 <= duration <= 120 else 70 if 15 <= duration <= 180 else 50
            
            # Calculate weighted final score
            final_score = (audio_score * 0.6 + visual_score * 0.25 + duration_score * 0.15)
            
            return {
                'final_score': round(final_score, 1),
                'audio_score': round(audio_score, 1),
                'visual_score': visual_score,
                'technical_score': duration_score,
                'breakdown': {
                    'communication': round(audio_score, 1),
                    'presentation': visual_score,
                    'technical_quality': duration_score
                }
            }
            
        except Exception as e:
            return {
                'final_score': 0,
                'error': f"Score calculation failed: {str(e)}"
            }
    
    def _generate_recommendations(self, audio_analysis: Dict, visual_analysis: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Audio recommendations
        speech_scores = audio_analysis.get('speech_analysis', {})
        
        if speech_scores.get('confidence_score', 0) < 50:
            recommendations.append("Practice speaking with more confidence and conviction")
        
        if speech_scores.get('clarity_score', 0) < 70:
            recommendations.append("Reduce filler words and speak more clearly")
        
        if speech_scores.get('professionalism_score', 0) < 60:
            recommendations.append("Include more professional terminology and achievements")
        
        # Visual recommendations
        lighting_quality = visual_analysis.get('lighting_quality', 'Unknown')
        if lighting_quality in ['Too Dark', 'Too Bright']:
            recommendations.append("Improve lighting setup for better video quality")
        
        if not recommendations:
            recommendations.append("Great video introduction! Keep up the excellent work.")
        
        return recommendations

# Initialize the video analyzer
video_analyzer = VideoAnalyzer() 