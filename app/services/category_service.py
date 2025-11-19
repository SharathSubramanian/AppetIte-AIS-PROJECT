import os
import joblib

MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "category_classifier.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "category_vectorizer.pkl")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


def tag_categories(ingredients_list):
    """
    Accepts a list of ingredient strings.
    Returns a list of category labels.
    """

    if not ingredients_list:
        return []

    if isinstance(ingredients_list, str):
        ingredients_list = [ingredients_list]

    text = " ".join(ingredients_list).lower().strip()

    X = vectorizer.transform([text])

    preds = model.predict(X)

    return preds.tolist()