"""
main_workflow.py

自动化中英文字幕生成主控脚本。
支持两种输入方式：1）用户手动输入原文 2）读取txt文件内容。
串联所有智能体，自动生成中英文SRT文件。
"""

import os
from agents.chunker_agent import ChineseChunkerAgent
from agents.translator_agent import TranslationAgent
from agents.english_srt_agent import EnglishSrtAgent
from agents.chinese_srt_agent import ChineseSrtAgent

OUTPUT_DIR = "output"

# 工具函数：获取用户输入的原文（支持手动输入和文件读取）
def get_input_text() -> str:
    print("请选择输入方式：")
    print("1. 直接粘贴输入原文")
    print("2. 读取txt文件内容")
    choice = input("请输入 1 或 2：").strip()
    if choice == "1":
        print("请输入/粘贴完整中文原文，输入完后回车并再输入一行 END 结束：")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        return "\n".join(lines)
    elif choice == "2":
        file_path = input("请输入txt文件路径：").strip()
        if not os.path.isfile(file_path):
            print("文件不存在，请检查路径！")
            exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print("无效选择，程序退出。")
        exit(1)

def main():
    # 1. 获取用户输入的原文
    input_text = get_input_text()
    print("\n原文内容：\n" + input_text)

    # 2. 中文切分
    print("\n正在切分中文文本...")
    chunker = ChineseChunkerAgent()
    chinese_chunks = chunker.chunk_text(input_text)
    print(f"切分结果（共{len(chinese_chunks)}条）：")
    for idx, chunk in enumerate(chinese_chunks, 1):
        print(f"{idx}. {chunk}")

    # 3. 翻译
    print("\n正在翻译为英文...")
    translator = TranslationAgent()
    english_chunks = translator.translate(chinese_chunks)
    print(f"翻译结果（共{len(english_chunks)}条）：")
    for idx, chunk in enumerate(english_chunks, 1):
        print(f"{idx}. {chunk}")

    # 4. 英文SRT生成
    print("\n正在生成英文SRT...")
    en_srt_agent = EnglishSrtAgent()
    print("英文短句列表：", english_chunks)
    en_srt_content, timestamps = en_srt_agent.generate_srt(english_chunks)
    print("英文SRT内容：\n", en_srt_content)
    print("英文SRT时间戳列表：", timestamps)

    # 5. 中文SRT生成（严格复用英文时间戳）
    print("正在生成中文SRT...")
    zh_srt_agent = ChineseSrtAgent()
    zh_srt_content = zh_srt_agent.generate_srt(chinese_chunks, timestamps)
    print("中文SRT内容：\n", zh_srt_content)

    # 6. 输出/保存SRT文件
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    en_srt_path = os.path.join(OUTPUT_DIR, "output_en.srt")
    zh_srt_path = os.path.join(OUTPUT_DIR, "output_zh.srt")
    with open(en_srt_path, "w", encoding="utf-8") as f:
        f.write(en_srt_content)
    with open(zh_srt_path, "w", encoding="utf-8") as f:
        f.write(zh_srt_content)
    print(f"\n英文SRT已保存到: {en_srt_path}")
    print(f"中文SRT已保存到: {zh_srt_path}")

if __name__ == "__main__":
    main() 