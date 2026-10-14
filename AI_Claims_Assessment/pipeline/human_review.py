from claims_agent.models import ClaimSummary, NeedsManual, HumanReviewNeeded
from claims_agent.context import ClaimContext
from pipeline.guardrails_out import check_output
from tools.case_tools import create_claim_case


def send_to_human(result: ClaimSummary | NeedsManual | HumanReviewNeeded, ctx: ClaimContext) -> dict:
    if isinstance(result, ClaimSummary):
        problems = check_output(result)
        if problems:
            ctx.log(f"Output guardrail blocked summary: {problems}")
            result = NeedsManual(claim_id=result.claim_id,
                                 reason="Output guardrail blocked the summary",
                                 last_feedback="; ".join(problems))

    case_id = create_claim_case(result)
    ctx.log(f"Case {case_id} saved for human adjuster")
    return {"case_id": case_id, "result": result, "audit_log": ctx.audit_log}