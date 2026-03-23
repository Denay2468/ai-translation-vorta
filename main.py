"""
main.py — CLI entry point for the Vorta AI Translation Tool.
Powered by Google Gemini (free API via aistudio.google.com)

Usage examples:

    # Mock mode — no API key needed, safe for testing
    python main.py --file sample_ts/vorta.en.xml --lang fr

    # Real Gemini AI translation
    python main.py --file sample_ts/vorta.en.xml --lang fr --use-ai

    # Preview without saving (dry run)
    python main.py --file sample_ts/vorta.en.xml --lang id --use-ai --dry-run

    # Verbose debug output
    python main.py --file sample_ts/vorta.en.xml --lang de --use-ai --verbose

Supported language codes (examples):
    fr = French        de = German      es = Spanish
    id = Indonesian    ja = Japanese    zh = Chinese
    ar = Arabic        pt = Portuguese  ko = Korean
"""

import argparse
import logging
import sys

from ts_parser import parse_ts, get_untranslated, write_ts
from translator import translate_messages


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description="Vorta AI Translation Tool — powered by Google Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --file sample_ts/vorta.en.xml --lang fr
  python main.py --file sample_ts/vorta.en.xml --lang id --use-ai
  python main.py --file sample_ts/vorta.en.xml --lang de --use-ai --dry-run

Before using --use-ai, set your key:
  Windows:      set GOOGLE_API_KEY=your-key-here
  Linux/macOS:  export GOOGLE_API_KEY="your-key-here"

Get your free key at: https://aistudio.google.com
        """,
    )
    arg_parser.add_argument(
        "--file",
        required=True,
        help="Path to the .ts or .xml Qt translation file",
    )
    arg_parser.add_argument(
        "--lang",
        required=True,
        help="Target language code, e.g. fr, de, id, ja",
    )
    arg_parser.add_argument(
        "--use-ai",
        action="store_true",
        default=False,
        help=(
            "Use Google Gemini AI for real translation. "
            "Requires GOOGLE_API_KEY environment variable. "
            "Without this flag, mock translations are used (safe for testing)."
        ),
    )
    arg_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview translations without writing back to the file.",
    )
    arg_parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Show detailed debug output.",
    )

    args = arg_parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # ── Step 1: Parse ──────────────────────────────────────────────────────
    logger.info(f"Parsing: {args.file}")
    messages, tree = parse_ts(args.file)
    logger.info(f"Total messages found: {len(messages)}")

    # ── Step 2: Filter ─────────────────────────────────────────────────────
    untranslated = get_untranslated(messages)

    if not untranslated:
        print("✨ Everything is already translated! Nothing to do.")
        sys.exit(0)

    mode_label = "Google Gemini AI" if args.use_ai else "mock (testing)"
    print(
        f"\nFound {len(untranslated)} string(s) to translate\n"
        f"  Target language : {args.lang}\n"
        f"  Mode            : {mode_label}\n"
        f"  File            : {args.file}\n"
    )

    if not args.use_ai:
        print(
            "  ℹ  Running in mock mode — translations are fake placeholders.\n"
            "     Add --use-ai to use real Gemini AI translation.\n"
            "     Get your free key at: https://aistudio.google.com\n"
        )

    # ── Step 3: Translate ──────────────────────────────────────────────────
    print("Translating..." if args.use_ai else "Generating mock translations...")
    translated = translate_messages(
        untranslated,
        target_lang=args.lang,
        use_ai=args.use_ai,
    )

    # ── Step 4: Preview ────────────────────────────────────────────────────
    print("\n── Results ────────────────────────────────────────")
    for msg in translated:
        print(f"  [{msg['context']}]")
        print(f"    EN : {msg['source']}")
        print(f"    {args.lang.upper()} : {msg['new_translation']}")
        print()

        if not args.dry_run:
            elem = msg["translation_el"]
            elem.text = msg["new_translation"]
            # Remove type="unfinished" so Qt recognises the string as done
            elem.attrib.pop("type", None)

    # ── Step 5: Save ───────────────────────────────────────────────────────
    if args.dry_run:
        print("🔍 Dry-run complete — no changes written to disk.")
    else:
        write_ts(tree, args.file)
        print(
            f"✅ Done! {len(translated)} string(s) translated "
            f"and saved to {args.file}"
        )


if __name__ == "__main__":
    main()
