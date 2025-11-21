from __future__ import annotations
import json
import logging
from typing import Dict, List, Optional
import random

logger = logging.getLogger(__name__)

# ==========================================================
# TRY LOADING THE MODEL
# ==========================================================
try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    _HAVE_TRANSFORMERS = True
except Exception:
    _HAVE_TRANSFORMERS = False


MODEL_NAME = "google/flan-t5-base"
LORA_WEIGHTS_DIR = "model/flan_t5_appetite_lora"

tokenizer = None
model = None
USE_MODEL = False

if _HAVE_TRANSFORMERS:
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(LORA_WEIGHTS_DIR)
        USE_MODEL = True
        logger.info("LoRA model loaded successfully.")
    except Exception as e:
        logger.warning("Model load failed. Using fallback. Error: %s", e)
        USE_MODEL = False


# ==========================================================
# STRONG JSON PROMPT
# ==========================================================
def _build_prompt(ingredients: List[str], category: Optional[str], mode: str) -> str:
    ing_str = ", ".join(ingredients) if ingredients else "basic pantry items"

    return f"""
Generate a recipe using these ingredients: {ing_str}

Your ENTIRE RESPONSE must be ONLY valid JSON in this EXACT format:

{{
  "title": "Short catchy title",
  "category": "{category if category else mode}",
  "ingredients": ["list", "of", "ingredients"],
  "instructions": "5–7 full sentences describing the cooking process."
}}

Rules:
- Title must be under 8 words.
- Instructions must be a normal paragraph, no bullet points.
- DO NOT include ingredients inside the title.
- DO NOT repeat sentences.
- DO NOT add extra fields.
"""


# ==========================================================
# MODEL GENERATOR
# ==========================================================
def _generate_with_model(prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_length=256,
        num_beams=5,
        early_stopping=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# ==========================================================
# JSON PARSER — EXTREMELY ROBUST
# ==========================================================
def _parse_json(text: str) -> Optional[Dict]:
    try:
        return json.loads(text)
    except Exception:
        # Try extracting JSON substring if HF model wrapped text
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except Exception:
            return None


# ==========================================================
# SUPER STRONG FALLBACK GENERATOR
# ==========================================================
def _fallback_recipe(ingredients: List[str], category: Optional[str], mode: str) -> Dict:
    ing = ingredients or ["basic pantry items"]

    # Title patterns
    title_patterns = [
        "Quick {main}",
        "Homestyle {main}",
        "Easy {main} Bowl",
        "Golden {main} Skillet",
        "Comfort {main} Mix",
    ]
    main = ", ".join(ing[:2]).title()
    title = random.choice(title_patterns).format(main=main)

    # Ingredients List – add small enhancements
    ingredient_list = ing + ["salt", "pepper", "oil"]

    # Instructions
    instructions = (
        f"Begin by preparing the main ingredients: {', '.join(ing)}. "
        "Heat a pan over medium heat and add a small amount of oil. "
        "Add the ingredients and sauté until fragrant, ensuring they cook evenly. "
        "Season with salt, pepper, and any herbs you prefer. "
        "Continue cooking until everything blends together smoothly and reaches a pleasant texture. "
        "Taste and adjust seasoning before serving warm."
    )

    return {
        "title": title,
        "category": category or mode,
        "ingredients": ingredient_list,
        "instructions": instructions,
    }


# ==========================================================
# PUBLIC FUNCTION
# ==========================================================
def generate_recipe(
    ingredients: List[str],
    category: Optional[str] = None,
    mode: str = "inventory",
) -> Dict:

    ingredients = [i.strip() for i in ingredients if i.strip()]

    # ------------------ TRY MODEL ------------------
    if USE_MODEL:
        try:
            prompt = _build_prompt(ingredients, category, mode)
            raw = _generate_with_model(prompt)
            parsed = _parse_json(raw)

            if parsed:
                return parsed

            logger.warning("Model returned non-JSON. Falling back.")
        except Exception as e:
            logger.warning("Model generation failed: %s", e)

    # ------------------ FALLBACK -------------------
    return _fallback_recipe(ingredients, category, mode)