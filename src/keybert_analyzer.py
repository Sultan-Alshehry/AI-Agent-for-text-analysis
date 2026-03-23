from typing import List, Tuple, Dict


# Extract keywords using KeyBERT model
def get_keybert_keywords(text: str, top_n: int = 5, ngram_range: Tuple[int, int] = (1, 2)) -> List[Dict[str, float]]:
    """Extract keywords from text using KeyBERT."""
    try:
        from keybert import KeyBERT
    except ImportError as exc:
        raise ImportError(
            "KeyBERT is not installed. Install with `pip install keybert sentence-transformers` "
            "or choose GenAI mode in send_prompt_online.analyze_text."
        ) from exc

# Mini LLM model is used for keyword extraction as it is faster and more efficient for this task
    model = KeyBERT(model="all-MiniLM-L6-v2")
    keywords = model.extract_keywords(
        text,
        keyphrase_ngram_range=ngram_range,
        stop_words="english",
        top_n=top_n,
        use_maxsum=True,
    )

    return [{"keyword": kw, "score": float(score)} for kw, score in keywords]
