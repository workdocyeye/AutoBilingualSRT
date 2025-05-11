"""
chinese_timestamp_agent.py

本模块实现中文SRT时间戳生成智能体（ChineseTimestampAgent），用于根据中文短句列表生成带有精确时间戳的SRT字幕内容。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
from config import TARGET_WPM, MIN_SUBTITLE_DURATION_MS, SUBTITLE_PAUSE_MS, INITIAL_OFFSET_MS
from utils.srt_utils import estimate_duration, generate_srt_entries, format_srt

class ChineseTimestampAgent:
    """
    中文SRT时间戳生成智能体：根据中文短句生成SRT字幕及时间戳。
    """
    def __init__(self, cpm=180, min_duration_ms=2000, pause_ms=200, initial_offset_ms=500, extra_sec=0.5):
        # cpm: 每分钟汉字数，表示朗读速度。数值越小，字幕显示时间越长。推荐范围：150~250。
        self.cpm = cpm  # 每分钟汉字数，调低以延长字幕时长，用户可调节
        # min_duration: 每条字幕最小显示时长（毫秒），防止短句闪烁。数值越大，短字幕显示时间越长。推荐范围：1500~2500。
        self.min_duration = min_duration_ms / 1000  # 转为秒，用户可调节
        # pause: 字幕间的停顿时长（毫秒），控制两条字幕之间的间隔。推荐范围：200~300。
        self.pause = pause_ms / 1000  # 转为秒，用户可调节
        # initial_offset: 首条字幕的初始偏移（毫秒），用于视频开头预留缓冲。推荐范围：300~1000。
        self.initial_offset = initial_offset_ms / 1000  # 转为秒，用户可调节
        # extra_sec: 每条字幕额外增加的缓冲秒数，进一步延长字幕显示时间，便于后期剪辑。推荐范围：0.5~1.0。
        self.extra_sec = extra_sec  # 每条字幕额外增加的缓冲秒数，用户可调节

    def generate_srt(self, chinese_chunks: list) -> tuple:
        """
        根据中文短句列表生成SRT字幕内容和时间戳列表。
        :param chinese_chunks: 中文短句列表
        :return: (SRT内容字符串, 时间戳列表)
        """
        timestamps = []
        current = datetime.timedelta(seconds=self.initial_offset)
        for text in chinese_chunks:
            duration = estimate_duration(
                text, wpm=self.cpm, min_duration=self.min_duration, lang="zh"
            ) + self.extra_sec  # 增加缓冲
            start = current
            end = start + datetime.timedelta(seconds=duration)
            timestamps.append((start, end))
            current = end + datetime.timedelta(seconds=self.pause)
        srt_entries = generate_srt_entries(chinese_chunks, timestamps)
        srt_content = format_srt(srt_entries)
        return srt_content, timestamps

# 示例用法
if __name__ == "__main__":
    agent = ChineseTimestampAgent()
    chinese_chunks = [
        "在很久很久以前，",
        "有一个美丽的村庄。",
        "村庄里住着许多善良的人们，",
        "他们每天辛勤劳作，",
        "生活幸福美满。"
    ]
    srt_content, timestamps = agent.generate_srt(chinese_chunks)
    print("中文SRT内容：\n")
    print(srt_content)
    print("时间戳列表：")
    for idx, (start, end) in enumerate(timestamps, 1):
        print(f"{idx}. {start} --> {end}") 