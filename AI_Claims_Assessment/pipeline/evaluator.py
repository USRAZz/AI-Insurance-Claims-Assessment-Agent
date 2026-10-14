from agents import Agent
from claims_agent.models import EvaluationResult

claim_evaluator = Agent(
    name="Claim Evaluator",
    instructions=(
        "Compare the draft summary to the evidence. Set has_unsupported_promise if it promises "
        "or implies approval/payment/refund, or states anything the evidence does not support. "
        "Set has_missing_evidence if evidence shows missing documents or gaps that the draft ignores. "
        "Set has_contradiction if the draft contradicts the evidence or itself "
        "(e.g. says policy is active when it is expired). "
        "is_acceptable is True ONLY if all three are False. "
        "If not acceptable, write specific feedback telling the writer what to fix."
    ),
    output_type=EvaluationResult,
)