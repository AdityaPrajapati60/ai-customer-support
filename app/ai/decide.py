from app.ai.agent import write_reply
from app.ai.classifier import classify
from app.ai.rules import CUSTOMER_STEPS, resolve_issue
from app.ai.schemas import AgentReply, Decision, PipelineResult


def decide(thread: str, has_attachments: bool = False) -> Decision:
    """Classify, draft a response, and apply deterministic escalation rules."""
    return run_pipeline(thread, has_attachments).decision


def run_pipeline(thread: str, has_attachments: bool = False) -> PipelineResult:
    """Run support processing without connecting to Gmail or sending a message."""
    classification = classify(thread)
    answer: AgentReply | None = None

    def escalate(reason: str, proposed_action: str | None = None) -> PipelineResult:
        return PipelineResult(
            classification=classification,
            agent_reply=answer,
            decision=Decision(
                action="escalate",
                section=classification.section,
                reply=classification.acknowledgement,
                reason=reason,
                proposed_action=proposed_action,
            ),
        )

    if has_attachments:
        return escalate("The email has attachments")
    if classification.needs_human:
        return escalate(classification.reason)

    answer = write_reply(thread, classification.section)
    if answer.action == "escalate":
        return escalate(answer.reasoning)
    if not answer.enough_information:
        return escalate("The knowledge base does not answer this")
    if answer.issue:
        step = resolve_issue(answer.issue)
        if step not in CUSTOMER_STEPS:
            return escalate(f"Next step: {step}", proposed_action=step)
    if answer.promises_an_action:
        return escalate("The reply promises an action")

    return PipelineResult(
        classification=classification,
        agent_reply=answer,
        decision=Decision(
            action="reply",
            section=classification.section,
            reply=answer.reply,
            reason=answer.reasoning,
        ),
    )
