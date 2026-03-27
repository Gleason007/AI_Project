import json
import os
import sys

# 将 src 目录加入路径，方便导入模块
sys.path.append(os.path.dirname(__file__))
from prompt_manager import PromptManager

def convert_to_ft_format(input_json_path, output_jsonl_path):
    """
    将 Golden Set 或标记后的生产数据转换为 SFT (Supervised Fine-tuning) 所需的 JSONL 格式。
    支持 OpenAI ChatCompletion 和 Llama-3 常见格式。
    """
    print(f" 正在转换数据: {input_json_path} -> {output_jsonl_path}")
    
    current_dir = os.path.dirname(__file__)
    prompt_mgr = PromptManager(os.path.join(current_dir, "..", "prompts"))
    
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    with open(output_jsonl_path, "w", encoding="utf-8") as f_out:
        for item in data:
            # 保证训练的 System Prompt 和预处理推理阶段调用的完全一致
            system_prompt = prompt_mgr.render_prompt(
                "agent_extractor", 
                "v2", 
                order_info=json.dumps({"amount": item['input']['order_amount']}, ensure_ascii=False),
                chat_history=item['input']['chat_history'],
                current_query=item['input']['current_query']
            )
            
            # 为微调数据集自动构造粗略的 CoT 数据
            expected_json = json.dumps(item['expected'], ensure_ascii=False)
            assistant_content = f"<thought>\n根据买卖双方的交互，判断核心争议点和风控等级。\n</thought>\n```json\n{expected_json}\n```"
            
            # 格式化为 OpenAI/Llama-3 常见的 SFT 消息格式
            ft_item = {
                "messages": [
                    {"role": "user", "content": system_prompt},
                    {"role": "assistant", "content": assistant_content}
                ]
            }
            f_out.write(json.dumps(ft_item, ensure_ascii=False) + "\n")
            
    print(f" 转换完成！共生成 {len(data)} 条微调样本。")

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    convert_to_ft_format(
        os.path.join(current_dir, "../data/golden_set.json"),
        os.path.join(current_dir, "../data/ft_training_ready.jsonl")
    )
