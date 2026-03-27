import os
import json
import logging
import re
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLMClient:
    """
    统一的 LLM 调用客户端，解耦业务代码与具体大模型厂商的 API。
    目前对接阿里云通义千问 (DashScope) 接口。
    """
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.model = os.getenv("LLM_MODEL", "qwen-turbo")
        self.api_available = False
        
        if self.api_key and self.api_key.startswith("sk-") and self.api_key != "your_dashscope_api_key_here":
            try:
                import dashscope
                dashscope.api_key = self.api_key
                self.api_available = True
                logging.info(f" DashScope API 初始化成功. 使用模型: {self.model}")
            except ImportError:
                logging.warning(" 未安装 dashscope 库，LLMC lient 将会自动 fallback 回 Mock 模式。请运行: pip install dashscope")
        else:
            logging.warning(" 未配置有效的 DASHSCOPE_API_KEY，LLMClient 将会自动 fallback 回 Mock 模式。")

    def call(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        调用大模型生成文本。
        """
        if not self.api_available:
            logging.warning(" API 不可用，触发 fallback... (返回空字符串交由外部 Mock 处理)")
            return ""

        import dashscope
        from dashscope import Generation

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        try:
            logging.info(f" 调用模型 {self.model} ...")
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format='message',
                temperature=temperature
            )
            
            if response.status_code == 200:
                content = response.output.choices[0]['message']['content']
                return content
            else:
                logging.error(f" 模型调用失败: {response.code} - {response.message}")
                return ""
        except Exception as e:
            logging.error(f" 大模型接口发生异常: {e}")
            return ""

    def parse_json_from_response(self, text: str) -> dict:
        """
        从模型返回的 markdown 文本中提取 JSON 结构，避免 ```json ``` 以及思维链 <thought> 标记导致解析失败。
        """
        if not text:
            return {}
            
        try:
            # 寻找最后一段 ```json 和 ``` 之间的内容
            import re
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                # 兜底截取大括号
                match = re.search(r"(\{.*\})", text, re.DOTALL)
                if match:
                    json_str = match.group(1)
                else:
                    json_str = text
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logging.error(f" JSON 解析失败: {e}\n原文: {text}")
            return {}

# 提供一个全局实例，方便各个模块直接调用
llm_client = LLMClient()
