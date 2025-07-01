"""
Tests for CV analyzer functionality including AI integration
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path

from recruitiq.core.cv_analyzer import CVAnalyzer


class TestCVAnalyzer:
    """Test CVAnalyzer class"""
    
    @pytest.fixture
    def cv_analyzer(self, db_session):
        """Create CVAnalyzer instance with mocked session"""
        with patch('recruitiq.core.cv_analyzer.get_session', return_value=db_session):
            return CVAnalyzer()
    
    def test_cv_analyzer_initialization_with_openai(self, cv_analyzer):
        """Test CV analyzer initialization with OpenAI"""
        with patch('recruitiq.core.cv_analyzer.openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.models.list.return_value = []
            mock_openai.return_value = mock_client
            
            analyzer = CVAnalyzer()
            assert analyzer.openai_client is not None
    
    def test_cv_analyzer_initialization_without_openai(self, cv_analyzer):
        """Test CV analyzer initialization without OpenAI"""
        with patch('recruitiq.core.cv_analyzer.openai.OpenAI', side_effect=ImportError):
            analyzer = CVAnalyzer()
            assert analyzer.openai_client is None
    
    def test_parse_txt_file(self, cv_analyzer, temp_cv_file):
        """Test parsing TXT CV file"""
        result = cv_analyzer.parse_cv_file(temp_cv_file)
        
        assert len(result) > 0
        assert "John Doe" in result
        assert "Software Engineer" in result
        assert "john@example.com" in result
        assert "Python" in result
    
    def test_parse_nonexistent_file(self, cv_analyzer):
        """Test parsing non-existent file"""
        with pytest.raises(FileNotFoundError):
            cv_analyzer.parse_cv_file("/path/to/nonexistent/file.txt")
    
    def test_parse_unsupported_format(self, cv_analyzer):
        """Test parsing unsupported file format"""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                cv_analyzer.parse_cv_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('recruitiq.core.cv_analyzer.PyPDF2')
    def test_parse_pdf_file(self, mock_pypdf2, cv_analyzer):
        """Test parsing PDF CV file"""
        # Mock PDF parsing
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample PDF content with John Doe"
        mock_reader.pages = [mock_page]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        try:
            result = cv_analyzer.parse_cv_file(temp_path)
            assert "Sample PDF content" in result
            assert "John Doe" in result
        finally:
            os.unlink(temp_path)
    
    @patch('recruitiq.core.cv_analyzer.Document')
    def test_parse_docx_file(self, mock_document, cv_analyzer):
        """Test parsing DOCX CV file"""
        # Mock DOCX parsing
        mock_doc = Mock()
        mock_paragraph = Mock()
        mock_paragraph.text = "Sample DOCX content with Jane Smith"
        mock_doc.paragraphs = [mock_paragraph]
        mock_document.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            temp_path = f.name
        
        try:
            result = cv_analyzer.parse_cv_file(temp_path)
            assert "Sample DOCX content" in result
            assert "Jane Smith" in result
        finally:
            os.unlink(temp_path)
    
    def test_extract_basic_contact_info(self, cv_analyzer, mock_cv_text):
        """Test basic contact information extraction"""
        contact_info = cv_analyzer._extract_basic_contact_info(mock_cv_text)
        
        assert contact_info['email'] == 'john.doe@email.com'
        assert contact_info['phone'] == '(555) 123-4567'
        assert 'linkedin.com/in/johndoe' in contact_info['linkedin']
        assert 'github.com/johndoe' in contact_info['github']
    
    def test_extract_basic_skills(self, cv_analyzer, mock_cv_text):
        """Test basic skills extraction"""
        skills = cv_analyzer._extract_basic_skills(mock_cv_text)
        
        assert 'programming_languages' in skills
        assert 'python' in skills['programming_languages']
        assert 'javascript' in skills['programming_languages']
        assert 'java' in skills['programming_languages']
        
        assert 'frameworks_libraries' in skills
        assert 'django' in skills['frameworks_libraries']
        assert 'flask' in skills['frameworks_libraries']
        
        assert 'cloud_devops' in skills
        assert 'aws' in skills['cloud_devops']
        assert 'docker' in skills['cloud_devops']
        assert 'kubernetes' in skills['cloud_devops']
    
    def test_extract_basic_experience(self, cv_analyzer, mock_cv_text):
        """Test basic experience extraction"""
        years = cv_analyzer._extract_basic_experience(mock_cv_text)
        
        assert years == 8  # From mock CV text
    
    def test_fallback_analysis(self, cv_analyzer, mock_cv_text):
        """Test fallback analysis when OpenAI is not available"""
        analysis = cv_analyzer._fallback_analysis(mock_cv_text)
        
        assert analysis['ai_powered'] is False
        assert 'personal_information' in analysis
        assert 'professional_summary' in analysis
        assert 'skills' in analysis
        assert 'cv_feedback' in analysis
        assert 'job_market_insights' in analysis
        
        # Check some extracted data
        assert analysis['personal_information']['email'] == 'john.doe@email.com'
        assert analysis['professional_summary']['years_of_experience'] == 8
        assert len(analysis['skills']) > 0
    
    @patch('recruitiq.core.cv_analyzer.openai.OpenAI')
    def test_ai_analyze_cv_success(self, mock_openai, cv_analyzer, mock_cv_text, mock_openai_response):
        """Test successful AI CV analysis"""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = json.dumps(mock_openai_response)
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        cv_analyzer.openai_client = mock_client
        
        analysis = cv_analyzer.ai_analyze_cv(mock_cv_text)
        
        assert analysis['ai_powered'] is True
        assert analysis['personal_information']['name'] == 'John Doe'
        assert analysis['professional_summary']['years_of_experience'] == 8
        assert len(analysis['skills']['programming_languages']) > 0
        assert analysis['cv_feedback']['overall_score'] == 7
    
    def test_ai_analyze_cv_short_text(self, cv_analyzer):
        """Test AI analysis with very short CV text"""
        short_text = "John"
        
        analysis = cv_analyzer.ai_analyze_cv(short_text)
        
        # Should fall back to basic analysis
        assert analysis['ai_powered'] is False
    
    @patch('recruitiq.core.cv_analyzer.openai.OpenAI')
    def test_ai_analyze_cv_api_error(self, mock_openai, cv_analyzer, mock_cv_text):
        """Test AI analysis with API error"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        cv_analyzer.openai_client = mock_client
        
        analysis = cv_analyzer.ai_analyze_cv(mock_cv_text)
        
        # Should fall back to basic analysis
        assert analysis['ai_powered'] is False
    
    def test_match_jobs_empty_skills(self, cv_analyzer, populated_db):
        """Test job matching with empty skills"""
        analysis = {'skills': {}}
        
        with patch.object(cv_analyzer, 'session', populated_db):
            matches = cv_analyzer.match_jobs(analysis)
        
        assert len(matches) == 0
    
    def test_match_jobs_with_skills(self, cv_analyzer, populated_db, mock_openai_response):
        """Test job matching with extracted skills"""
        with patch.object(cv_analyzer, 'session', populated_db):
            matches = cv_analyzer.match_jobs(mock_openai_response)
        
        assert len(matches) > 0
        
        # Check match structure
        for match in matches:
            assert 'job' in match
            assert 'match_score' in match
            assert 'matched_skills' in match
            assert 'experience_match' in match
            assert match['match_score'] >= 0
    
    def test_suggest_scraping_query_with_insights(self, cv_analyzer, mock_openai_response):
        """Test scraping query suggestion from job market insights"""
        query = cv_analyzer.suggest_scraping_query(mock_openai_response)
        
        # Should return first suitable job title
        assert query == "senior software engineer"
    
    def test_suggest_scraping_query_fallback(self, cv_analyzer):
        """Test scraping query suggestion fallback"""
        analysis = {
            'skills': {
                'programming_languages': ['python', 'javascript'],
                'frameworks_libraries': ['django'],
                'cloud_devops': ['aws']
            }
        }
        
        query = cv_analyzer.suggest_scraping_query(analysis)
        
        # Should build query from skills
        assert 'python' in query
        assert 'javascript' in query or 'django' in query
    
    def test_suggest_scraping_query_default(self, cv_analyzer):
        """Test scraping query suggestion with no skills"""
        analysis = {'skills': {}}
        
        query = cv_analyzer.suggest_scraping_query(analysis)
        
        assert query == "software engineer"
    
    def test_display_cv_analysis_ai_powered(self, cv_analyzer, mock_openai_response, capsys):
        """Test displaying AI-powered CV analysis"""
        cv_analyzer.display_cv_analysis(mock_openai_response)
        
        captured = capsys.readouterr()
        assert "AI-Powered CV Analysis" in captured.out
        assert "John Doe" in captured.out
        assert "8 years" in captured.out
        assert "CV Score: 7/10" in captured.out
    
    def test_display_cv_analysis_basic(self, cv_analyzer, capsys):
        """Test displaying basic CV analysis"""
        basic_analysis = {
            'ai_powered': False,
            'personal_information': {'email': 'test@example.com'},
            'skills': {'programming_languages': ['python']},
            'word_count': 100
        }
        
        cv_analyzer.display_cv_analysis(basic_analysis)
        
        captured = capsys.readouterr()
        assert "Basic CV Analysis" in captured.out
        assert "test@example.com" in captured.out
        assert "python" in captured.out
        assert "Basic Pattern Matching" in captured.out
    
    def test_display_job_matches_empty(self, cv_analyzer, capsys):
        """Test displaying empty job matches"""
        cv_analyzer.display_job_matches([])
        
        captured = capsys.readouterr()
        assert "No matching jobs found" in captured.out
    
    def test_display_job_matches_with_data(self, cv_analyzer, populated_db, capsys):
        """Test displaying job matches with data"""
        # Create mock matches
        job = populated_db.query(populated_db.bind.execute("SELECT * FROM job_postings LIMIT 1")).first()
        matches = [{
            'job': job,
            'match_score': 85.5,
            'matched_skills': ['python', 'django'],
            'experience_match': True
        }] if job else []
        
        if matches:
            with patch('recruitiq.core.cv_analyzer.Confirm.ask', return_value=False):
                cv_analyzer.display_job_matches(matches)
            
            captured = capsys.readouterr()
            assert "Found 1 Matching Jobs" in captured.out
            assert "85.5%" in captured.out
    
    @patch('recruitiq.core.cv_analyzer.Prompt.ask')
    @patch('recruitiq.core.cv_analyzer.Confirm.ask')
    def test_interactive_cv_analysis_success(self, mock_confirm, mock_prompt, cv_analyzer, temp_cv_file, mock_openai_response):
        """Test interactive CV analysis workflow"""
        mock_prompt.return_value = temp_cv_file
        mock_confirm.side_effect = [True, False]  # Continue to matching, don't scrape
        
        with patch.object(cv_analyzer, 'ai_analyze_cv', return_value=mock_openai_response):
            with patch.object(cv_analyzer, 'match_jobs', return_value=[]):
                cv_analyzer.interactive_cv_analysis()
        
        # Should complete without errors
        assert True
    
    @patch('recruitiq.core.cv_analyzer.Prompt.ask')
    def test_interactive_cv_analysis_file_not_found(self, mock_prompt, cv_analyzer, capsys):
        """Test interactive CV analysis with non-existent file"""
        mock_prompt.return_value = "/nonexistent/file.pdf"
        
        cv_analyzer.interactive_cv_analysis()
        
        captured = capsys.readouterr()
        assert "File not found" in captured.out
    
    def test_run_targeted_scraping(self, cv_analyzer, mock_openai_response):
        """Test targeted scraping functionality"""
        with patch('recruitiq.core.cv_analyzer.IndeedScraper') as mock_indeed:
            with patch('recruitiq.core.cv_analyzer.RemoteOKScraper') as mock_remote:
                with patch('recruitiq.core.cv_analyzer.validate_job_data', return_value=True):
                    with patch('recruitiq.core.cv_analyzer.update_or_create_job_posting'):
                        # Mock scrapers
                        mock_indeed_instance = Mock()
                        mock_indeed_instance.search_jobs.return_value = [{'title': 'test job'}]
                        mock_indeed.return_value = mock_indeed_instance
                        
                        mock_remote_instance = Mock()
                        mock_remote_instance.search_jobs.return_value = [{'title': 'test remote job'}]
                        mock_remote.return_value = mock_remote_instance
                        
                        cv_analyzer._run_targeted_scraping("python developer", mock_openai_response)
                        
                        # Should have called both scrapers
                        mock_indeed_instance.search_jobs.assert_called_once()
                        mock_remote_instance.search_jobs.assert_called_once()
    
    def test_setup_openai_client_with_env_var(self, cv_analyzer):
        """Test OpenAI client setup with environment variable"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('recruitiq.core.cv_analyzer.openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_client.models.list.return_value = []
                mock_openai.return_value = mock_client
                
                client = cv_analyzer._setup_openai_client()
                
                assert client is not None
                mock_openai.assert_called_once_with(api_key='test-key')
    
    def test_setup_openai_client_no_key(self, cv_analyzer, capsys):
        """Test OpenAI client setup without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('recruitiq.core.cv_analyzer.Prompt.ask', return_value=''):
                client = cv_analyzer._setup_openai_client()
                
                assert client is None
                captured = capsys.readouterr()
                assert "API key is required" in captured.out 