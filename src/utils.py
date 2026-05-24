def format_sources(sources):

    if isinstance(sources, list):

        return "\n".join([
            f"- {s}"
            for s in sources
        ])

    return sources
