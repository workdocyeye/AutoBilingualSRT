"""
chinese_srt_agent.py

本模块实现中文SRT生成智能体（ChineseSrtAgent），用于根据原始中文短句和英文SRT时间戳同步生成标准中文SRT字幕内容。
"""

import sys
import os
# 将项目根目录（config.py 所在目录）加入到模块查找路径，便于直接运行和测试
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.srt_utils import generate_srt_entries, format_srt

class ChineseSrtAgent:
    """
    中文SRT生成智能体：根据原始中文短句和英文SRT时间戳同步生成标准中文SRT字幕内容。
    """
    def generate_srt(self, chinese_chunks: list, timestamps: list) -> str:
        """
        根据中文短句和英文SRT时间戳生成标准中文SRT内容。
        :param chinese_chunks: 中文短句列表
        :param timestamps: 时间戳列表，每个元素为 (start, end)，类型为 datetime.timedelta
        :return: 中文SRT文件内容字符串
        """
        srt_entries = generate_srt_entries(chinese_chunks, timestamps)
        srt_content = format_srt(srt_entries)
        return srt_content

# 示例用法
if __name__ == "__main__":
    agent = ChineseSrtAgent()
    chinese_chunks = [
        "在很久很久以前，",
        "有一个美丽的村庄。",
        "村庄里住着许多善良的人们，",
        "他们每天辛勤劳作，",
        "生活幸福美满。"
    ]
    # 示例时间戳（与英文SRT保持严格同步，实际应由英文SRT生成智能体输出）
    import datetime
    timestamps = [
        (datetime.timedelta(seconds=0.5), datetime.timedelta(seconds=2.5)),
        (datetime.timedelta(seconds=2.7), datetime.timedelta(seconds=4.0)),
        (datetime.timedelta(seconds=4.2), datetime.timedelta(seconds=6.0)),
        (datetime.timedelta(seconds=6.2), datetime.timedelta(seconds=7.5)),
        (datetime.timedelta(seconds=7.7), datetime.timedelta(seconds=9.0)),
    ]
    srt_content = agent.generate_srt(chinese_chunks, timestamps)
    print("中文SRT内容：\n")
    print(srt_content) 