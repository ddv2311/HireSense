import ast
import re
import os
from typing import Dict, List, Optional, Tuple
import subprocess
import tempfile
from datetime import datetime
import json

class CodeAnalyzer:
    """
    Coding Sample Analyzer for technical assessment
    Analyzes code quality, complexity, best practices, and technical skills
    """
    
    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }
        
        self.complexity_thresholds = {
            'low': 5,
            'medium': 10,
            'high': 20
        }
    
    def analyze_code_sample(self, file_path: str, language: Optional[str] = None) -> Dict:
        """
        Analyze a code sample and provide comprehensive assessment
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Code file not found: {file_path}")
            
            # Detect language if not provided
            if not language:
                language = self._detect_language(file_path)
            
            # Read code content
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # Perform analysis based on language
            if language == 'python':
                analysis = self._analyze_python_code(code_content)
            elif language in ['javascript', 'typescript']:
                analysis = self._analyze_javascript_code(code_content)
            else:
                analysis = self._analyze_generic_code(code_content, language)
            
            # Add general metrics
            general_metrics = self._calculate_general_metrics(code_content)
            analysis.update(general_metrics)
            
            # Calculate overall score
            overall_score = self._calculate_code_score(analysis)
            analysis['overall_score'] = overall_score
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_code_recommendations(analysis)
            analysis['analyzed_at'] = datetime.now().isoformat()
            
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            }
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        _, ext = os.path.splitext(file_path)
        return self.supported_languages.get(ext.lower(), 'unknown')
    
    def _analyze_python_code(self, code: str) -> Dict:
        """Analyze Python code specifically"""
        try:
            # Parse AST
            tree = ast.parse(code)
            
            # Count different elements
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            # Calculate complexity
            complexity_score = self._calculate_python_complexity(tree)
            
            # Check for best practices
            best_practices = self._check_python_best_practices(code, tree)
            
            # Analyze documentation
            docstring_coverage = self._calculate_docstring_coverage(functions, classes)
            
            return {
                'language': 'python',
                'functions_count': len(functions),
                'classes_count': len(classes),
                'imports_count': len(imports),
                'complexity_score': complexity_score,
                'best_practices': best_practices,
                'docstring_coverage': docstring_coverage,
                'syntax_valid': True
            }
            
        except SyntaxError as e:
            return {
                'language': 'python',
                'syntax_valid': False,
                'syntax_error': str(e),
                'complexity_score': 0,
                'best_practices': {'score': 0, 'issues': ['Syntax errors present']}
            }
    
    def _analyze_javascript_code(self, code: str) -> Dict:
        """Analyze JavaScript/TypeScript code"""
        # Basic analysis for JavaScript
        functions = len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\(.*?\)\s*=>', code))
        classes = len(re.findall(r'class\s+\w+', code))
        imports = len(re.findall(r'import\s+.*?from|require\s*\(', code))
        
        # Check for modern JS features
        modern_features = self._check_modern_js_features(code)
        
        # Basic complexity estimation
        complexity_score = self._estimate_js_complexity(code)
        
        return {
            'language': 'javascript',
            'functions_count': functions,
            'classes_count': classes,
            'imports_count': imports,
            'complexity_score': complexity_score,
            'modern_features': modern_features,
            'syntax_valid': True  # Simplified for demo
        }
    
    def _analyze_generic_code(self, code: str, language: str) -> Dict:
        """Generic code analysis for other languages"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Basic metrics
        return {
            'language': language,
            'total_lines': len(lines),
            'code_lines': len(non_empty_lines),
            'comment_lines': len([line for line in lines if line.strip().startswith(('#', '//', '/*'))]),
            'complexity_score': min(len(non_empty_lines) // 10, 20),  # Rough estimate
            'syntax_valid': True
        }
    
    def _calculate_general_metrics(self, code: str) -> Dict:
        """Calculate general code metrics"""
        lines = code.split('\n')
        
        return {
            'total_lines': len(lines),
            'blank_lines': len([line for line in lines if not line.strip()]),
            'comment_lines': len([line for line in lines if line.strip().startswith(('#', '//', '/*', '*'))]),
            'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith(('#', '//', '/*', '*'))]),
            'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'max_line_length': max(len(line) for line in lines) if lines else 0
        }
    
    def _calculate_python_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity for Python code"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _check_python_best_practices(self, code: str, tree: ast.AST) -> Dict:
        """Check Python best practices"""
        issues = []
        score = 100
        
        # Check for PEP 8 violations (simplified)
        lines = code.split('\n')
        
        # Line length check
        long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 79]
        if long_lines:
            issues.append(f"Lines too long (>79 chars): {len(long_lines)} lines")
            score -= min(20, len(long_lines) * 2)
        
        # Check for proper naming conventions
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        bad_function_names = [name for name in functions if not re.match(r'^[a-z_][a-z0-9_]*$', name)]
        if bad_function_names:
            issues.append(f"Non-PEP8 function names: {bad_function_names}")
            score -= len(bad_function_names) * 5
        
        # Check for global variables (simplified)
        if 'global ' in code:
            issues.append("Global variables detected")
            score -= 10
        
        return {
            'score': max(0, score),
            'issues': issues
        }
    
    def _calculate_docstring_coverage(self, functions: List, classes: List) -> Dict:
        """Calculate documentation coverage"""
        total_items = len(functions) + len(classes)
        if total_items == 0:
            return {'coverage': 100, 'documented': 0, 'total': 0}
        
        documented = 0
        
        # Check functions
        for func in functions:
            if ast.get_docstring(func):
                documented += 1
        
        # Check classes
        for cls in classes:
            if ast.get_docstring(cls):
                documented += 1
        
        coverage = (documented / total_items) * 100
        
        return {
            'coverage': round(coverage, 1),
            'documented': documented,
            'total': total_items
        }
    
    def _check_modern_js_features(self, code: str) -> Dict:
        """Check for modern JavaScript features"""
        features = {
            'arrow_functions': bool(re.search(r'=>', code)),
            'const_let': bool(re.search(r'\b(const|let)\b', code)),
            'template_literals': bool(re.search(r'`.*\$\{.*\}.*`', code)),
            'destructuring': bool(re.search(r'\{.*\}\s*=', code)),
            'async_await': bool(re.search(r'\b(async|await)\b', code)),
            'classes': bool(re.search(r'\bclass\b', code))
        }
        
        modern_score = sum(features.values()) / len(features) * 100
        
        return {
            'features': features,
            'modern_score': round(modern_score, 1)
        }
    
    def _estimate_js_complexity(self, code: str) -> int:
        """Estimate JavaScript complexity"""
        complexity = 1
        
        # Count control structures
        complexity += len(re.findall(r'\b(if|while|for|switch)\b', code))
        complexity += len(re.findall(r'\b(catch|finally)\b', code))
        complexity += len(re.findall(r'(\|\||&&)', code))
        
        return complexity
    
    def _calculate_code_score(self, analysis: Dict) -> Dict:
        """Calculate overall code quality score"""
        scores = {
            'readability': 0,
            'complexity': 0,
            'best_practices': 0,
            'documentation': 0
        }
        
        # Readability score (based on line length, comments)
        total_lines = analysis.get('total_lines', 1)
        comment_ratio = analysis.get('comment_lines', 0) / total_lines
        avg_line_length = analysis.get('average_line_length', 0)
        
        readability = 100
        if avg_line_length > 80:
            readability -= min(30, (avg_line_length - 80) * 2)
        if comment_ratio < 0.1:
            readability -= 20
        
        scores['readability'] = max(0, readability)
        
        # Complexity score
        complexity = analysis.get('complexity_score', 0)
        if complexity <= self.complexity_thresholds['low']:
            scores['complexity'] = 100
        elif complexity <= self.complexity_thresholds['medium']:
            scores['complexity'] = 80
        elif complexity <= self.complexity_thresholds['high']:
            scores['complexity'] = 60
        else:
            scores['complexity'] = 40
        
        # Best practices score
        if 'best_practices' in analysis:
            scores['best_practices'] = analysis['best_practices'].get('score', 0)
        else:
            scores['best_practices'] = 70  # Default for non-Python
        
        # Documentation score
        if 'docstring_coverage' in analysis:
            scores['documentation'] = analysis['docstring_coverage']['coverage']
        else:
            scores['documentation'] = 60  # Default
        
        # Calculate weighted final score
        final_score = (
            scores['readability'] * 0.25 +
            scores['complexity'] * 0.25 +
            scores['best_practices'] * 0.3 +
            scores['documentation'] * 0.2
        )
        
        return {
            'final_score': round(final_score, 1),
            'breakdown': scores,
            'grade': self._get_grade(final_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_code_recommendations(self, analysis: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Check overall score
        overall_score = analysis.get('overall_score', {}).get('final_score', 0)
        
        if overall_score < 70:
            recommendations.append("Focus on improving overall code quality")
        
        # Specific recommendations based on analysis
        if analysis.get('complexity_score', 0) > self.complexity_thresholds['medium']:
            recommendations.append("Consider breaking down complex functions into smaller ones")
        
        if 'best_practices' in analysis and analysis['best_practices'].get('score', 0) < 80:
            recommendations.append("Review and follow language-specific best practices")
        
        if 'docstring_coverage' in analysis and analysis['docstring_coverage']['coverage'] < 50:
            recommendations.append("Add more documentation and comments to your code")
        
        if analysis.get('average_line_length', 0) > 100:
            recommendations.append("Consider breaking long lines for better readability")
        
        if not recommendations:
            recommendations.append("Excellent code quality! Keep up the great work.")
        
        return recommendations
    
    def analyze_github_repository(self, repo_url: str) -> Dict:
        """
        Analyze a GitHub repository (simplified implementation)
        In a full implementation, this would clone and analyze the entire repo
        """
        return {
            'repo_url': repo_url,
            'analysis_type': 'github_repository',
            'message': 'GitHub repository analysis would require additional implementation',
            'recommendations': [
                'Clone repository and analyze multiple files',
                'Check commit history and contribution patterns',
                'Analyze project structure and dependencies'
            ]
        }

# Initialize the code analyzer
code_analyzer = CodeAnalyzer() 