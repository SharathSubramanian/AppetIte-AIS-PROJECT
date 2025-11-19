from typing import Optional

import torch

from ..config import MAX_INPUT_LEN
from ..deps import get_model_and_tokenizer, get_device


def generate_recipe(ingredients_text: str, category: Optional[str] = None,
                    max_new_tokens: int = 256) -> str:
    model, tokenizer = get_model_and_tokenizer()
    device = get_device()

    cat_part = ""
    if category:
        cat_part = f"{category} "

    prompt = (
        f"Given the following ingredients: {ingredients_text}\n"
        f"Write a {cat_part}cooking recipe.\n"
        f"Format STRICTLY as:\n"
        f"Title: <recipe title>\n"
        f"\n"
        f"Instructions:\n"
        f"1. <step 1>\n"
        f"2. <step 2>\n"
        f"3. <step 3>\n"
        f"Each step MUST be on a new line.\n"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_INPUT_LEN,
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3,
        )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if "Instructions:" in text:
        text = text.replace("Instructions:", "\n\nInstructions:\n")
    text = text.replace(". ", ".\n")

    return text