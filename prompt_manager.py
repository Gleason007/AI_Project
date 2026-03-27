import os

class PromptManager:
    """
    【AI 工程化模块】: Prompt 管理器
    用于统一管理项目中各个 Agent 的提示词版本，通过 jinja2 或 Python 字符串模板实现动态渲染。
    这避免了提示词与核心业务代码强耦合（硬编码），是企业级 AI 产品的基本规范。
    """
    
    def __init__(self, prompts_dir: str):
        self.prompts_dir = prompts_dir
        self.cache = {}
        
    def load_prompt(self, agent_name: str, version: str = "v1") -> str:
        """从文件系统加载指定版本和角色的 Prompt Template"""
        filename = f"{agent_name}_{version}.md"
        filepath = os.path.join(self.prompts_dir, filename)
        
        if filepath in self.cache:
            return self.cache[filepath]
            
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"未找到指定的提示词模板: {filepath}")
            
        with open(filepath, "r", encoding="utf-8") as f:
            template = f.read()
            self.cache[filepath] = template
            return template
            
    def render_prompt(self, agent_name: str, version: str, **kwargs) -> str:
        """
        动态渲染 Prompt
        :param kwargs: 如 order_info, chat_history, current_query 等需要在 prompt 中替换的变量
        """
        template = self.load_prompt(agent_name, version)
        
        # 实际项目中可以使用 jinja2 获得更强大的循环和条件控制能力
        # 这里为了避免模板中原生的 JSON 大括号冲突，使用精简的字符串替换
        rendered = template
        for key, value in kwargs.items():
            rendered = rendered.replace(f"{{{key}}}", str(value))
            
        return rendered

# 示例调用
if __name__ == "__main__":
    manager = PromptManager(os.path.join(os.path.dirname(__file__), "..", "prompts"))
    print("PromptManager 已加载。可以统一管理提示词版本。")
