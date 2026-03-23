"""
translator.py — AI-powered translation using Google Gemini.

HOW TO SET YOUR API KEY (Windows CMD):
    set GOOGLE_API_KEY=your-key-here          (current session only)
    setx GOOGLE_API_KEY "your-key-here"       (permanent)

HOW TO SET YOUR API KEY (Linux/macOS):
    export GOOGLE_API_KEY="your-key-here"

Get your free key at: https://aistudio.google.com
"""

import os
import time
import logging

logger = logging.getLogger(__name__)

# ── Model to use ──────────────────────────────────────────────────────────────
# gemini-1.5-flash is free, fast, and perfect for translation tasks.
GEMINI_MODEL = "gemini-1.5-flash"

# ── System prompt ─────────────────────────────────────────────────────────────
# Critical: without strict instructions Gemini may add "Here is the translation:"
# which would corrupt the XML output.
SYSTEM_PROMPT = (
    "You are a professional UI translator specializing in desktop backup software. "
    "When given a string to translate, return ONLY the translated text. "
    "No explanations, no quotes, no preamble, no punctuation changes. "
    "Preserve any placeholders like %1, %2, {name}, or HTML tags exactly as-is. "
    "Match the tone: concise, imperative, suitable for buttons and menu items."
)


def _get_model():
    """Lazily create the Gemini model only when AI translation is needed."""
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError(
            "The 'google-generativeai' package is not installed.\n"
            "Run:  pip install google-generativeai"
        )

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "\n[ERROR] GOOGLE_API_KEY environment variable is not set.\n"
            "Get your free key at: https://aistudio.google.com\n"
            "Then on Windows CMD run:  set GOOGLE_API_KEY=your-key-here\n"
            "Or permanent:            setx GOOGLE_API_KEY \"your-key-here\""
        )

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )
    return model


def ai_translate(text: str, target_lang: str, context_name: str, model) -> str:
    """
    Translate a single string using Gemini.

    Args:
        text:         The source English string.
        target_lang:  Target language code, e.g. 'fr', 'de', 'id'.
        context_name: Qt context name — gives the model UI placement hints.
        model:        Gemini model instance (created once, reused).

    Returns:
        Translated string.
    """
    prompt = (
        f"Translate this UI text into {target_lang}.\n"
        f"UI context (Qt class name): {context_name}\n"
        f"Text: {text}"
    )

    response = model.generate_content(prompt)
    return response.text.strip()


def mock_translate(text: str, target_lang: str) -> str:
    """
    Mock translation for testing without any API key.
    Returns a clearly fake string so you can verify the pipeline works.
    """
    return f"[{target_lang.upper()}] {text}"


def translate_messages(
    messages: list,
    target_lang: str,
    use_ai: bool = False,
    retry_attempts: int = 3,
    retry_delay: float = 2.0,
) -> list:
    """
    Translate a list of message dicts, adding 'new_translation' to each.

    Args:
        messages:       List of message dicts from ts_parser.get_untranslated().
        target_lang:    Target language code.
        use_ai:         If True, call Gemini API. If False, use mock translation.
        retry_attempts: How many times to retry a failed API call.
        retry_delay:    Seconds to wait between retries.

    Returns:
        The same list with 'new_translation' added to each dict.
    """
    if not messages:
        return messages

    model = None
    if use_ai:
        model = _get_model()
        logger.info(f"Using Gemini model: {GEMINI_MODEL}")

    total = len(messages)
    for i, msg in enumerate(messages, start=1):
        source = msg["source"]
        context = msg["context"]

        if use_ai:
            translated = _translate_with_retry(
                source, target_lang, context, model,
                retry_attempts, retry_delay
            )
            print(f"  [{i}/{total}] {source!r} → {translated!r}")
        else:
            translated = mock_translate(source, target_lang)

        msg["new_translation"] = translated

    return messages


def _translate_with_retry(
    text: str,
    target_lang: str,
    context_name: str,
    model,
    attempts: int,
    delay: float,
) -> str:
    """Call ai_translate with linear-backoff retry on failure."""
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return ai_translate(text, target_lang, context_name, model)
        except Exception as e:
            last_error = e
            if attempt < attempts:
                wait = delay * attempt
                logger.warning(
                    f"Attempt {attempt} failed: {e}. "
                    f"Retrying in {wait:.1f}s..."
                )
                time.sleep(wait)

    # All retries exhausted — safe fallback so we don't corrupt the XML file
    logger.error(f"All {attempts} attempts failed for '{text}': {last_error}")
    return f"[TRANSLATION FAILED: {text}]"
