"""
ts_parser.py — Parse and write Qt Linguist .ts/.xml translation files.

Renamed from parser.py to avoid shadowing Python's built-in 'parser' module.
"""

import sys
import xml.etree.ElementTree as ET


def parse_ts(file_path: str):
    """
    Parse a Qt .ts file and return (messages, tree).

    Each message dict contains:
        context       - <context><name> value
        source        - original English string
        translation_el - reference to the <translation> XML element
        translation_text - current translation (may be empty)
        is_unfinished  - True if type="unfinished" attribute is set
    """
    try:
        tree = ET.parse(file_path)
    except ET.ParseError as e:
        print(f"[ERROR] Could not parse XML file '{file_path}': {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"[ERROR] File not found: '{file_path}'")
        sys.exit(1)

    root = tree.getroot()
    messages = []

    for context in root.findall("context"):
        context_name_elem = context.find("name")
        context_name = (
            context_name_elem.text.strip()
            if context_name_elem is not None and context_name_elem.text
            else "Unknown"
        )

        for message in context.findall("message"):
            source_elem = message.find("source")
            translation_elem = message.find("translation")

            if source_elem is None or translation_elem is None:
                continue

            source_text = (source_elem.text or "").strip()
            translation_text = (translation_elem.text or "").strip()
            is_unfinished = translation_elem.get("type") == "unfinished"

            # Skip messages with no source text at all
            if not source_text:
                continue

            messages.append({
                "context": context_name,
                "source": source_text,
                "translation_el": translation_elem,
                "translation_text": translation_text,
                "is_unfinished": is_unfinished,
            })

    return messages, tree


def get_untranslated(messages: list) -> list:
    """Return messages that are empty OR marked unfinished."""
    return [
        m for m in messages
        if not m["translation_text"] or m["is_unfinished"]
    ]


def write_ts(tree, file_path: str) -> None:
    """Write the updated XML tree back to disk."""
    try:
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
    except OSError as e:
        print(f"[ERROR] Could not write file '{file_path}': {e}")
        sys.exit(1)
