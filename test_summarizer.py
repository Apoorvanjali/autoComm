"""
Test script for ML-based text summarization
Tests different length and style combinations
"""

import requests
import json

# Test text
test_text = """Artificial intelligence has revolutionized the way we interact with technology. Machine learning algorithms can now process vast amounts of data and identify patterns that humans might miss. Deep learning, a subset of machine learning, uses neural networks with multiple layers to analyze complex data structures. These technologies are being applied in various fields including healthcare, finance, and autonomous vehicles. Natural language processing enables computers to understand and generate human language, making chatbots and virtual assistants more sophisticated. Computer vision allows machines to interpret and understand visual information from the world. As AI continues to advance, ethical considerations become increasingly important, including issues of privacy, bias, and job displacement."""

API_URL = "http://localhost:5000/api/summarize"

def test_summarization(length, style):
    """Test summarization with given parameters"""
    print(f"\n{'='*80}")
    print(f"Testing: Length={length.upper()}, Style={style.upper()}")
    print(f"{'='*80}")
    
    payload = {
        "text": test_text,
        "summary_length": length,
        "summary_style": style
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        data = response.json()
        
        if data.get('success'):
            print(f"\n✅ SUCCESS!")
            print(f"Original Length: {data['original_length']} characters")
            print(f"Summary Length: {data['summary_length']} characters")
            print(f"Reduction: {round((1 - data['summary_length']/data['original_length'])*100, 1)}%")
            print(f"\nSummary:\n{'-'*80}")
            print(data['summary'])
            print(f"{'-'*80}")
        else:
            print(f"\n❌ ERROR: {data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    print("🧪 ML-Based Text Summarization Test Suite")
    print("Testing all combinations of length and style options\n")
    
    # Test all combinations
    lengths = ['short', 'medium', 'long']
    styles = ['paragraph', 'bullet', 'abstract']
    
    for length in lengths:
        for style in styles:
            test_summarization(length, style)
    
    print(f"\n{'='*80}")
    print("✅ All tests completed!")
    print(f"{'='*80}")
