import os
from openai import OpenAI

# ================= 配置区域 =================
# 请在环境变量中设置 OPENAI_API_KEY，或者直接在这里填入字符串
# 如果使用其他服务商（如 DeepSeek, Moonshot），请修改 BASE_URL 和 MODEL
API_KEY = "666" # 替换为你的api-key
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1") # 替换为你的API基础URL
MODEL_NAME = "deepseek-chat"  # 替换为你的模型名称

# 初始化 OpenAI 客户端
client_llm = None
if API_KEY and API_KEY != "your-api-key-here":
    client_llm = OpenAI(api_key=API_KEY, base_url=BASE_URL)
else:
    print("警告: 未检测到有效的 API Key。LLM 筛选功能将无法使用。")
    print("请设置 OPENAI_API_KEY 环境变量或在脚本中填入 Key。")
# ==========================================