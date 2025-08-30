"""
Data formatting utilities for n8n integration
"""
from datetime import datetime, timezone
from typing import Dict, Any
from .text_processor import generate_summary, extract_keywords, extract_key_phrases
from .security import SecurityValidator, sanitize_for_processing


def create_n8n_payload(company_domain: str, article_title: str, article: str) -> Dict[str, Any]:
    """
    Create a structured payload ready for n8n consumption
    
    Args:
        company_domain: Company domain name
        article_title: Title of the article
        article: Full article content
        
    Returns:
        Dictionary containing processed data for n8n
    """
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Sanitize content for text processing (preserves content for analysis)
    safe_article = sanitize_for_processing(article)
    safe_title = sanitize_for_processing(article_title)
    safe_domain = sanitize_for_processing(company_domain)
    
    # Process article content using sanitized text
    summary = generate_summary(safe_article)
    keywords = extract_keywords(safe_article)
    phrases = extract_key_phrases(safe_article)
    
    return {
        'metadata': {
            'company_domain': safe_domain,
            'article_title': safe_title,
            'processed_at': current_time,
            'article_length': len(article),
            'word_count': len(article.split())
        },
        'content': {
            'title': safe_title,
            'body': safe_article,
            'summary': summary,
            'keywords': keywords,
            'phrases': phrases
        },
        'payload': {
            'webhook_data': {
                'domain': safe_domain,
                'title': safe_title,
                'content': safe_article,
                'summary': summary,
                'keywords': keywords,
                'phrases': phrases,
                'timestamp': current_time,
                'metadata': {
                    'word_count': len(article.split()),
                    'char_count': len(article)
                }
            }
        }
    }


def validate_article_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate incoming article data with comprehensive security checks
    
    Args:
        data: Dictionary containing article data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if data is None:
        return False, 'No data provided'
    
    if not isinstance(data, dict):
        return False, 'Invalid data format'
    
    # Check for required fields first
    required_fields = ['companyDomain', 'articleTitle', 'article']
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not str(data.get(field, '')).strip():
            missing_fields.append(field)
    
    if missing_fields:
        return False, f'Missing required fields: {", ".join(missing_fields)}'
    
    # Run comprehensive security validation
    is_valid, errors = SecurityValidator.comprehensive_validation(data)
    if not is_valid:
        return False, '; '.join(errors)
    
    return True, ''


def sanitize_input_data(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Clean and sanitize input data using security validator
    
    Args:
        data: Raw input data
        
    Returns:
        Dictionary with cleaned and sanitized data
    """
    return SecurityValidator.sanitize_article_data(data)