"""
LLM factory - all agents and the orchestrator obtain their chat model here.

The demo runs Claude on **Amazon Bedrock** via LangChain's ``ChatBedrockConverse``
(Bedrock Converse API). Credentials come from the standard AWS credential chain
(env vars, shared profile, IAM role / instance profile), so no Anthropic API key
is required.

Environment variables:
    BEDROCK_MODEL_ID       Bedrock model or inference-profile ID (default below)
    AWS_REGION             Region hosting Bedrock (falls back to AWS_DEFAULT_REGION)
    AWS_PROFILE            Optional named profile from ~/.aws/credentials
    AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN
                           Optional static credentials (picked up by boto3)
    BEDROCK_ENDPOINT_URL   Optional VPC endpoint / custom Bedrock runtime URL
"""

from .factory import (
    DEFAULT_BEDROCK_MODEL_ID,
    DEFAULT_AWS_REGION,
    get_bedrock_model_id,
    get_aws_region,
    get_chat_model,
    describe_llm_config,
    supports_sampling_params,
    infer_provider,
)

__all__ = [
    "DEFAULT_BEDROCK_MODEL_ID",
    "DEFAULT_AWS_REGION",
    "get_bedrock_model_id",
    "get_aws_region",
    "get_chat_model",
    "describe_llm_config",
    "supports_sampling_params",
    "infer_provider",
]
