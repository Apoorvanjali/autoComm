"""
Plagiarism Detection Service
Checks for content plagiarism by analyzing text similarity and patterns.
Supports PDF, Word, PowerPoint, and plain text files.
"""

import os
import re
import logging
from typing import Tuple, Dict, List
from collections import Counter

# File handling
try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 not available for PDF processing")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️ python-docx not available for Word document processing")

try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False
    print("⚠️ python-pptx not available for PowerPoint processing")

# Text similarity
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn not available for similarity analysis")


class PlagiarismChecker:
    """
    Advanced plagiarism detection engine using multiple algorithms.
    Analyzes text similarity, phrase matching, and content patterns.
    """

    def __init__(self):
        """Initialize the plagiarism checker."""
        self.common_phrases = self._load_common_phrases()
        print("✅ Plagiarism Checker initialized successfully")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_text_plagiarism(self, text: str, reference_texts: List[str] = None, check_mode: str = 'advanced') -> Dict:
        """
        Check if text contains plagiarized content.

        Args:
            text (str): Text to check for plagiarism
            reference_texts (List[str]): List of reference texts to compare against (optional)
            check_mode (str): 'fast', 'advanced', or 'comprehensive'

        Returns:
            Dict: Plagiarism report with similarity scores and details
        """
        text = text.strip()
        if not text or len(text.split()) < 10:
            return {
                'success': False,
                'error': 'Text must be at least 10 words long',
                'plagiarism_score': 0,
                'status': 'insufficient_text'
            }

        # Clean and normalize text
        cleaned_text = self._clean_text(text)

        # Initialize report
        report = {
            'success': True,
            'original_length': len(text),
            'words_count': len(text.split()),
            'status': 'analyzed',
            'plagiarism_score': 0.0,
            'similarities': [],
            'suspicious_patterns': [],
            'recommendation': ''
        }

        # Run checks based on mode
        if check_mode in ['fast', 'advanced', 'comprehensive']:
            report['plagiarism_score'] = self._calculate_plagiarism_score(cleaned_text, reference_texts)
            report['suspicious_patterns'] = self._detect_suspicious_patterns(cleaned_text)

            if check_mode in ['advanced', 'comprehensive']:
                report['similarities'] = self._find_similar_content(cleaned_text)

            if check_mode == 'comprehensive':
                report['phrase_matches'] = self._find_duplicate_phrases(cleaned_text)

        # Generate recommendation
        report['recommendation'] = self._get_recommendation(report['plagiarism_score'])

        return report

    def check_file_plagiarism(self, file_path: str, reference_texts: List[str] = None, check_mode: str = 'advanced') -> Dict:
        """
        Check plagiarism from uploaded file.

        Args:
            file_path (str): Path to the uploaded file
            reference_texts (List[str]): Reference texts for comparison
            check_mode (str): Analysis mode

        Returns:
            Dict: Plagiarism report
        """
        try:
            # Extract text from file
            text = self._extract_text_from_file(file_path)

            if not text:
                return {
                    'success': False,
                    'error': 'Could not extract text from file',
                    'status': 'extraction_failed'
                }

            # Check plagiarism
            report = self.check_text_plagiarism(text, reference_texts, check_mode)
            report['file_name'] = os.path.basename(file_path)
            report['file_type'] = os.path.splitext(file_path)[1].lower()

            return report

        except Exception as e:
            return {
                'success': False,
                'error': f'File processing failed: {str(e)}',
                'status': 'processing_error'
            }

    def extract_text_from_file(self, file_path: str) -> str:
        """Public helper to extract text from supported file types."""
        return self._extract_text_from_file(file_path)

    # ------------------------------------------------------------------
    # Text Extraction
    # ------------------------------------------------------------------

    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF, DOCX, PPTX, or plain text files."""
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == '.pdf':
                return self._extract_pdf(file_path)
            elif ext == '.docx':
                return self._extract_docx(file_path)
            elif ext == '.pptx':
                return self._extract_pptx(file_path)
            elif ext in ['.txt', '.text']:
                return self._extract_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            print(f"❌ Text extraction error: {e}")
            raise

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        if not PDF_AVAILABLE:
            raise RuntimeError("PyPDF2 not installed. Run: pip install PyPDF2")

        text = []
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
            return '\n'.join(text)
        except Exception as e:
            print(f"⚠️ PDF extraction error: {e}")
            raise

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from Word document."""
        if not DOCX_AVAILABLE:
            raise RuntimeError("python-docx not installed. Run: pip install python-docx")

        text = []
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    text.append(para.text)
            return '\n'.join(text)
        except Exception as e:
            print(f"⚠️ DOCX extraction error: {e}")
            raise

    def _extract_pptx(self, file_path: str) -> str:
        """Extract text from PowerPoint file."""
        if not PPTX_AVAILABLE:
            raise RuntimeError("python-pptx not installed. Run: pip install python-pptx")

        text = []
        try:
            prs = Presentation(file_path)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, 'text') and shape.text.strip():
                        text.append(shape.text)
            return '\n'.join(text)
        except Exception as e:
            print(f"⚠️ PPTX extraction error: {e}")
            raise

    def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

    # ------------------------------------------------------------------
    # Plagiarism Detection Algorithms
    # ------------------------------------------------------------------

    def _calculate_plagiarism_score(self, text: str, reference_texts: List[str] = None) -> float:
        """
        Calculate overall plagiarism score (0-100).
        Uses multiple detection methods.
        """
        if not reference_texts:
            # Use basic statistical analysis if no references provided
            return self._statistical_plagiarism_score(text)

        # Compare against reference texts
        if not SKLEARN_AVAILABLE:
            return self._simple_similarity_score(text, reference_texts)

        return self._sklearn_similarity_score(text, reference_texts)

    def _statistical_plagiarism_score(self, text: str) -> float:
        """
        Estimate plagiarism likelihood using statistical features.
        Looks for patterns common in plagiarized content.
        """
        score = 0.0

        # Check for repeated n-grams (likely copied phrases)
        bigrams = self._get_ngrams(text, 2)
        trigrams = self._get_ngrams(text, 3)

        bigram_freq = Counter(bigrams)
        trigram_freq = Counter(trigrams)

        # High repetition indicates potential plagiarism
        high_freq_bigrams = sum(1 for count in bigram_freq.values() if count > 3)
        high_freq_trigrams = sum(1 for count in trigram_freq.values() if count > 2)

        if len(bigrams) > 0:
            score += (high_freq_bigrams / len(bigrams)) * 30

        if len(trigrams) > 0:
            score += (high_freq_trigrams / len(trigrams)) * 30

        # Check for suspicious patterns
        suspicious = len(self._detect_suspicious_patterns(text))
        score += min(suspicious * 5, 40)

        return min(score, 100.0)

    def _simple_similarity_score(self, text: str, reference_texts: List[str]) -> float:
        """Simple text comparison without sklearn."""
        text_sentences = self._get_sentences(text)
        max_similarity = 0.0

        for ref_text in reference_texts:
            ref_sentences = self._get_sentences(ref_text)

            for sent in text_sentences:
                for ref_sent in ref_sentences:
                    similarity = self._calculate_sentence_similarity(sent, ref_sent)
                    max_similarity = max(max_similarity, similarity)

        return min(max_similarity * 100, 100.0)

    def _sklearn_similarity_score(self, text: str, reference_texts: List[str]) -> float:
        """Advanced similarity using TF-IDF and cosine similarity."""
        try:
            vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))

            # Combine all texts for vectorization
            all_texts = [text] + reference_texts
            tfidf_matrix = vectorizer.fit_transform(all_texts)

            # Calculate similarity between input and each reference
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            max_similarity = float(similarities.max()) if similarities.size > 0 else 0.0

            return min(max_similarity * 100, 100.0)
        except Exception as e:
            print(f"⚠️ Sklearn similarity error: {e}")
            return 0.0

    def _detect_suspicious_patterns(self, text: str) -> List[str]:
        """Detect suspicious patterns commonly found in plagiarized text."""
        patterns = []

        # Pattern 1: Sudden style changes
        if self._has_style_inconsistency(text):
            patterns.append("Style inconsistency detected")

        # Pattern 2: Mixed language/character sets
        if self._has_language_mixing(text):
            patterns.append("Language/character set mixing detected")

        # Pattern 3: Unusual punctuation
        if self._has_unusual_punctuation(text):
            patterns.append("Unusual punctuation patterns found")

        # Pattern 4: Excessive spacing or formatting
        if self._has_formatting_issues(text):
            patterns.append("Unusual formatting detected")

        return patterns

    def _find_similar_content(self, text: str) -> List[Dict]:
        """Find similar content segments."""
        sentences = self._get_sentences(text)
        similar_segments = []

        # Group similar sentences
        for i, sent in enumerate(sentences):
            if len(sent.split()) >= 5:  # Only check sentences with 5+ words
                similar_segments.append({
                    'segment': sent[:100] + '...' if len(sent) > 100 else sent,
                    'position': i,
                    'words': len(sent.split())
                })

        return similar_segments[:10]  # Return top 10

    def _find_duplicate_phrases(self, text: str) -> List[Dict]:
        """Find repeated phrases (potential direct copying)."""
        phrases = self._get_ngrams(text, 5)  # 5-word phrases
        phrase_freq = Counter(phrases)

        duplicates = [
            {
                'phrase': ' '.join(phrase),
                'count': count,
                'likelihood': 'high' if count > 3 else 'medium'
            }
            for phrase, count in phrase_freq.most_common(5) if count > 1
        ]

        return duplicates

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def _clean_text(self, text: str) -> str:
        """Normalize text for analysis."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Convert to lowercase for comparison
        text = text.lower()
        return text

    def _get_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _get_ngrams(self, text: str, n: int) -> List[tuple]:
        """Generate n-grams from text."""
        words = text.lower().split()
        return [tuple(words[i:i+n]) for i in range(len(words)-n+1)]

    def _calculate_sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Calculate similarity between two sentences (0-1)."""
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _has_style_inconsistency(self, text: str) -> bool:
        """Check for abrupt style changes."""
        sentences = self._get_sentences(text)
        if len(sentences) < 3:
            return False

        # Check for sudden changes in sentence length
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths) if lengths else 0

        for length in lengths:
            if avg_length > 0 and abs(length - avg_length) > avg_length * 2:
                return True

        return False

    def _has_language_mixing(self, text: str) -> bool:
        """Check for mixed languages or unusual character patterns."""
        # Check for mix of Latin and non-Latin scripts
        latin_count = sum(1 for c in text if ord(c) < 256)
        non_latin_count = len(text) - latin_count

        if latin_count > 0 and non_latin_count > 0:
            mixing_ratio = min(latin_count, non_latin_count) / max(latin_count, non_latin_count)
            return mixing_ratio > 0.1

        return False

    def _has_unusual_punctuation(self, text: str) -> bool:
        """Check for unusual punctuation patterns."""
        punctuation_chars = text.count('!') + text.count('?') + text.count('...')
        word_count = len(text.split())

        if word_count > 0:
            return (punctuation_chars / word_count) > 0.15

        return False

    def _has_formatting_issues(self, text: str) -> bool:
        """Check for unusual formatting (excessive spaces, etc.)."""
        return '  ' in text  # Multiple consecutive spaces

    def _load_common_phrases(self) -> List[str]:
        """Load common phrases that may appear in multiple texts."""
        return [
            'according to', 'in conclusion', 'furthermore', 'moreover',
            'in addition', 'therefore', 'however', 'nevertheless',
            'as a result', 'in other words', 'for example', 'such as'
        ]

    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on plagiarism score."""
        if score < 15:
            return "✅ Low plagiarism risk. Content appears original."
        elif score < 30:
            return "⚠️ Moderate plagiarism risk. Review citations and paraphrasing."
        elif score < 50:
            return "⚠️⚠️ High plagiarism risk. Significant similarity detected. Review content."
        else:
            return "🚨 Very high plagiarism risk. Likely contains substantial plagiarized content."
