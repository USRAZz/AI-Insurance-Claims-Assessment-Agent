from agents import Runner
from agents.exceptions import ModelBehaviorError

from claims_agent.context import ClaimContext
from claims_agent.models import ClaimSummary, EvidenceBundle, NeedsManual
from pipeline.writer import claim_writer
from pipeline.evaluator import claim_evaluator

MAX_REVISIONS = 3


async def run_revision_loop(bundle: EvidenceBundle, ctx: ClaimContext) -> ClaimSummary | NeedsManual:
    evidence = bundle.model_dump_json(indent=2)
    prompt = f"Evidence:\n{evidence}"
    last_feedback = ""

    for attempt in range(1, MAX_REVISIONS + 1):
        ctx.revision_count = attempt
        try:
            draft = (await Runner.run(claim_writer, prompt, context=ctx)).final_output
        except ModelBehaviorError as e:      # model validators rejected the draft
            last_feedback = f"Your output was invalid: {e}"
            ctx.log(f"Attempt {attempt}: writer output invalid")
            prompt = f"Evidence:\n{evidence}\n\nFix this: {last_feedback}"
            continue

        try:                                  # <-- new: protects the evaluator call
            review = (await Runner.run(
                claim_evaluator,
                f"Evidence:\n{evidence}\n\nDraft:\n{draft.model_dump_json(indent=2)}",
                context=ctx,
            )).final_output
        except ModelBehaviorError as e:
            last_feedback = f"Evaluator output was invalid: {e}"
            ctx.log(f"Attempt {attempt}: evaluator output invalid")
            continue

        if review.is_acceptable:
            ctx.log(f"Attempt {attempt}: draft accepted")
            return draft

        last_feedback = review.feedback
        ctx.log(f"Attempt {attempt}: rejected - {last_feedback}")
        prompt = (f"Evidence:\n{evidence}\n\nYour previous draft:\n{draft.model_dump_json(indent=2)}"
                  f"\n\nRevise it. Fix this: {last_feedback}")

    return NeedsManual(
        claim_id=bundle.facts.claim_id,
        reason=f"Draft still rejected after {MAX_REVISIONS} attempts",
        last_feedback=last_feedback,
    )