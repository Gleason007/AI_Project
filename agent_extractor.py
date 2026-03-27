import json
import time
import os
from prompt_manager import PromptManager
from llm_client import llm_client

current_dir = os.path.dirname(__file__)
prompt_mgr = PromptManager(os.path.join(current_dir, "..", "prompts"))

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
    # === 新增：真实大模型 API 链路 ===
    try:
        if llm_client.api_available:
            system_prompt = prompt_mgr.render_prompt(
                "agent_extractor", 
                "v2", 
                order_info=json.dumps(order_info, ensure_ascii=False),
                chat_history=chat_history,
                current_query=current_query
            )
            # 真实大模型调用，无内置 sleep
            response_text = llm_client.call(system_prompt=system_prompt, user_prompt="")
            
            if response_text:
                result = llm_client.parse_json_from_response(response_text)
                if result and "core_conflict" in result:
                    return result
            # 若无有效 JSON，走 Mock
    except Exception as e:
        pass # 发生异常，降级走 Mock

    # === 原有 Mock 链路 (Fallback) ===
    # 模拟大模型调用延迟 (思考时间)
    time.sleep(1.5)
    
    # 简单的基于关键词的"伪大模型" Mock 逻辑，用于演示不同场景
    query_lower = current_query.lower()
    chat_lower = chat_history.lower()
    text_lower = query_lower + " " + chat_lower
    
    # 默认返回结构
    mock_result = {
        "core_conflict": "未知问题",
        "buyer_intent": "咨询",
        "seller_attitude": "未知",
        "emotion_score": 1,
        "summary": "用户进线咨询，暂无明显冲突。",
        "need_additional_evidence": False
    }

    # 场景1：极端人身威胁 (高优先级)
    if "杀" in text_lower or "死" in text_lower or "命" in text_lower:
        mock_result["core_conflict"] = "极端情绪/人身威胁"
        mock_result["buyer_intent"] = "投诉/威胁"
        mock_result["emotion_score"] = 10
        mock_result["summary"] = "系统检测到用户言辞极端，存在人身攻击倾向，已自动标记为高危案例。"
        mock_result["need_additional_evidence"] = False

    # 场景2：假货/质量纠纷/严重客诉/态度投诉
    elif "假货" in text_lower or "12315" in text_lower or "投诉" in text_lower or "骗子" in text_lower or "态度" in text_lower:
        mock_result["core_conflict"] = "疑似售假/严重质量问题"
        mock_result["buyer_intent"] = "投诉要求赔偿"
        mock_result["emotion_score"] = 9
        mock_result["summary"] = "买家质疑商品质量或涉及诚信/态度争议，情绪极度愤怒，威胁投诉。"
        mock_result["need_additional_evidence"] = True
        mock_result["seller_attitude"] = "商家坚称无误或服务态度不好"

    # 场景3：错发货/换货诉求/漏发
    elif "错" in text_lower or "不对" in text_lower or "换" in text_lower or "颜色" in text_lower or "漏发" in text_lower:
        mock_result["core_conflict"] = "错发货"
        mock_result["buyer_intent"] = "换货"
        mock_result["emotion_score"] = 4
        mock_result["summary"] = "买方反馈颜色或型号发错，或存在漏发配件，要求处理。"
        mock_result["need_additional_evidence"] = False
        mock_result["seller_attitude"] = "商家承认发错"

    # 场景4：商品破损/面料损耗/轻微补偿 (白名单潜在用例)
    elif "破" in text_lower or "烂" in text_lower or "坏" in text_lower or "碎" in text_lower or "球" in text_lower or "损耗" in text_lower or "补" in text_lower:
        mock_result["core_conflict"] = "商品破损" if ("破" in text_lower or "碎" in text_lower or "烂" in text_lower or "坏" in text_lower or "补" in text_lower) else "正常面料损耗"
        mock_result["buyer_intent"] = "咨询" if "补偿" in text_lower else "仅退款"
        mock_result["emotion_score"] = 8 if "骗子" in text_lower else 5
        mock_result["summary"] = f"买家反馈收到商品出现{mock_result['core_conflict']}，寻求部分补偿或仅退款。"
        # 如果聊天记录里没有提到图片/照片，则提示需要证据
        if "照片" in text_lower or "截图" in text_lower or "图" in text_lower:
            mock_result["need_additional_evidence"] = False
            mock_result["seller_attitude"] = "商家拒绝处理"
        else:
            mock_result["need_additional_evidence"] = True
            mock_result["seller_attitude"] = "商家要求提供凭证"

    # 场景5：物流/发货延迟/快递
    elif "发货" in text_lower or "物流" in text_lower or "丢" in text_lower or "还没到" in text_lower or "快递" in text_lower:
        mock_result["core_conflict"] = "发货延迟/物流停滞"
        mock_result["buyer_intent"] = "仅退款" if ("退款" in text_lower and "只能退款" not in text_lower) else "催发货"
        mock_result["emotion_score"] = 6
        mock_result["summary"] = "买家因物流几天未更新进线咨询，情绪较为焦急。"
        mock_result["need_additional_evidence"] = False

    # 场景6：尺码问题 (注意避免命中常用的"下"字)
    elif "鞋码" in text_lower or "尺码" in text_lower or "穿不下" in text_lower or "偏小" in text_lower or "偏大" in text_lower or "太小" in text_lower:
        mock_result["core_conflict"] = "尺码差异/缩水嫌疑"
        mock_result["buyer_intent"] = "咨询"
        mock_result["emotion_score"] = 5
        mock_result["summary"] = "买家认为实物尺码与标准不符，涉及定责争议。"
        mock_result["need_additional_evidence"] = True
        
    return mock_result
