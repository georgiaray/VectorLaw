#!/usr/bin/env python3
"""
Language Detection and Translation Script

This script provides functions for detecting languages in text and translating
non-English text to English. Supports both full translation and English-only filtering.
"""

import re
import time
from pathlib import Path
from typing import Optional, Tuple

from langdetect import detect, DetectorFactory
from nltk import sent_tokenize

DetectorFactory.seed = 0  # For consistent results

try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False
    print("Warning: deep-translator not installed. Translation features will be unavailable.")


def chinese_sent_tokenize(text: str) -> list:
    """
    Tokenize Chinese text into sentences using Chinese punctuation marks.
    Chinese uses different punctuation: 。(period), ！(exclamation), ？(question mark)
    Also handles some English-style punctuation mixed in Chinese text.
    """
    # Replace Chinese punctuation with placeholder + newline for splitting
    text = re.sub(r'([。！？!?；])', r'\1\n', text)
    
    # Split by newlines and filter out empty strings
    sentences = [s.strip() for s in text.split('\n') if s.strip()]
    
    # Filter out very short "sentences" that are likely headers or page numbers
    sentences = [s for s in sentences if len(s) > 3]
    
    return sentences


def smart_sent_tokenize(text: str, language: str = 'auto') -> list:
    """
    Tokenize text into sentences based on language.
    For Chinese (zh), uses Chinese punctuation.
    For other languages, uses NLTK's sent_tokenize.
    """
    if language in ['zh', 'zh-CN', 'zh-TW']:
        return chinese_sent_tokenize(text)
    else:
        # Use NLTK for English and other Latin-script languages
        return sent_tokenize(text)


def detect_language(text: str, sample_size: int = 1000) -> str:
    """
    Detect the language of a text sample.
    
    Args:
        text: Text to detect language for
        sample_size: Number of characters to use for detection (default: 1000)
    
    Returns:
        Language code (e.g., 'en', 'pt', 'zh', 'fr')
    """
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        raise ValueError("Text is empty or invalid")
    
    # Use a sample for faster detection
    sample = text[:sample_size] if len(text) > sample_size else text
    return detect(sample)


def filter_english_sentences(text: str) -> Optional[str]:
    """
    Filter text to keep only English sentences.
    Detects language of each sentence and removes non-English ones.
    Returns filtered English-only text.
    
    Args:
        text: Text to filter
    
    Returns:
        Filtered text containing only English sentences, or None if input is invalid
    """
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        return None
    
    # Tokenize text into sentences
    sentences = sent_tokenize(text)
    english_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        
        # Skip empty sentences
        if not sentence:
            continue
        
        # Skip very short sentences (likely headers, page numbers, etc.)
        if len(sentence) < 10:
            english_sentences.append(sentence)  # Keep short text as-is
            continue
        
        try:
            # Detect language of this sentence
            detected_lang = detect(sentence)
            
            if detected_lang == 'en':
                english_sentences.append(sentence)
        except Exception:
            # If detection fails, keep the sentence (conservative approach)
            english_sentences.append(sentence)
    
    # Join the English sentences back together
    filtered_text = ' '.join(english_sentences)
    return filtered_text if filtered_text else None


def map_language_code(lang: str) -> str:
    """
    Map language codes from detection to GoogleTranslator format.
    Detection returns 'zh', but GoogleTranslator needs 'zh-CN' or 'zh-TW'.
    
    Args:
        lang: Language code from detection
    
    Returns:
        Mapped language code for translation
    """
    language_map = {
        'zh': 'zh-CN',  # Default Chinese to Simplified
        'zh-cn': 'zh-CN',
        'zh-tw': 'zh-TW',
    }
    return language_map.get(lang.lower(), lang)


def translate_text(
    text: str,
    source_lang: Optional[str] = None,
    target_lang: str = 'en',
    detect_source: bool = True
) -> Optional[str]:
    """
    Translate text to English (or another target language).
    
    Args:
        text: Text to translate
        source_lang: Source language code (e.g., 'pt', 'zh', 'fr'). If None, will be detected.
        target_lang: Target language code (default: 'en')
        detect_source: If True and source_lang is None, automatically detect source language
    
    Returns:
        Translated text, or None if translation fails or text is invalid
    """
    if not HAS_TRANSLATOR:
        raise ImportError("deep-translator is required for translation. Install it with: pip install deep-translator")
    
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        return None
    
    # Detect source language if needed
    if detect_source and source_lang is None:
        try:
            detected_lang = detect_language(text)
            source_lang = map_language_code(detected_lang)
        except Exception as e:
            print(f"Language detection failed: {e}")
            return None
    
    # If already in target language, return as-is
    if source_lang == target_lang:
        return text
    
    # Use language-aware tokenization
    tokenized_text = smart_sent_tokenize(text, source_lang)
    
    # Translate sentences one by one
    translated_sentences = []
    for sentence in tokenized_text:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        try:
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(sentence)
            translated_sentences.append(translated)
        except Exception as e:
            print(f"Translation error for sentence: {e}")
            # Keep original sentence on error
            translated_sentences.append(sentence)
    
    return ' '.join(translated_sentences) if translated_sentences else None


def process_text(
    text: str,
    mode: str = 'auto',
    source_lang: Optional[str] = None
) -> Tuple[Optional[str], str]:
    """
    Process text by detecting language and either translating or filtering.
    
    Args:
        text: Text to process
        mode: Processing mode - 'auto' (translate if not English), 'translate' (always translate), 
              'filter' (keep English only), or 'detect_only' (just detect language)
        source_lang: Source language code (optional, will be detected if not provided)
    
    Returns:
        Tuple of (processed_text, detected_language)
    """
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        return None, 'unknown'
    
    try:
        detected_lang = detect_language(text) if source_lang is None else source_lang
    except Exception as e:
        print(f"Language detection failed: {e}")
        return None, 'unknown'
    
    if mode == 'detect_only':
        return text, detected_lang
    
    if mode == 'filter':
        processed = filter_english_sentences(text)
        return processed, detected_lang
    
    if mode == 'translate' or (mode == 'auto' and detected_lang != 'en'):
        if not HAS_TRANSLATOR:
            print("Warning: Translation requested but deep-translator not available. Returning original text.")
            return text, detected_lang
        processed = translate_text(text, source_lang=detected_lang, detect_source=False)
        return processed, detected_lang
    
    # Already English or mode is 'auto' and text is English
    return text, detected_lang


# Note: This module is designed to be imported and used by other scripts.
# For processing CSV files with checkpointing, use process.py instead.
