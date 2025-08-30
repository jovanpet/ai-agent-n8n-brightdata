"""
Text processing utilities for article analysis
"""
import re
import math
from collections import Counter, defaultdict
from typing import List, Dict, Tuple


def generate_summary(text: str, max_sentences: int = 3) -> str:
    """
    Generate a summary by taking the first few sentences
    
    Args:
        text: Input text to summarize
        max_sentences: Maximum number of sentences to include
        
    Returns:
        Summary string
    """
    if not text or not text.strip():
        return ""
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= max_sentences:
        return '. '.join(sentences)
    
    return '. '.join(sentences[:max_sentences]) + '...'


def extract_keywords(text: str, max_keywords: int = 15) -> List[str]:
    """
    Extract keywords using TF-IDF-like scoring with improved filtering
    
    Args:
        text: Input text to analyze
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords sorted by relevance
    """
    if not text or len(text.strip()) < 50:
        return []
    
    # Enhanced stop words list
    stop_words = get_extended_stop_words()
    
    # Clean and tokenize text
    words = preprocess_text(text, stop_words)
    
    if len(words) < 10:
        return list(set(words))[:max_keywords]
    
    # Calculate term frequency
    word_freq = Counter(words)
    total_words = len(words)
    
    # Calculate TF scores
    tf_scores = {}
    for word, freq in word_freq.items():
        tf_scores[word] = freq / total_words
    
    # Calculate document frequency (simulate corpus with sentences)
    sentences = re.split(r'[.!?]+', text)
    doc_freq = defaultdict(int)
    
    for sentence in sentences:
        sentence_words = set(preprocess_text(sentence.lower(), stop_words))
        for word in sentence_words:
            if word in word_freq:
                doc_freq[word] += 1
    
    # Calculate TF-IDF scores
    tfidf_scores = {}
    num_sentences = len([s for s in sentences if s.strip()])
    
    for word in word_freq:
        if doc_freq[word] > 0:
            idf = math.log(num_sentences / doc_freq[word])
            tfidf_scores[word] = tf_scores[word] * idf
        else:
            tfidf_scores[word] = tf_scores[word]
    
    # Boost longer words and words that appear early in text
    boosted_scores = {}
    text_words = words[:100]  # First 100 words get position boost
    
    for word, score in tfidf_scores.items():
        # Length boost (favor longer, more specific terms)
        length_boost = min(len(word) / 6, 2.0) if len(word) > 4 else 1.0
        
        # Position boost (early words are often more important)
        position_boost = 1.2 if word in text_words else 1.0
        
        # Frequency threshold (avoid very rare words)
        if word_freq[word] >= 2 or len(word) > 6:
            boosted_scores[word] = score * length_boost * position_boost
    
    # Sort by score and return top keywords
    sorted_keywords = sorted(boosted_scores.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, _ in sorted_keywords[:max_keywords]]


def extract_key_phrases(text: str, max_phrases: int = 8) -> List[str]:
    """
    Extract meaningful phrases that contain important keywords
    
    Args:
        text: Input text to analyze
        max_phrases: Maximum number of phrases to return
        
    Returns:
        List of key phrases sorted by relevance
    """
    if not text or len(text.strip()) < 100:
        return []
    
    stop_words = get_extended_stop_words()
    
    # First get the top keywords to guide phrase extraction
    keywords = extract_keywords(text, max_keywords=20)
    keyword_set = set(keywords)
    
    # Split into sentences and clean
    sentences = re.split(r'[.!?]+', text)
    phrases = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:
            continue
            
        # Extract words from sentence
        words = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
        
        # Look for 2-4 word combinations that contain keywords
        for i in range(len(words) - 1):
            for length in [2, 3, 4]:
                if i + length <= len(words):
                    phrase_words = words[i:i + length]
                    
                    # Check if phrase contains at least one keyword
                    has_keyword = any(word in keyword_set for word in phrase_words)
                    
                    # Filter out phrases with too many stop words
                    non_stop_count = sum(1 for w in phrase_words if w not in stop_words)
                    
                    # Only keep phrases that:
                    # 1. Contain at least one keyword
                    # 2. Have enough meaningful words
                    # 3. Don't start or end with stop words
                    if (has_keyword and 
                        non_stop_count >= max(1, length // 2) and
                        phrase_words[0] not in stop_words and 
                        phrase_words[-1] not in stop_words):
                        
                        phrase = ' '.join(phrase_words)
                        if len(phrase) > 8 and phrase not in phrases:
                            phrases.append(phrase)
    
    # Count phrase frequency and calculate relevance scores
    phrase_freq = Counter(phrases)
    scored_phrases = []
    
    for phrase, freq in phrase_freq.items():
        phrase_words = phrase.split()
        
        # Calculate keyword density in phrase
        keyword_count = sum(1 for word in phrase_words if word in keyword_set)
        keyword_density = keyword_count / len(phrase_words)
        
        # Score based on frequency, keyword density, and phrase length
        base_score = freq * keyword_density
        length_bonus = 1 + (len(phrase_words) - 2) * 0.1  # Slight bonus for longer phrases
        
        # Bonus for phrases that appear multiple times or have high keyword density
        if freq >= 2 or keyword_density >= 0.5:
            final_score = base_score * length_bonus
            scored_phrases.append((phrase, final_score))
    
    # Sort and return top phrases
    scored_phrases.sort(key=lambda x: x[1], reverse=True)
    return [phrase for phrase, _ in scored_phrases[:max_phrases]]


def preprocess_text(text: str, stop_words: set) -> List[str]:
    """
    Clean and tokenize text for keyword extraction
    
    Args:
        text: Input text to process
        stop_words: Set of stop words to filter out
        
    Returns:
        List of cleaned words
    """
    # Convert to lowercase and extract words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter words
    filtered_words = []
    for word in words:
        if (len(word) >= 3 and 
            word not in stop_words and 
            not word.isdigit() and
            len(word) <= 20):  # Avoid very long words (likely errors)
            filtered_words.append(word)
    
    return filtered_words


def get_extended_stop_words() -> set:
    """
    Extended list of stop words for better filtering
    
    Returns:
        Set of stop words
    """
    return {
        # Basic stop words
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
        'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy',
        'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'that', 'with',
        'have', 'this', 'will', 'your', 'from', 'they', 'know', 'want', 'been',
        'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just',
        'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them',
        'well', 'were', 'what',
        
        # Additional common words
        'also', 'after', 'back', 'other', 'more', 'most', 'first', 'last',
        'each', 'which', 'there', 'would', 'could', 'should', 'about', 'into',
        'only', 'think', 'where', 'being', 'both', 'during', 'before', 'after',
        'above', 'below', 'between', 'through', 'same', 'different', 'another',
        'without', 'within', 'still', 'again', 'against', 'while', 'since',
        
        # Articles and prepositions
        'a', 'an', 'as', 'at', 'be', 'by', 'do', 'he', 'if', 'in', 'is', 'it',
        'my', 'no', 'of', 'on', 'or', 'so', 'to', 'up', 'we', 'me', 'am',
        
        # Common verbs that are rarely keywords
        'said', 'says', 'going', 'goes', 'went', 'come', 'came', 'made', 'makes',
        'look', 'looks', 'looked', 'give', 'gives', 'gave', 'told', 'tell',
        'asked', 'ask', 'find', 'found', 'left', 'right', 'start', 'started',
        'stop', 'stopped', 'turn', 'turned', 'work', 'worked', 'play', 'played', 'quot',
        
        # Time and quantity words that are usually not meaningful
        'year', 'years', 'month', 'months', 'week', 'weeks', 'today', 'tomorrow',
        'yesterday', 'always', 'never', 'often', 'sometimes', 'usually', 'once',
        'twice', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'
    }