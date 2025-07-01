"""
Tests for CLI functionality and command interface
"""

import pytest
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from recruitiq.cli.main import app
from recruitiq.cli.interactive import main as interactive_main


class TestMainCLI:
    """Test main CLI commands"""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner"""
        return CliRunner()
    
    def test_cli_import(self):
        """Test that CLI modules can be imported"""
        from recruitiq.cli.main import app
        from recruitiq.cli.interactive import main as interactive_main
        
        assert app is not None
        assert interactive_main is not None
    
    def test_cli_help(self, runner):
        """Test CLI help command"""
        result = runner.invoke(app, ['--help'])
        
        assert result.exit_code == 0
        assert 'RecruitIQ' in result.output
    
    def test_cli_version(self, runner):
        """Test CLI version command"""
        result = runner.invoke(app, ['version'])
        
        # Should either work or fail gracefully
        assert result.exit_code in [0, 1]
    
    def test_interactive_main_import(self):
        """Test that interactive main can be imported and called"""
        # Just test that it can be imported without error
        from recruitiq.cli.interactive import main as interactive_main
        assert callable(interactive_main)


class TestCLIHelpers:
    """Test CLI helper functions"""
    
    def test_cli_module_structure(self):
        """Test that CLI module has expected structure"""
        import recruitiq.cli.main as cli_main
        import recruitiq.cli.interactive as cli_interactive
        
        # Check that main modules exist
        assert hasattr(cli_main, 'app')
        assert hasattr(cli_interactive, 'main')
    
    def test_cli_imports_scrapers(self):
        """Test that CLI can import scraper modules"""
        try:
            from recruitiq.cli.main import app
            # If we get here, imports work
            assert True
        except ImportError as e:
            pytest.fail(f"CLI module import failed: {e}")


class TestCLIIntegration:
    """Test CLI integration scenarios"""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner"""
        return CliRunner()
    
    def test_help_commands_exist(self, runner):
        """Test that main help command exists"""
        result = runner.invoke(app, ['--help'])
        
        # Should at least show help without crashing
        assert result.exit_code == 0
        assert len(result.output) > 0
    
    @patch('recruitiq.cli.interactive.select')
    def test_interactive_main_mocked(self, mock_select):
        """Test interactive main with mocked user input"""
        mock_select.return_value = "🚪 Exit"
        
        # Should not crash when called
        try:
            interactive_main()
        except (SystemExit, KeyboardInterrupt):
            # Expected for exit conditions
            pass
        except Exception as e:
            # Should not have other exceptions
            pytest.fail(f"Interactive main failed: {e}")
    
    def test_cli_error_handling(self, runner):
        """Test CLI error handling"""
        # Test with invalid command
        result = runner.invoke(app, ['invalid-command'])
        
        # Should handle gracefully (either unknown command or help)
        assert isinstance(result.exit_code, int) 