"""
chunker_agent.py

本模块实现中文切分智能体（ChineseChunkerAgent），用于将长段中文文本智能切分为适合字幕的短句或小段落。
"""

import sys
import os
# 将项目根目录（config.py 所在目录）加入到模块查找路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from prompts.chunker_prompts import BASIC_CHUNK_PROMPT

class ChineseChunkerAgent:
    """
    中文切分智能体：负责将长段中文文本切分为适合字幕的短句。
    """
    def __init__(self):
        # 初始化 OpenAI 客户端，兼容 DeepSeek API
        self.client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        self.model = OPENAI_MODEL

    def chunk_text(self, input_text: str) -> list:
        """
        调用 LLM，将长段中文文本切分为短句列表。
        :param input_text: 原始长段中文文本
        :return: 切分后的短句列表
        """
        # 构造 prompt
        prompt = BASIC_CHUNK_PROMPT.format(input_text=input_text)
        # 调用 LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的字幕助手。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        # 解析 LLM 返回内容
        content = response.choices[0].message.content.strip()
        # 假设 LLM 返回的是 Python 列表格式，使用 eval 解析（实际部署时建议更安全的解析方式）
        try:
            result = eval(content)
            if isinstance(result, list):
                return [str(s).strip() for s in result]
            else:
                return [content]
        except Exception:
            # 如果解析失败，直接返回原始内容
            return [content]

# 示例用法
if __name__ == "__main__":
    agent = ChineseChunkerAgent()
    test_text = "在很久很久以前，有一个美丽的村庄。村庄里住着许多善良的人们，他们每天辛勤劳作，生活幸福美满。"
    chunks = agent.chunk_text(test_text)
    print("切分结果：")
    for idx, chunk in enumerate(chunks, 1):
        print(f"{idx}. {chunk}") 