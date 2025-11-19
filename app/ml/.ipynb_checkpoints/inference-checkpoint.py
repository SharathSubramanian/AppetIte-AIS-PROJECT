# app/ml/inference.py
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Dict

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel


# ---- Paths & constants ----

BASE_MODEL_NAME = "google/flan-t5-base"
# Path: project_root/model/flan_t5_appetite_lora
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PEFT_WEIGHTS_DIR = PROJECT_ROOT / "model" / "flan_t5_appetite_lora"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ---- Lazy-loaded globals ----

_tokenizer = None
_model = None


def _load_model_and_tokenizer():
    """
    Lazy-load FLAN-T5 base and attach LoRA weights.
    This is called once, then kept in memory.
    """
    global _tokenizer, _model

    if _tokenizer is not None and _model is not None:
        return _tokenizer, _model

    # 1) Load base model + tokenizer
    _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    base_model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_NAME)

    # 2) Attach LoRA weights
    _model = PeftModel.from_pretrained(base_model, PEFT_WEIGHTS_DIR)

    _model.to(DEVICE)
    _model.eval()

    return _tokenizer, _model


# ---- Prompt & parsing helpers ----

def _build_prompt(ingredients: List[str], category: Optional[str] = None) -> str:
    """
    Prompt template for the FLAN model.

    We force a structured format so we can parse:
    Title:
    Ingredients:
    - ...
    Instructions:
    1) ...
    """
    ingredient_str = ", ".join(ingredients) if ingredients else "no specific ingredients"

    category_part = f"\nPreferred category: {category}." if category else ""

    prompt = f"""
You are an AI chef for a smart pantry app called AppetIte.

Given the available ingredients:
{ingredient_str}
{category_part}

Generate ONE recipe that:
- Uses as many of the given ingredients as is reasonable.
- Is simple and practical to cook.
- Fits the category if specified.

Respond in EXACTLY this format:

Title: <one-line title>

Ingredients:
- ingredient 1
- ingredient 2
- ...

Instructions:
1. First step
2. Second step
3. ...

Do not add any extra sections.
"""
    return prompt.strip()


def _parse_recipe_output(text: str) -> Dict[str, str | List[str]]:
    """
    Parse the model's text output into {title, ingredients, instructions}.
    Handles messy cases where Title and Instructions are on the same line.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    title = "Untitled Recipe"
    ingredients: List[str] = []
    instructions_lines: List[str] = []

    section = None  # "title" | "ingredients" | "instructions" | None

    for line in lines:
        lower = line.lower()

        # Case 1: "Title: ... Instructions: ..."
        if "title:" in lower and "instructions:" in lower:
            # Split at "instructions:"
            before, after = line.split("Instructions:", 1)
            # Extract title from before
            if "Title:" in before:
                title_part = before.split("Title:", 1)[1].strip()
                if title_part:
                    title = title_part
            # The rest becomes the first instructions line
            first_instr = after.strip()
            if first_instr:
                instructions_lines.append(first_instr)
            section = "instructions"
            continue

        # Case 2: normal "Title:" line
        if lower.startswith("title:"):
            section = "title"
            t = line.split(":", 1)[1].strip()
            if t:
                title = t
            continue

        # Case 3: "Ingredients:"
        if lower.startswith("ingredients:"):
            section = "ingredients"
            continue

        # Case 4: "Instructions:"
        if lower.startswith("instructions:"):
            section = "instructions"
            continue

        # Content lines
        if section == "ingredients":
            # Expect "- item" or similar
            if line.startswith(("-", "*", "•")):
                ingredients.append(line.lstrip("-*• ").strip())
            else:
                # If the model didn't format nicely, still treat as ingredient
                ingredients.append(line.strip())

        elif section == "instructions":
            instructions_lines.append(line)

    if not ingredients:
        ingredients = ["See recipe description"]

    instructions_text = "\n".join(instructions_lines).strip()
    if not instructions_text:
        instructions_text = "Follow standard cooking steps."

    return {
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions_text,
    }


# ---- Public API ----

def generate_recipe_from_ingredients(
    ingredients: List[str],
    category: Optional[str] = None,
    max_new_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> Dict[str, str | List[str]]:
    """
    Main inference function.

    Returns a dict with:
    - title: str
    - ingredients: List[str]
    - instructions: str
    """
    tokenizer, model = _load_model_and_tokenizer()

    prompt = _build_prompt(ingredients, category)

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    ).to(DEVICE)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            num_beams=1,
        )

    decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    parsed = _parse_recipe_output(decoded)

    
    if not parsed["ingredients"] or parsed["ingredients"] == ["See recipe description"]:
        parsed["ingredients"] = ingredients if ingredients else ["See recipe description"]

    return parsed