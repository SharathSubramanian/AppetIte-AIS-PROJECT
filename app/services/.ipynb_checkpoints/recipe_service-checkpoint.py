from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel
import torch

BASE_MODEL = "google/flan-t5-base"
LORA_PATH = "model/flan_t5_appetite_lora"

print("Loading base FLAN-T5...")
base_model = AutoModelForSeq2SeqLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.float32,
    device_map="cpu"
)

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(LORA_PATH)

print("Applying LoRA adapters...")
model = PeftModel.from_pretrained(
    base_model,
    LORA_PATH,
    dtype=torch.float32
)

model = model.to("cpu")
model.eval()


def clean_text(text: str):
    """Remove weird repeats & fix header duplication."""
    text = text.replace("TitleTitle", "Title")
    text = text.replace("InstructionsInstructions", "Instructions")
    text = text.strip()
    return text


def split_instructions(raw: str):
    """
    Convert raw instruction string → list[str],
    dedupe repeated lines, remove garbage.
    """
    lines = raw.split("\n")
    steps = []

    seen = set()
    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Remove step numbering like "1." or "Step 1:"
        line = line.lstrip("0123456789. ").strip()

        if len(line) < 3:
            continue

        if line not in seen:
            seen.add(line)
            steps.append(line)

    return steps



def generate_recipe(ingredients: str):
    prompt = (
        "Generate a complete recipe.\n"
        f"Ingredients: {ingredients}\n\n"
        "Format:\n"
        "Title: <recipe title>\n"
        "Instructions:\n"
        "1. <short step>\n"
        "2. <short step>\n"
        "3. <short step>\n"
        "Do NOT repeat steps.\n"
    )

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to("cpu")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=250,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3,   
            repetition_penalty=2.0,   
            length_penalty=1.0,
        )

    raw = tokenizer.decode(outputs[0], skip_special_tokens=True)
    raw = clean_text(raw)

    if "Title:" in raw:
        title_part = raw.split("Title:", 1)[1]
        if "Instructions:" in title_part:
            title = title_part.split("Instructions:", 1)[0].strip()
        else:
            title = title_part.strip()
    else:
        title = "Generated Recipe"

    if "Instructions:" in raw:
        instr_raw = raw.split("Instructions:", 1)[1].strip()
    else:
        instr_raw = raw

    instructions = split_instructions(instr_raw)

    if not instructions:
        instructions = ["Mix ingredients and cook."]

    return title, instructions


def generate_recipe_from_ingredients(ingredients: str):
    return generate_recipe(ingredients)