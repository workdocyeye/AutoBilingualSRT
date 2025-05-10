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
import sys

# GUI 配置对话框
import tkinter as tk
from tkinter import filedialog, messagebox

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

# GUI 配置对话框
class SubtitleConfigDialog:
    def __init__(self, root):
        self.root = root
        self.root.title("字幕生成设置")
        self.input_text = ""
        self.input_mode = tk.StringVar(value="manual")
        self.time_basis = tk.StringVar(value="en")
        self.file_path = tk.StringVar(value="")

        # 输入方式选择
        tk.Label(root, text="请选择输入方式：").pack(anchor="w")
        tk.Radiobutton(root, text="手动输入", variable=self.input_mode, value="manual", command=self.show_manual_input).pack(anchor="w")
        tk.Radiobutton(root, text="选择txt文件", variable=self.input_mode, value="file", command=self.show_file_input).pack(anchor="w")

        # 手动输入文本框
        self.text_input = tk.Text(root, height=10, width=60)
        self.text_input.pack()
        self.text_input.insert("1.0", "请输入/粘贴完整中文原文...")

        # 文件选择按钮
        self.file_frame = tk.Frame(root)
        self.file_entry = tk.Entry(self.file_frame, textvariable=self.file_path, width=50)
        self.file_entry.pack(side="left")
        self.file_btn = tk.Button(self.file_frame, text="选择文件", command=self.select_file)
        self.file_btn.pack(side="left")
        self.file_frame.pack_forget()  # 默认隐藏

        # 时间分配依据
        tk.Label(root, text="请选择SRT时间戳分配依据：").pack(anchor="w")
        tk.Radiobutton(root, text="以英文为主", variable=self.time_basis, value="en").pack(anchor="w")
        tk.Radiobutton(root, text="以中文为主", variable=self.time_basis, value="zh").pack(anchor="w")

        # 确认按钮
        tk.Button(root, text="开始生成", command=self.on_confirm).pack(pady=10)

    def show_manual_input(self):
        self.text_input.pack()
        self.file_frame.pack_forget()

    def show_file_input(self):
        self.text_input.pack_forget()
        self.file_frame.pack()

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.file_path.set(path)

    def on_confirm(self):
        if self.input_mode.get() == "manual":
            self.input_text = self.text_input.get("1.0", "end").strip()
            if not self.input_text:
                messagebox.showerror("错误", "请输入原文内容！")
                return
        else:
            path = self.file_path.get()
            if not path:
                messagebox.showerror("错误", "请选择txt文件！")
                return
            with open(path, "r", encoding="utf-8") as f:
                self.input_text = f.read()
        self.root.quit()  # 关闭窗口

# 主流程函数，支持传入 input_text 和 time_basis

def main(input_text=None, time_basis=None):
    if input_text is None or time_basis is None:
        # 兼容命令行老逻辑
        input_text = get_input_text()
        print("\n原文内容：\n" + input_text)
        time_basis = "en"

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

    # 4. SRT生成
    if time_basis == "zh":
        print("\n以中文为依据生成时间戳...")
        from agents.chinese_timestamp_agent import ChineseTimestampAgent
        zh_timestamp_agent = ChineseTimestampAgent()
        zh_srt_content, timestamps = zh_timestamp_agent.generate_srt(chinese_chunks)
        zh_srt_agent = ChineseSrtAgent()
        zh_srt_content = zh_srt_agent.generate_srt(chinese_chunks, timestamps)
        en_srt_agent = ChineseSrtAgent()
        en_srt_content = en_srt_agent.generate_srt(english_chunks, timestamps)
    else:
        print("\n以英文为依据生成时间戳...")
        en_srt_agent = EnglishSrtAgent()
        en_srt_content, timestamps = en_srt_agent.generate_srt(english_chunks)
        zh_srt_agent = ChineseSrtAgent()
        zh_srt_content = zh_srt_agent.generate_srt(chinese_chunks, timestamps)

    # 5. 输出/保存SRT文件
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
    # 判断是否为交互式终端，优先弹出GUI
    try:
        import tkinter as tk
        root = tk.Tk()
        dialog = SubtitleConfigDialog(root)
        root.mainloop()
        input_text = dialog.input_text
        time_basis = dialog.time_basis.get()
        main(input_text, time_basis)
    except Exception as e:
        print("GUI 启动失败，回退到命令行模式：", e)
        main() 