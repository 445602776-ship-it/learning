import pandas as pd
import streamlit as st

@st.cache_data
def load_all():
    path = "data/学习.xlsx"
    sheets = {
        "p2p": "采购到付款(P2P)",
        "o2c": "销售到收款（O2C）",
        "reverse": "逆向特殊场景",
        "interface": "接口清单",
        "ups": "上下游知识库模板",
        "scene": "场景",
        "faq": "高频问题速查",
    }
    data = {}
    for key, sheet in sheets.items():
        data[key] = pd.read_excel(path, sheet_name=sheet)
    return data