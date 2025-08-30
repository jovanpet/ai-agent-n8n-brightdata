"""
Tests for data formatting utilities
"""
import pytest
from datetime import datetime
from app.utils.data_formatter import (
    create_n8n_payload,
    validate_article_data,
    sanitize_input_data
)


class TestCreateN8nPayload:
    """Test n8n payload creation functionality"""
    
    def test_create_n8n_payload_basic(self):
        company_domain = "example.com"
        article_title = "Test Article"
        article = "This is a test article about artificial intelligence and machine learning. " \
                 "It contains multiple sentences and should generate keywords and phrases. " \
                 "The content is long enough for proper analysis and processing."
        
        result = create_n8n_payload(company_domain, article_title, article)
        
        # Check structure
        assert "metadata" in result
        assert "content" in result
        assert "n8n_payload" in result
        
        # Check metadata
        metadata = result["metadata"]
        assert metadata["company_domain"] == company_domain
        assert metadata["article_title"] == article_title
        assert "processed_at" in metadata
        assert metadata["article_length"] == len(article)
        assert metadata["word_count"] == len(article.split())
        
        # Check content
        content = result["content"]
        assert content["title"] == article_title
        assert content["body"] == article
        assert "summary" in content
        assert "keywords" in content
        assert "phrases" in content
        assert isinstance(content["keywords"], list)
        assert isinstance(content["phrases"], list)
        
        # Check n8n_payload
        n8n_payload = result["n8n_payload"]
        assert "webhook_data" in n8n_payload
        webhook_data = n8n_payload["webhook_data"]
        assert webhook_data["domain"] == company_domain
        assert webhook_data["title"] == article_title
        assert webhook_data["content"] == article
        assert "timestamp" in webhook_data
        assert "metadata" in webhook_data
    
    def test_create_n8n_payload_timestamp_format(self):
        result = create_n8n_payload("test.com", "Title", "Content here with enough text.")
        
        # Check timestamp is valid ISO format
        timestamp = result["metadata"]["processed_at"]
        assert isinstance(timestamp, str)
        # Should be able to parse as datetime
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_create_n8n_payload_short_article(self):
        result = create_n8n_payload("test.com", "Short", "Short content.")
        
        # Should still work but with empty keywords/phrases
        assert result["content"]["keywords"] == []
        assert result["content"]["phrases"] == []


class TestValidateArticleData:
    """Test article data validation functionality"""
    
    def test_validate_article_data_valid(self):
        valid_data = {
            "companyDomain": "example.com",
            "articleTitle": "Valid Article Title",
            "article": "This is a valid article with sufficient content for processing. " * 5
        }
        
        is_valid, error_message = validate_article_data(valid_data)
        assert is_valid is True
        assert error_message == ""
    
    def test_validate_article_data_missing_fields(self):
        incomplete_data = {
            "companyDomain": "example.com",
            "articleTitle": "Title"
            # Missing article field
        }
        
        is_valid, error_message = validate_article_data(incomplete_data)
        assert is_valid is False
        assert "Missing required fields" in error_message
        assert "article" in error_message
    
    def test_validate_article_data_empty_fields(self):
        empty_data = {
            "companyDomain": "",
            "articleTitle": "   ",
            "article": "Valid content here with enough text for processing."
        }
        
        is_valid, error_message = validate_article_data(empty_data)
        assert is_valid is False
        assert "Missing required fields" in error_message
    
    def test_validate_article_data_no_data(self):
        is_valid, error_message = validate_article_data(None)
        assert is_valid is False
        assert error_message == "No data provided"
        
        is_valid, error_message = validate_article_data({})
        assert is_valid is False
        assert error_message == "Missing required fields: companyDomain, articleTitle, article"
    
    def test_validate_article_data_short_article(self):
        short_data = {
            "companyDomain": "example.com",
            "articleTitle": "Title",
            "article": "Too short"
        }
        
        is_valid, error_message = validate_article_data(short_data)
        assert is_valid is False
        assert "too short" in error_message
    
    def test_validate_article_data_short_domain(self):
        short_domain_data = {
            "companyDomain": "ex",
            "articleTitle": "Valid Title",
            "article": "This is a valid article with sufficient content for processing." * 3
        }
        
        is_valid, error_message = validate_article_data(short_domain_data)
        assert is_valid is False
        assert "too short" in error_message
    
    def test_validate_article_data_short_title(self):
        short_title_data = {
            "companyDomain": "example.com",
            "articleTitle": "Ti",
            "article": "This is a valid article with sufficient content for processing." * 3
        }
        
        is_valid, error_message = validate_article_data(short_title_data)
        assert is_valid is False
        assert "too short" in error_message


class TestSanitizeInputData:
    """Test input data sanitization functionality"""
    
    def test_sanitize_input_data_basic(self):
        raw_data = {
            "companyDomain": "  example.com  ",
            "articleTitle": "  Test Article Title  ",
            "article": "  Article content here  "
        }
        
        result = sanitize_input_data(raw_data)
        
        assert result["company_domain"] == "example.com"
        assert result["article_title"] == "Test Article Title"
        assert result["article"] == "Article content here"
    
    def test_sanitize_input_data_missing_fields(self):
        incomplete_data = {
            "companyDomain": "example.com"
            # Missing other fields
        }
        
        result = sanitize_input_data(incomplete_data)
        
        assert result["company_domain"] == "example.com"
        assert result["article_title"] == ""
        assert result["article"] == ""
    
    def test_sanitize_input_data_non_string_values(self):
        mixed_data = {
            "companyDomain": 123,
            "articleTitle": None,
            "article": ["list", "content"]
        }
        
        result = sanitize_input_data(mixed_data)
        
        # Should convert everything to strings and strip
        assert result["company_domain"] == "123"
        assert result["article_title"] == "None"
        assert result["article"] == "['list', 'content']"
    
    def test_sanitize_input_data_empty_input(self):
        result = sanitize_input_data({})
        
        assert result["company_domain"] == ""
        assert result["article_title"] == ""
        assert result["article"] == ""


# Integration tests
class TestDataFormatterIntegration:
    """Integration tests for data formatting functions"""
    
    def test_full_data_processing_flow(self):
        """Test the complete flow from raw input to n8n payload"""
        raw_input = {
            "companyDomain": "  tech-company.com  ",
            "articleTitle": "  AI Revolution in Business  ",
            "article": """
            Artificial intelligence is revolutionizing the way businesses operate. 
            Companies are implementing AI solutions to automate processes and improve efficiency. 
            Machine learning algorithms analyze customer data to provide personalized experiences. 
            Natural language processing helps businesses understand customer feedback better. 
            The future of business will be heavily influenced by AI technologies.
            """
        }
        
        # Step 1: Validate
        is_valid, error_message = validate_article_data(raw_input)
        assert is_valid is True
        
        # Step 2: Sanitize
        clean_data = sanitize_input_data(raw_input)
        assert clean_data["company_domain"] == "tech-company.com"
        assert clean_data["article_title"] == "AI Revolution in Business"
        
        # Step 3: Create payload
        payload = create_n8n_payload(
            clean_data["company_domain"],
            clean_data["article_title"],
            clean_data["article"]
        )
        
        # Verify final payload structure and content
        assert payload["metadata"]["company_domain"] == "tech-company.com"
        assert payload["content"]["title"] == "AI Revolution in Business"
        assert len(payload["content"]["keywords"]) > 0
        assert len(payload["content"]["phrases"]) > 0
        assert payload["n8n_payload"]["webhook_data"]["domain"] == "tech-company.com"
    
    def test_error_handling_flow(self):
        """Test error handling in the complete flow"""
        invalid_inputs = [
            {},  # Empty
            {"companyDomain": "test"},  # Missing fields
            {"companyDomain": "test.com", "articleTitle": "Title", "article": "Short"},  # Too short
        ]
        
        for invalid_input in invalid_inputs:
            is_valid, error_message = validate_article_data(invalid_input)
            assert is_valid is False
            assert len(error_message) > 0