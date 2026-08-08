import re
from html import unescape


_BLOCK_TAGS = ("think", "analysis", "reasoning")


def sanitize_model_output(text):
    """Remove hidden reasoning tags from model output before rendering to users."""
    if not text:
        return ""

    # Decode escaped tags like &lt;think&gt; so they can be removed reliably.
    cleaned = unescape(str(text))

    # Remove full hidden-reasoning blocks first.
    for tag in _BLOCK_TAGS:
        cleaned = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}>",
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )

    # Remove dangling opening/closing tags if model returns malformed content.
    for tag in _BLOCK_TAGS:
        cleaned = re.sub(rf"</?{tag}\b[^>]*>", "", cleaned, flags=re.IGNORECASE)

    # Keep formatting readable while removing extra gaps caused by stripping blocks.
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()