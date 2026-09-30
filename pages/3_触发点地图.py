import streamlit as st
from utils.loader import load_all

st.title("🗺️ 触发点地图")
data = load_all()

tab1, tab2, tab3 = st.tabs(["P2P", "O2C", "逆向"])

with tab1:
    st.dataframe(data["p2p"], use_container_width=True)

with tab2:
    st.dataframe(data["o2c"], use_container_width=True)

with tab3:
    st.dataframe(data["reverse"], use_container_width=True)