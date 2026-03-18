import json
import time

def extract_intent_and_info(order_info: dict, chat_history: str, current_query: str) -> dict:
    """
    大模型 Agent 1: 争议信息提取器 (Information Extractor)
    
    真实业务中，此处将调用各大厂的 LLM API (如阿里通义千问、OpenAI GPT-4等)，
    并注入System Prompt（如 Prompt设计文档_电商售后智能客服.md 所示），
    结合 Few-Shot 给出 JSON 格式的输出。
    
    本函数在这里作为演示(Demo)用途，使用 Mock 数据模拟大模型的输出结果。
    
    :param order_info: 订单基础数据（如：金额、品类、物流状态）
    :param chat_history: 买卖双方历史聊天记录（文本化）
    :param current_query: 用户本次进线的诉求
    :return: 包含核心冲突、买家意图、卖家态度、情绪得分等结构化信息的字典
    """
    # 模拟大模型调用延迟 (思考时间)
    time.sleep(1.5)
    
    # 简单的基于关键词的"伪大模型" Mock 逻辑，用于演示不同场景
    query_lower = current_query.lower()
    chat_lower = chat_history.lower()
    
    # 默认返回结构
    mock_result = {
        "core_conflict": "未知问题",
        "buyer_intent": "咨询",
        "seller_attitude": "未知",
        "emotion_score": 1,
        "summary": "用户进线咨询，暂无明显冲突。",
        "need_additional_evidence": False
    }

    # 场景1：商品破损，用户愤怒
    if "破" in query_lower or "烂" in query_lower or "坏" in query_lower:
        mock_result["core_conflict"] = "商品破损"
        mock_result["buyer_intent"] = "仅退款"
        mock_result["emotion_score"] = 8 if "骗子" in query_lower or "投诉" in query_lower or "破" in query_lower else 5
        mock_result["summary"] = "买家反馈收到商品破损，要求仅退款。卖家未及时给出妥善解决方案。"
        # 如果聊天记录里没有提到图片/照片，则提示需要证据
        if "没有图片" in chat_lower or ("照片" not in chat_lower and "截图" not in chat_lower):
            mock_result["need_additional_evidence"] = True
            mock_result["seller_attitude"] = "商家要求提供破损照片"
        else:
            mock_result["seller_attitude"] = "商家已拒绝仅退款，要求退货退款"
            
    # 场景2：发货延迟，用户焦急
    elif "发货" in query_lower or "还没到" in query_lower or "物流" in query_lower:
        mock_result["core_conflict"] = "发货延迟/物流停滞"
        mock_result["buyer_intent"] = "催发货"
        mock_result["seller_attitude"] = "商家安抚等待物流更新"
        mock_result["summary"] = "买家因物流几天未更新进线催促发货，情绪较为焦急。"
        mock_result["emotion_score"] = 6
        
    # 场景3：假货/质量问题，极其愤怒
    elif "假货" in query_lower or "12315" in query_lower or "骗" in query_lower:
        mock_result["core_conflict"] = "疑似售假/严重质量问题"
        mock_result["buyer_intent"] = "投诉要求赔偿"
        mock_result["seller_attitude"] = "商家坚称是正品"
        mock_result["summary"] = "买家质疑商品为假货，情绪极度愤怒，扬言要投诉到12315要求赔偿。"
        mock_result["emotion_score"] = 10
        mock_result["need_additional_evidence"] = True
        
    return mock_result
