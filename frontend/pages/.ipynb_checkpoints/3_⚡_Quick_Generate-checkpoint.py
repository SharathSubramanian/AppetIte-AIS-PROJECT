import streamlit as st
from utils.api import quick_generate

st.title("⚡ Quick Generate Recipe")

ingredients = st.text_area("Enter ingredients (comma-separated):")

if st.button("Generate"):
    ing_list = [i.strip() for i in ingredients.split(",") if i.strip()]
    data, code = quick_generate(st.session_state.token, ing_list)
    if code == 200:
        rec = data["recipe"]
        st.subheader(rec["title"])
        st.write("### Ingredients")
        st.write(rec["ingredients"])
        st.write("### Instructions")
        st.write(rec["instructions"])
    else:
        st.error("Generation failed.")