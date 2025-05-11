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
from tkinter import ttk, filedialog, messagebox

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
        # ========== API Key 相关 ===========
        self.api_key_var = tk.StringVar()
        self.api_key_path = os.path.join(os.path.dirname(__file__), "api_key.txt")
        self.load_api_key()
        # API Key输入区
        api_frame = tk.LabelFrame(root, text="API Key 设置", font=("微软雅黑", 11, "bold"), padx=10, pady=8)
        api_frame.pack(fill="x", padx=12, pady=6)
        tk.Label(api_frame, text="请输入API Key：", font=("微软雅黑", 10)).pack(side="left")
        api_entry = tk.Entry(api_frame, textvariable=self.api_key_var, width=36, font=("微软雅黑", 10), show="*")
        api_entry.pack(side="left", padx=6)
        tk.Label(api_frame, text="（仅首次输入，自动记住，下次自动填充）", fg="#888888", font=("微软雅黑", 9)).pack(side="left")
        # 参数变量
        self.param_vars = {
            "zh": {
                "cpm": tk.IntVar(value=180),
                "min_duration_ms": tk.IntVar(value=2000),
                "pause_ms": tk.IntVar(value=200),
                "initial_offset_ms": tk.IntVar(value=500),
                "extra_sec": tk.DoubleVar(value=0.5),
            },
            "en": {
                "wpm": tk.IntVar(value=150),
                "min_duration_ms": tk.IntVar(value=1000),
                "pause_ms": tk.IntVar(value=200),
                "initial_offset_ms": tk.IntVar(value=500),
                "extra_sec": tk.DoubleVar(value=0.0),
            }
        }
        # 参数说明
        self.param_help = {
            "wpm": "每分钟单词数，影响英文字幕显示速度（120~180）",
            "min_duration_ms": "每条字幕最小显示时长（毫秒），防止短句闪烁（800~1500）",
            "pause_ms": "字幕间的停顿时长（毫秒），控制两条字幕之间的间隔（200~300）",
            "initial_offset_ms": "首条字幕的初始偏移（毫秒），用于视频开头预留缓冲（300~1000）",
            "extra_sec": "每条字幕额外增加的缓冲秒数，便于后期剪辑（0~1.0）",
            "cpm": "每分钟汉字数，影响中文字幕显示速度（150~250）"
        }
        # ===== 输入方式分区 =====
        input_frame = tk.LabelFrame(root, text="输入方式", font=("微软雅黑", 11, "bold"), padx=10, pady=8)
        input_frame.pack(fill="x", padx=12, pady=6)
        tk.Radiobutton(input_frame, text="手动输入", variable=self.input_mode, value="manual", font=("微软雅黑", 11), padx=12, pady=6, command=self.show_manual_input).pack(anchor="w")
        tk.Radiobutton(input_frame, text="选择txt文件", variable=self.input_mode, value="file", font=("微软雅黑", 11), padx=12, pady=6, command=self.show_file_input).pack(anchor="w")
        # 手动输入文本框
        self.text_input = tk.Text(input_frame, height=8, width=60, font=("微软雅黑", 10))
        self.text_input.pack(pady=4)
        self.text_input.insert("1.0", "请输入/粘贴完整中文原文...")
        # 文件选择按钮
        self.file_frame = tk.Frame(input_frame)
        self.file_entry = tk.Entry(self.file_frame, textvariable=self.file_path, width=50, font=("微软雅黑", 10))
        self.file_entry.pack(side="left", padx=2)
        self.file_btn = tk.Button(self.file_frame, text="选择文件", font=("微软雅黑", 10, "bold"), command=self.select_file)
        self.file_btn.pack(side="left", padx=4)
        self.file_frame.pack_forget()
        # ===== 时间依据分区 =====
        time_frame = tk.LabelFrame(root, text="SRT时间戳分配依据", font=("微软雅黑", 11, "bold"), padx=10, pady=8)
        time_frame.pack(fill="x", padx=12, pady=6)
        tk.Radiobutton(time_frame, text="以英文为主", variable=self.time_basis, value="en", font=("微软雅黑", 11), padx=12, pady=6, command=self.show_en_params).pack(anchor="w")
        tk.Radiobutton(time_frame, text="以中文为主", variable=self.time_basis, value="zh", font=("微软雅黑", 11), padx=12, pady=6, command=self.show_zh_params).pack(anchor="w")
        # ===== 参数设置分区 =====
        self.zh_param_frame = tk.LabelFrame(root, text="中文参数设置", font=("微软雅黑", 11, "bold"), padx=10, pady=8)
        self.en_param_frame = tk.LabelFrame(root, text="英文参数设置", font=("微软雅黑", 11, "bold"), padx=10, pady=8)
        for key, var in self.param_vars["zh"].items():
            row = tk.Frame(self.zh_param_frame)
            row.pack(fill="x", padx=2, pady=2)
            tk.Label(row, text=key+"：", width=18, anchor="w", font=("微软雅黑", 10)).pack(side="left")
            tk.Entry(row, textvariable=var, width=10, font=("微软雅黑", 10)).pack(side="left")
            tk.Label(row, text=self.param_help.get(key, ""), fg="#888888", font=("微软雅黑", 9)).pack(side="left", padx=8)
        for key, var in self.param_vars["en"].items():
            row = tk.Frame(self.en_param_frame)
            row.pack(fill="x", padx=2, pady=2)
            tk.Label(row, text=key+"：", width=18, anchor="w", font=("微软雅黑", 10)).pack(side="left")
            tk.Entry(row, textvariable=var, width=10, font=("微软雅黑", 10)).pack(side="left")
            tk.Label(row, text=self.param_help.get(key, ""), fg="#888888", font=("微软雅黑", 9)).pack(side="left", padx=8)
        self.en_param_frame.pack(fill="x", padx=12, pady=6)
        # ===== 开始生成按钮 =====
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="开始生成", font=("微软雅黑", 12, "bold"), width=16, height=2, bg="#4F81BD", fg="white", command=self.on_confirm).pack()
        # ====== 窗口关闭事件绑定 ======
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    def show_manual_input(self):
        self.text_input.pack(pady=4)
        self.file_frame.pack_forget()
    def show_file_input(self):
        self.text_input.pack_forget()
        self.file_frame.pack(pady=4)
    def show_zh_params(self):
        self.en_param_frame.pack_forget()
        self.zh_param_frame.pack(fill="x", padx=12, pady=6)
    def show_en_params(self):
        self.zh_param_frame.pack_forget()
        self.en_param_frame.pack(fill="x", padx=12, pady=6)
    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.file_path.set(path)
    def load_api_key(self):
        """从本地文件加载API Key"""
        try:
            if os.path.exists(self.api_key_path):
                with open(self.api_key_path, "r", encoding="utf-8") as f:
                    self.api_key_var.set(f.read().strip())
        except Exception:
            pass
    def save_api_key(self):
        """保存API Key到本地文件"""
        try:
            with open(self.api_key_path, "w", encoding="utf-8") as f:
                f.write(self.api_key_var.get().strip())
        except Exception:
            pass
    def on_close(self):
        """窗口关闭时强制终止程序"""
        os._exit(0)
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
        self.params = {
            "zh": {k: v.get() for k, v in self.param_vars["zh"].items()},
            "en": {k: v.get() for k, v in self.param_vars["en"].items()},
        }
        self.save_api_key()  # 保存API Key
        self.root.quit()

# 主流程函数，支持传入 input_text 和 time_basis

def main(input_text=None, time_basis=None, agent_params=None):
    if input_text is None or time_basis is None:
        # 兼容命令行老逻辑
        input_text = get_input_text()
        print("\n原文内容：\n" + input_text)
        time_basis = "en"
        agent_params = {  # 默认参数
            "zh": {"cpm": 180, "min_duration_ms": 2000, "pause_ms": 200, "initial_offset_ms": 500, "extra_sec": 0.5},
            "en": {"wpm": 150, "min_duration_ms": 1000, "pause_ms": 200, "initial_offset_ms": 500, "extra_sec": 0.0},
        }

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
        zh_timestamp_agent = ChineseTimestampAgent(**agent_params["zh"])
        zh_srt_content, timestamps = zh_timestamp_agent.generate_srt(chinese_chunks)
        zh_srt_agent = ChineseSrtAgent()
        zh_srt_content = zh_srt_agent.generate_srt(chinese_chunks, timestamps)
        en_srt_agent = ChineseSrtAgent()
        en_srt_content = en_srt_agent.generate_srt(english_chunks, timestamps)
    else:
        print("\n以英文为依据生成时间戳...")
        en_srt_agent = EnglishSrtAgent(**agent_params["en"])
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
        agent_params = getattr(dialog, 'params', None)
        main(input_text, time_basis, agent_params)
    except Exception as e:
        print("GUI 启动失败，回退到命令行模式：", e)
        main() 