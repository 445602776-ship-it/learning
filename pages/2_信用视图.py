import streamlit as st
import graphviz

st.title("🎯 信用视图")

tab1, tab2 = st.tabs(["采购侧（P2P）", "销售侧（O2C）"])

with tab1:
    st.subheader("采购到付款全景")
    g = graphviz.Digraph()
    g.attr(rankdir="LR")

    # 节点
    nodes = {
        "合同": "合同提交\n信用检查",
        "预付": "预付申请\n预付锁定",
        "支付": "支付成功\n预付占用",
        "验收": "到货验收\n验收释放",
        "对账": "采购对账\n差额释放",
        "付款": "付款成功\n付款核销",
        "核销": "应付核销\n核销清零",
    }
    for k, v in nodes.items():
        g.node(k, v, shape="box", style="filled", fillcolor="#FFCCCC")

    # 边
    g.edge("合同", "预付")
    g.edge("预付", "支付")
    g.edge("支付", "验收")
    g.edge("验收", "对账")
    g.edge("对账", "付款")
    g.edge("付款", "核销")

    st.graphviz_chart(g)

    st.info("点击节点查看详情（可扩展为交互式）")

with tab2:
    st.subheader("销售到收款全景")
    g = graphviz.Digraph()
    g.attr(rankdir="LR")

    nodes = {
        "合同": "合同提交\n信用检查",
        "订单": "销售订单\n信用检查",
        "交货": "交货单提交\n业务锁定",
        "货权": "货权交接\n业务占用",
        "结算": "销售结算\n差额占用",
        "收款": "收款认领\n收款核销",
        "核销": "核销应收\n释放额度",
    }
    for k, v in nodes.items():
        g.node(k, v, shape="box", style="filled", fillcolor="#CCE5FF")

    g.edge("合同", "订单")
    g.edge("订单", "交货")
    g.edge("交货", "货权")
    g.edge("货权", "结算")
    g.edge("结算", "收款")
    g.edge("收款", "核销")

    st.graphviz_chart(g)