import base64
from typing import List

def encode_bytes_to_base64(image_bytes: bytes) -> str:
    """Encodes image bytes to a Base64 string."""
    return base64.b64encode(image_bytes).decode('utf-8')

def get_model_list(model_list_env_var: str | None) -> List[str]:
    """
    Parses the comma-separated model list from the environment variable.
    Raises a ValueError if the variable is not set or is empty.
    """
    if not model_list_env_var:
        # This check makes the type checker understand that if the function proceeds,
        # model_list_env_var must be a non-empty string.
        raise ValueError("LLM_MODELS environment variable is not set or is empty.")
    return [model.strip() for model in model_list_env_var.split(",")]