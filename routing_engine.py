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
    # 规则：订单金额 < 50元 AND 用户历史信用 = 高 AND (核心冲突点 = 实物损坏/损耗/质量类)
    refund_whitelist_conflicts = ["商品破损", "正常面料损耗", "疑似售假/严重质量问题"]
    if order_amount < 50 and user_credit_score == "高" and conflict in refund_whitelist_conflicts:
        return {
            "route_action": "自动退款",
            "reason": "命中极速信誉退款白名单：小额破损/损耗无纠纷",
            "next_step": "system_refund"
        }
    
    # 2. 高危复杂争议，紧急人工干预流
    # 规则：用户情绪指数 >= 8 OR 包含极端意图 (针对威胁等场景)
    if emotion >= 9 or (emotion >= 8 and buyer_intent in ["投诉要求赔偿", "投诉/威胁", "索赔退一赔三"]):
        return {
            "route_action": "已转交高级专员加急接手",
            "reason": "命中高危客诉规则：情绪极高或包含严重/威胁意图",
            "next_step": "human_escalation"
        }
        
    # 3. 证据不足，触发大模型Agent 2引导举证流
    # 重要：仅针对"质量/破损/尺码"等需要实物照片才能定责的争议类型才要求举证
    # 对于"物流/发货/错发/漏发"等可通过系统数据核实的争议，直接进入常规排队
    evidence_required_conflicts = ["商品破损", "正常面料损耗", "尺码差异/缩水嫌疑", "疑似售假/严重质量问题"]
    if need_evidence and conflict in evidence_required_conflicts:
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
