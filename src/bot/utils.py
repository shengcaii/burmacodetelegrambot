import base64
from typing import List
import random
import httpx
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def encode_bytes_to_base64(image_bytes: bytes) -> str:
    """Encodes image bytes to a Base64 string."""
    return base64.b64encode(image_bytes).decode('utf-8')

def get_model_list(llm_models: str | None) -> List[str]:
    """
    Parses the comma-separated model list from the environment variable.
    Raises a ValueError if the variable is not set or is empty.
    """
    if not llm_models:
        # This check makes the type checker understand that if the function proceeds,
        # model_list_env_var must be a non-empty string.
        raise ValueError("LLM_MODELS environment variable is not set or is empty.")
    return [model.strip() for model in llm_models.split(",")]

async def try_models(
    models: List[str],
    payload_base: Dict[str, Any],
    headers: Dict[str, str],
    endpoint: str,
    timeout: int = 60,
) -> str | None:
    """
    Tries a list of models in random order to get a response.

    Args:
        models: A list of model names to try.
        payload_base: The base payload for the API request.
        headers: The request headers.
        endpoint: The API endpoint URL.
        timeout: The request timeout in seconds.

    Returns:
        The response content as a string on success, or None if all models fail.
    """
    shuffled_models = random.sample(models, len(models))
    logger.info(f"Attempting models in order: {shuffled_models}")

    async with httpx.AsyncClient(timeout=timeout) as client:
        for model in shuffled_models:
            payload = payload_base.copy()
            payload["model"] = model
            try:
                logger.info(f"Trying model: {model}")
                response = await client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                response_data = response.json()
                # Add a check for expected structure before accessing keys
                if (
                    "choices" in response_data
                    and response_data["choices"]
                    and "message" in response_data["choices"][0]
                    and "content" in response_data["choices"][0]["message"]
                ):
                    return response_data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"Model {model} returned an unexpected response structure: {response_data}")
                    continue # Try next model
            except httpx.HTTPStatusError as e:
                logger.warning(f"Model {model} failed with status {e.response.status_code}: {e.response.text}")
            except Exception as e:
                logger.error(f"An unexpected error occurred with model {model}: {e}", exc_info=True)

    logger.error("All available models failed to respond.")
    return None
