"""
Amazon Bedrock chat-model factory.

Replaces the previous direct ``ChatAnthropic`` construction scattered across the
agents and orchestrator with a single, environment-driven entry point. The
returned object is a LangChain ``BaseChatModel`` so existing ``ainvoke`` calls
and LangGraph wiring are unchanged.
"""

import os
import re
import logging
from typing import Any, Dict, Optional

from langchain_aws import ChatBedrockConverse

logger = logging.getLogger(__name__)

# Claude Opus 5.5 via the US cross-region inference profile (Bedrock exposes the
# current Claude models only through geo/global profiles, not in-region IDs).
# Override with BEDROCK_MODEL_ID - e.g. eu.anthropic.claude-opus-5-5,
# global.anthropic.claude-opus-5-5, or us.anthropic.claude-sonnet-5-5.
#
# The demo previously used claude-sonnet-4-20250514 on the Anthropic API. Its
# Bedrock equivalent (us.anthropic.claude-sonnet-4-20250514-v1:0) reaches end of
# life on Bedrock on 2026-10-14, so it is not used as the default.
DEFAULT_BEDROCK_MODEL_ID = "us.anthropic.claude-opus-5-5"
DEFAULT_AWS_REGION = "us-east-1"

# Claude 5.x models (Opus/Sonnet/Haiku/Fable/Mythos 5+) reject non-default
# sampling parameters (temperature / top_p / top_k) with a 400. Older models
# still accept them, so we only forward temperature when the model allows it.
_NO_SAMPLING_PARAMS = re.compile(r"claude-(opus|sonnet|haiku|fable|mythos)-5(\b|[-.])")


def supports_sampling_params(model_id: str) -> bool:
    """True if the model accepts temperature / top_p / top_k."""
    return _NO_SAMPLING_PARAMS.search(model_id) is None


def get_bedrock_model_id() -> str:
    """Bedrock model / inference-profile ID from the environment."""
    return os.getenv("BEDROCK_MODEL_ID", DEFAULT_BEDROCK_MODEL_ID)


def get_aws_region() -> str:
    """AWS region for Bedrock, honouring both AWS_REGION and AWS_DEFAULT_REGION."""
    return os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or DEFAULT_AWS_REGION


def get_chat_model(
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    model_id: Optional[str] = None,
) -> ChatBedrockConverse:
    """
    Build a Bedrock-backed Claude chat model.

    Args:
        temperature: Sampling temperature (agents pass their own per-domain value).
            Ignored - with a debug log - for Claude 5.x models, which reject it.
        max_tokens: Optional response cap; Bedrock applies the model default if None.
        model_id: Optional override of BEDROCK_MODEL_ID for a single caller.

    Credentials are resolved by boto3's default chain. Static keys, a named
    profile (AWS_PROFILE) or an attached IAM role all work without code changes.
    """
    resolved_model = model_id or get_bedrock_model_id()
    kwargs: Dict[str, Any] = {
        "model": resolved_model,
        "region_name": get_aws_region(),
    }
    if supports_sampling_params(resolved_model):
        kwargs["temperature"] = temperature
    else:
        logger.debug(
            "Model %s does not accept sampling parameters; ignoring temperature=%s",
            resolved_model, temperature,
        )
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    profile = os.getenv("AWS_PROFILE")
    if profile:
        kwargs["credentials_profile_name"] = profile

    endpoint_url = os.getenv("BEDROCK_ENDPOINT_URL")
    if endpoint_url:
        kwargs["base_url"] = endpoint_url

    return ChatBedrockConverse(**kwargs)


def describe_llm_config() -> Dict[str, Any]:
    """Non-secret summary of the LLM configuration, for startup logs / health."""
    has_static_keys = bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))
    return {
        "provider": "amazon-bedrock",
        "model_id": get_bedrock_model_id(),
        "sampling_params": supports_sampling_params(get_bedrock_model_id()),
        "region": get_aws_region(),
        "credentials": (
            "static-keys" if has_static_keys
            else f"profile:{os.getenv('AWS_PROFILE')}" if os.getenv("AWS_PROFILE")
            else "default-chain (role / instance profile / shared config)"
        ),
        "endpoint_url": os.getenv("BEDROCK_ENDPOINT_URL") or None,
    }
