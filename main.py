import streamlit as st
import time

from agent_extractor import extract_intent_and_info
from routing_engine import route_ticket
from agent_responder import generate_empathy_response

st.set_page_config(
    page_title="智能售后控制台 Demo | AI Routing System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


custom_css = """
<style>
    /* 隐藏顶部导航条和底部水印 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* 紧凑顶部留白 */
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}
    
    /* 标题样式定制 */
    h1 {
        font-weight: 600;
        color: #1E293B;
        font-size: 1.8rem !important;
        margin-bottom: 0.5rem;
    }
    .sub-head {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 2rem;
        font-family: monospace;
    }
    
    /* 卡片与模块的精致边框 */
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 5px;
    }
    
    /* 状态指示器小绿点/小红点 */
    .status-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    .dot-green { background-color: #22C55E; }
    .dot-red { background-color: #EF4444; }
    .dot-yellow { background-color: #F59E0B; }
    
    /* 按钮样式微调 */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        font-weight: 500;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 顶部导航区
st.markdown("""
    <h1>电商售后智能决策平台 Demo <span style="font-size: 14px; font-weight: normal; background: #E2E8F0; padding: 2px 8px; border-radius: 4px; margin-left: 10px">v2.1 API_Connected</span></h1>
    <div class="sub-head">项目: 智能售后决策平台 | 模型: qwen-max-01</div>
""", unsafe_allow_html=True)

# 侧边栏：用来充当工单进线系统模拟器
with st.sidebar:
    st.markdown("<h3 style='font-size: 1.1em; color: #475569;'>工单模拟投递器 (Simulator)</h3>", unsafe_allow_html=True)
    st.caption("此面板用于向主引擎推送测试工单数据。")
    order_amount = st.number_input("订单金额 (CNY)", min_value=0.0, max_value=10000.0, value=35.0, step=1.0)
    credit_score = st.selectbox("买家风控画像评级", ["高", "中", "低"])
    
    chat_history = st.text_area(
        "历史聊天数据 (Chat Logs)",
        value="买家: 衣服上的印花整个裂开了，怎么回事啊？\n卖家: 亲亲，这不是质量问题哦，是洗涤不当。\n买家: 我刚拆开都没穿好吗？\n卖家: 那您退货退款吧。\n买家: 我凭什么出运费？没有图片你要不要看？",
        height=150
    )
    current_query = st.text_input("当前进线诉求 (User Query)", value="衣服破的不成样子了！这是骗子店吧！要求处理！")
    
    run_engine = st.button("投递工单入列", type="primary")

# 占位符，如果没有开始跑流，显示一个仪表盘的空状态
if not run_engine:
    st.info("ℹ️ 系统处于监听状态。请在左侧侧边栏配置工单参数，点击「投递工单入列」以触发大模型链路。")
    # 可以加点大厂后台常见的假数据展示
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("今日自动接管客诉", "12,845", "12%", delta_color="normal")
    col_b.metric("平均意图识别耗时", "1.4s", "-0.2s", delta_color="inverse")
    col_c.metric("拦截资损风险", "¥38,400", "5%", delta_color="normal")
    col_d.metric("NPS (安抚防滑点)", "4.8/5.0", "0.2", delta_color="normal")

else:
    order_info = {"amount": order_amount}
    
    # 将页面划分为左中右三栏，更符合 B 端监控大屏的布局
    col_data, col_trace, col_result = st.columns([1, 1.2, 1])
    
    with col_data:
        st.markdown("<h4 style='font-size: 1em; color: #334155;'>原始数据 (Raw Inputs)</h4>", unsafe_allow_html=True)
        st.code(f"金额: ¥{order_amount} | 风控: {credit_score}\n\n[近期对话]\n{chat_history}\n\n[最新诉求]\n{current_query}", language="text")

    with col_trace:
        st.markdown("<h4 style='font-size: 1em; color: #334155;'>运行轨迹 (Execution Trace)</h4>", unsafe_allow_html=True)
        
        # 使用 st.status 做步骤指示，看起来更像后端在跑日志
        with st.status("正在解析非结构化文本...", expanded=True) as status:
            st.write("调用 Agent 1 (Information Extractor)...")
            extracted_json = extract_intent_and_info(order_info, chat_history, current_query)
            st.write("抽取完毕。执行风控路由匹配...")
            
            time.sleep(0.5)
            route_result = route_ticket(extracted_json, order_info, credit_score)
            
            st.write("调用 Agent 2 (Empathy Responder) 生成话术...")
            response_text = generate_empathy_response(
                summary=extracted_json['summary'],
                emotion_score=extracted_json['emotion_score'],
                route_action=route_result['route_action']
            )
            status.update(label="链路执行完成", state="complete", expanded=False)
            
        # 提取结果展示
        st.write("**Agent 1 结构化输出:**")
        st.json(extracted_json)

    with col_result:
        st.markdown("<h4 style='font-size: 1em; color: #334155;'>最终决策 (Final Decision)</h4>", unsafe_allow_html=True)
        
        # 动态状态灯指示
        if route_result['next_step'] == "system_refund":
            status_html = '<span class="status-dot dot-green"></span> 极速阻断与退款'
        elif route_result['next_step'] == "human_escalation":
            status_html = '<span class="status-dot dot-red"></span> 高危转交人工'
        else:
            status_html = '<span class="status-dot dot-yellow"></span> 补充凭证或常规排队'
            
        st.markdown(f"<div style='padding: 10px; background: white; border-radius: 6px; border-left: 4px solid #475569;'>{status_html}<br><br><b>策略原因:</b> {route_result['reason']}</div>", unsafe_allow_html=True)
        
        st.markdown("<br><h4 style='font-size: 1em; color: #334155;'>拟定安抚话术输出</h4>", unsafe_allow_html=True)
        # 用清爽的对话框
        st.info(response_text)
