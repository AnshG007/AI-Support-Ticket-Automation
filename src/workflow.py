from src.chains import (
    create_resolution_chain,
    create_response_chain,
    create_router,
    create_triage_chain
)

from src.schemas import TicketResult

#Friendly labels used only in terminal display

CHAIN_LABELS = {
    "billing": "Billing Chain",
    "technical": "Technical Chain",
    "account": "Account Chain",
    "cancellation_refund": "Cancellation/Refund Chain",
    "order_delivery": "Order/Delivery Chain",
    "general": "General Chain"
}

def build_workflow(llm):
    """
    Create all chains needed to process one support ticket.

    Args:
        llm: A LangChain chat model from create_llm().

    Returns:
        dict: Named chains used by process_ticket().

    Example:
        workflow = build_workflow(llm)
        result = process_ticket(ticket, workflow)
    """

    return {
        "triage_chain": create_triage_chain(llm),
        "router": create_router(llm),
        "resolution_chain": create_resolution_chain(llm),
        "response_chain": create_response_chain(llm)
    }

def process_ticket(ticket, workflow):
    """
    Run the full automation workflow for a single support ticket.

    Steps:
        1. Triage the ticket (category, priority, language)
        2. Route to a specialized analysis chain
        3. Decide the resolution
        4. Generate the customer response
        5. Return a final TicketResult

    Args:
        ticket (dict): One ticket with ticket_id, customer_name, and ticket.
        workflow (dict): Chains created by build_workflow().

    Returns:
        TicketResult: Final structured result for this ticket.

    Example:
        result = process_ticket(
            {
                "ticket_id": "TKT-1001",
                "customer_name": "Rahul Sharma",
                "ticket": "I was charged twice.",
            },
            workflow,
        )
        print(result.category, result.resolution_type)
    """
    customer_name = ticket["customer_name"]
    ticket_text = ticket["ticket"]

    # ---- Stage 1: Ticket Triage ----
    triage = workflow["triage_chain"].invoke({
        "customer_name":customer_name,
        "ticket": ticket_text
    })

    print(f"Category: {triage.category}")
    print(f"Priority: {triage.priority}")
    print(f"Routing to: {CHAIN_LABELS.get(triage.category, 'General Chain')}")

    # ---- Stage 2 + 3: Routing and Case Analysis ----
    # The router looks at "category" and calls the matching analysis chain.

    case_analysis = workflow["router"].invoke({
        "category":triage.category,
        "customer_name":customer_name,
        "ticket":ticket_text
    })

    # Convert analysis to text so later prompts stay simple and reusable.

    case_analysis_text = case_analysis.model_dump_json(indent=2)

    # ---- Stage 4: Resolution Decision ----

    resolution = workflow["resolution_chain"].invoke(
        {
            "customer_name": customer_name,
            "ticket": ticket_text,
            "category": triage.category,
            "priority": triage.priority,
            "language": triage.language,
            "case_analysis": case_analysis_text,
        }
    )
    # ---- Stage 5: Response Generation ----
    # This step only writes the reply. It follows the decision above.

    response_text = workflow["response_chain"].invoke(
        {
            "customer_name": customer_name,
            "ticket": ticket_text,
            "category": triage.category,
            "priority": triage.priority,
            "language": triage.language,
            "case_analysis": case_analysis_text,
            "resolution_type": resolution.resolution_type,
            "recommended_action": resolution.recommended_action,
            "requires_human": resolution.requires_human,
            "resolution_reason": resolution.reason,
        }
    )

    # ---- Stage 6: Final Structured Output ----
    return TicketResult(
        ticket_id=ticket["ticket_id"],
        customer_name=customer_name,
        category=triage.category,
        priority=triage.priority,
        language=triage.language,
        case_summary=case_analysis_text,
        resolution_type=resolution.resolution_type,
        recommended_action=resolution.recommended_action,
        requires_human=resolution.requires_human,
        resolution_reason=resolution.reason,
        response=response_text.strip(),
    )

