from functools import lru_cache
from typing import Any, Dict, List, Tuple
import re


SCIENTIFIC_EMBEDDING_CANDIDATES = (
    ("allenai/specter2_base", "SPECTER2"),
    ("allenai/specter", "SPECTER"),
    ("sentence-transformers/scibert-base-nli-stsb-mean-tokens", "SciBERT"),
)

BLOCKED_CHUNK_PHRASES = (
    "pdf available",
    "available at",
    "all rights reserved",
    "creativecommons",
    "preprint",
    "arxiv",
    "copyright",
)
MAX_TOPIC_TERMS = 4
MIN_ALPHA_WORDS_PER_CHUNK = 5
MIN_CHUNK_WORDS = 5
MIN_SENTENCE_CHUNKS = 5
MIN_WINDOW_WORDS = 12
TOPIC_WINDOW_SIZE = 45
TOPIC_WINDOW_STEP = 30


@lru_cache(maxsize=1)
def load_scientific_embedding_model() -> Tuple[object, str]:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers is required for KeyBERT + BERTopic analysis. "
            "Install with `pip install sentence-transformers`."
        ) from exc

    load_errors = []
    for index, (model_name, model_label) in enumerate(SCIENTIFIC_EMBEDDING_CANDIDATES):
        try:
            model = SentenceTransformer(model_name)
            if index > 0:
                print(f"Using fallback scientific embedding model: {model_label} ({model_name})")
            else:
                print(f"Using scientific embedding model: {model_label} ({model_name})")
            return model, model_name
        except Exception as exc:
            load_errors.append(f"{model_name}: {exc}")

    error_details = "; ".join(load_errors)
    raise RuntimeError(
        "Unable to load any scientific embedding model. "
        f"Tried: {error_details}"
    )


MEANINGLESS_TOPIC_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
    'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
    'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
    'them', 'our', 'your', 'their', 'its', 'doi', 'pp', 'vol', 'issue', 'page', 'no', 'et', 'al', 'ibid', 'op', 'cit', 'cf',
    'supra', 'infra', 'loc', 'abstract', 'introduction', 'conclusion', 'references',
    'bibliography', 'appendix', 'acknowledgments', 'acknowledgements', 'method', 'methods',
    'results', 'discussion', 'figure', 'table', 'fig', 'tab', 'section', 'chapter', 'author',
    'authors', 'year', 'years', 'published', 'journal', 'paper', 'article', 'book', 'volume',
    'available', 'pdf', 'www', 'http', 'https', 'copyright', 'preprint', 'license', 'doiorg'
}

MEANINGLESS_TOPIC_WORDS.update({
    'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
    'september', 'october', 'november', 'december'
})

GENERIC_TOPIC_LABEL_TOKENS = {
    'approach', 'based', 'collaborative', 'framework', 'management', 'model', 'models',
    'nature', 'process', 'study', 'studies', 'system', 'systems', 'use', 'using', 'work'
}

REFERENCE_SECTION_PATTERNS = (
    r'(?im)^references\s*$' ,
    r'(?im)^bibliography\s*$' ,
    r'(?im)^acknowledg(?:e)?ments?\s*$' ,
    r'(?im)^funding\s*$' ,
    r'(?im)^declarations?\s*$' ,
    r'(?im)^conflicts? of interest\s*$' ,
    r'(?im)^appendix(?:es)?\s*$'
)


def _trim_scientific_tail_sections(text: str) -> str:
    cut_index = len(text)
    for pattern in REFERENCE_SECTION_PATTERNS:
        match = re.search(pattern, text)
        if match:
            cut_index = min(cut_index, match.start())
    return text[:cut_index]


def _normalize_token(token: str) -> str:
    return re.sub(r'[^a-z]', '', token.lower())


def _normalized_topic_tokens(term: str) -> List[str]:
    return [_normalize_token(token) for token in term.split() if _normalize_token(token)]


def _clean_scientific_text(text: str) -> str:
    text = _trim_scientific_tail_sections(text)
    text = re.sub(r'\b10\.\d{4,9}/[^\s]+', '', text)
    text = re.sub(r'\b(?:pp?\.\s*\d+(?:-\d+)?|page\s+\d+|p\.\s*\d+)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(?:vol(?:ume)?\.?\s*\d+|iss(?:ue)?\.?\s*\d+|n(?:o|r)\.?\s*\d+)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(\s*[\w\s,]+\s+et\s+al\.?\s*,\s*\d{4}[^\)]*\)', '', text)
    text = re.sub(r'\[[\w\s,;,-]*\d{4}[^\]]*\]', '', text)
    text = re.sub(r'\[[0-9,;\-\s]+\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'(?im)^.*\b(?:pdf\s+available|available\s+at|creativecommons|all rights reserved|preprint)\b.*$', '', text)
    text = re.sub(r'[†*‡§¶#]', '', text)
    text = re.sub(r'\b\d+(?:\.\d+)+\s+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _is_informative_chunk(chunk: str) -> bool:
    words = chunk.split()
    if len(words) < MIN_CHUNK_WORDS:
        return False

    alpha_words = [word for word in words if re.search(r'[A-Za-z]', word)]
    if len(alpha_words) < MIN_ALPHA_WORDS_PER_CHUNK:
        return False

    lowered_chunk = chunk.lower()
    if any(phrase in lowered_chunk for phrase in BLOCKED_CHUNK_PHRASES):
        return False

    cleaned_words = [_normalize_token(word) for word in alpha_words]
    cleaned_words = [word for word in cleaned_words if word]
    if not cleaned_words:
        return False

    if sum(word in MEANINGLESS_TOPIC_WORDS for word in cleaned_words) / len(cleaned_words) > 0.6:
        return False

    titlecase_words = sum(word[:1].isupper() for word in words if word and word[0].isalpha())
    if titlecase_words >= max(4, len(words) // 2) and ',' in chunk:
        return False

    return True


def _build_topic_chunks(text: str) -> List[str]:
    sentence_candidates = [
        sentence.strip()
        for sentence in re.split(r'(?<=[.!?])\s+', text)
        if sentence.strip()
    ]
    sentences = [sentence for sentence in sentence_candidates if _is_informative_chunk(sentence)]
    if len(sentences) >= MIN_SENTENCE_CHUNKS:
        return sentences

    word_candidates = [word for word in text.split() if len(word) > 1]
    windows = [
        ' '.join(word_candidates[index:index + TOPIC_WINDOW_SIZE])
        for index in range(0, len(word_candidates), TOPIC_WINDOW_STEP)
        if len(word_candidates[index:index + TOPIC_WINDOW_SIZE]) >= MIN_WINDOW_WORDS
    ]
    filtered_windows = [window for window in windows if _is_informative_chunk(window)]
    return filtered_windows or sentences


def _is_valid_topic_term(term: str) -> bool:
    tokens = _normalized_topic_tokens(term)
    if not tokens:
        return False
    if any(token in MEANINGLESS_TOPIC_WORDS for token in tokens):
        return False
    if len(tokens) == 1 and len(tokens[0]) <= 2:
        return False
    return True


def _score_topic_term(term: str, score: float) -> float:
    tokens = _normalized_topic_tokens(term)
    if not tokens:
        return -1.0

    phrase_bonus = 1.5 if len(tokens) >= 2 else 0.0
    specificity_bonus = min(sum(len(token) for token in tokens) / 20.0, 1.0)
    acronym_penalty = 0.2 if len(tokens) == 1 and len(tokens[0]) <= 3 else 0.0
    generic_penalty = 0.7 * sum(token in GENERIC_TOPIC_LABEL_TOKENS for token in tokens)
    return float(score) + phrase_bonus + specificity_bonus - acronym_penalty - generic_penalty


def _rank_topic_terms(topic_words: List[tuple]) -> List[str]:
    ranked_candidates = []
    seen_terms = set()
    for word, score in topic_words:
        if not isinstance(word, str):
            continue
        cleaned_word = word.strip()
        if len(cleaned_word) <= 1 or not _is_valid_topic_term(cleaned_word):
            continue

        normalized_term = ' '.join(_normalized_topic_tokens(cleaned_word))
        if not normalized_term or normalized_term in seen_terms:
            continue

        ranked_candidates.append((cleaned_word, _score_topic_term(cleaned_word, score)))
        seen_terms.add(normalized_term)

    ranked_candidates.sort(key=lambda item: item[1], reverse=True)

    ranked_terms = []
    covered_single_terms = set()
    for candidate, _ in ranked_candidates:
        candidate_tokens = _normalized_topic_tokens(candidate)
        if len(candidate_tokens) == 1 and candidate_tokens[0] in covered_single_terms:
            continue
        ranked_terms.append(candidate)
        if len(candidate_tokens) >= 2:
            covered_single_terms.update(candidate_tokens)
        if len(ranked_terms) >= MAX_TOPIC_TERMS:
            break

    return ranked_terms


def _looks_like_author_topic(keywords: List[str]) -> bool:
    phrases = [keyword for keyword in keywords[:3] if len(_normalized_topic_tokens(keyword)) == 2]
    if len(phrases) < 2:
        return False

    phrase_tokens = [_normalized_topic_tokens(phrase) for phrase in phrases]
    flattened_tokens = [token for tokens in phrase_tokens for token in tokens]
    if len(flattened_tokens) != len(set(flattened_tokens)):
        return False

    if any(token in GENERIC_TOPIC_LABEL_TOKENS or token in MEANINGLESS_TOPIC_WORDS for token in flattened_tokens):
        return False

    return True


def _build_topic_result(topic_id: int, count: int, keywords: List[str]) -> Dict[str, Any]:
    return {
        "topic_id": topic_id,
        "topic_name": keywords[0],
        "keywords": keywords[:MAX_TOPIC_TERMS],
        "count": count,
        "representative_words": keywords[:MAX_TOPIC_TERMS],
    }


def _extract_ranked_topics(topic_model: Any, topic_info: Any, top_n_topics: int) -> List[Dict[str, Any]]:
    results = []
    for _, row in topic_info.iterrows():
        if row['Topic'] == -1 or len(results) >= top_n_topics:
            continue

        topic_words = topic_model.get_topic(row['Topic'])
        if not topic_words:
            continue

        keywords = _rank_topic_terms(topic_words)
        if not keywords or _looks_like_author_topic(keywords):
            continue

        results.append(_build_topic_result(int(row['Topic']), int(row['Count']), keywords))

    results.sort(
        key=lambda topic: (
            1 if isinstance(topic.get("topic_name"), str) and ' ' in topic["topic_name"].strip() else 0,
            topic.get("count", 0),
        ),
        reverse=True,
    )
    return results

# Extract topics using BERTopic model
def get_bertopic_topics(
    text: str, top_n_topics: int = 5, min_topic_size: int = 2
) -> List[Dict[str, Any]]:
    try:
        from bertopic import BERTopic
    except ImportError as exc:
        raise ImportError(
            "BERTopic is not installed. Install with `pip install bertopic sentence-transformers`"
        ) from exc

    embedding_model, embedding_model_name = load_scientific_embedding_model()

    text = _clean_scientific_text(text)
    sentences = _build_topic_chunks(text)
    if len(sentences) < 2:
        return []

    try:
        # BERTopic with parameters for meaningful topics
        topic_model = BERTopic(
            embedding_model=embedding_model,
            min_topic_size=min_topic_size,
            verbose=False,
            language="english",
            n_gram_range=(1, 2)
        )

        # Fit and transform
        topics, probs = topic_model.fit_transform(sentences)
        
        # Get topic info
        topic_info = topic_model.get_topic_info()
        return _extract_ranked_topics(topic_model, topic_info, top_n_topics)
        
    except Exception as e:
        print(f"BERTopic error with embedding model {embedding_model_name}: {e}")
        return []
    