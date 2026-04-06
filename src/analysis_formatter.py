
import re


def normalize(items):
    if items is None:
        return []
    if isinstance(items, list):
        return items
    return [items]


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
        phrase = next((item for item in keywords if isinstance(item, str) and ' ' in item.strip() and item.strip()), None)
        if phrase:
            return phrase.strip()
        keyword = next((item for item in keywords if isinstance(item, str) and item.strip()), None)
        if keyword:
            return keyword.strip()

    return None


def _split_topic_text(topic_text):
    return [
        part.strip()
        for part in re.split(r",|\n|;", topic_text)
        if isinstance(part, str) and part.strip()
    ]


def normalize_keyword_labels(keywords, limit=5):
    labels = []

    def append_label(label):
        cleaned = label.strip()
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


def normalize_topic_labels(topics, limit=5):
    labels = []

    def append_label(label):
        cleaned = label.strip()
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


def stringify_analysis_items(items, limit=5):
    if items is None:
        return ""

    if isinstance(items, str):
        return items.strip()

    if isinstance(items, dict):
        keyword = items.get("keyword") or items.get("key")
        if keyword is not None:
            return str(keyword)

        label = _choose_topic_label(items)
        return label or str(items)

    if isinstance(items, list):
        formatted_items = []
        for item in items[:limit]:
            text = stringify_analysis_items(item, limit=limit)
            if text:
                formatted_items.append(text)
        return ", ".join(formatted_items)

    return str(items)

def format_analysis_for_ui(summary, keywords, topics):
    keyword_labels = normalize_keyword_labels(keywords)
    topic_labels = normalize_topic_labels(topics)
    summary_text = summary.strip() if isinstance(summary, str) else ""

    if keyword_labels:
        keywords_text = ", ".join(keyword_labels)
    else:
        keywords_text = stringify_analysis_items(keywords)

    # Format topics as bullet list
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
