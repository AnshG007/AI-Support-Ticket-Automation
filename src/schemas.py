from typing import Literal
from pydantic import BaseModel , Field

#Allowed Values Used across triage and resolution stages

Category = Literal[
    "billing",
    "technical",
    "account",
    "cancellation_refund",
    "order_delivery",
    "general",
]

Priority = Literal["low" , "medium" , "high" , "critical"]

ResolutionType = Literal[
    "self_service",
    "resolve",
    "escalate",
    "request_information"
]

class TicketTriage(BaseModel):
    """Structured result of Stage 1 — ticket triage."""

    category: Category = Field(description="Support ticket category")
    priority: Priority = Field(description="Urgency of the ticket")
    language: str = Field(description="Language used in the customer ticket")


class BillingAnalysis(BaseModel):
    """Case analysis fields for billing tickets."""

    issue: str = Field(description="Short summary of the billing problem")
    amount: str = Field(description="Money amount mentioned, or 'unknown'")
    transaction_count: int = Field(description="Number of charges mentioned")
    refund_required: bool = Field(description="Whether a refund appears needed")


class TechnicalAnalysis(BaseModel):
    """Case analysis fields for technical tickets."""

    issue: str = Field(description="Short summary of the technical problem")
    affected_feature: str = Field(description="Feature or area that is broken")
    error_message: str = Field(description="Error text if mentioned, else 'none'")
    troubleshooting_required: bool = Field(
        description="Whether troubleshooting steps are still needed"
    )


class AccountAnalysis(BaseModel):
    """Case analysis fields for account tickets."""

    issue: str = Field(description="Short summary of the account problem")
    access_problem: bool = Field(description="Whether login/access is blocked")
    verification_required: bool = Field(
        description="Whether identity verification is needed"
    )
    account_status: str = Field(
        description="Likely account status, for example active, locked, or unknown"
    )


class CancellationRefundAnalysis(BaseModel):
    """Case analysis fields for cancellation and refund tickets."""

    request_type: str = Field(
        description="What the customer wants, for example cancel, refund, or both"
    )
    reason: str = Field(description="Reason given by the customer")
    refund_required: bool = Field(description="Whether a refund is requested")
    retention_opportunity: bool = Field(
        description="Whether there may be a chance to retain the customer"
    )


class OrderDeliveryAnalysis(BaseModel):
    """Case analysis fields for order and delivery tickets."""

    issue: str = Field(description="Short summary of the order/delivery problem")
    order_status: str = Field(
        description="Current status if mentioned, otherwise unknown"
    )
    delivery_problem: bool = Field(description="Whether delivery is the main issue")
    customer_request: str = Field(description="What the customer wants to be done")


class GeneralAnalysis(BaseModel):
    """Case analysis fields for general tickets."""

    issue: str = Field(description="Short summary of the customer issue")
    customer_request: str = Field(description="What the customer is asking for")
    additional_context: str = Field(
        description="Any extra useful context from the ticket"
    )


class ResolutionDecision(BaseModel):
    """Structured result of Stage 4 — resolution decision."""

    resolution_type: ResolutionType = Field(
        description="Chosen next-step type for the support system"
    )
    recommended_action: str = Field(description="Concrete action to take next")
    requires_human: bool = Field(description="True if a human agent is needed")
    reason: str = Field(description="Why this resolution was chosen")


class TicketResult(BaseModel):
    """
    Final structured output for one processed support ticket.

    This is what gets saved to the results JSON file.
    """

    ticket_id: str
    customer_name: str
    category: str
    priority: str
    language: str
    case_summary: str
    resolution_type: str
    recommended_action: str
    requires_human: bool
    resolution_reason: str
    response: str