
def normalize(items):
    if items is None:
        return []
    if isinstance(items, list):
        return items
    return [items]


def _choose_topic_label(topic):
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

def format_analysis_for_ui(summary, keywords, topics):
    keywords_list = normalize(keywords)
    topics_list = normalize(topics)

    if keywords_list and isinstance(keywords_list[0], dict):
        keywords_text = "\n".join(
            f"- {item.get('keyword', item.get('key', str(item)))} ({item.get('score', '')})"
            for item in keywords_list
        )
    else:
        keywords_text = "\n".join(str(item) for item in keywords_list)

    # Format topics as bullet list
    topics_text = ""
    if topics_list:
        topic_keywords = []
        for topic in topics_list[:5]:  # Limit to top 5 topics
            label = _choose_topic_label(topic)
            if label:
                topic_keywords.append(f"- {label}")
        
        if topic_keywords:
            topics_text = "\n".join(topic_keywords)
        else:
            topics_text = "No topics found"

    display_text = (
        f"Summary:\n{summary}\n\n"
        f"Keywords:\n{keywords_text}\n\n"
        f"Topics:\n{topics_text}"
    )

    return display_text
