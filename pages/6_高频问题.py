import streamlit as st
from utils.loader import load_all

st.title("❓ 高频问题速查")
data = load_all()
faq = data["faq"]

keyword = st.text_input("🔍 搜索问题")
if keyword:
    faq = faq[faq["现场问"].str.contains(keyword, na=False)]

for _, row in faq.iterrows():
    with st.expander(row["现场问"]):
        st.markdown(f"**答案**：{row['答案']}")
        st.markdown(f"**去哪找**：{row['关键描述（去哪找）']}")