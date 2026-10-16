"""
llm_config.py: shared LLM settings for all pipeline agents (new small helper file).

- loads the OpenAI key from .env
- one place to change the model
- output_schema(): tells the SDK to use a non-strict JSON schema. Pydantic still
  validates every output, but our extra rules (min_length, > 0 ...) are allowed.
"""

import os

from agents import AgentOutputSchema, ModelSettings
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MODEL_SETTINGS = ModelSettings(temperature=0)


def output_schema(model_class):
    return AgentOutputSchema(model_class, strict_json_schema=False)
