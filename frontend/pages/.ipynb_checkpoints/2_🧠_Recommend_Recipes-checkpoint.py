import streamlit as st
from utils.api import get_pantry, get_recommendations

st.title("🧠 Recommend Recipes Using Pantry")

if "token" not in st.session_state:
    st.error("Login required")
    st.stop()

category = st.text_input("Category filter (optional)")

if st.button("Get Recommendations"):
    data, code = get_recommendations(st.session_state.token, category)
    if code == 200:
        for rec in data:
            st.subheader(rec["title"])
            st.write("### Ingredients:")
            st.write(rec["ingredients"])
            st.write("### Instructions:")
            st.write(rec["instructions"])
            st.write("---")
    else:
        st.error("Failed to generate recommendations.")