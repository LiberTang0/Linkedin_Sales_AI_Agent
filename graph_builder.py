"""LangGraph workflow builder for the LinkedIn outreach."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from langgraph.graph import StateGraph, END

from .browser import LinkedInBrowser
from .prompts import (
    generate_sales_message,
    generate_discovery_message,
    generate_presentation_message,
    generate_objection_message,
    generate_closing_message,
)


@dataclass
class SalesState:
    """Mutable state passed between graph nodes."""

    profiles: List[str] = field(default_factory=list)
    profile_index: int = 0
    status: Dict[str, bool] = field(default_factory=dict)  # url -> success flag


# ---------------------------------------------------------------------------
# Node definitions
# ---------------------------------------------------------------------------


try:
    from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore
except ImportError:  # Older langgraph fallback
    SqliteSaver = None  # type: ignore

def build_graph(browser: LinkedInBrowser, search_query: str, *, checkpointer=None) -> StateGraph:
    """Return a compiled LangGraph ready to run."""

    sg: StateGraph[SalesState] = StateGraph(SalesState)

    # ---------------- collector -----------------
    def collect_profiles(state: SalesState) -> SalesState:
        if not state.profiles:
            state.profiles = browser.search_profiles(search_query, max_results=10)
        return state

    # ---------------- connect & initial message -----------------
    def outreach(state: SalesState) -> SalesState:
        if state.profile_index >= len(state.profiles):
            return state

        profile_url = state.profiles[state.profile_index]
        slug = profile_url.split("/")[-2]
        name = slug.replace("-", " ").title()

        # Send connection request with note
        note = generate_sales_message(profile_name=name)
        browser.connect_with_profile(profile_url, message=note)
        return state

    # ------------- discovery / qualification -----------------
    def discovery(state: SalesState) -> SalesState:
        if state.profile_index >= len(state.profiles):
            return state
        profile_url = state.profiles[state.profile_index]
        slug = profile_url.split("/")[-2]
        name = slug.replace("-", " ").title()
        msg = generate_discovery_message(profile_name=name)
        browser.send_message(profile_url, msg)
        return state

    # ------------- presentation / demo -----------------
    def presentation(state: SalesState) -> SalesState:
        if state.profile_index >= len(state.profiles):
            return state
        profile_url = state.profiles[state.profile_index]
        slug = profile_url.split("/")[-2]
        name = slug.replace("-", " ").title()
        msg = generate_presentation_message(profile_name=name)
        browser.send_message(profile_url, msg)
        return state

    # ------------- handle objections -----------------
    def objections(state: SalesState) -> SalesState:
        if state.profile_index >= len(state.profiles):
            return state
        profile_url = state.profiles[state.profile_index]
        slug = profile_url.split("/")[-2]
        name = slug.replace("-", " ").title()
        msg = generate_objection_message(profile_name=name)
        browser.send_message(profile_url, msg)
        return state

    # ------------- closing the deal -----------------
    def closing(state: SalesState) -> SalesState:
        if state.profile_index >= len(state.profiles):
            return state
        profile_url = state.profiles[state.profile_index]
        slug = profile_url.split("/")[-2]
        name = slug.replace("-", " ").title()
        msg = generate_closing_message(profile_name=name)
        browser.send_message(profile_url, msg)
        # mark status success true (simplified)
        state.status[profile_url] = True
        # advance to next profile
        state.profile_index += 1
        return state

    # ---------------- wiring -----------------
    sg.add_node("collect_profiles", collect_profiles)
    sg.set_entry_point("collect_profiles")

    sg.add_node("outreach", outreach)
    sg.add_node("discovery", discovery)
    sg.add_node("presentation", presentation)
    sg.add_node("objections", objections)
    sg.add_node("closing", closing)

    sg.add_edge("collect_profiles", "outreach")
    sg.add_edge("outreach", "discovery")
    sg.add_edge("discovery", "presentation")
    sg.add_edge("presentation", "objections")
    sg.add_edge("objections", "closing")

    # Loop until all profiles processed
    def continue_condition(state: SalesState) -> str | None:
        if state.profile_index < len(state.profiles):
            return "outreach"
        return END

    sg.add_conditional_edges("closing", continue_condition, path_map=["outreach", END])

    return sg.compile(checkpointer=checkpointer) 