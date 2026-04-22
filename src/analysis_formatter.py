
import re

try:
    import wordninja
except ImportError:
    wordninja = None


"""
AI Analysis Formatting Module
------------------------------
Handles normalization, selection, and formatting of AI-generated
analysis outputs for display in the UI, including:

- Keyword and topic normalization
- Label cleanup, deduplication, and ordering
- Restoration of compacted keyword phrases
- Mode-aware formatting (e.g., BERTs vs GenAI)
- Consistent string output for summaries, keywords, and topics
"""


PRESERVED_ACRONYMS = {"ai", "api", "eu", "uk", "us", "llm", "llms", "ml", "nlp", "gpt", "gdpr"}


# -------------------------------------------------------------------
# Generic helpers
# -------------------------------------------------------------------


def normalize(items):
    if items is None:
        return []
    if isinstance(items, list):
        return items
    return [items]


def _split_topic_text(topic_text):
    return [
        part.strip()
        for part in re.split(r",|\n|;", topic_text)
        if isinstance(part, str) and part.strip()
    ]


def _compact_letters(value):
    return re.sub(r"[^a-z]", "", value.lower())



# -------------------------------------------------------------------
# Topic selection
# -------------------------------------------------------------------


def _choose_topic_label(topic):
    if isinstance(topic, str):
        cleaned = topic.strip()
        if cleaned and not cleaned.startswith("Topic "):
            return cleaned
        return None

    if not isinstance(topic, dict):
        return None

    topic_name = topic.get("topic_name")
    if isinstance(topic_name, str) and topic_name.strip() and not topic_name.startswith("Topic "):
        return topic_name.strip()

    keywords = topic.get("keywords", [])
    if isinstance(keywords, list):
        
    # Prefer multi-word phrase
        phrase = next((item for item in keywords if isinstance(item, str) and ' ' in item.strip() and item.strip()), None)
        if phrase:
            return phrase.strip()
        
    # Fallback to single keyword
        keyword = next((item for item in keywords if isinstance(item, str) and item.strip()), None)
        if keyword:
            return keyword.strip()

    return None


# -------------------------------------------------------------------
# Label formatting
# -------------------------------------------------------------------


def _format_bert_label(label):
    tokens = re.split(r"(\W+)", label.strip())
    formatted_tokens = []

    for token in tokens:
        if not token:
            continue
        if token.isalpha():
            lowered = token.lower()
            if lowered in PRESERVED_ACRONYMS:
                formatted_tokens.append(lowered.upper())
            else:
                formatted_tokens.append(lowered.capitalize())
            continue
        formatted_tokens.append(token)

    return "".join(formatted_tokens)


def _format_label_for_mode(label, mode=None):
    cleaned = label.strip()
    if not cleaned:
        return cleaned
    if mode == "berts":
        return _format_bert_label(cleaned)
    return cleaned


# -------------------------------------------------------------------
# Keyword restoration
# -------


def _restore_compact_keyword_label(label, source_text=None, max_words=5):
    cleaned = " ".join(label.strip().split())
    if not cleaned or not isinstance(source_text, str) or not source_text.strip():
        return cleaned

    if " " in cleaned or "-" in cleaned or not cleaned.isalpha() or not cleaned.islower() or len(cleaned) < 12:
        return cleaned

    target = _compact_letters(cleaned)
    if not target:
        return cleaned

    source_words = re.findall(r"[A-Za-z]+", source_text)
    for start_index in range(len(source_words)):
        compact_candidate = ""
        phrase_words = []
        for word in source_words[start_index:start_index + max_words]:
            normalized_word = _compact_letters(word)
            if not normalized_word:
                continue
            compact_candidate += normalized_word
            phrase_words.append(word.lower())
            if compact_candidate == target and len(phrase_words) >= 2:
                return " ".join(phrase_words)
            if len(compact_candidate) >= len(target):
                break

    if wordninja is not None:
        segmented_words = wordninja.split(cleaned)
        segmented_target = "".join(word.lower() for word in segmented_words)
        if len(segmented_words) >= 2 and segmented_target == target:
            return " ".join(word.lower() for word in segmented_words)

    return cleaned


# -------------------------------------------------------------------
# Label normalization
# -------------------------------------------------------------------


def normalize_keyword_labels(keywords, limit=5, source_text=None, mode=None):
    labels = []

    def append_label(label):
        cleaned = _restore_compact_keyword_label(label, source_text=source_text)
        cleaned = _format_label_for_mode(cleaned, mode=mode)
        if not cleaned or cleaned in labels:
            return
        labels.append(cleaned)


    def collect(value):
        if len(labels) >= limit or value is None:
            return

        if isinstance(value, str):
            for part in _split_topic_text(value):
                append_label(part)
                if len(labels) >= limit:
                    break
            return

        if isinstance(value, dict):
            keyword = value.get("keyword") or value.get("key")
            if isinstance(keyword, str) and keyword.strip():
                append_label(keyword)
            return

        if isinstance(value, list):
            for item in value:
                collect(item)
                if len(labels) >= limit:
                    break

    collect(keywords)
    return labels


def normalize_topic_labels(topics, limit=5, mode=None):
    labels = []


    def append_label(label):
        cleaned = _format_label_for_mode(label, mode=mode)
        if not cleaned or cleaned.startswith("Topic ") or cleaned in labels:
            return
        labels.append(cleaned)


    def collect(value):
        if len(labels) >= limit or value is None:
            return

        if isinstance(value, str):
            for part in _split_topic_text(value):
                append_label(part)
                if len(labels) >= limit:
                    break
            return

        if isinstance(value, dict):
            label = _choose_topic_label(value)
            if label:
                append_label(label)
            return

        if isinstance(value, list):
            for item in value:
                collect(item)
                if len(labels) >= limit:
                    break

    collect(topics)
    return labels


# -------------------------------------------------------------------
# UI formatting
# -------------------------------------------------------------------


def stringify_analysis_items(items, limit=5, source_text=None, mode=None):
    if items is None:
        return ""

    if isinstance(items, str):
        return _format_label_for_mode(
            _restore_compact_keyword_label(items, source_text=source_text),
            mode=mode,
        )

    if isinstance(items, dict):
        keyword = items.get("keyword") or items.get("key")
        if keyword is not None:
            return _format_label_for_mode(
                _restore_compact_keyword_label(str(keyword), source_text=source_text),
                mode=mode,
            )

        label = _choose_topic_label(items)
        if label:
            return _format_label_for_mode(label, mode=mode)
        return str(items)

    if isinstance(items, list):
        formatted_items = []
        for item in items[:limit]:
            text = stringify_analysis_items(item, limit=limit, source_text=source_text, mode=mode)
            if text:
                formatted_items.append(text)
        return ", ".join(formatted_items)

    return str(items)


def format_analysis_for_ui(summary, keywords, topics, source_text=None, mode=None):
    keyword_labels = normalize_keyword_labels(keywords, source_text=source_text, mode=mode)
    topic_labels = normalize_topic_labels(topics, mode=mode)
    summary_text = summary.strip() if isinstance(summary, str) else ""

    if keyword_labels:
        keywords_text = ", ".join(keyword_labels)
    else:
        keywords_text = stringify_analysis_items(keywords, source_text=source_text, mode=mode)

    topics_text = "No topics found"
    if topic_labels:
        topics_text = "\n".join(f"- {label}" for label in topic_labels)

    sections = []
    if summary_text:
        sections.append(f"Summary:\n{summary_text}")

    sections.append(f"Keywords:\n{keywords_text}")
    sections.append(f"Topics:\n{topics_text}")

    display_text = "\n\n".join(sections)

    return display_text
