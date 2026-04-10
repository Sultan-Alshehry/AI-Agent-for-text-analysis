from typing import Dict, List


KEYBERT_MODEL_NAME = "all-MiniLM-L6-v2"

# Extract keywords using KeyBERT model
def get_keybert_keywords(text: str, top_n: int = 5) -> List[Dict[str, float]]:
    try:
        from keybert import KeyBERT
    except ImportError as exc:
        raise ImportError(
            "KeyBERT is not installed. Install with `pip install keybert sentence-transformers` "
            "or choose GenAI mode in send_prompt_online.analyze_text."
        ) from exc

    model = KeyBERT(model=KEYBERT_MODEL_NAME)
    
    # Extract words
    keywords = model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 1),
        stop_words="english",
        top_n=top_n * 3,
        use_maxsum=True,
        use_mmr=True,
        diversity=0.3,
    )

    # Filter for meaningful words only
    filtered_keywords = []
    for kw, score in keywords:
        if (len(kw.split()) == 1 and 
            len(kw) > 3 and
            not any(c.isdigit() for c in kw) and
            kw.lower() not in ['that', 'with', 'have', 'this', 'will', 'your', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were']):
            
            filtered_keywords.append({"keyword": kw, "score": float(score)})
    
    # Return top results
    return sorted(filtered_keywords, key=lambda x: x["score"], reverse=True)[:top_n]
