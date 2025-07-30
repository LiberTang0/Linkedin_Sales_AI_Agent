"""CLI entry-point to run the LinkedIn Sales Agent."""

from __future__ import annotations

import os
import argparse

from dotenv import load_dotenv

from .browser import LinkedInBrowser
from .graph_builder import build_graph
from . import graph_builder  # for access to SalesState


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Hippocrate EMR LinkedIn Sales Agent")
    parser.add_argument(
        "--query",
        default="solo health professional",
        help="LinkedIn search query to find target profiles",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (default: UI visible)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_dotenv()

    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not (email and password):
        raise SystemExit(
            "❌ Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in your environment or .env file."
        )

    # Optional persistent checkpointer
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore
    except ImportError:
        SqliteSaver = None  # type: ignore

    saver = SqliteSaver("checkpoints.sqlite") if SqliteSaver else None

    with LinkedInBrowser(email, password, headless=args.headless) as browser:
        print("🔐 Logging into LinkedIn…")
        browser.login()
        print("✅ Login successful! Starting outreach workflow…")

        graph = build_graph(browser, search_query=args.query, checkpointer=saver)

        # Use deterministic thread_id so we resume if interrupted
        config = {"configurable": {"thread_id": "default"}}
        final_state = graph.invoke(graph_builder.SalesState(), config=config)
        # final_state is a dict of state values
        print("🎉 Outreach completed for", len(final_state.get("profiles", [])), "profiles!")


if __name__ == "__main__":
    main() 