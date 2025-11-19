import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re

MODEL_PATH = "model/flan_t5_appetite_lora"

# Load tokenizer + LoRA fine-tuned model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
model.eval()


def extract_title_and_instructions(text: str):
    """
    FLAN sometimes generates:
    'Title: ... Instructions: ...'
    or just plain text. This cleans and splits reliably.
    """

    text = text.replace("TitleTitle", "Title").replace("InstructionsInstructions", "Instructions")
    text = text.strip()

    # Normalize markers
    text = text.replace("TITLE:", "Title:").replace("INSTRUCTIONS:", "Instructions:")

    # Try extracting Title
    title_match = re.search(r"Title\s*[:\-]\s*(.+?)(?:Instructions|$)", text, re.DOTALL | re.IGNORECASE)

    if title_match:
        title = title_match.group(1).strip()
    else:
        # fallback
        title = "Generated Recipe"

    # Extract instructions
    instr_match = re.search(r"Instructions\s*[:\-]\s*(.+)", text, re.DOTALL | re.IGNORECASE)

    if instr_match:
        instructions = instr_match.group(1).strip()
    else:
        # fallback to entire text
        instructions = text

    # Make sure instructions have numbered steps
    if not re.search(r"\d\.", instructions):
        instructions = "1. " + instructions.replace("\n", " ")

    return title, instructions


def generate_recipe_from_ingredients(ingredients: str):
    """
    Return: (title, instructions)
    Exactly as required by recipe_router + RecipeResponse.
    """

    prompt = (
        f"Create a detailed cooking recipe using the following ingredients: {ingredients}.\n"
        f"Provide the output in this format:\n"
        f"Title: <recipe name>\n"
        f"Instructions: <step-by-step instructions>"
    )

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=380,
            num_beams=4,
            temperature=0.7,
            top_p=0.9,
            early_stopping=True
        )

    raw_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract clean output
    title, instructions = extract_title_and_instructions(raw_text)

    return title, instructions