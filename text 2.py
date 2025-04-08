#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
from typing import List, Tuple, Optional

class ExperienceExtractor:
    def __init__(self):
        self.keywords = ['year', 'years', 'yrs', 'yr']
        self.min_phrases = ['minimum', 'at least', 'min']
        self.max_phrases = ['maximum', 'max', 'up to']
        self.range_indicators = ['to', '-', 'and']
        self.numeric_chars = set('0123456789.')
        self.plus_minus = set('+-')

    def extract_experience(self, job_description: str) -> Tuple[Optional[str], Optional[str]]:
        job_description = self._standardize_text(job_description)
        words = job_description.split()
        experience_phrases = self._find_experience_phrases(words)

        normalized_ranges = []
        for phrase in experience_phrases:
            normalized = self._normalize_experience(phrase)
            if normalized:
                normalized_ranges.append((phrase, normalized))

        return normalized_ranges[0] if normalized_ranges else (None, None)

    def _standardize_text(self, text: str) -> str:
        text = text.lower()
        # Handle special characters by adding spaces around them
        for char in '+-':
            text = text.replace(char, f' {char} ')
        # Remove punctuation (keeping spaces and alphanumeric)
        cleaned = []
        for char in text:
            if char.isalnum() or char in ' .+-':
                cleaned.append(char)
        return ''.join(cleaned)

    def _find_experience_phrases(self, words: List[str]) -> List[str]:
        phrases = []
        for i, word in enumerate(words):
            if any(key in word for key in self.keywords):
                start = max(0, i - 5)
                end = min(len(words), i + 5)
                context = words[start:end]
                phrases.append(' '.join(context))
        return phrases

    def _extract_numbers(self, text: str) -> List[float]:
        numbers = []
        current_num = []
        in_number = False
        
        for char in text + ' ':  # Add space to trigger final number processing
            if char in self.numeric_chars:
                current_num.append(char)
                in_number = True
            elif in_number:
                num_str = ''.join(current_num)
                try:
                    num = float(num_str)
                    numbers.append(num)
                except ValueError:
                    pass
                current_num = []
                in_number = False
        
        return numbers

    def _normalize_experience(self, phrase: str) -> Optional[str]:
        if 'fresh' in phrase or 'graduate' in phrase:
            return "Entry Level"

        numbers = self._extract_numbers(phrase)
        if not numbers:
            return None

        def fmt(x): return int(x) if x.is_integer() else round(x, 1)

        words = phrase.split()
        contains_min = any(min_word in words for min_word in self.min_phrases)
        contains_max = any(max_word in words for max_word in self.max_phrases)
        contains_range = any(ind in words for ind in self.range_indicators)
        contains_plus = '+' in words

        if contains_min:
            min_val = numbers[0]
            return f"{fmt(min_val)} - {fmt(min_val+2)} Years"
        elif contains_max:
            max_val = numbers[0]
            return f"{fmt(max_val-2)} - {fmt(max_val)} Years"
        elif contains_plus and len(numbers) == 1:
            min_val = numbers[0]
            return f"{fmt(min_val)} - {fmt(min_val+2)} Years"
        elif contains_range and len(numbers) >= 2:
            return f"{fmt(min(numbers))} - {fmt(max(numbers))} Years"
        elif len(numbers) == 1:
            return f"{fmt(numbers[0])} - {fmt(numbers[0]+2)} Years"
        return None

# Streamlit UI
st.set_page_config(page_title="Experience Extractor", layout="wide")

st.title("Job Experience Extractor")
st.write("Paste job descriptions below to extract and normalize experience requirements.")

input_text = st.text_area("Enter one or more job descriptions (separated by new lines):", height=200)

if input_text:
    extractor = ExperienceExtractor()
    results = []

    for jd in input_text.strip().split('\n'):
        phrase, normalized = extractor.extract_experience(jd)
        display_phrase = phrase if phrase else "None"
        display_norm = normalized if normalized else "None"
        results.append({
            "Job Description": jd[:80] + "..." if len(jd) > 80 else jd,
            "Extracted Phrase": display_phrase,
            "Normalized Range": display_norm
        })

    df = pd.DataFrame(results)
    st.table(df)

    # Download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name='extracted_experience.csv',
        mime='text/csv',
    )