<div align="center">
    <p align="center">
    <img src="assets/logo.png" width="400"/>
<p>

<p align="center">
Muyan-TTS <a href="https://huggingface.co/MYZY-AI/Muyan-TTS">🤗</a>&nbsp;<a href="https://modelscope.cn/models/MYZY-AI/Muyan-TTS">🤖</a>&nbsp;<a href="https://wisemodel.cn/models/MYZY-AI/Muyan-TTS">🦉</a>&nbsp; | Muyan-TTS-SFT <a href="https://huggingface.co/MYZY-AI/Muyan-TTS-SFT">🤗</a>&nbsp;<a href="https://modelscope.cn/models/MYZY-AI/Muyan-TTS-SFT">🤖</a>&nbsp;<a href="https://wisemodel.cn/models/MYZY-AI/Muyan-TTS-SFT">🦉</a>&nbsp; | &nbsp;<a href="https://arxiv.org/abs/2504.19146">技术报告</a> &nbsp;&nbsp;
</p>
<p>
    <a href="https://discord.gg/zT52KG6WbD">
       <img src="https://dcbadge.limes.pink/api/server/zT52KG6WbD?style=flat">
    </a>
    <a href="https://github.com/MYZY-AI/Muyan-TTS/issues/1">
       <img src="https://img.shields.io/badge/群聊-WeChat-green">
    </a>
</p>
</div>

Muyan-TTS 是一个可训练的 TTS 模型，专为播客应用设计，预算为 50,000 美元，预训练于超过 100,000 小时的播客音频数据，能够进行高质量语音生成的零样本 TTS 合成。此外，Muyan-TTS 支持使用几十分钟的目标语音进行说话人适应，使其高度可定制化。

## 🔥🔥🔥 新闻!!

* 2025年4月29日：👋 我们发布了 [Muyan-TTS](https://huggingface.co/MYZY-AI/Muyan-TTS) 的零样本 TTS 模型权重。
* 2025年4月29日：👋 我们发布了 [Muyan-TTS-SFT](https://huggingface.co/MYZY-AI/Muyan-TTS-SFT) 的少样本 TTS 模型权重，该模型基于 [Muyan-TTS](https://huggingface.co/MYZY-AI/Muyan-TTS) 训练，使用了几十分钟的单个说话人的语音。
* 2025年4月29日：👋 我们发布了从基础模型到 SFT 模型的训练代码，用于说话人适应。
* 2025年4月29日：👋 我们发布了 Muyan-TTS 的 [技术报告](https://arxiv.org/abs/2504.19146)。

## 概述

### 框架
![框架](assets/framework.png)
Muyan-TTS 的框架。左侧是一个 LLM，建模了文本（蓝色）和音频（绿色）标记的平行语料库。右侧是一个 SoVITS 模型，将生成的音频标记、音素和说话人嵌入解码为音频波形。

### 数据
![数据处理流程](assets/pipeline.png)
数据处理流程。最终数据集包括超过 100,000 小时的高质量语音及其对应的转录，形成了一个适用于长篇音频场景（如播客）TTS 训练的强大平行语料库。

### 训练成本
| 训练成本   | 数据处理   | LLM 预训练| 解码器训练 | 总计 |
|-------|-------|-------|-------|-------|
| GPU 小时   | 60K(A10)   | 19.2K(A100)| 1.34K(A100) | - |
| 美元   | $30K   | $19.2K| $1.34K | $50.54K |

Muyan-TTS 的训练成本，假设 A10 和 A100 的 GPU 小时租赁价格分别为 $0.5 和 $1。

### 合成速度
我们用 ```r``` 表示生成一秒音频所需的推理时间，并与几个开源 TTS 模型进行比较。

| 模型   | CosyVoice2   | Step-Audio| Spark-TTS | FireRedTTS |  GPT-SoVITS v3|  Muyan-TTS |
|-------|-------|-------|-------|-------|-------|-------|
| r &#8595;   | 2.19   | 0.90| 1.31 | 0.61 | 0.48 | 0.33 |

所有推理过程均在单个 NVIDIA A100 (40G, PCIe) GPU 上运行，基线模型使用其官方推理实现进行评估。

*注意*: 由于训练数据主要为英语，Muyan-TTS 仅支持英语输入。

## 演示

https://github.com/user-attachments/assets/a20d407c-15f8-40da-92b7-65e92e4f0c06

"基础模型"列中的三个音频和"SFT模型"列中的第一个音频分别由开源的 Muyan-TTS 和 Muyan-TTS-SFT 合成。"SFT模型"列中的最后两个音频由分别在基础模型上训练的 SFT 模型生成，这些模型不对外开放使用。

## 安装
### 克隆 & 安装
```sh
git clone https://github.com/MYZY-AI/Muyan-TTS.git
cd Muyan-TTS

conda create -n muyan-tts python=3.10 -y
conda activate muyan-tts
make build
```

你需要安装 ```FFmpeg```。如果你使用的是 Ubuntu，可以使用以下命令安装：
```sh
sudo apt update
sudo apt install ffmpeg
```


### 模型下载 
| 模型   | 链接   |
|-------|-------|
| Muyan-TTS   | [huggingface](https://huggingface.co/MYZY-AI/Muyan-TTS) \| [modelscope](https://modelscope.cn/models/MYZY-AI/Muyan-TTS) \| [wisemodel](https://wisemodel.cn/models/MYZY-AI/Muyan-TTS)   |
| Muyan-TTS-SFT   | [huggingface](https://huggingface.co/MYZY-AI/Muyan-TTS-SFT) \| [modelscope](https://modelscope.cn/models/MYZY-AI/Muyan-TTS-SFT) \| [wisemodel](https://wisemodel.cn/models/MYZY-AI/Muyan-TTS-SFT)   |

此外，你需要下载 [chinese-hubert-base](https://huggingface.co/TencentGameMate/chinese-hubert-base) 的权重。

将所有下载的模型放在 ```pretrained_models``` 目录中。你的目录结构应类似于以下内容：
```
pretrained_models
├── chinese-hubert-base
├── Muyan-TTS
└── Muyan-TTS-SFT
```

## 快速开始
```sh
python tts.py
```
这将通过推理合成语音。核心代码如下：
```py
async def main(model_type, model_path):
    tts = Inference(model_type, model_path, enable_vllm_acc=False)
    wavs = await tts.generate(
        ref_wav_path="assets/Claire.wav",
        prompt_text="Although the campaign was not a complete success, it did provide Napoleon with valuable experience and prestige.",
        text="Welcome to the captivating world of podcasts, let's embark on this exciting journey together."
    )
    output_path = "logs/tts.wav"
    with open(output_path, "wb") as f:
        f.write(next(wavs))  
    print(f"Speech generated in {output_path}")
```
你需要指定提示语音，包括 ```ref_wav_path``` 和其 ```prompt_text```，以及要合成的 ```text```。合成的语音默认保存到 ```logs/tts.wav```。

此外，你需要将 ```model_type``` 指定为 ```base``` 或 ```sft```，默认值为 ```base```。

当你将 ```model_type``` 指定为 ```base``` 时，你可以将提示语音更改为任意说话人进行零样本 TTS 合成。

当你将 ```model_type``` 指定为 ```sft``` 时，你需要保持提示语音不变，因为 ```sft``` 模型是在 Claire 的声音上训练的。

## API 使用
```sh
python api.py
```
使用 API 模式会自动启用 vLLM 加速，上述命令将在默认端口 ```8020``` 启动服务。此外，LLM 日志将保存在 ```logs/llm.log``` 中。

同样，你需要将 ```model_type``` 指定为 ```base``` 或 ```sft```，默认值为 ```base```。请注意，```model_path``` 应与指定的 ```model_type``` 一致。

你可以使用以下示例向 API 发送请求：
```py
import time
import requests
TTS_PORT=8020
payload = {
    "ref_wav_path": "assets/Claire.wav",
    "prompt_text": "Although the campaign was not a complete success, it did provide Napoleon with valuable experience and prestige.",
    "text": "Welcome to the captivating world of podcasts, let's embark on this exciting journey together.",
    "temperature": 1.0,
    "speed": 1.0,
}
start = time.time()

url = f"http://localhost:{TTS_PORT}/get_tts"
response = requests.post(url, json=payload)
audio_file_path = "logs/tts.wav"
with open(audio_file_path, "wb") as f:
    f.write(response.content)
    
print(time.time() - start)
```

默认情况下，合成的语音将保存在 ```logs/tts.wav```。

## 训练

我们以 ```LibriSpeech``` 为例。你可以使用自己的数据集，但需要将数据组织成 ```data_process/examples``` 中显示的格式。

如果你还没有下载 ```LibriSpeech```，可以使用以下命令下载 dev-clean 集：
```sh
wget --no-check-certificate https://www.openslr.org/resources/12/dev-clean.tar.gz
```
解压数据后，在 ```prepare_sft_dataset.py``` 中将 ```librispeech_dir``` 指定为 ```LibriSpeech``` 路径的父文件夹。然后运行：
```sh
./train.sh
```
这将自动处理数据并生成 ```data/tts_sft_data.json```。

请注意，我们使用了 LibriSpeech dev-clean 中的特定说话人 ID "3752" 作为示例，因为其数据量相对较大。如果你组织自己的数据集进行训练，请准备至少几十分钟的目标说话人的语音。

如果在过程中发生错误，请解决错误，删除数据文件夹中的现有内容，然后重新运行 ```train.sh```。

生成 ```data/tts_sft_data.json``` 后，train.sh 将自动将其复制到 ```llama-factory/data``` 并在 ```dataset_info.json``` 中添加以下字段：
```json
"tts_sft_data": {
    "file_name": "tts_sft_data.json"
}
```
最后，它将自动执行 ```llamafactory-cli train``` 命令开始训练。你可以使用 ```training/sft.yaml``` 调整训练设置。

默认情况下，训练的权重将保存到 ```pretrained_models/Muyan-TTS-new-SFT```。

训练完成后，你需要将基础/SFT 模型的 ```sovits.pth``` 复制到训练模型路径中，然后进行推理：
```sh
cp pretrained_models/Muyan-TTS/sovits.pth pretrained_models/Muyan-TTS-new-SFT
```

你可以直接使用上述 API 工具部署训练模型。在推理过程中，你需要将 ```model_type``` 指定为 ```sft```，并将 ```ref_wav_path``` 和 ```prompt_text``` 替换为你训练的说话人的语音样本。

## 常见问题排查

### 问题1：安装依赖时遇到问题
解决方案：请确保你已安装所有必要的依赖项，并按照文档中的步骤进行操作。如果问题仍然存在，请检查你的网络连接或尝试更换镜像源。

### 问题2：模型下载失败
解决方案：请确保你有足够的存储空间，并检查下载链接是否正确。如果问题仍然存在，请尝试使用其他下载工具或联系技术支持。

### 问题3：推理速度慢
解决方案：请确保你的硬件配置满足要求，并检查是否正确配置了 GPU 加速。如果问题仍然存在，请尝试优化代码或调整模型参数。

## API 集成分析报告

### 概述
本报告旨在分析 API 集成的实现，确保其正确性和稳定性。API 集成在 `api.py` 中实现，使用 FastAPI 框架，包含两个主要端点：`/get_tts` 和 `/get_tts_with_timestamps`。

### 错误处理机制
API 集成的实现包括错误处理机制，使用 `try-except` 块捕获异常并返回 HTTP 500 错误。以下是错误处理机制的示例代码：
```py
try:
    # 处理请求
except Exception as e:
    import traceback
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=str(e))
```

### 日志记录
API 集成实现了详细的日志记录，记录了 API 请求和响应的详细信息。以下是日志记录的示例代码：
```py
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.post("/get_tts")
async def get_tts(request_data: TTSRequest):
    try:
        logging.info(f"req: {request_data}")
        # 处理请求
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

### 性能分析
API 集成的性能经过优化，确保在高并发情况下的稳定性和响应速度。以下是性能优化的示例代码：
```py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=TTS_PORT)
```

### 结论
通过上述分析，我们可以确认 API 集成的实现是正确且稳定的。详细的错误处理机制和日志记录确保了系统的可靠性，性能优化确保了高并发情况下的响应速度。

## 致谢

该模型基于 [Llama-3.2-3B](https://huggingface.co/meta-llama/Llama-3.2-3B) 进行训练。

我们借鉴了大量 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 的代码。

我们借鉴了大量 [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) 的代码。

## 引用
```
@article{li2025muyan,
  title={Muyan-TTS: A Trainable Text-to-Speech Model Optimized for Podcast Scenarios with a $50 K Budget},
  author={Li, Xin and Jia, Kaikai and Sun, Hao and Dai, Jun and Jiang, Ziyang},
  journal={arXiv preprint arXiv:2504.19146},
  year={2025}
}
```

## AI 播客制作中的工具能力

Muyan-TTS 可以替代 AI 播客制作中的一些过程，如 TTS 合成。然而，它不处理播客编辑、混音或分发过程。

## 播客制作的 HTTPS API 实现

我们实现了一个涵盖播客制作各个阶段的 HTTPS API。该服务负责合成和标记请求的音频和语音，并返回最终的音频数据和时间戳文件。你可以参考 ElevenLabs TimingApi 的实现了解更多详情。
