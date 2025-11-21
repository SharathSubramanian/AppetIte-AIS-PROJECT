# app/ml/inference.py

from __future__ import annotations

import logging
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Try loading transformers + model
# ------------------------------------------------------------
try:
    from transformers import (
        AutoTokenizer,
        T5ForConditionalGeneration,
    )
    _HAVE_TRANSFORMERS = True
except Exception:
    _HAVE_TRANSFORMERS = False

# Your model directory
MODEL_DIR = "model/flan_t5_appetite_lora"

tokenizer = None
model = None
USE_MODEL = False


# ------------------------------------------------------------
# Try loading your fine-tuned model
# ------------------------------------------------------------
if _HAVE_TRANSFORMERS:
    try:
        if os.path.exists(MODEL_DIR):
            logger.info(f"Loading FLAN-T5 model from {MODEL_DIR} ...")
            tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
            model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)
            USE_MODEL = True
            logger.info("FLAN-T5 + LoRA loaded successfully.")
        else:
            raise FileNotFoundError(f"Model directory not found: {MODEL_DIR}")
    except Exception as e:
        logger.warning(f"Model load failed. Using fallback generator. Error: {e}")
        USE_MODEL = False
else:
    logger.warning("Transformers not available. Using fallback generator.")
    USE_MODEL = False


# ------------------------------------------------------------
# Categories you want
# ------------------------------------------------------------
CATEGORY_LABELS = [
    "healthy",
    "cheat meal",
    "easy to cook",
    "comfort food",
    "high protein",
]


# ------------------------------------------------------------
# Prompt builder
# ------------------------------------------------------------
def _build_prompt(ingredients: List[str], category: Optional[str], mode: str):
    ing_text = ", ".join(ingredients) if ingredients else "basic pantry items"

    prompt = (
        f"Create a recipe using: {ing_text}. "
        f"Category preference: {category if category else 'any'}. "
        "Respond EXACTLY in the following format:\n"
        "TITLE: <title>\n"
        "CATEGORY: <one label from healthy, cheat meal, easy to cook, comfort food, high protein>\n"
        "INGREDIENTS: <comma separated list>\n"
        "INSTRUCTIONS: <single paragraph of cooking steps>\n"
    )
    return prompt


# ------------------------------------------------------------
# Parse model output precisely
# ------------------------------------------------------------
def _parse_output(text: str) -> Dict:
    """
    Fixes the issue where FLAN outputs everything in one big line.
    We split carefully and sanitize.
    """

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    title, category = None, None
    ingredients, instructions = [], ""

    for line in lines:
        upper = line.upper()

        if upper.startswith("TITLE:"):
            title = line.split(":", 1)[1].strip()

        elif upper.startswith("CATEGORY:"):
            category = line.split(":", 1)[1].strip().lower()
            if category not in CATEGORY_LABELS:
                category = "easy to cook"

        elif upper.startswith("INGREDIENTS:"):
            raw = line.split(":", 1)[1].strip()
            ingredients = [x.strip() for x in raw.split(",") if x.strip()]

        elif upper.startswith("INSTRUCTIONS:"):
            instructions = line.split(":", 1)[1].strip()

    # final fallbacks
    if not title:
        title = "Simple Recipe"
    if not ingredients:
        ingredients = ["See recipe description"]
    if not instructions:
        instructions = "Follow standard cooking steps."

    return {
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
        "category": category,
    }


# ------------------------------------------------------------
# Model-based generation
# ------------------------------------------------------------
def _generate_with_model(prompt: str) -> Dict:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    output = model.generate(
        **inputs,
        max_length=256,
        temperature=0.7,
        top_p=0.9,
    )
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    return _parse_output(decoded)


# ------------------------------------------------------------
# Rule-based fallback
# ------------------------------------------------------------
def _fallback_recipe(ingredients: List[str], category: Optional[str]):
    title = "Simple " + ", ".join(ingredients).title() if ingredients else "Simple Pantry Meal"
    return {
        "title": title,
        "ingredients": ingredients or ["basic pantry items"],
        "instructions": (
            "1. Combine listed ingredients.\n"
            "2. Cook on medium heat.\n"
            "3. Adjust seasoning.\n"
            "4. Serve warm."
        ),
        "category": category or "easy to cook",
    }


# ------------------------------------------------------------
# PUBLIC API: Used by backend
# ------------------------------------------------------------
def generate_recipe(
    ingredients: List[str],
    category: Optional[str] = None,
    mode: str = "inventory",
) -> Dict:

    ingredients = [x.strip() for x in ingredients if x.strip()]

    if USE_MODEL:
        try:
            prompt = _build_prompt(ingredients, category, mode)
            return _generate_with_model(prompt)
        except Exception as e:
            logger.error(f"Model failed, using fallback. Error: {e}")

    # fallback
    return _fallback_recipe(ingredients, category)