# app/ml/inference.py

from __future__ import annotations

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Optional: Hugging Face FLAN-T5 + LoRA
# If anything fails, we fall back to a rule-based generator so the app still works.
# ------------------------------------------------------------------------------

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer  # type: ignore

    _HAVE_TRANSFORMERS = True
except Exception:
    _HAVE_TRANSFORMERS = False

MODEL_NAME = "google/flan-t5-base"
LORA_WEIGHTS_DIR = "model/flan_t5_appetite_lora"  # where your LoRA weights live

tokenizer = None
model = None
USE_MODEL = False

if _HAVE_TRANSFORMERS:
    try:
        logger.info("Loading FLAN-T5 model for AppetIte...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        # NOTE: If you want to actually apply LoRA, you can integrate `peft` here.
        # For robustness in this project, we keep it simple.
        USE_MODEL = True
        logger.info("FLAN-T5 loaded successfully.")
    except Exception as e:  # pragma: no cover - defensive
        logger.warning(
            "Could not load FLAN-T5; falling back to rule-based generator. Error: %s",
            e,
        )
        USE_MODEL = False
else:
    logger.warning("transformers not installed; using rule-based generator only.")


# ------------------------------------------------------------------------------
# Helpers for prompt construction and parsing
# ------------------------------------------------------------------------------

CATEGORY_LABELS = [
    "healthy",
    "cheat meal",
    "easy to cook",
    "comfort food",
    "high protein",
]


def _build_prompt(
    ingredients: List[str],
    category: Optional[str],
    mode: str = "inventory",
) -> str:
    """
    Build a natural language prompt for FLAN-T5.
    """
    ing_text = ", ".join(ingredients) if ingredients else "basic pantry staples"

    if mode == "quick":
        prefix = "Create a very quick recipe"
    else:
        prefix = "Create a detailed home-cooked recipe"

    if category and category in CATEGORY_LABELS:
        prefix += f" that fits the '{category}' category"

    prompt = (
        f"{prefix} using the following ingredients: {ing_text}.\n"
        "Return the result in this format:\n"
        "Title: <recipe title>\n"
        "Category: <one of healthy, cheat meal, easy to cook, comfort food, high protein>\n"
        "Ingredients: <comma-separated ingredients list>\n"
        "Instructions: <step-by-step instructions in one paragraph>\n"
    )
    return prompt


def _generate_with_model(prompt: str) -> str:
    """
    Run FLAN-T5 generation and decode to text.
    If anything fails, we raise and the caller will fall back.
    """
    assert tokenizer is not None and model is not None
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    outputs = model.generate(
        **inputs,
        max_length=256,
        num_beams=4,
        early_stopping=True,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def _parse_generated_text(text: str, fallback_title: str) -> Dict:
    """
    Try to parse model output in the 'Title / Category / Ingredients / Instructions' format.
    If parsing fails, we fall back to a simple structure.
    """
    title = None
    category = None
    ingredients: List[str] = []
    instructions_lines: List[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        low = line.lower()

        if low.startswith("title:"):
            title = line.split(":", 1)[1].strip() or fallback_title
        elif low.startswith("category:"):
            category = line.split(":", 1)[1].strip().lower() or None
        elif low.startswith("ingredients:"):
            ing_part = line.split(":", 1)[1]
            ingredients = [x.strip() for x in ing_part.split(",") if x.strip()]
        elif low.startswith("instructions:"):
            instr_part = line.split(":", 1)[1].strip()
            instructions_lines.append(instr_part)
        elif instructions_lines:
            # subsequent lines after "Instructions:" belong to instructions
            instructions_lines.append(line)

    if not title:
        title = fallback_title

    if not ingredients:
        # fallback: we couldn't parse, so don't lose the info
        ingredients = ["See recipe description"]

    instructions = " ".join(x for x in instructions_lines if x) or "Follow standard cooking steps."

    return {
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
        "category": category,
    }


# ------------------------------------------------------------------------------
# Rule-based fallback generator
# ------------------------------------------------------------------------------

def _fallback_title(
    ingredients: List[str],
    category: Optional[str],
    mode: str,
) -> str:
    main = ", ".join(sorted(set(ingredients))) if ingredients else "Pantry"
    if not main:
        main = "Pantry"

    if category == "healthy":
        prefix = "Light & Fresh"
    elif category == "cheat meal":
        prefix = "Indulgent"
    elif category == "easy to cook":
        prefix = "Easy One-Pot"
    elif category == "comfort food":
        prefix = "Cozy"
    elif category == "high protein":
        prefix = "Protein-Packed"
    else:
        prefix = "Simple"

    if mode == "quick":
        suffix = "Quick Fix"
    else:
        suffix = "Dinner"

    return f"{prefix} {main.title()} {suffix}"


def _fallback_recipe(
    ingredients: List[str],
    category: Optional[str],
    mode: str,
) -> Dict:
    title = _fallback_title(ingredients, category, mode)

    if not ingredients:
        ingredients_list = ["basic pantry staples"]
    else:
        ingredients_list = ingredients

    instructions = (
        "1. Gather all the ingredients listed above.\n"
        "2. Heat a pan over medium heat with a little oil.\n"
        "3. Add the main ingredients and cook until tender.\n"
        "4. Season with salt, pepper, and any spices you like.\n"
        "5. Taste and adjust seasoning, then serve warm."
    )

    return {
        "title": title,
        "ingredients": ingredients_list,
        "instructions": instructions,
        "category": category,
    }


# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------

def generate_recipe(
    ingredients: List[str],
    category: Optional[str] = None,
    mode: str = "inventory",
) -> Dict:
    """
    Main entry point used by the services layer.

    - `mode="inventory"`: recipes suggested from pantry inventory
    - `mode="quick"`: "Quick generate" style recipe
    """
    ingredients = [x.strip() for x in ingredients if x and x.strip()]

    if USE_MODEL:
        try:
            prompt = _build_prompt(ingredients, category, mode)
            text = _generate_with_model(prompt)
            fallback_title = _fallback_title(ingredients, category, mode)
            return _parse_generated_text(text, fallback_title=fallback_title)
        except Exception as e:  # pragma: no cover - defensive
            logger.warning("Model generation failed, using fallback. Error: %s", e)

    # Rule-based fallback
    return _fallback_recipe(ingredients, category, mode)