#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import streamlit as st
import pandas as pd

class ExperienceExtractor:
    def __init__(self):
        self.keywords = ['year', 'years', 'yrs', 'yr']
        self.min_phrases = ['minimum', 'at least', 'min']
        self.max_phrases = ['maximum', 'max', 'up to']
        self.range_indicators = ['to', '-', 'and']

    def extract_experience(self, job_description):
        job_description = self._standardize_text(job_description)
        words = job_description.split()
        experience_phrases = self._find_experience_phrases(words)

        normalized_ranges = []
        for phrase in experience_phrases:
            normalized = self._normalize_experience(phrase)
            if normalized:
                normalized_ranges.append((phrase, normalized))

        return normalized_ranges[0] if normalized_ranges else (None, None)

    def _standardize_text(self, text):
        text = text.lower().replace('+', ' + ').replace('-', ' - ')
        text = re.sub(r"[^\w\s\+\-\.]", "", text)
        return text

    def _find_experience_phrases(self, words):
        phrases = []
        for i, word in enumerate(words):
            if any(key in word for key in self.keywords):
                start = max(0, i - 5)
                end = min(len(words), i + 5)
                context = words[start:end]
                phrases.append(' '.join(context))
        return phrases

    def _normalize_experience(self, phrase):
        numbers = [float(n) for n in re.findall(r'\d+(?:\.\d+)?', phrase)]
        if not numbers:
            return None
        if 'fresh' in phrase or 'graduate' in phrase:
            return "Entry Level"

        def fmt(x): return int(x) if x.is_integer() else round(x, 1)

        if any(min_word in phrase for min_word in self.min_phrases):
            min_val = numbers[0]
            return f"{fmt(min_val)} - {fmt(min_val+2)} Years"
        if any(max_word in phrase for max_word in self.max_phrases):
            max_val = numbers[0]
            return f"{fmt(max_val-2)} - {fmt(max_val)} Years"
        if '+' in phrase and len(numbers) == 1:
            min_val = numbers[0]
            return f"{fmt(min_val)} - {fmt(min_val+2)} Years"
        if any(ind in phrase for ind in self.range_indicators) and len(numbers) >= 2:
            return f"{fmt(min(numbers))} - {fmt(max(numbers))} Years"
        if len(numbers) == 1:
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

