# 介绍

Muyan-TTS 是一个基于深度学习的文本到语音合成系统。它利用了最新的语音合成技术，能够生成高质量的语音输出。

## 主要功能

- 支持多种语言的文本到语音合成
- 提供API接口，方便集成到其他应用中
- 支持自定义语音模型的训练和微调

## 使用场景

- 播客制作
- 语音助手
- 语音导航系统

# 安装

## 前提条件

- Python 3.7 或更高版本
- pip

## 安装步骤

1. 克隆项目仓库：

```bash
git clone https://github.com/ovenzeze/Muyan-TTS.git
cd Muyan-TTS
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

# 使用

## 基本使用说明

1. 运行 `api.py` 启动API服务：

```bash
python api.py
```

2. 运行 `tts.py` 进行语音合成：

```bash
python tts.py
```

## 高级使用说明

- 可以通过修改 `api.py` 和 `tts.py` 中的参数来调整语音合成的效果。

## 示例

- 示例代码可以在 `examples` 目录中找到。

# API文档

## 可用API概述

- `/get_tts`：生成语音
- `/get_tts_with_timestamps`：生成带时间戳的语音

## 详细API使用说明

### `/get_tts`

- 请求方法：POST
- 请求参数：
  - `ref_wav_path`：参考音频文件路径
  - `prompt_text`：提示文本
  - `text`：要合成的文本
  - `temperature`：温度参数（可选）
  - `repetition_penalty`：重复惩罚参数（可选）
  - `speed`：语速（可选）
  - `scaling_factor`：缩放因子（可选）

### `/get_tts_with_timestamps`

- 请求方法：POST
- 请求参数：
  - `ref_wav_path`：参考音频文件路径
  - `prompt_text`：提示文本
  - `text`：要合成的文本
  - `temperature`：温度参数（可选）
  - `repetition_penalty`：重复惩罚参数（可选）
  - `speed`：语速（可选）
  - `scaling_factor`：缩放因子（可选）

# 训练

## 数据准备

- 训练数据的处理可以参考 `prepare_sft_dataset.py`。

## 训练过程

- 运行 `train.sh` 脚本进行训练。

## 微调

- 可以通过修改 `train.sh` 中的参数来进行微调。

# 故障排除

## 常见问题及解决方案

- 如果遇到API无法启动的问题，请检查依赖是否安装完整。
- 如果语音合成效果不理想，可以尝试调整 `api.py` 和 `tts.py` 中的参数。

# 致谢

- 感谢所有为本项目做出贡献的开发者。

# 参考文献

- 相关参考文献和引用。
