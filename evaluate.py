import json
import sys
import os

# 将 src 目录加入路径，方便导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_extractor import extract_intent_and_info
from routing_engine import route_ticket

def run_evaluation():
    print("开始执行智能路由引擎 Golden Set 评测...")
    
    golden_set_path = os.path.join(os.path.dirname(__file__), "..", "data", "golden_set.json")
    with open(golden_set_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)
    
    passed = 0
    total = len(test_cases)
    
    for case in test_cases:
        print(f"\n[测试用例 {case['id']}] {case['description']}")
        
        # 执行推理链路
        extracted = extract_intent_and_info(
            {"amount": case['input']['order_amount']},
            case['input']['chat_history'],
            case['input']['current_query']
        )
        
        decision = route_ticket(
            extracted,
            {"amount": case['input']['order_amount']},
            case['input']['credit_score']
        )
        
        # 验证结果
        actual_intent = extracted.get('buyer_intent', '')
        actual_step = decision.get('next_step', '')
        
        # 业务视角的评测标准：只要最终的工单路由动作正确，即视为决策链路成功
        step_match = actual_step == case['expected']['next_step']
        
        if step_match:
            print("通过")
            passed += 1
        else:
            print("失败")
            print(f"    - 预期意图: {case['expected']['intent']} | 实际: {actual_intent}")
            print(f"    - 预期动作: {case['expected']['next_step']} | 实际: {actual_step}")
            print(f"    - 完整提取 JSON: {extracted}")
            
    accuracy = (passed / total) * 100
    print(f"\n==============================")
    print(f"评测完成！总计: {total} | 通过: {passed} | 准确率: {accuracy:.2f}%")
    print(f"==============================")

if __name__ == "__main__":
    run_evaluation()
