import streamlit as st
from utils.loader import load_all

st.title("📋 场景大全")
data = load_all()
scene = data["scene"]

# 筛选
col1, col2, col3 = st.columns(3)
with col1:
    risk = st.multiselect("风险等级", scene["风险等级"].unique())
with col2:
    category = st.multiselect("场景分类", scene["场景分类"].unique())
with col3:
    name = st.multiselect("场景名称", scene["场景名称"].unique())

filtered = scene.copy()
if risk:
    filtered = filtered[filtered["风险等级"].isin(risk)]
if category:
    filtered = filtered[filtered["场景分类"].isin(category)]
if name:
    filtered = filtered[filtered["场景名称"].isin(name)]

st.dataframe(filtered, use_container_width=True)