import streamlit as st
import pandas as pd

st.title("📖 名词库")

# 加载所有名词 Sheet
sheet_names = [
    "名词-核心主体", "名词-授信类型", "名词-额度处理",
    "名词-信用台账", "名词-评级授信", "名词-信用敞口限额",
    "名词-信用账龄跟踪", "名词-业务流程", "名词-系统配置", "名词-接口"
]

data = {}
for sheet in sheet_names:
    data[sheet] = pd.read_excel("data/学习.xlsx", sheet_name=sheet)

# 搜索
keyword = st.text_input("🔍 搜索名词")

for sheet, df in data.items():
    if keyword:
        df = df[df["名词"].str.contains(keyword, na=False) |
                df["一句话解释"].str.contains(keyword, na=False)]
    if not df.empty:
        st.subheader(sheet.replace("名词-", ""))
        st.dataframe(df, use_container_width=True)