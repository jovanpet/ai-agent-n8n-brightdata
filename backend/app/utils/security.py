"""
Security utilities for input validation and sanitization
"""
import re
import html
from typing import Dict, Any, List, Tuple


class SecurityValidator:
    """Security validation and sanitization utilities"""
    
    # Maximum allowed lengths for different fields
    MAX_DOMAIN_LENGTH = 255
    MAX_TITLE_LENGTH = 500
    MAX_ARTICLE_LENGTH = 1_000_000  # 1MB of text
    
    # Dangerous patterns that could indicate injection attempts
    DANGEROUS_PATTERNS = [
        # Script injection patterns
        r'<script[\s\S]*?</script>',
        r'<iframe[\s\S]*?</iframe>',
        r'javascript:[\s\S]*',
        r'vbscript:[\s\S]*',
        r'on\w+\s*=[\s\S]*',  # Any event handler
        r'alert\s*\(',
        r'eval\s*\(',
        r'document\.',
        
        # SQL injection patterns
        r'union\s+select[\s\S]*',
        r'drop\s+table[\s\S]*',
        r'delete\s+from[\s\S]*',
        r'insert\s+into[\s\S]*',
        r'update\s+[\s\S]*\s+set',
        r'exec\s*\([\s\S]*\)',
        r'execute\s*\([\s\S]*\)',
        r'xp_cmdshell',
        
        # Command injection patterns
        r'\|\s*nc\s[\s\S]*',
        r'\|\s*netcat\s[\s\S]*',
        r';\s*rm\s[\s\S]*',
        r';\s*curl\s[\s\S]*',
        r';\s*wget\s[\s\S]*',
        r'`[^`]*`',
        r'\$\([^)]*\)',
        r'cat\s+/etc/',
        
        # Path traversal
        r'\.\./',
        r'\.\.\\',
        
        # Template injection
        r'\{\{[^}]*\}\}',
        r'\{%[^%]*%\}',
        r'\{\$[^}]*\}',
        
        # XSS patterns
        r'<img[\s\S]*?onerror[\s\S]*?>',
        r'<svg[\s\S]*?onload[\s\S]*?>',
        r'data:text/html[\s\S]*',
        r'data:image/svg\+xml[\s\S]*',
    ]
    
    # Common phishing/malicious domains (basic list)
    SUSPICIOUS_DOMAINS = {
        'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly',
        'clickjacking.com', 'phishing.com', 'malware.com'
    }
    
    @classmethod
    def sanitize_text(cls, text: str, allow_html: bool = False) -> str:
        """
        Sanitize text input to prevent injection attacks
        
        Args:
            text: Raw text input
            allow_html: Whether to preserve HTML tags (escaped)
            
        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Remove null bytes and control characters
        text = text.replace('\x00', '').replace('\r\n', '\n')
        
        # Remove or escape HTML depending on allow_html flag
        if allow_html:
            # Escape HTML to prevent XSS but preserve structure
            text = html.escape(text, quote=True)
        else:
            # Strip HTML tags completely
            text = re.sub(r'<[^>]+>', '', text)
            text = html.unescape(text)  # Decode HTML entities
        
        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            text = re.sub(pattern, '[FILTERED]', text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @classmethod
    def validate_domain(cls, domain: str) -> Tuple[bool, str]:
        """
        Validate domain name for security issues
        
        Args:
            domain: Domain to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not domain or not isinstance(domain, str):
            return False, "Domain is required"
        
        domain = domain.lower().strip()
        
        # Check length
        if len(domain) > cls.MAX_DOMAIN_LENGTH:
            return False, f"Domain too long (max {cls.MAX_DOMAIN_LENGTH} characters)"
        
        if len(domain) < 3:
            return False, "Domain too short"
        
        # Basic domain format validation
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, domain):
            return False, "Invalid domain format"
        
        # Check for suspicious domains
        if domain in cls.SUSPICIOUS_DOMAINS:
            return False, "Domain appears to be suspicious"
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, domain, re.IGNORECASE):
                return False, "Domain contains suspicious patterns"
        
        return True, ""
    
    @classmethod
    def validate_article_content(cls, content: str) -> Tuple[bool, str]:
        """
        Validate article content for security and quality
        
        Args:
            content: Article content to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content or not isinstance(content, str):
            return False, "Article content is required"
        
        content = content.strip()
        
        # Check length limits
        if len(content) > cls.MAX_ARTICLE_LENGTH:
            return False, f"Article too long (max {cls.MAX_ARTICLE_LENGTH} characters)"
        
        if len(content) < 50:
            return False, "Article too short (minimum 50 characters)"
        
        # Check for suspicious content ratio
        suspicious_char_count = len(re.findall(r'[<>{}\[\]\\`$]', content))
        if suspicious_char_count > len(content) * 0.1:  # More than 10% suspicious chars
            return False, "Content contains too many suspicious characters"
        
        # Check for repeated patterns that might indicate spam
        if cls._detect_spam_patterns(content):
            return False, "Content appears to be spam or auto-generated"
        
        # Check for extremely long words (possible injection payloads)
        words = content.split()
        for word in words:
            if len(word) > 100:  # Any word longer than 100 chars is suspicious
                return False, "Content contains suspiciously long words"
        
        return True, ""
    
    @classmethod
    def validate_title(cls, title: str) -> Tuple[bool, str]:
        """
        Validate article title
        
        Args:
            title: Title to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not title or not isinstance(title, str):
            return False, "Title is required"
        
        title = title.strip()
        
        # Check length
        if len(title) > cls.MAX_TITLE_LENGTH:
            return False, f"Title too long (max {cls.MAX_TITLE_LENGTH} characters)"
        
        if len(title) < 3:
            return False, "Title too short (minimum 3 characters)"
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                return False, "Title contains suspicious patterns"
        
        return True, ""
    
    @classmethod
    def sanitize_article_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive sanitization of article submission data
        
        Args:
            data: Raw article data
            
        Returns:
            Sanitized data dictionary
        """
        if not isinstance(data, dict):
            return {}
        
        sanitized = {}
        
        # Sanitize company domain
        domain = data.get('companyDomain', '')
        sanitized['company_domain'] = cls.sanitize_text(str(domain), allow_html=False)[:cls.MAX_DOMAIN_LENGTH]
        
        # Sanitize title
        title = data.get('articleTitle', '')
        sanitized['article_title'] = cls.sanitize_text(str(title), allow_html=False)[:cls.MAX_TITLE_LENGTH]
        
        # Sanitize article content
        article = data.get('article', '')
        sanitized['article'] = cls.sanitize_text(str(article), allow_html=False)[:cls.MAX_ARTICLE_LENGTH]
        
        return sanitized
    
    @classmethod
    def comprehensive_validation(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Run all validation checks on article data
        
        Args:
            data: Article data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not isinstance(data, dict):
            return False, ["Invalid data format"]
        
        # Extract and sanitize data
        domain = str(data.get('companyDomain', '')).strip()
        title = str(data.get('articleTitle', '')).strip()
        article = str(data.get('article', '')).strip()
        
        # Validate domain
        is_valid, error = cls.validate_domain(domain)
        if not is_valid:
            errors.append(f"Domain validation failed: {error}")
        
        # Validate title
        is_valid, error = cls.validate_title(title)
        if not is_valid:
            errors.append(f"Title validation failed: {error}")
        
        # Validate article content
        is_valid, error = cls.validate_article_content(article)
        if not is_valid:
            errors.append(f"Article validation failed: {error}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def _detect_spam_patterns(cls, text: str) -> bool:
        """
        Detect common spam patterns in text
        
        Args:
            text: Text to analyze
            
        Returns:
            True if spam patterns detected
        """
        # Check for excessive repetition
        words = text.lower().split()
        if len(words) > 20:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # If any word appears more than 20% of the time, it's likely spam
            max_freq = max(word_freq.values())
            if max_freq > len(words) * 0.2:
                return True
        
        # Check for excessive punctuation or special characters
        special_chars = len(re.findall(r'[!@#$%^&*()_+=\[\]{};:"|<>?]', text))
        if special_chars > len(text) * 0.15:  # More than 15% special chars
            return True
        
        # Check for common spam phrases
        spam_phrases = [
            'click here', 'buy now', 'limited time', 'act now', 'free money',
            'earn money fast', 'work from home', 'lose weight fast',
            'enlarge your', 'nigerian prince', 'lottery winner'
        ]
        
        text_lower = text.lower()
        spam_count = sum(1 for phrase in spam_phrases if phrase in text_lower)
        if spam_count >= 2:  # Multiple spam phrases indicate spam
            return True
        
        return False


def sanitize_for_processing(text: str) -> str:
    """
    Quick sanitization function for text processing
    Removes dangerous content while preserving text for analysis
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text safe for processing
    """
    return SecurityValidator.sanitize_text(text, allow_html=True)