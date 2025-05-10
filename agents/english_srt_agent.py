"""
english_srt_agent.py

本模块实现英文SRT生成与计时智能体（EnglishSrtAgent），用于根据英文短句列表生成带有精确时间戳的SRT字幕内容。
"""

import sys
import os
# 将项目根目录（config.py 所在目录）加入到模块查找路径，便于直接运行和测试
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
from config import TARGET_WPM, MIN_SUBTITLE_DURATION_MS, SUBTITLE_PAUSE_MS, INITIAL_OFFSET_MS
from utils.srt_utils import estimate_duration, generate_srt_entries, format_srt

class EnglishSrtAgent:
    """
    英文SRT生成与计时智能体：根据英文短句生成SRT字幕及时间戳。
    """
    def __init__(self, wpm=TARGET_WPM, min_duration_ms=MIN_SUBTITLE_DURATION_MS, pause_ms=SUBTITLE_PAUSE_MS, initial_offset_ms=INITIAL_OFFSET_MS):
        self.wpm = wpm
        self.min_duration = min_duration_ms / 1000  # 转为秒
        self.pause = pause_ms / 1000  # 转为秒
        self.initial_offset = initial_offset_ms / 1000  # 转为秒

    def generate_srt(self, english_chunks: list) -> tuple:
        """
        根据英文短句列表生成SRT字幕内容和时间戳列表。
        :param english_chunks: 英文短句列表
        :return: (SRT内容字符串, 时间戳列表)
        """
        timestamps = []
        current = datetime.timedelta(seconds=self.initial_offset)
        for text in english_chunks:
            duration = estimate_duration(text, self.wpm, self.min_duration)
            start = current
            end = start + datetime.timedelta(seconds=duration)
            timestamps.append((start, end))
            # 下一个字幕的开始时间 = 当前结束时间 + 停顿
            current = end + datetime.timedelta(seconds=self.pause)
        # 生成SRT条目
        srt_entries = generate_srt_entries(english_chunks, timestamps)
        srt_content = format_srt(srt_entries)
        return srt_content, timestamps

# 示例用法
if __name__ == "__main__":
    agent = EnglishSrtAgent()
    english_chunks = [
        "Once upon a time,",
        "There is a beautiful village.",
        "The village is home to many kind-hearted people,",
        "They work hard every day,",
        "Life is happy and fulfilling."
    ]
    srt_content, timestamps = agent.generate_srt(english_chunks)
    print("英文SRT内容：\n")
    print(srt_content)
    print("时间戳列表：")
    for idx, (start, end) in enumerate(timestamps, 1):
        print(f"{idx}. {start} --> {end}")
