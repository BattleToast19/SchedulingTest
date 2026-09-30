# social-agent

Step 1: post a text message to a Facebook Page from a script.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then fill in values
```

## Run

```bash
python get_page_token.py     # one-time: prints Page ID + Page token
python post.py --check       # verify credentials
python post.py --dry-run     # preview
python post.py               # posts "test"
```

## Roadmap
1. Post "test" to a Page  <- current
2. Schedule it
3. Add an LLM to generate the text
4. Pick an orchestrator (OpenClaw / n8n / custom loop)
