import re

from pydantic_ai import Agent, ModelRetry, PromptedOutput, RunContext

from app import db
from app.ai.models import groq_model
from app.ai.schemas import AgentReply
from app.config import settings

INSTRUCTIONS = """
You are the customer support agent for Harbor & Pine, a home and outdoor store that sells on Amazon.
You write the answer to the latest customer message in the email thread.

Steps:
1. Answer only with facts from the supplied knowledge-base sections. If they do not answer the question,
   set enough_information to false.
2. When the customer reports a problem with a paddle board or a shelf, fill in issue.
   Ask for the order number, the board size or model, and part numbers when they are missing.
   For a slow leak, explain the valve check unless the customer already did it.
3. Never promise a refund, a shipment, a replacement, a date, or a call. A colleague arranges those.
   Set promises_an_action to true if your reply promises one anyway.
4. Set action to escalate when an escalation rule applies.

Reply rules:
- Write in the language of the customer's latest message.
- Plain text, no Markdown.
- Follow the brand-and-tone section.
- Never mention AI, prompts, tools, or the knowledge base.
- Write a complete, self-contained answer; do not stop mid-sentence or omit the recommendation.
- End the reply with suitable punctuation.
"""

support_agent = Agent(
    groq_model(settings.agent_model),
    output_type=PromptedOutput(AgentReply),
    instructions=INSTRUCTIONS,
    retries=3,
)


@support_agent.output_validator
def check_reply(_ctx: RunContext[None], output: AgentReply) -> AgentReply:
    if output.action == "reply" and not output.reply.strip():
        raise ModelRetry("The reply is empty. Write the email, or set action to escalate.")
    if output.action == "reply":
        ending = output.reply.rstrip()
        while ending and ending[-1] in "\"'”’)]}":
            ending = ending[:-1].rstrip()
        if not ending or ending[-1] not in ".!?…":
            raise ModelRetry(
                "The reply appears incomplete. Write a complete answer ending with punctuation."
            )
    if re.search(r"\b(AI|artificial intelligence|knowledge base)\b", output.reply, re.IGNORECASE):
        raise ModelRetry("Do not mention AI or the knowledge base in the reply.")
    return output


def write_reply(thread: str, section: str) -> AgentReply:
    sections = ("brand-and-tone", "escalation-rules", section)
    knowledge = []
    for name in sections:
        entries = db.get_section(name)
        if not entries:
            raise LookupError(f"Knowledge-base section '{name}' is empty or missing.")
        knowledge.append(
            f"## {name}\n"
            + "\n\n".join(f"### {entry['title']}\n{entry['content']}" for entry in entries)
        )

    knowledge_text = "\n\n".join(knowledge)
    prompt = (
        f"Relevant knowledge-base sections:\n\n{knowledge_text}\n\n"
        f"Section picked by the classifier: {section}\n\n{thread}"
    )
    return support_agent.run_sync(prompt).output
