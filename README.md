# LinkedIn Sales Agent

This project implements an automated LinkedIn outreach bot that targets solo healthcare professionals and pitches **Hippocrate EMR** using state-of-the-art LLM driven sales scripts.

The agent is implemented with:

* **LangGraph** – graph-based orchestration of workflow steps.
* **LangChain & OpenAI** – LLM prompts & message generation.
* **Playwright** – reliable browser automation for LinkedIn interactions.
* **LangSmith** – observability & tracing.

---

## ⚠️ Legal & Ethical Notice
LinkedIn’s Terms of Service prohibit unauthorized automation. **Use this code responsibly and at your own risk.** The maintainers assume no liability for account bans or legal issues.

---

## Quick Start

### 1. Install system dependencies
```bash
# Install Playwright browsers (only once)
python -m playwright install
```

### 2. Create a virtual environment & install Python deps
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # installs langgraph >=0.0.51 for @node decorator support
```

### 3. Configure environment variables
Create a `.env` file (copy `.env.example`) and set:

```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
GOOGLE_API_KEY=your_google_genai_key
LANGCHAIN_API_KEY=lsm-...   # Optional for LangSmith observability
LANGCHAIN_TRACING_V2=true
```

### 4. Run the agent
```bash
python -m agent.main
```
The browser launches (non-headless by default). The agent logs in, searches for solo healthcare professionals, sends a personalised connection request, and follows up with a short pitch message.

---

## Project Structure
```
linkedin_sales_agent/
├── agent/
│   ├── __init__.py
│   ├── browser.py          # Playwright helper class
│   ├── prompts.py          # LLM prompt templates
│   ├── graph_builder.py    # LangGraph workflow
│   └── main.py             # Entry-point CLI
├── requirements.txt
└── README.md
```

## Extending
* **Search Query**: Edit `main.py` to tweak the `search_query` phrase.
* **Prompt Engineering**: Update `prompts.py` for different outreach styles.
* **Graph Logic**: Modify `graph_builder.py` to add extra steps (e.g., profile data scraping, CRM logging, etc.).

---

## Observability with LangSmith
Set `LANGCHAIN_TRACING_V2=true` and provide `LANGCHAIN_API_KEY`. Workflow runs will appear in your LangSmith dashboard for deep debugging and analytics.

---

## License
MIT 