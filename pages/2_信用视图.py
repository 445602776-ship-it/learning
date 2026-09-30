import streamlit as st
import graphviz
import pandas as pd
from utils.loader import load_all

st.set_page_config(page_title="信用视图", page_icon="🎯", layout="wide")

st.title("🎯 信用视图")

# ==================== 加载数据 ====================
try:
    data = load_all()
    p2p = data["p2p"]
    o2c = data["o2c"]
    reverse = data["reverse"]
except Exception as e:
    st.error(f"数据加载失败：{e}")
    st.stop()

# ==================== 节点详情数据 ====================
# 每个节点的详细说明
NODE_DETAIL = {
    "合同提交": {
        "系统": "合同管理",
        "单据": "合同",
        "事件": "提交10",
        "信用动作": "信用检查",
        "接口": "信用检查及额度处理",
        "对接人": "合同组",
        "说明": "合同提交时触发信用检查，校验客商是否有逾期、敞口是否超限。",
    },
    "预付申请提交": {
        "系统": "财务管理",
        "单据": "预付申请单1301",
        "事件": "提交10",
        "信用动作": "预付锁定（正数）",
        "接口": "客商授信信息查询 + 信用检查及额度处理",
        "对接人": "财务组",
        "说明": "先查可用额度是否足够，够则做预付锁定，冻结对应额度。",
    },
    "预付支付成功": {
        "系统": "财务管理",
        "单据": "预付申请单1301",
        "事件": "支付成功20",
        "信用动作": "预付占用（正数），锁定转占用",
        "接口": "信用检查及额度处理",
        "对接人": "财务组",
        "说明": "支付成功后，锁定转占用，形成真实正敞口。",
    },
    "到货/验收": {
        "系统": "采购/库存",
        "单据": "到货单XYDJLX002 / 入库单",
        "事件": "验收成功40",
        "信用动作": "验收释放（正数）",
        "接口": "信用检查及额度处理",
        "对接人": "采购组/库存组",
        "说明": "物资类走货权交接，服务类走服务验收，工程类走工程验收。",
    },
    "采购对账": {
        "系统": "采购管理",
        "单据": "采购对账单XYDJLX001",
        "事件": "对账成功160",
        "信用动作": "差额释放",
        "接口": "信用检查及额度处理",
        "对接人": "采购组",
        "说明": "非末次对账，累计对账＞累计释放才调增；末次对账，累计对账≠累计释放时调整。",
    },
    "付款申请支付": {
        "系统": "财务管理",
        "单据": "付款申请单1306",
        "事件": "支付成功20",
        "信用动作": "付款核销（正数）",
        "接口": "信用检查及额度处理",
        "对接人": "财务组",
        "说明": "付款成功后核销应付，减少负敞口。",
    },
    "交货单提交": {
        "系统": "销售管理",
        "单据": "交货单DN",
        "事件": "提交10",
        "信用动作": "业务锁定",
        "接口": "信用检查及额度处理",
        "对接人": "销售组",
        "说明": "交货单提交即锁定，为后续占用预留额度。有预收款时优先用备用金。",
    },
    "货权交接": {
        "系统": "销售管理",
        "单据": "交货单DN",
        "事件": "货权交接",
        "信用动作": "业务占用",
        "接口": "信用检查及额度处理",
        "对接人": "销售组",
        "说明": "货权交接后形成真实占用。优先用客户备用金，剩余用信用额度。",
    },
    "销售结算": {
        "系统": "销售管理",
        "单据": "销售结算单BL",
        "事件": "结算成功50",
        "信用动作": "差额占用",
        "接口": "信用检查及额度处理",
        "对接人": "销售组",
        "说明": "结算时按累计结算与累计占用的差额做调整。",
    },
    "收款认领": {
        "系统": "财务管理",
        "单据": "收款认领单2003",
        "事件": "核销成功60",
        "信用动作": "收款核销（正数）",
        "接口": "信用检查及额度处理",
        "对接人": "财务组",
        "说明": "回款核销后释放占用额度。",
    },
}


def find_node_detail(name):
    """模糊匹配节点详情"""
    for k, v in NODE_DETAIL.items():
        if k in name or name in k:
            return v
    return None


# ==================== 视图切换 ====================
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 全景图", "🔍 节点详情", "⚖️ P2P vs O2C", "💰 额度流向"])


# ==================== Tab 1：全景图 ====================
with tab1:
    st.subheader("信用管理全景图")
    st.caption("从左到右依次是：合同层 → 业务层 → 财务层 → 信用层")

    side = st.radio("选择主线", ["采购侧（P2P）", "销售侧（O2C）"], horizontal=True)

    if side == "采购侧（P2P）":
        g = graphviz.Digraph()
        g.attr(rankdir="LR", bgcolor="transparent")
        g.attr("node", fontname="Microsoft YaHei", fontsize="12", color="#333333")
        g.attr("edge", fontname="Microsoft YaHei", color="#FF6600", penwidth="2.5", arrowsize="1.2")

        # 合同层
        with g.subgraph(name="cluster_contract") as c:
            c.attr(label="合同层", style="dashed", color="#8888CC")
            c.node("C1", "合同提交\n信用检查", shape="box", style="filled", fillcolor="#CCCCFF")

        # 业务层
        with g.subgraph(name="cluster_biz") as c:
            c.attr(label="业务层", style="dashed", color="#88CC88")
            c.node("B1", "到货/验收\n验收释放", shape="box", style="filled", fillcolor="#CCFFCC")
            c.node("B2", "采购对账\n差额释放", shape="box", style="filled", fillcolor="#CCFFCC")

        # 财务层
        with g.subgraph(name="cluster_fin") as c:
            c.attr(label="财务层", style="dashed", color="#FFAA88")
            c.node("F1", "预付申请\n预付锁定", shape="box", style="filled", fillcolor="#FFDDCC")
            c.node("F2", "预付支付\n预付占用", shape="box", style="filled", fillcolor="#FFDDCC")
            c.node("F3", "付款申请\n付款核销", shape="box", style="filled", fillcolor="#FFDDCC")

        # 信用层
        with g.subgraph(name="cluster_credit") as c:
            c.attr(label="信用层", style="dashed", color="#FF8888")
            c.node("CR1", "信用台账\n锁定/占用/释放", shape="box", style="filled", fillcolor="#FFCCCC")

        # 连线
        g.edge("C1", "F1")
        g.edge("F1", "F2")
        g.edge("F2", "CR1")
        g.edge("B1", "CR1")
        g.edge("B2", "CR1")
        g.edge("F3", "CR1")

        st.graphviz_chart(g, use_container_width=True)

    else:
        g = graphviz.Digraph()
        g.attr(rankdir="LR", bgcolor="transparent")
        g.attr("node", fontname="Microsoft YaHei", fontsize="12", color="#333333")
        g.attr("edge", fontname="Microsoft YaHei", color="#FF6600", penwidth="2.5", arrowsize="1.2")

        with g.subgraph(name="cluster_contract") as c:
            c.attr(label="合同层", style="dashed", color="#8888CC")
            c.node("C1", "合同提交\n信用检查", shape="box", style="filled", fillcolor="#CCCCFF")

        with g.subgraph(name="cluster_biz") as c:
            c.attr(label="业务层", style="dashed", color="#88CC88")
            c.node("B1", "销售订单提交\n信用检查", shape="box", style="filled", fillcolor="#CCFFCC")
            c.node("B2", "交货单提交\n业务锁定", shape="box", style="filled", fillcolor="#CCFFCC")
            c.node("B3", "货权交接\n业务占用", shape="box", style="filled", fillcolor="#CCFFCC")
            c.node("B4", "销售结算\n差额占用", shape="box", style="filled", fillcolor="#CCFFCC")

        with g.subgraph(name="cluster_fin") as c:
            c.attr(label="财务层", style="dashed", color="#FFAA88")
            c.node("F1", "收款认领\n收款核销", shape="box", style="filled", fillcolor="#FFDDCC")

        with g.subgraph(name="cluster_credit") as c:
            c.attr(label="信用层", style="dashed", color="#FF8888")
            c.node("CR1", "信用台账\n锁定/占用/释放", shape="box", style="filled", fillcolor="#FFCCCC")

        g.edge("C1", "B1")
        g.edge("B1", "B2")
        g.edge("B2", "B3")
        g.edge("B3", "B4")
        g.edge("B2", "CR1")
        g.edge("B3", "CR1")
        g.edge("B4", "CR1")
        g.edge("F1", "CR1")

        st.graphviz_chart(g, use_container_width=True)


# ==================== Tab 2：节点详情 ====================
with tab2:
    st.subheader("节点详情查询")
    st.caption("选择任意节点，查看该节点的详细信用处理逻辑")

    # 收集所有节点名
    all_nodes = set()
    for df in [p2p, o2c]:
        if "节点" in df.columns:
            all_nodes.update(df["节点"].dropna().tolist())

    node_list = sorted(all_nodes)
    selected = st.selectbox("选择节点", ["请选择"] + node_list)

    if selected != "请选择":
        detail = find_node_detail(selected)

        if detail:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**上游系统**：{detail['系统']}")
                st.markdown(f"**单据**：{detail['单据']}")
                st.markdown(f"**事件**：{detail['事件']}")
            with col2:
                st.markdown(f"**信用动作**：{detail['信用动作']}")
                st.markdown(f"**调用接口**：{detail['接口']}")
                st.markdown(f"**对接人**：{detail['对接人']}")

            st.info(f"💡 说明：{detail['说明']}")

        # 同时显示原始表格行
        st.markdown("---")
        st.markdown("**原始触发点数据**")
        for df in [p2p, o2c]:
            if "节点" in df.columns:
                match = df[df["节点"] == selected]
                if not match.empty:
                    st.dataframe(match, use_container_width=True)


# ==================== Tab 3：P2P vs O2C ====================
with tab3:
    st.subheader("P2P vs O2C 对照")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 采购到付款（P2P）")
        st.markdown("""
        **主线**：合同 → 预付 → 支付 → 验收 → 对账 → 付款 → 核销

        | 阶段 | 信用动作 |
        |---|---|
        | 合同提交 | 信用检查 |
        | 预付提交 | 预付锁定 |
        | 支付成功 | 预付占用 |
        | 验收成功 | 验收释放 |
        | 对账成功 | 差额释放 |
        | 付款成功 | 付款核销 |
        """)

    with col2:
        st.markdown("### 销售到收款（O2C）")
        st.markdown("""
        **主线**：合同 → 订单 → 交货 → 货权交接 → 结算 → 收款 → 核销

        | 阶段 | 信用动作 |
        |---|---|
        | 合同提交 | 信用检查 |
        | 订单提交 | 信用检查 |
        | 交货提交 | 业务锁定 |
        | 货权交接 | 业务占用 |
        | 结算成功 | 差额占用 |
        | 收款核销 | 收款核销 |
        """)

    st.markdown("---")
    st.subheader("核心差异")

    diff_data = pd.DataFrame([
        {"维度": "主跟踪单据", "P2P": "采购合同", "O2C": "交货单（物资）/ 销售订单（服务）"},
        {"维度": "锁定动作", "P2P": "预付锁定", "O2C": "业务锁定"},
        {"维度": "占用动作", "P2P": "预付占用", "O2C": "业务占用"},
        {"维度": "释放动作", "P2P": "验收释放", "O2C": "收款核销"},
        {"维度": "调整动作", "P2P": "差额释放", "O2C": "差额占用"},
        {"维度": "核销动作", "P2P": "付款核销", "O2C": "收款核销"},
        {"维度": "备用金", "P2P": "无", "O2C": "有客户备用金，优先使用"},
        {"维度": "正敞口含义", "P2P": "我方垫资（预付未到货）", "O2C": "我方垫资（赊销未回款）"},
        {"维度": "负敞口含义", "P2P": "对方对我方支持（货到未付款）", "O2C": "对方对我方支持（客户预付未发货）"},
    ])
    st.dataframe(diff_data, use_container_width=True, hide_index=True)


# ==================== Tab 4：额度流向 ====================
with tab4:
    st.subheader("额度流向")
    st.caption("展示每个节点对额度的具体影响")

    side = st.radio("选择主线", ["采购侧（P2P）", "销售侧（O2C）"], horizontal=True, key="flow_side")

    if side == "采购侧（P2P）":
        flow = pd.DataFrame([
            {"节点": "合同提交", "锁定": "", "占用": "", "释放": "", "核销": "", "说明": "信用检查，不动额度"},
            {"节点": "预付申请提交", "锁定": "＋", "占用": "", "释放": "", "核销": "", "说明": "预付锁定，可用减少"},
            {"节点": "预付支付成功", "锁定": "－", "占用": "＋", "释放": "", "核销": "", "说明": "锁定转占用"},
            {"节点": "到货/验收", "锁定": "", "占用": "", "释放": "＋", "核销": "", "说明": "验收释放"},
            {"节点": "采购对账", "锁定": "", "占用": "", "释放": "＋/－", "核销": "", "说明": "差额释放"},
            {"节点": "付款申请支付", "锁定": "", "占用": "", "释放": "", "核销": "＋", "说明": "付款核销"},
            {"节点": "预付款退款", "锁定": "", "占用": "－", "释放": "", "核销": "", "说明": "占用回退"},
            {"节点": "采购退货出库", "锁定": "", "占用": "", "释放": "－", "核销": "", "说明": "验收释放负数"},
            {"节点": "采购退货冲销", "锁定": "", "占用": "", "释放": "＋", "核销": "", "说明": "冲销反向"},
        ])
    else:
        flow = pd.DataFrame([
            {"节点": "合同提交", "锁定": "", "占用": "", "释放": "", "核销": "", "说明": "信用检查，不动额度"},
            {"节点": "销售订单提交", "锁定": "", "占用": "", "释放": "", "核销": "", "说明": "信用检查，不动额度"},
            {"节点": "交货单提交", "锁定": "＋", "占用": "", "释放": "", "核销": "", "说明": "业务锁定"},
            {"节点": "货权交接", "锁定": "－", "占用": "＋", "释放": "", "核销": "", "说明": "锁定转占用，备用金优先"},
            {"节点": "销售结算", "锁定": "", "占用": "＋/－", "释放": "", "核销": "", "说明": "差额占用"},
            {"节点": "收款认领核销", "锁定": "", "占用": "", "释放": "", "核销": "＋", "说明": "收款核销，释放额度"},
            {"节点": "销售退货", "锁定": "", "占用": "－", "释放": "", "核销": "", "说明": "业务占用负数"},
            {"节点": "贷项销售", "锁定": "", "占用": "－", "释放": "", "核销": "", "说明": "业务占用负数"},
            {"节点": "借项销售", "锁定": "", "占用": "＋", "释放": "", "核销": "", "说明": "业务占用正数"},
            {"节点": "交货单删除", "锁定": "", "占用": "－", "释放": "", "核销": "", "说明": "业务占用负数"},
            {"节点": "交货单冲销", "锁定": "", "占用": "－", "释放": "", "核销": "", "说明": "业务占用负数"},
            {"节点": "销售结算冲销", "锁定": "", "占用": "作废", "释放": "", "核销": "", "说明": "差额占用（作废）"},
        ])

    st.dataframe(flow, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**图示说明**")
    st.markdown("""
    - `＋`：增加（正数）
    - `－`：减少（负数）
    - `＋/－`：可能增加也可能减少，取决于差额
    - 空格：该动作不动对应字段
    """)