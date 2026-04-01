
def normalize(items):
    if items is None:
        return []
    if isinstance(items, list):
        return items
    return [items]

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

    topics_text = "\n".join(str(item) for item in topics_list)

    display_text = (
        f"Summary:\n{summary}\n\n"
        f"Keywords:\n{keywords_text}\n\n"
        f"Topics:\n{topics_text}"
    )

    return display_text