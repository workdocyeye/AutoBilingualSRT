# 自动化中英文字幕生成工具

## 项目简介

本项目是一个基于 Python 和大语言模型（如 DeepSeek/OpenAI API）的自动化中英文字幕生成工具。它能够将用户输入的中文文本智能切分、翻译为英文，并自动生成严格同步的中英双语 SRT 字幕文件。界面美观，参数可调，支持 API Key 记忆，适合视频创作者、教育工作者、字幕组等场景。

---

## 功能特性

- **智能切分**：自动将长段中文文本切分为适合字幕显示的短句。
- **高质量翻译**：调用 LLM 实现上下文一致、自然流畅的中英互译。
- **精准时间戳**：根据朗读速度等参数自动计算每条字幕的显示时长和时间戳。
- **中英同步**：英文和中文字幕严格时间对齐，适合双语字幕需求。
- **参数自定义**：支持自定义朗读速度、最小显示时长、字幕间隔等关键参数。
- **美观易用的 GUI**：商业级界面，参数说明清晰，支持 API Key 记忆。
- **安全隐私**：API Key 本地保存，输出文件自动忽略上传，适合团队协作。

---

## 安装与环境配置

1. **克隆项目**
   ```bash
   git clone git@github.com:workdocyeye/AutoBilingualSRT.git
   cd AutoBilingualSRT
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **准备 API Key**
   - 启动程序后，首次在界面输入你的 LLM API Key（如 DeepSeek/OpenAI），系统会自动记住，下次无需重复输入。

---

## 使用方法

### 图形界面启动

```bash
python main_workflow.py
```

- 按界面提示输入/选择原文、调整参数、输入 API Key，点击"开始生成"即可自动生成中英文 SRT 文件，保存在 `output/` 目录下。

### 命令行模式

如 GUI 启动失败，会自动切换为命令行模式，按提示操作即可。

---

## 主要参数说明

| 参数名                | 说明                                   | 推荐范围         |
|----------------------|----------------------------------------|------------------|
| wpm / cpm            | 每分钟单词数/汉字数，影响字幕显示速度   | 英文 120~180，中文 150~250 |
| min_duration_ms      | 每条字幕最小显示时长（毫秒）            | 800~2500         |
| pause_ms             | 字幕间的停顿时长（毫秒）                | 200~300          |
| initial_offset_ms    | 首条字幕的初始偏移（毫秒）              | 300~1000         |
| extra_sec            | 每条字幕额外增加的缓冲秒数              | 0~1.0            |

所有参数均可在界面中灵活调整，旁边有详细说明。

---

## 目录结构

```
createsrt/
├── agents/                # 各类智能体（切分、翻译、SRT生成等）
├── prompts/               # LLM提示词
├── utils/                 # 工具函数
├── output/                # 输出的SRT文件（自动忽略上传）
├── main_workflow.py       # 主控脚本（含GUI）
├── config.py              # 配置参数
├── requirements.txt       # 依赖列表
├── .gitignore             # 忽略配置
├── api_key.txt            # API Key（自动忽略上传）
└── 字幕工作流开发文档.md   # 详细开发文档
```

---

## 贡献与反馈

欢迎提交 Issue、PR 或建议！
如需定制开发、集成 TTS、视频嵌字幕等高级功能，请联系作者。

---

## License

本项目采用 MIT License，详见 LICENSE 文件。

---

## 致谢

- [DeepSeek](https://deepseek.com/) / [OpenAI](https://openai.com/)
- [srt Python 库](https://github.com/cdown/srt)

---

如需更详细的开发说明，请参阅项目内的《字幕工作流开发文档.md》。 