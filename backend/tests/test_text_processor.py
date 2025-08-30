"""
Tests for text processing utilities
"""
import pytest
from app.utils.text_processor import (
    generate_summary,
    extract_keywords,
    extract_key_phrases,
    preprocess_text,
    get_extended_stop_words
)


class TestGenerateSummary:
    """Test summary generation functionality"""
    
    def test_generate_summary_basic(self):
        text = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence."
        result = generate_summary(text, max_sentences=2)
        expected = "This is the first sentence. This is the second sentence..."
        assert result == expected
    
    def test_generate_summary_with_ellipsis(self):
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = generate_summary(text, max_sentences=2)
        assert result.endswith("...")
        assert "First sentence" in result
        assert "Second sentence" in result
    
    def test_generate_summary_short_text(self):
        text = "Only one sentence."
        result = generate_summary(text, max_sentences=3)
        assert result == "Only one sentence"
    
    def test_generate_summary_empty_text(self):
        assert generate_summary("") == ""
        assert generate_summary("   ") == ""
        assert generate_summary(None) == ""
    
    def test_generate_summary_different_punctuation(self):
        text = "Question sentence? Exclamation sentence! Normal sentence."
        result = generate_summary(text, max_sentences=2)
        assert "Question sentence" in result
        assert "Exclamation sentence" in result


class TestExtractKeywords:
    """Test keyword extraction functionality"""
    
    def test_extract_keywords_basic(self):
        text = "artificial intelligence machine learning technology innovation artificial intelligence machine learning"
        keywords = extract_keywords(text, max_keywords=10)
        # Check that meaningful words are extracted (might not be all due to TF-IDF scoring)
        keyword_string = ' '.join(keywords).lower()
        assert any(word in keyword_string for word in ["artificial", "intelligence", "machine", "learning", "technology"])
    
    def test_extract_keywords_filters_stop_words(self):
        text = "The quick brown fox jumps over the lazy dog. The fox is very quick and intelligent."
        keywords = extract_keywords(text, max_keywords=10)
        # Should not contain common stop words
        assert "the" not in keywords
        assert "is" not in keywords
        assert "and" not in keywords
        # Should contain meaningful words
        assert "fox" in keywords or "quick" in keywords
    
    def test_extract_keywords_short_text(self):
        short_text = "Too short"
        keywords = extract_keywords(short_text)
        assert keywords == []
    
    def test_extract_keywords_empty_text(self):
        assert extract_keywords("") == []
        assert extract_keywords(None) == []
    
    def test_extract_keywords_max_limit(self):
        long_text = " ".join([f"word{i}" for i in range(100)]) * 3  # Create many unique words
        keywords = extract_keywords(long_text, max_keywords=5)
        assert len(keywords) <= 5


class TestExtractKeyPhrases:
    """Test key phrase extraction functionality"""
    
    def test_extract_key_phrases_basic(self):
        text = "Machine learning algorithms are becoming increasingly sophisticated. " \
               "Artificial intelligence systems can now process natural language. " \
               "Deep learning networks show remarkable performance in image recognition. " \
               "Machine learning algorithms continue to evolve rapidly."
        phrases = extract_key_phrases(text, max_phrases=5)
        assert any("machine learning" in phrase for phrase in phrases)
        assert any("artificial intelligence" in phrase for phrase in phrases)
    
    def test_extract_key_phrases_short_text(self):
        short_text = "Too short for phrases."
        phrases = extract_key_phrases(short_text)
        assert phrases == []
    
    def test_extract_key_phrases_empty_text(self):
        assert extract_key_phrases("") == []
        assert extract_key_phrases(None) == []
    
    def test_extract_key_phrases_max_limit(self):
        long_text = ("This is a sentence about data science and machine learning. " * 10)
        phrases = extract_key_phrases(long_text, max_phrases=3)
        assert len(phrases) <= 3


class TestPreprocessText:
    """Test text preprocessing functionality"""
    
    def test_preprocess_text_basic(self):
        text = "The Quick Brown Fox Jumps!"
        stop_words = {"the", "and", "is"}
        result = preprocess_text(text, stop_words)
        assert "quick" in result
        assert "brown" in result
        assert "fox" in result
        assert "jumps" in result
        assert "the" not in result
    
    def test_preprocess_text_filters_short_words(self):
        text = "I am a big dog"
        stop_words = set()
        result = preprocess_text(text, stop_words)
        # Should filter out words shorter than 3 characters
        assert "am" not in result
        assert "big" in result
        assert "dog" in result
    
    def test_preprocess_text_filters_digits(self):
        text = "The year 2024 was great with 100 improvements"
        stop_words = {"the", "was", "with"}
        result = preprocess_text(text, stop_words)
        assert "2024" not in result
        assert "100" not in result
        assert "year" in result
        assert "great" in result
    
    def test_preprocess_text_handles_long_words(self):
        text = "Normal word verylongwordthatshouldbefilteredout another"
        stop_words = set()
        result = preprocess_text(text, stop_words)
        assert "normal" in result
        assert "another" in result
        assert "verylongwordthatshouldbefilteredout" not in result


class TestGetExtendedStopWords:
    """Test stop words functionality"""
    
    def test_get_extended_stop_words_returns_set(self):
        stop_words = get_extended_stop_words()
        assert isinstance(stop_words, set)
        assert len(stop_words) > 0
    
    def test_get_extended_stop_words_contains_basic_words(self):
        stop_words = get_extended_stop_words()
        assert "the" in stop_words
        assert "and" in stop_words
        assert "for" in stop_words
        assert "are" in stop_words
    
    def test_get_extended_stop_words_contains_extended_words(self):
        stop_words = get_extended_stop_words()
        assert "also" in stop_words
        assert "would" in stop_words
        assert "always" in stop_words


# Integration tests
class TestTextProcessorIntegration:
    """Integration tests for text processing functions"""
    
    def test_full_article_processing(self):
        article = """
        Artificial intelligence and machine learning are transforming the business landscape. 
        Companies are increasingly adopting AI technologies to improve efficiency and innovation. 
        Deep learning algorithms can process vast amounts of data and identify complex patterns. 
        Natural language processing enables computers to understand human communication. 
        Machine learning models continue to evolve and become more sophisticated over time.
        """
        
        # Test all functions work together
        summary = generate_summary(article)
        keywords = extract_keywords(article)
        phrases = extract_key_phrases(article)
        
        assert len(summary) > 0
        assert len(keywords) > 0
        assert len(phrases) > 0
        
        # Check for expected content
        assert "artificial" in keywords or "intelligence" in keywords
        assert any("machine learning" in phrase for phrase in phrases)
    
    def test_edge_case_handling(self):
        """Test how functions handle edge cases"""
        edge_cases = ["", "   ", "A", "Short text.", None]
        
        for case in edge_cases:
            # Should not crash on any edge case
            if case is not None:
                summary = generate_summary(case)
                keywords = extract_keywords(case) 
                phrases = extract_key_phrases(case)
                
                assert isinstance(summary, str)
                assert isinstance(keywords, list)
                assert isinstance(phrases, list)