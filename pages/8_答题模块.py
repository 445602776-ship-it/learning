import streamlit as st
import pandas as pd
from datetime import datetime
from utils.quiz_loader import load_quiz

st.set_page_config(page_title="答题模块", page_icon="📝", layout="wide")

st.title("📝 信用管理答题模块")

# ==================== 加载题库 ====================
try:
    quiz = load_quiz()
except Exception as e:
    st.error(f"题库加载失败：{e}")
    st.stop()

if quiz.empty:
    st.warning("题库为空，请检查 data/题库.xlsx")
    st.stop()

# ==================== 错题本 ====================
if "wrong_book" not in st.session_state:
    st.session_state["wrong_book"] = []

# ==================== 侧边栏设置 ====================
with st.sidebar:
    st.header("🎯 答题设置")

    mode = st.radio("答题模式", ["练习模式（即时反馈）", "考试模式（交卷后反馈）"])

    # 分类筛选
    categories = ["全部"] + sorted(quiz["分类"].unique().tolist())
    selected_category = st.selectbox("分类", categories)

    # 题型筛选
    qtypes = ["全部"] + sorted(quiz["题型"].unique().tolist())
    selected_qtype = st.selectbox("题型", qtypes)

    # 难度筛选
    difficulties = ["全部"] + sorted(quiz["难度"].unique().tolist())
    selected_difficulty = st.selectbox("难度", difficulties)

    # 题目数量
    max_count = len(quiz)
    count = st.slider("题目数量", min_value=5, max_value=min(50, max_count), value=10)

    start = st.button("🚀 开始答题", type="primary", use_container_width=True)

    st.markdown("---")
    st.caption(f"题库共 {len(quiz)} 题")

# ==================== 筛选题目 ====================
filtered = quiz.copy()
if selected_category != "全部":
    filtered = filtered[filtered["分类"] == selected_category]
if selected_qtype != "全部":
    filtered = filtered[filtered["题型"] == selected_qtype]
if selected_difficulty != "全部":
    filtered = filtered[filtered["难度"] == selected_difficulty]

# ==================== 开始答题 ====================
if start:
    if filtered.empty:
        st.sidebar.error("没有符合筛选条件的题目")
    else:
        sample_n = min(count, len(filtered))
        st.session_state["quiz_questions"] = filtered.sample(sample_n).to_dict("records")
        st.session_state["quiz_answers"] = {}
        st.session_state["quiz_submitted"] = False
        st.session_state["quiz_mode"] = "练习" if "练习" in mode else "考试"


# ==================== 答题区 ====================
if "quiz_questions" not in st.session_state:
    st.info("👈 在左侧设置答题条件，点击「开始答题」")
    st.subheader("📊 题库统计")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总题数", len(quiz))
    with col2:
        st.metric("单选题", len(quiz[quiz["题型"] == "单选"]))
    with col3:
        st.metric("多选题", len(quiz[quiz["题型"] == "多选"]))
    with col4:
        st.metric("判断题", len(quiz[quiz["题型"] == "判断"]))
    st.stop()

quiz_questions = st.session_state["quiz_questions"]
quiz_answers = st.session_state["quiz_answers"]
submitted = st.session_state["quiz_submitted"]
is_practice = st.session_state["quiz_mode"] == "练习"

# ==================== 逐题展示 ====================
st.subheader(f"共 {len(quiz_questions)} 题")
st.progress(len(quiz_answers) / len(quiz_questions))

for i, q in enumerate(quiz_questions):
    qid = q["题号"]
    qtype = q["题型"]

    st.markdown(f"---")
    st.markdown(f"**第 {i+1} 题**  ·  {qtype}  ·  {q['难度']}  ·  {q['分类']}")
    st.markdown(f"**{q['题干']}**")

    # 选项准备
    options = []
    for letter in ["A", "B", "C", "D"]:
        opt = str(q.get(f"选项{letter}", "")).strip()
        if opt:
            options.append((letter, opt))

    # 单选题
    if qtype == "单选":
        labels = ["请选择"] + [f"{letter}. {opt}" for letter, opt in options]
        key = f"radio_{qid}"
        disabled = submitted

        answer = st.radio(
            f"选择_{qid}",
            labels,
            key=key,
            disabled=disabled,
            label_visibility="collapsed",
        )
        if answer and answer != "请选择" and not disabled:
            quiz_answers[qid] = answer[0]

    # 多选题
    elif qtype == "多选":
        labels = [f"{letter}. {opt}" for letter, opt in options]
        key = f"multi_{qid}"
        disabled = submitted  # ← 关键修改：只在提交后禁用

        answer = st.multiselect(
            f"选择_{qid}",
            labels,
            key=key,
            disabled=disabled,
            label_visibility="collapsed",
        )
        if answer and not disabled:
            quiz_answers[qid] = "".join(sorted([a[0] for a in answer]))

    # 判断题
    elif qtype == "判断":
        key = f"judge_{qid}"
        disabled = submitted  # ← 关键修改

        answer = st.radio(
            f"判断_{qid}",
            ["请选择", "对", "错"],  # ← 关键修改：加占位项
            key=key,
            disabled=disabled,
            horizontal=True,
            label_visibility="collapsed",
        )
        if answer and answer != "请选择" and not disabled:
            quiz_answers[qid] = answer

    # 填空题
    elif qtype == "填空":
        key = f"fill_{qid}"
        disabled = submitted or (is_practice and qid in quiz_answers)

        answer = st.text_input(
            f"填空_{qid}",
            key=key,
            disabled=disabled,
            label_visibility="collapsed",
        )
        if answer and not disabled:
            quiz_answers[qid] = answer.strip()

    # 练习模式或已交卷：显示对错
    if submitted or (is_practice and qid in quiz_answers):
        correct = str(q["正确答案"]).strip().upper()
        user = str(quiz_answers.get(qid, "")).strip().upper()

        # 判断题不需要 upper
        if qtype == "判断":
            correct = str(q["正确答案"]).strip()
            user = str(quiz_answers.get(qid, "")).strip()
        # 填空题不强转大写
        if qtype == "填空":
            correct = str(q["正确答案"]).strip()
            user = str(quiz_answers.get(qid, "")).strip()

        if user == correct:
            st.success(f"✅ 回答正确！正确答案：{q['正确答案']}")
        else:
            st.error(f"❌ 回答错误。你的答案：{quiz_answers.get(qid, '未作答')}　正确答案：{q['正确答案']}")
        st.info(f"💡 解析：{q['解析']}")
        st.caption(f"📖 来源：{q['来源']}")

# ==================== 提交按钮 ====================
if not submitted:
    st.markdown("---")
    if st.button("📤 提交答卷", type="primary", use_container_width=True):
        st.session_state["quiz_submitted"] = True


# ==================== 成绩单 ====================
if submitted:
    st.markdown("---")
    st.header("📊 成绩单")

    correct_count = 0
    wrong_list = []

    for q in quiz_questions:
        qid = q["题号"]
        qtype = q["题型"]
        correct = str(q["正确答案"]).strip()
        user = str(quiz_answers.get(qid, "")).strip()

        # 单选/多选做 upper 比较
        if qtype in ["单选", "多选"]:
            correct_cmp = correct.upper()
            user_cmp = user.upper()
        else:
            correct_cmp = correct
            user_cmp = user

        if user_cmp == correct_cmp and user != "":
            correct_count += 1
        else:
            wrong_list.append({
                "题号": qid,
                "题型": qtype,
                "难度": q["难度"],
                "题干": q["题干"],
                "你的答案": user if user else "未作答",
                "正确答案": correct,
                "解析": q["解析"],
                "来源": q["来源"],
            })

    total = len(quiz_questions)
    score = round(correct_count / total * 100, 1) if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("得分", f"{score} 分")
    with col2:
        st.metric("总题数", total)
    with col3:
        st.metric("正确", correct_count)
    with col4:
        st.metric("错误", total - correct_count)

    if score >= 90:
        st.success("🎉 优秀！你已经掌握了核心知识点。")
    elif score >= 70:
        st.info("👍 良好，建议复习错题。")
    else:
        st.warning("📖 还需加强，建议重新学习相关章节。")

    # ==================== 错题本 ====================
    if wrong_list:
        st.subheader("❌ 错题本")
        wrong_df = pd.DataFrame(wrong_list)
        st.dataframe(wrong_df, use_container_width=True)

        # 保存到 session_state
        if st.button("📥 保存错题到错题本"):
            for w in wrong_list:
                st.session_state["wrong_book"].append({
                    **w,
                    "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
            st.success(f"已保存 {len(wrong_list)} 道错题")
    else:
        st.balloons()
        st.success("🎊 全部答对！")

    # ==================== 重新答题 ====================
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 重新答题", use_container_width=True):
            for k in ["quiz_questions", "quiz_answers", "quiz_submitted", "quiz_mode"]:
                st.session_state.pop(k, None)
            st.rerun()
    with col2:
        if st.button("📕 只做错题", use_container_width=True):
            if wrong_list:
                st.session_state["quiz_questions"] = [
                    q for q in quiz_questions
                    if q["题号"] in [w["题号"] for w in wrong_list]
                ]
                st.session_state["quiz_answers"] = {}
                st.session_state["quiz_submitted"] = False
                st.rerun()
            else:
                st.warning("没有错题")

# ==================== 历史错题本 ====================
st.markdown("---")
st.header("📕 我的错题本")

if not st.session_state["wrong_book"]:
    st.info("暂无错题记录")
else:
    wb_df = pd.DataFrame(st.session_state["wrong_book"])
    st.dataframe(wb_df, use_container_width=True)

    if st.button("🗑️ 清空错题本"):
        st.session_state["wrong_book"] = []
        st.rerun()