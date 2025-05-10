"""
srt_utils.py

本模块封装 SRT 字幕相关的通用工具函数，包括时间戳格式化、SRT 条目生成等。
"""

import srt
import datetime
from typing import List

# 工具函数：根据英文文本和朗读速率计算持续时长（秒）
def estimate_duration(text: str, wpm: int = 150, min_duration: float = 1.0, lang: str = "en") -> float:
    """
    根据文本和朗读速率估算朗读时长（秒）。
    :param text: 字幕文本
    :param wpm: 英文为每分钟单词数，中文为每分钟汉字数
    :param min_duration: 最小持续时长（秒）
    :param lang: "en" 或 "zh"
    :return: 估算的持续时长（秒）
    """
    if lang == "zh":
        char_count = len([c for c in text if c.strip()])
        cpm = wpm  # 这里wpm参数实际为cpm
        duration = max(char_count / cpm * 60, min_duration)
    else:
        word_count = len(text.split())
        duration = max(word_count / wpm * 60, min_duration)
    return duration

# 工具函数：生成 SRT 条目列表
def generate_srt_entries(texts: List[str], timestamps: List[tuple]) -> List[srt.Subtitle]:
    """
    根据文本和时间戳生成 SRT 条目列表。
    :param texts: 字幕文本列表
    :param timestamps: 时间戳列表，每个元素为 (start, end)，类型为 datetime.timedelta
    :return: SRT 条目列表
    """
    entries = []
    for idx, (text, (start, end)) in enumerate(zip(texts, timestamps), 1):
        entries.append(srt.Subtitle(index=idx, start=start, end=end, content=text))
    return entries

# 工具函数：格式化 SRT 文件内容
def format_srt(subtitles: List[srt.Subtitle]) -> str:
    """
    将 SRT 条目列表格式化为标准 SRT 文件内容。
    :param subtitles: SRT 条目列表
    :return: SRT 文件内容字符串
    """
    return srt.compose(subtitles) 