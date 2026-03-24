"""
Text Summarization Service
Uses BART transformer model with intelligent extraction-based fallback.
Works reliably for any length of input text.
"""

import re
import logging
from collections import Counter

# Try loading transformer-based summarizer (best quality)
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not available, using extraction-based summarization")

# Length configuration mapping (in tokens/chars)
LENGTH_CONFIGS = {
    'short':  {'min_length': 30,  'max_length': 130},   # ~30-65 words
    'medium': {'min_length': 80,  'max_length': 250},   # ~40-125 words
    'long':   {'min_length': 150, 'max_length': 400},   # ~75-200 words
}

# Extraction ratio for fallback
EXTRACTION_RATIOS = {
    'short': 0.15,
    'medium': 0.30,
    'long': 0.45,
}


class TextSummarizer:
    def __init__(self):
        """
        Initialize the text summarizer. Tries BART model first, falls back
        to TF-IDF-style extractive summarizer.
        """
        self.summarizer = None
        self._model_init_attempted = False

        # Do not download/load heavy models at app startup. We initialize
        # transformer pipelines lazily on the first summarize request.
        if TRANSFORMERS_AVAILABLE:
            print("✅ Text Summarizer ready (transformer model will load on first use)")
        else:
            print("✅ Text Summarizer initialized with extractive fallback")

    def _ensure_model(self):
        """Initialize transformer model once, on demand."""
        if self._model_init_attempted or not TRANSFORMERS_AVAILABLE:
            return

        self._model_init_attempted = True

        # Prefer a lighter DistilBART model first, then a higher-quality fallback.
        for model_name in [
            "sshleifer/distilbart-cnn-6-6",
            "facebook/bart-large-cnn",
        ]:
            try:
                self.summarizer = pipeline(
                    "summarization",
                    model=model_name,
                    tokenizer=model_name,
                )
                print(f"✅ Text Summarizer initialized with model: {model_name}")
                return
            except Exception as e:
                print(f"⚠️  Model {model_name} unavailable: {e}")

        print("✅ Falling back to extractive summarization (no transformer model loaded)")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def summarize(self, text, length='medium', style='paragraph'):
        """
        Summarize the given text.

        Args:
            text (str): Input text (any length, any topic)
            length (str): 'short' | 'medium' | 'long'
            style (str): 'paragraph' | 'bullet' | 'abstract'

        Returns:
            str: Summarized and formatted text
        """
        text = self._clean_text(text)

        if not text or len(text.split()) < 20:
            return text  # Too short to summarize

        try:
            if self.summarizer is None and TRANSFORMERS_AVAILABLE:
                self._ensure_model()

            if self.summarizer:
                summary = self._abstractive_summarize(text, length)
            else:
                summary = self._extractive_summarize(text, length)

            return self._format_summary(summary, style)

        except Exception as e:
            print(f"❌ Summarization error: {e} — using extractive fallback")
            try:
                summary = self._extractive_summarize(text, length)
                return self._format_summary(summary, style)
            except Exception as e2:
                print(f"❌ Extractive fallback also failed: {e2}")
                # Ultimate fallback: first N sentences
                sentences = re.split(r'(?<=[.!?])\s+', text)
                return '. '.join(sentences[:3]) + '.'

    # ------------------------------------------------------------------
    # Abstractive summarization (transformer-based)
    # ------------------------------------------------------------------

    def _abstractive_summarize(self, text, length):
        """
        Use HuggingFace pipeline for abstractive summarization.
        Handles texts of arbitrary length via chunking.
        """
        config = LENGTH_CONFIGS.get(length, LENGTH_CONFIGS['medium'])
        max_len = config['max_length']
        min_len = config['min_length']

        words = text.split()
        CHUNK_WORDS = 800  # safe for BART's 1024-token limit

        if len(words) <= CHUNK_WORDS:
            # Single-pass summarization
            result = self.summarizer(
                text,
                max_length=max_len,
                min_length=min(min_len, max(1, len(words) // 4)),
                do_sample=False,
                truncation=True,
            )
            return result[0]['summary_text']
        else:
            # Multi-chunk: summarize chunks, then summarize summaries
            chunks = self._chunk_text(text, CHUNK_WORDS)
            chunk_summaries = []

            for chunk in chunks:
                if len(chunk.split()) < 20:
                    continue
                try:
                    res = self.summarizer(
                        chunk,
                        max_length=max_len,
                        min_length=min(min_len, max(1, len(chunk.split()) // 4)),
                        do_sample=False,
                        truncation=True,
                    )
                    chunk_summaries.append(res[0]['summary_text'])
                except Exception as e:
                    print(f"⚠️ Chunk summarization skipped: {e}")

            if not chunk_summaries:
                raise ValueError("All chunks failed in abstractive summarization")

            combined = ' '.join(chunk_summaries)

            # If combined is still long, summarize once more
            if len(combined.split()) > CHUNK_WORDS:
                final = self.summarizer(
                    combined,
                    max_length=max_len,
                    min_length=min_len,
                    do_sample=False,
                    truncation=True,
                )
                return final[0]['summary_text']

            return combined

    # ------------------------------------------------------------------
    # Extractive summarization (TF-IDF scoring — no model needed)
    # ------------------------------------------------------------------

    def _extractive_summarize(self, text, length='medium'):
        """
        Score sentences by importance using word frequency (TF-IDF inspired).
        Works for any topic, any language that uses spaces.
        """
        ratio = EXTRACTION_RATIOS.get(length, 0.30)

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if len(s.split()) > 3]

        if len(sentences) <= 3:
            return text  # Already short enough

        # Build word frequency table (excluding stopwords)
        STOPWORDS = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'shall', 'can',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            'it', 'its', 'this', 'that', 'these', 'those', 'and', 'but',
            'or', 'nor', 'so', 'yet', 'as', 'if', 'when', 'then', 'than',
            'also', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'each', 'more', 'other', 'some',
            'such', 'no', 'only', 'same', 'too', 'very', 'just', 'not',
            'i', 'we', 'you', 'he', 'she', 'they', 'them', 'their', 'our',
            'your', 'my', 'his', 'her', 'up', 'out', 'which', 'who', 'what',
        }

        words = re.findall(r'\b\w+\b', text.lower())
        freq = Counter(w for w in words if w not in STOPWORDS and len(w) > 2)

        # Normalize frequencies
        if freq:
            max_freq = freq.most_common(1)[0][1]
            freq = {k: v / max_freq for k, v in freq.items()}

        # Score each sentence
        scored = []
        for i, sentence in enumerate(sentences):
            words_in_sent = re.findall(r'\b\w+\b', sentence.lower())
            score = sum(freq.get(w, 0) for w in words_in_sent if w not in STOPWORDS)
            # Normalize by sentence length to avoid bias towards long sentences
            score = score / max(len(words_in_sent), 1)
            # Small bonus to early and late sentences (topic + conclusion)
            if i == 0:
                score *= 1.5
            elif i == len(sentences) - 1:
                score *= 1.2
            scored.append((score, i, sentence))

        # Select top-scoring sentences (preserving original order)
        num_to_select = max(2, int(len(sentences) * ratio))
        top = sorted(scored, key=lambda x: -x[0])[:num_to_select]
        top.sort(key=lambda x: x[1])  # restore original order

        return ' '.join(s for _, _, s in top)

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def _format_summary(self, summary, style):
        """
        Format the summary text according to desired output style.
        """
        summary = summary.strip()

        if style == 'bullet':
            sentences = re.split(r'(?<=[.!?])\s+', summary)
            bullets = [f"• {s.strip()}" for s in sentences if s.strip()]
            return '\n'.join(bullets) if bullets else summary

        elif style == 'abstract':
            sentences = re.split(r'(?<=[.!?])\s+', summary)
            sentences = [s.strip() for s in sentences if s.strip()]
            if not sentences:
                return summary

            result = f"**Abstract**\n\n{sentences[0]}"
            if len(sentences) > 1:
                key_points = [f"• {s}" for s in sentences[1:]]
                result += "\n\n**Key Points:**\n" + '\n'.join(key_points)
            return result

        else:  # 'paragraph' or unknown
            return summary

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _clean_text(self, text):
        """
        Clean input text: remove excessive whitespace, fix encoding issues.
        """
        text = text.strip()
        # Normalize whitespace
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    def _chunk_text(self, text, chunk_words):
        """
        Split text into word-count-limited chunks, breaking on sentence boundaries.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        chunks = []
        current_chunk = []
        current_count = 0

        for sentence in sentences:
            word_count = len(sentence.split())
            if current_count + word_count > chunk_words and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_count = word_count
            else:
                current_chunk.append(sentence)
                current_count += word_count

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks