from typing import Literal

from pydantic import BaseModel, Field

Section = Literal[
    "paddle-boards",
    "shelving",
    "returns-and-warranty",
    "shipping",
    "other",
]


class Classification(BaseModel):
    section: Section
    language: str = Field(description="Language of the latest customer message")
    needs_human: bool = Field(description="True when an always-escalate rule applies")
    reason: str = Field(description="One sentence explaining the classification")
    acknowledgement: str = Field(
        description="Short note in the customer's language that a colleague will reply"
    )


class Issue(BaseModel):
    product: Literal["paddle-board", "shelving"]
    problem: Literal[
        "missing-accessory",
        "slow-leak",
        "seam-split",
        "missing-hardware",
        "damaged-panels",
        "damaged-frame",
        "wrong-finish",
    ]
    order_number: str | None = None
    days_since_delivery: int | None = None
    valve_checked: bool = Field(default=False, description="True when the valve check was done")
    part_numbers: list[str] = Field(
        default_factory=list, description="Part numbers of damaged panels"
    )


class AgentReply(BaseModel):
    action: Literal["reply", "escalate"]
    reply: str = Field(description="The email to the customer, plain text")
    reasoning: str = Field(description="Knowledge-base facts used and why")
    enough_information: bool = Field(
        description="True when the knowledge base answers the question"
    )
    promises_an_action: bool = Field(
        description="True when the reply promises a refund, shipment, replacement, date, or call"
    )
    issue: Issue | None = Field(
        default=None, description="Product issue facts, when the customer reports one"
    )


class Decision(BaseModel):
    action: Literal["reply", "escalate"]
    section: str
    reply: str
    reason: str
    proposed_action: str | None = None


class PipelineResult(BaseModel):
    classification: Classification
    agent_reply: AgentReply | None
    decision: Decision
