"""
Tests for job market analyzer functionality
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

from recruitiq.core.analyzer import JobAnalyzer
from recruitiq.db.models import JobPosting


class TestJobAnalyzer:
    """Test JobAnalyzer class"""
    
    @pytest.fixture
    def analyzer(self, db_session):
        """Create JobAnalyzer instance with mocked session"""
        with patch('recruitiq.core.analyzer.get_session', return_value=db_session):
            return JobAnalyzer()
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None
        assert hasattr(analyzer, 'session')
        assert hasattr(analyzer, 'filters')
        assert analyzer.filters == {}
    
    def test_generate_summary_stats_empty_db(self, analyzer, db_session):
        """Test summary stats with empty database"""
        stats = analyzer.generate_summary_stats()
        
        assert "error" in stats
        assert "No job data available" in stats["error"]
    
    def test_generate_summary_stats_with_data(self, analyzer, populated_db):
        """Test summary stats with populated database"""
        with patch.object(analyzer, 'session', populated_db):
            stats = analyzer.generate_summary_stats()
        
        assert "error" not in stats
        assert stats["total_jobs"] == 4
        assert "top_titles" in stats
        assert "top_locations" in stats
        assert "top_companies" in stats
        assert "platform_distribution" in stats
        assert "employment_types" in stats
        assert "last_updated" in stats
        
        # Check specific data
        assert len(stats["top_titles"]) > 0
        assert len(stats["platform_distribution"]) > 0
    
    def test_calculate_salary_stats_no_data(self, analyzer, db_session):
        """Test salary calculations with no salary data"""
        with patch.object(analyzer, 'session', db_session):
            stats = analyzer._calculate_salary_stats()
        
        assert "error" in stats
        assert "No salary data available" in stats["error"]
    
    def test_calculate_salary_stats_with_data(self, analyzer, populated_db):
        """Test salary calculations with data"""
        with patch.object(analyzer, 'session', populated_db):
            stats = analyzer._calculate_salary_stats()
        
        assert "error" not in stats
        assert "average_salary" in stats
        assert "median_salary" in stats
        assert "min_salary" in stats
        assert "max_salary" in stats
        assert "jobs_with_salary" in stats
        
        # Check values make sense
        assert stats["min_salary"] <= stats["average_salary"] <= stats["max_salary"]
        assert stats["jobs_with_salary"] > 0
    
    def test_analyze_job_trends(self, analyzer, populated_db):
        """Test job trend analysis"""
        with patch.object(analyzer, 'session', populated_db):
            trends = analyzer.analyze_job_trends(days=30)
        
        assert "error" not in trends
        assert "period_days" in trends
        assert "daily_postings" in trends
        assert "platform_trends" in trends
        assert "total_jobs_period" in trends
        
        assert trends["period_days"] == 30
        assert isinstance(trends["daily_postings"], list)
        assert isinstance(trends["platform_trends"], list)
    
    def test_get_skills_analysis_no_data(self, analyzer, db_session):
        """Test skills analysis with no data"""
        with patch.object(analyzer, 'session', db_session):
            skills = analyzer.get_skills_analysis()
        
        assert "error" in skills
        assert "No job description data available" in skills["error"]
    
    def test_get_skills_analysis_with_data(self, analyzer, populated_db):
        """Test skills analysis with job descriptions"""
        with patch.object(analyzer, 'session', populated_db):
            skills = analyzer.get_skills_analysis()
        
        assert "error" not in skills
        assert "top_skills" in skills
        assert "total_jobs_analyzed" in skills
        assert "skills_searched" in skills
        
        # Should find some skills from our sample data
        assert skills["total_jobs_analyzed"] > 0
        assert len(skills["top_skills"]) > 0
        
        # Check that common skills are found
        skill_names = [skill[0] for skill in skills["top_skills"]]
        assert any(skill in ['python', 'javascript', 'react', 'aws', 'docker'] for skill in skill_names)
    
    def test_display_summary_with_data(self, analyzer, populated_db, capsys):
        """Test display summary output"""
        with patch.object(analyzer, 'session', populated_db):
            analyzer.display_summary()
        
        captured = capsys.readouterr()
        assert "RecruitIQ Job Market Analysis" in captured.out
        assert "Total Jobs:" in captured.out
    
    def test_display_skills_analysis_with_data(self, analyzer, populated_db, capsys):
        """Test display skills analysis output"""
        with patch.object(analyzer, 'session', populated_db):
            analyzer.display_skills_analysis()
        
        captured = capsys.readouterr()
        assert "Most In-Demand Skills" in captured.out
    
    def test_display_geographic_analysis(self, analyzer, populated_db, capsys):
        """Test geographic analysis display"""
        with patch.object(analyzer, 'session', populated_db):
            analyzer.display_geographic_analysis()
        
        captured = capsys.readouterr()
        assert "Geographic Job Market Analysis" in captured.out
        assert "Remote Work Statistics" in captured.out
    
    def test_display_salary_intelligence(self, analyzer, populated_db, capsys):
        """Test salary intelligence display"""
        with patch.object(analyzer, 'session', populated_db):
            analyzer.display_salary_intelligence()
        
        captured = capsys.readouterr()
        assert "Salary Intelligence Dashboard" in captured.out
    
    def test_display_company_insights(self, analyzer, populated_db, capsys):
        """Test company insights display"""
        with patch.object(analyzer, 'session', populated_db):
            analyzer.display_company_insights()
        
        captured = capsys.readouterr()
        assert "Company Hiring Insights" in captured.out
    
    @patch('recruitiq.core.analyzer.RecruitIQReporter')
    def test_generate_html_report_success(self, mock_reporter_class, analyzer):
        """Test HTML report generation success"""
        mock_reporter = Mock()
        mock_reporter.generate_executive_summary.return_value = "test_report.html"
        mock_reporter_class.return_value = mock_reporter
        
        result = analyzer.generate_html_report("executive", days=30)
        
        assert result == "test_report.html"
        mock_reporter.generate_executive_summary.assert_called_once_with(30)
    
    @patch('recruitiq.core.analyzer.RecruitIQReporter')
    def test_generate_html_report_import_error(self, mock_reporter_class, analyzer, capsys):
        """Test HTML report generation with import error"""
        mock_reporter_class.side_effect = ImportError("plotly not found")
        
        result = analyzer.generate_html_report("executive")
        
        assert result == ""
        captured = capsys.readouterr()
        assert "HTML reporting requires additional packages" in captured.out
    
    def test_setup_advanced_filters(self, analyzer):
        """Test setting up advanced filters"""
        # Test that filters can be set
        analyzer.filters = {
            'days': 30,
            'job_titles': ['python developer'],
            'companies': ['google'],
            'locations': ['san francisco'],
            'salary_range': (100000, 200000)
        }
        
        assert analyzer.filters['days'] == 30
        assert len(analyzer.filters['job_titles']) == 1
        assert len(analyzer.filters['companies']) == 1
        assert len(analyzer.filters['locations']) == 1
        assert analyzer.filters['salary_range'] == (100000, 200000)
    
    def test_analyzer_error_handling(self, analyzer):
        """Test error handling in analyzer methods"""
        # Test with broken session
        with patch.object(analyzer, 'session') as mock_session:
            mock_session.query.side_effect = Exception("Database error")
            
            stats = analyzer.generate_summary_stats()
            assert "error" in stats
            assert "Database error" in stats["error"]
    
    def test_analyzer_with_filters_applied(self, analyzer, populated_db):
        """Test analyzer with various filters applied"""
        with patch.object(analyzer, 'session', populated_db):
            # Set some filters
            analyzer.filters = {
                'days': 7,
                'job_titles': ['python'],
                'salary_range': (100000, 200000)
            }
            
            # Test that analysis still works with filters
            stats = analyzer.generate_summary_stats()
            assert "error" not in stats
    
    def test_recent_jobs_calculation(self, analyzer, populated_db):
        """Test recent jobs calculation"""
        with patch.object(analyzer, 'session', populated_db):
            stats = analyzer.generate_summary_stats()
            
            # All our sample jobs should be recent (created within last 7 days)
            assert stats["recent_jobs_7_days"] >= 0
            assert stats["recent_jobs_7_days"] <= stats["total_jobs"]
    
    def test_platform_distribution_accuracy(self, analyzer, populated_db):
        """Test platform distribution accuracy"""
        with patch.object(analyzer, 'session', populated_db):
            stats = analyzer.generate_summary_stats()
            
            platforms = dict(stats["platform_distribution"])
            
            # Check that all expected platforms are present
            assert "Indeed" in platforms
            assert "LinkedIn" in platforms
            assert "RemoteOK" in platforms
            assert "Company Sites" in platforms
            
            # Check total matches expected count
            total_platform_jobs = sum(platforms.values())
            assert total_platform_jobs == stats["total_jobs"] 