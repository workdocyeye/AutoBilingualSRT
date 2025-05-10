"""
translator_agent.py

本模块实现翻译智能体（TranslationAgent），用于将中文短句列表翻译为英文短句列表。
"""

import sys
import os
# 将项目根目录（config.py 所在目录）加入到模块查找路径，便于直接运行和测试
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from prompts.translator_prompts import BASIC_TRANSLATE_PROMPT

class TranslationAgent:
    """
    翻译智能体：负责将中文短句列表翻译为英文短句列表。
    """
    def __init__(self):
        # 初始化 OpenAI 客户端，兼容 DeepSeek API
        self.client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        self.model = OPENAI_MODEL

    def translate(self, chinese_chunks: list) -> list:
        """
        调用 LLM，将中文短句列表翻译为英文短句列表。
        :param chinese_chunks: 中文短句列表
        :return: 英文短句列表
        """
        english_chunks = []
        for idx, chunk in enumerate(chinese_chunks):
            # 构造 prompt
            prompt = BASIC_TRANSLATE_PROMPT.format(input_text=chunk)
            # 调用 LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的中英字幕翻译助手。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            # 解析 LLM 返回内容
            content = response.choices[0].message.content.strip()
            english_chunks.append(content)
        return english_chunks

# 示例用法
if __name__ == "__main__":
    agent = TranslationAgent()
    # 示例中文短句列表（可替换为任意测试内容）
    chinese_chunks = [
        "在很久很久以前，",
        "有一个美丽的村庄。",
        "村庄里住着许多善良的人们，",
        "他们每天辛勤劳作，",
        "生活幸福美满。"
    ]
    english_chunks = agent.translate(chinese_chunks)
    print("翻译结果：")
    for idx, chunk in enumerate(english_chunks, 1):
        print(f"{idx}. {chunk}") 