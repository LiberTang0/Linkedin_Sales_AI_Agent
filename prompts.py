"""LLM prompt utilities for sales messaging."""

from __future__ import annotations

# NOTE: switched to Google Gemini per user request
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------
_SALES_SYSTEM_PROMPT = (
    "You are an expert SaaS sales representative for Hippocrate EMR, a modern "
    "electronic medical record platform purpose-built for solo healthcare providers. "
    "Craft concise, value-centric outreach messages that resonate with clinicians who "
    "juggle both patient care and administrative tasks on their own. Highlight "
    "efficiency and ease-of-use." 
)


# cache Gemini client
_llm: ChatGoogleGenerativeAI | None = None


def _get_llm() -> ChatGoogleGenerativeAI:  # Lazy-init helper
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)
    return _llm


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _simple_generate(system_prompt: str, human_template: str, **fmt) -> str:
    """Utility to call LLM with minimal boilerplate."""
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_template.format(**fmt)),
        ]
    )
    return _get_llm()(prompt_value=prompt).content.strip()


def generate_discovery_message(profile_name: str) -> str:
    """Questions to qualify prospect's needs."""
    return _simple_generate(
        _SALES_SYSTEM_PROMPT,
        (
            "Start a discovery conversation with {profile_name}. Ask 1-2 concise "
            "questions to understand their current EMR workflow, top pain points, and budget. "
            "Keep it friendly and consultative; no selling yet."
        ),
        profile_name=profile_name,
    )


def generate_presentation_message(profile_name: str) -> str:
    """Follow-up highlighting core product value."""
    return _simple_generate(
        _SALES_SYSTEM_PROMPT,
        (
            "Send a short LinkedIn message to {profile_name} summarizing the 3 key features of "
            "Hippocrate EMR that solve their solo-practice challenges. Offer a quick demo link."
        ),
        profile_name=profile_name,
    )


def generate_objection_message(profile_name: str) -> str:
    """Handle common objections (price, migration, compliance)."""
    return _simple_generate(
        _SALES_SYSTEM_PROMPT,
        (
            "{profile_name} is hesitant about switching EMRs due to cost and data migration. "
            "Craft a reassuring response addressing affordability plans and white-glove migration assistance."
        ),
        profile_name=profile_name,
    )


def generate_closing_message(profile_name: str) -> str:
    """Close with a clear CTA."""
    return _simple_generate(
        _SALES_SYSTEM_PROMPT,
        (
            "Politely ask {profile_name} if they'd be open to starting a 14-day free trial of "
            "Hippocrate EMR next week. Include the link to Sign Up: https://www.hippocrate.org/shop/product/hippocrate-sign-up-2 "
        ),
        profile_name=profile_name,
    )

# ---------------------------------------------------------------------------
# Existing API
# ---------------------------------------------------------------------------

def generate_sales_message(profile_name: str, specialty: str | None = None) -> str:
    """Return a personalised connection note (~300 chars)."""
    if not specialty:
        specialty = "healthcare professional"

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=_SALES_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    "Compose a friendly yet professional LinkedIn connection request "
                    "(max 300 characters) tailored to {profile_name}, a solo {specialty}. "
                    "Focus on the key pain points: administrative burden, EMR costs, and "
                    "patient record management. Close with a low-pressure call-to-action "
                    "to explore Hippocrate EMR."
                )
            ),
        ]
    )
    llm = _get_llm()
    return llm(prompt_value=prompt.format(profile_name=profile_name, specialty=specialty)).content.strip() 