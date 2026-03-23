# Vorta AI Translation Tool

A CLI tool that automatically fills in missing Qt Linguist (`.ts`/`.xml`)
translations using **Google Gemini AI** — free, no credit card needed.

Built as a GSoC exploration project for the
[Borg Collective](https://python-gsoc.org/ideas.html) (Borg, Borgmatic, Vorta).

---

## Project Structure

```
ai-translation-vorta/
├── main.py                  ← CLI entry point
├── ts_parser.py             ← Parse & write Qt .ts XML files
├── translator.py            ← Gemini AI translation logic  ⭐
├── requirements.txt         ← Python dependencies
├── README.md
├── sample_ts/
│   └── vorta.en.xml         ← Sample file with unfinished strings
└── tests/
    └── test_ts_parser.py    ← 17 unit tests
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get your free Google Gemini API key

1. Go to **https://aistudio.google.com**
2. Sign in with your Google account
3. Click **"Get API key"** → **"Create API key"**
4. Copy your key — it looks like `AIzaSy...`

### 3. Set the environment variable

**Windows CMD:**
```cmd
set GOOGLE_API_KEY=AIzaSy...your-key-here
```

**Windows (permanent):**
```
Win+R → sysdm.cpl → Advanced → Environment Variables → New
  Name:  GOOGLE_API_KEY
  Value: AIzaSy...your-key-here
```

**Linux / macOS:**
```bash
export GOOGLE_API_KEY="AIzaSy...your-key-here"
```

---

## Usage

```bash
# Mock mode — no API key needed, tests the full pipeline
python main.py --file sample_ts/vorta.en.xml --lang fr

# Real Gemini AI translation
python main.py --file sample_ts/vorta.en.xml --lang fr --use-ai

# Preview without writing to disk (dry run)
python main.py --file sample_ts/vorta.en.xml --lang id --use-ai --dry-run

# Verbose output
python main.py --file sample_ts/vorta.en.xml --lang de --use-ai --verbose
```

---

## Running Tests

```bash
python -m unittest tests/test_ts_parser.py -v
```

17 tests covering parser, filter, write-back, and mock translator.

---

## How It Works

```
.ts file → parse → filter unfinished → Gemini AI → write back
```

1. **Parse** — reads Qt `.ts` XML, extracts all `<message>` elements
2. **Filter** — selects only strings that are empty or `type="unfinished"`
3. **Translate** — sends each string to Gemini with a strict system prompt
4. **Write** — updates XML in-place, removes `type="unfinished"` attributes

---

## Why Google Gemini?

- ✅ Completely free tier via aistudio.google.com
- ✅ No credit card required
- ✅ Works from Indonesia and most countries
- ✅ `gemini-1.5-flash` is fast and accurate for UI translation tasks
