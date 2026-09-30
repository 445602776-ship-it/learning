import pandas as pd
import streamlit as st

STANDARD_COLS = [
    "题号", "题型", "分类", "难度", "题干",
    "选项A", "选项B", "选项C", "选项D",
    "正确答案", "解析", "来源"
]


@st.cache_data
def load_quiz():
    """加载题库.xlsx 的所有 sheet，合并成一个 DataFrame"""
    path = "data/题库.xlsx"
    xls = pd.ExcelFile(path)

    dfs = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet, dtype=str)
        df = df.dropna(how="all")  # 去掉全空行

        # 只保留标准列，缺失的补齐
        for c in STANDARD_COLS:
            if c not in df.columns:
                df[c] = ""
        df = df[STANDARD_COLS]

        # 去掉没有题号的空行
        df = df[df["题号"].notna() & (df["题号"].str.strip() != "")]
        dfs.append(df)

    quiz = pd.concat(dfs, ignore_index=True)
    quiz = quiz.fillna("")
    return quiz