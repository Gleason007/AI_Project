def route_ticket(extracted_info: dict, order_info: dict, user_credit_score: str) -> dict:
    """
    风控路由与决策系统 (Routing System)
    
    依据 PRD_电商售后大模型智能路由引擎.md 中的外挂规则系统（非大模型）进行逻辑判断。
    根据 Agent 1 提取的参数和订单系统参数，决定客诉工单的流转方向。
    
    :param extracted_info: Agent 1 提取并结构化后的争议信息 JSON (dict)
    :param order_info: 订单基础数据流 (金额等)
    :param user_credit_score: 用户历史信用画像 ("高", "中", "低")
    :return: 包含被触发红线/绿线路由的动作字典
    """
    order_amount = order_info.get("amount", 0)
    conflict = extracted_info.get("core_conflict", "")
    emotion = extracted_info.get("emotion_score", 1)
    buyer_intent = extracted_info.get("buyer_intent", "")
    need_evidence = extracted_info.get("need_additional_evidence", False)
    
    # 1. 低危无争议，极速退款流 (系统放行退款)
    # 规则：订单金额 < 50元 AND 用户历史信用 = 高 AND 核心冲突点 = 商品破损
    if order_amount < 50 and user_credit_score == "高" and conflict == "商品破损" and not need_evidence:
        return {
            "route_action": "自动退款",
            "reason": "命中极速信誉退款白名单：小额破损无纠纷",
            "next_step": "system_refund"
        }
    
    # 2. 高危复杂争议，紧急人工干预流
    # 规则：用户情绪指数 >= 8 AND 买方诉求 = 投诉赔偿
    if emotion >= 8 and buyer_intent == "投诉要求赔偿":
        return {
            "route_action": "已转交高级专员加急接手",
            "reason": "命中高危客诉规则：情绪满分且要求升级投诉",
            "next_step": "human_escalation"
        }
        
    # 3. 证据不足，触发大模型Agent 2引导举证流
    if need_evidence:
        return {
            "route_action": "要求用户上传凭证图片/视频",
            "reason": "核心冲突需依据，尚未达到系统默认退款门槛",
            "next_step": "guide_evidence"
        }
        
    # 4. 默认常规安抚与审核流
    return {
        "route_action": "人工初审排队中，预计24h内回复",
        "reason": "常规争议进线，需人工排查",
        "next_step": "normal_queue"
    }
