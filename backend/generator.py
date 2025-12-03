"""
generator.py
Local LLM generator wrapper for the chatbot. No cloud API calls.
Pairs with pii_masker to ensure sensitive information is never sent raw.
"""

from transformers import pipeline
from .pii_masker import mask_pii

# FREE offline model — can later be switched to Mistral, LLaMA, Falcon, etc.
generator = pipeline(
    "text-generation",
    model="gpt2",
    max_new_tokens=200,
    pad_token_id=50256
)

SYSTEM_PROMPT = (
    "You are a smart retail assistant. You only answer using the given context. "
    "If information is missing, say 'I don't know'. Avoid hallucination."
)


def generate_response(user_message: str, context: str) -> str:
    """
    Generates a response using a local model.
    PII is masked before constructing the prompt.
    """
    masked_message = mask_pii(user_message)

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context: {context}\n"
        f"User: {masked_message}\n"
        f"Assistant:"
    )

    output = generator(prompt)[0]["generated_text"]

    # Return only the assistant reply portion
    if "Assistant:" in output:
        return output.split("Assistant:")[-1].strip()

    return output.strip()
