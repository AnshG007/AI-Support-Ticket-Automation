"""
LangChain chains used by the support ticket workflow.

Each function builds one clear stage:
- triage
- specialized case analysis (one chain per category)
- resolution decision
- customer response
"""

from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch

from src.schemas import (
    AccountAnalysis,
    BillingAnalysis,
    CancellationRefundAnalysis,
    GeneralAnalysis,
    OrderDeliveryAnalysis,
    ResolutionDecision,
    TechnicalAnalysis,
    TicketTriage,
)

# Project root so prompt paths work no matter where we run from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# Short focus text passed into the shared case-analysis prompt.
ANALYSIS_FOCUS = {
    "billing": (
        "- issue\n"
        "- amount\n"
        "- transaction_count\n"
        "- refund_required"
    ),
    "technical": (
        "- issue\n"
        "- affected_feature\n"
        "- error_message\n"
        "- troubleshooting_required"
    ),
    "account": (
        "- issue\n"
        "- access_problem\n"
        "- verification_required\n"
        "- account_status"
    ),
    "cancellation_refund": (
        "- request_type\n"
        "- reason\n"
        "- refund_required\n"
        "- retention_opportunity"
    ),
    "order_delivery": (
        "- issue\n"
        "- order_status\n"
        "- delivery_problem\n"
        "- customer_request"
    ),
    "general": (
        "- issue\n"
        "- customer_request\n"
        "- additional_context"
    ),
}


def load_prompt(file_path):
    """
    Load a prompt template text file from disk.

    Args:
        file_path (str | Path): Path to a .txt prompt file.

    Returns:
        str: The full prompt text.

    Example:
        text = load_prompt("prompts/classification_prompt.txt")
        print(text[:40])
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found: {path}")


def create_triage_chain(llm):
    """
    Build the Stage 1 triage chain.

    The chain classifies a ticket into category, priority, and language
    using structured output.

    Args:
        llm: A LangChain chat model.

    Returns:
        Runnable: A chain that returns a TicketTriage object.

    Example:
        triage_chain = create_triage_chain(llm)
        result = triage_chain.invoke(
            {"customer_name": "Rahul", "ticket": "I was charged twice."}
        )
    """
    # Load the prompt from the prompts folder.
    prompt_text = load_prompt("prompts/classification_prompt.txt")
    prompt = ChatPromptTemplate.from_template(prompt_text)

    # Structured output keeps the triage result easy to use later.
    structured_llm = llm.with_structured_output(TicketTriage)
    return prompt | structured_llm


def _create_analysis_chain(llm, category, schema):
    """
    Build one specialized case-analysis chain for a category.

    Args:
        llm: A LangChain chat model.
        category (str): Ticket category name, for example "billing".
        schema: Pydantic model used for structured analysis output.

    Returns:
        Runnable: A chain that returns the category-specific analysis model.
    """
    prompt_text = load_prompt("prompts/case_analysis_prompt.txt")
    prompt = ChatPromptTemplate.from_template(prompt_text)

    # Fill category-specific values once when the chain is created.
    prompt = prompt.partial(
        category=category,
        analysis_focus=ANALYSIS_FOCUS[category],
    )

    structured_llm = llm.with_structured_output(schema)
    return prompt | structured_llm


def create_billing_chain(llm):
    """
    Build the billing case-analysis chain.

    Args:
        llm: A LangChain chat model.

    Returns:
        Runnable: Chain that returns BillingAnalysis.
    """
    return _create_analysis_chain(llm, "billing", BillingAnalysis)


def create_technical_chain(llm):
    """
    Build the technical case-analysis chain.

    Args:
        llm: A LangChain chat model.

    Returns:
        Runnable: Chain that returns TechnicalAnalysis.
    """
    return _create_analysis_chain(llm, "technical", TechnicalAnalysis)


def create_account_chain(llm):
    """
    Build the account case-analysis chain.

    Args:
        llm: A LangChain chat model.

    Returns:
        Runnable: Chain that returns AccountAnalysis.
    """
    return _create_analysis_chain(llm, "account", AccountAnalysis)


def create_cancellation_refund_chain(llm):
    """
    Build the cancellation/refund case-analysis chain.

    Args:
        llm: A LangChain chat model.

    Returns:
        Runnable: Chain that returns CancellationRefundAnalysis.
    """
    return _create_analysis_chain(
        llm, "cancellation_refund", CancellationRefundAnalysis
    )


def create_order_delivery_chain(llm):
    """
    Build the order/delivery case-analysis chain.

    Args:
        llm: A LangChain chat model.

    Returns:
        Runnable: Chain that returns OrderDeliveryAnalysis.
    """
    return _create_analysis_chain(llm, "order_delivery", OrderDeliveryAnalysis)


def create_general_chain(llm):
    """
    Build the general case-analysis chain.

    Args:
        llm: A LangChain chat model.

    Returns:
        Runnable: Chain that returns GeneralAnalysis.
    """
    return _create_analysis_chain(llm, "general", GeneralAnalysis)


def create_router(llm):
    """
    Build a RunnableBranch that routes tickets by category.

    This is Stage 2 of the workflow. Based on triage.category, the ticket
    is sent to the matching specialized analysis chain.

    Args:
        llm: A LangChain chat model.

    Returns:
        RunnableBranch: A router that returns a category-specific analysis.

    Example:
        router = create_router(llm)
        analysis = router.invoke(
            {
                "category": "billing",
                "customer_name": "Rahul",
                "ticket": "I was charged twice.",
            }
        )
    """
    billing_chain = create_billing_chain(llm)
    technical_chain = create_technical_chain(llm)
    account_chain = create_account_chain(llm)
    cancellation_refund_chain = create_cancellation_refund_chain(llm)
    order_delivery_chain = create_order_delivery_chain(llm)
    general_chain = create_general_chain(llm)

    # Route the ticket to a specialized chain based on its category.
    return RunnableBranch(
        (lambda x: x["category"] == "billing", billing_chain),
        (lambda x: x["category"] == "technical", technical_chain),
        (lambda x: x["category"] == "account", account_chain),
        (lambda x: x["category"] == "cancellation_refund", cancellation_refund_chain),
        (lambda x: x["category"] == "order_delivery", order_delivery_chain),
        general_chain,  # default fallback
    )


def create_resolution_chain(llm):
    """
    Build the Stage 4 resolution decision chain.

    This chain decides what should happen next. It does not write the
    customer reply.

    Args:
        llm: A LangChain chat model.

    Returns:
        Runnable: A chain that returns a ResolutionDecision object.
    """
    prompt_text = load_prompt("prompts/resolution_prompt.txt")
    prompt = ChatPromptTemplate.from_template(prompt_text)
    structured_llm = llm.with_structured_output(ResolutionDecision)
    return prompt | structured_llm


def create_response_chain(llm):
    """
    Build the Stage 5 customer response chain.

    This chain only writes the reply. It should follow the resolution
    decision that was already made in Stage 4.

    Args:
        llm: A LangChain chat model.

    Returns:
        Runnable: A chain that returns response text as a string.
    """
    prompt_text = load_prompt("prompts/response_prompt.txt")
    prompt = ChatPromptTemplate.from_template(prompt_text)

    # Plain text output is enough for the customer-facing reply.
    return prompt | llm | StrOutputParser()