from app.ml.inference import _generate_with_model, _build_prompt

ingredients = ["chicken", "butter"]
prompt = _build_prompt(ingredients, None, mode="quick")

print("PROMPT:\n", prompt)
print("---- RAW MODEL OUTPUT ----")
print(_generate_with_model(prompt))