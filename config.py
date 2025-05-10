"""
项目配置文件，集中管理API密钥、模型参数、字幕参数等。
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（如 API 密钥等敏感信息）
load_dotenv()

# =====================
# DeepSeek/OpenAI API 配置
# =====================
# API 密钥建议写在 .env 文件中，避免泄露
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# DeepSeek API 的 base_url，兼容 OpenAI 格式
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
# 默认模型名称
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")

# =====================
# 字幕生成相关参数
# =====================
# 英文朗读速率（每分钟单词数）
TARGET_WPM = 150
# 每条字幕最小显示时长（毫秒）
MIN_SUBTITLE_DURATION_MS = 1000
# 字幕间的停顿时长（毫秒）
SUBTITLE_PAUSE_MS = 200
# 首条字幕的初始偏移（毫秒）
INITIAL_OFFSET_MS = 500

# =====================
# Prompt 路径（可选）
# =====================
# 各智能体的提示词文件路径，便于集中管理和后续扩展
CHUNKER_PROMPT_PATH = "prompts/chunker_prompts.py"
TRANSLATOR_PROMPT_PATH = "prompts/translator_prompts.py" 