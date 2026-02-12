"""
Text Summarization Service
Uses fallback extraction-based summarization when AI models are not available
"""

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not available, using fallback summarization")

import logging
import re

# Length configuration mapping
LENGTH_CONFIGS = {
    'short': {'min_length': 60, 'max_length': 160},    # ~30-80 words
    'medium': {'min_length': 160, 'max_length': 300},  # ~80-150 words
    'long': {'min_length': 300, 'max_length': 500}     # ~150-250 words
}

class TextSummarizer:
    def __init__(self):
        """
        Initialize the text summarization model
        """
        self.summarizer = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                # Load pre-trained summarization model from Hugging Face
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    tokenizer="facebook/bart-large-cnn"
                )
                print("✅ Text Summarizer initialized successfully")
            except Exception as e:
                # Fallback to a smaller model if the main one fails
                print(f"⚠️  Main model failed, trying fallback: {e}")
                try:
                    self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
                    print("✅ Fallback Text Summarizer initialized successfully")
                except Exception as e2:
                    print(f"❌ Failed to initialize text summarizer: {e2}")
                    self.summarizer = None
        else:
            print("✅ Text Summarizer initialized with extraction-based method")

    def summarize(self, text, length='medium', style='paragraph'):
        """
        Summarize the given text using AI
        
        Args:
            text (str): Input text to summarize
            length (str): Summary length - 'short', 'medium', or 'long'
            style (str): Summary style - 'paragraph', 'bullet', or 'abstract'
            
        Returns:
            str: Summarized text
        """
        try:
            if not self.summarizer:
                summary = self._fallback_summarize(text)
                return self._format_summary(summary, style)
            
            # Get length configuration
            length_config = LENGTH_CONFIGS.get(length, LENGTH_CONFIGS['medium'])
            max_length = length_config['max_length']
            min_length = length_config['min_length']
            
            # Clean and prepare text
            text = text.strip()
            
            # Handle very long texts by chunking
            if len(text) > 1000:
                # Split into chunks and summarize each
                chunks = self._split_text(text, 1000)
                summaries = []
                
                for chunk in chunks:
                    if len(chunk.strip()) < 50:  # Skip very short chunks
                        continue
                    
                    result = self.summarizer(
                        chunk,
                        max_length=max_length,
                        min_length=min(min_length, len(chunk.split())//4),
                        do_sample=False
                    )
                    summaries.append(result[0]['summary_text'])
                
                # Combine all summaries
                combined_summary = " ".join(summaries)
                
                # If combined summary is still too long, summarize it again
                if len(combined_summary) > max_length * 2:
                    final_result = self.summarizer(
                        combined_summary,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False
                    )
                    summary = final_result[0]['summary_text']
                else:
                    summary = combined_summary
            else:
                # Summarize directly for shorter texts
                result = self.summarizer(
                    text,
                    max_length=max_length,
                    min_length=min(min_length, len(text.split())//4),
                    do_sample=False
                )
                summary = result[0]['summary_text']
            
            # Apply style formatting
            return self._format_summary(summary, style)
                
        except Exception as e:
            print(f"❌ Summarization error: {e}")
            return self._fallback_summarize(text)

    def _format_summary(self, summary, style):
        """
        Format the summary according to the specified style
        
        Args:
            summary (str): The raw summary text
            style (str): The desired style - 'paragraph', 'bullet', or 'abstract'
            
        Returns:
            str: Formatted summary
        """
        if style == 'paragraph':
            # Default style, return as-is
            return summary
        
        elif style == 'bullet':
            # Convert to bullet points
            sentences = re.split(r'(?<=[.!?])\s+', summary.strip())
            bullets = [f"• {sentence.strip()}" for sentence in sentences if sentence.strip()]
            return '\n'.join(bullets)
        
        elif style == 'abstract':
            # Format as abstract with key points
            sentences = re.split(r'(?<=[.!?])\s+', summary.strip())
            if len(sentences) == 0:
                return summary
            
            # First sentence as main abstract
            abstract_text = f"**Abstract**\n\n{sentences[0].strip()}"
            
            # Remaining sentences as key points
            if len(sentences) > 1:
                key_points = [f"• {sentence.strip()}" for sentence in sentences[1:] if sentence.strip()]
                if key_points:
                    abstract_text += f"\n\n**Key Points:**\n" + '\n'.join(key_points)
            
            return abstract_text
        
        else:
            # Unknown style, return as paragraph
            return summary

    def _split_text(self, text, chunk_size):
        """
        Split text into chunks for processing
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_length += len(word) + 1
            if current_length > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def _fallback_summarize(self, text, ratio=0.3):
        """
        Fallback summarization using simple sentence extraction
        """
        try:
            sentences = text.split('. ')
            if len(sentences) <= 3:
                return text
            
            # Take first sentence, some middle sentences, and last sentence
            num_sentences = max(2, int(len(sentences) * ratio))
            
            # Take first sentence
            summary_sentences = [sentences[0]]
            
            # Take some sentences from middle
            middle_start = len(sentences) // 3
            middle_end = 2 * len(sentences) // 3
            middle_sentences = sentences[middle_start:middle_end]
            
            # Select sentences with important keywords
            important_keywords = ['important', 'significant', 'key', 'main', 'primary', 'essential', 'crucial']
            for sentence in middle_sentences:
                if any(keyword in sentence.lower() for keyword in important_keywords):
                    summary_sentences.append(sentence)
                    if len(summary_sentences) >= num_sentences - 1:
                        break
            
            # Add more sentences if needed
            for sentence in sentences[1:-1]:
                if sentence not in summary_sentences:
                    summary_sentences.append(sentence)
                    if len(summary_sentences) >= num_sentences - 1:
                        break
            
            # Add last sentence if meaningful
            if len(sentences) > 1 and sentences[-1] not in summary_sentences:
                summary_sentences.append(sentences[-1])
            
            return '. '.join(summary_sentences[:num_sentences]) + '.'
            
        except Exception as e:
            print(f"❌ Fallback summarization error: {e}")
            # Ultimate fallback - return first few sentences
            sentences = text.split('. ')[:3]
            return '. '.join(sentences) + '.'