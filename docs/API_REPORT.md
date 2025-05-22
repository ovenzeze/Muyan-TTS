# Muyan-TTS API 实现报告

## 概述

本报告评估了 Muyan-TTS 项目中当前的 HTTP API 实现，将其与文档中的 API 规范进行比较，并提供了解决已识别问题的修改计划。

## 当前 API 文档

根据 `INTRODUCTION.md` 中的文档，Muyan-TTS 项目提供了两个主要的 API 端点：

1. `/get_tts`：从文本生成语音
2. `/get_tts_with_timestamps`：生成带有词级时间戳的语音

这两个端点都接受以下参数：
- `ref_wav_path`：参考音频文件路径（必需）
- `prompt_text`：提示文本（必需）
- `text`：要合成的文本（必需）
- `temperature`：温度参数（可选，默认值：1.0）
- `repetition_penalty`：重复惩罚参数（可选，默认值：1.0）
- `speed`：语速（可选，默认值：1.0）
- `scaling_factor`：缩放因子（可选，默认值：1.0）

## 当前实现分析

API 在 `api.py` 中使用 FastAPI 实现。实现包括：

- 两个 Pydantic 模型：`TTSRequest` 和 `TimestampRequest`
- 两个 API 端点：`/get_tts` 和 `/get_tts_with_timestamps`
- 在主块中初始化 TTS 模型

### 已识别的问题

1. **初始化问题**：`tts` 变量仅在 `if __name__ == "__main__":` 块中初始化，但在 API 端点中使用。这意味着当作为模块导入时，API 端点将无法工作。

2. **返回类型问题**：`get_tts_with_timestamps` 函数返回一个包含 `StreamingResponse` 对象的字典，这是不可序列化的，会导致运行时错误。

3. **错误处理**：对于 `ref_wav_path` 参数中缺失的文件或其他常见错误，没有特定的错误处理。

4. **时间戳生成**：`generate_timestamps` 函数中的时间戳生成过于简单，无法提供准确的词级时间戳。它只是将音频持续时间均匀地分配给所有单词。

5. **CORS 处理**：API 中没有 CORS 处理，这可能会在从 Web 应用程序调用 API 时导致问题。

6. **安全问题**：API 没有任何身份验证或速率限制机制。

7. **文档不一致**：API 文档提到参数是可选的，实现也正确地将它们设置为可选，但没有对边缘情况进行验证或处理。

## 修改计划

### 1. 修复初始化问题

将 TTS 模型初始化移到 `if __name__ == "__main__":` 块外，确保在模块被导入时可用。

```python
# 在模块级别初始化 TTS 模型
model_type = "base"
model_path = "pretrained_models/Muyan-TTS"
tts = Inference(model_type, model_path, enable_vllm_acc=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=TTS_PORT)
```

### 2. 修复时间戳 API 的返回类型问题

修改 `get_tts_with_timestamps` 端点以正确返回音频和时间戳：

选项 1：返回包含音频文件 URL 和时间戳的 JSON 响应：
```python
@app.post("/get_tts_with_timestamps")
async def get_tts_with_timestamps(request_data: TimestampRequest):
    # ... 现有代码 ...
    
    # 将音频保存到临时文件
    audio_file_path = f"temp/{int(time.time())}.wav"
    os.makedirs("temp", exist_ok=True)
    with open(audio_file_path, "wb") as f:
        f.write(tts_response)
    
    # 返回包含文件 URL 和时间戳的 JSON
    return {
        "audio_url": f"/audio/{os.path.basename(audio_file_path)}",
        "timestamps": timestamps
    }

# 添加一个路由来提供音频文件
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    return FileResponse(f"temp/{filename}", media_type="audio/wav")
```

选项 2：使用可以处理二进制数据和 JSON 的自定义响应类：
```python
from fastapi.responses import JSONResponse
import base64

@app.post("/get_tts_with_timestamps")
async def get_tts_with_timestamps(request_data: TimestampRequest):
    # ... 现有代码 ...
    
    # 将音频编码为 base64
    audio_base64 = base64.b64encode(tts_response).decode("utf-8")
    
    # 返回包含 base64 音频和时间戳的 JSON
    return JSONResponse({
        "audio_base64": audio_base64,
        "timestamps": timestamps
    })
```

### 3. 改进错误处理

为常见问题添加更具体的错误处理：

```python
@app.post("/get_tts")
async def get_tts(request_data: TTSRequest):
    try:
        # 检查参考音频文件是否存在
        if not os.path.exists(request_data.ref_wav_path):
            raise HTTPException(status_code=404, detail=f"参考音频文件未找到：{request_data.ref_wav_path}")
        
        # ... 现有代码 ...
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

### 4. 改进时间戳生成

实现更准确的时间戳生成方法：

```python
def generate_timestamps(self, text, synthesized_audio, sample_rate=16000):
    """
    使用基于音素的方法生成更准确的词级时间戳。
    这是一个更复杂实现的占位符。
    """
    # 对于实际实现，考虑使用强制对齐工具，如：
    # - Montreal Forced Aligner
    # - Gentle
    # - DeepSpeech 的对齐功能
    
    words = text.split()
    num_words = len(words)
    duration = len(synthesized_audio) / sample_rate
    
    # 简单实现（改进版）
    # 假设具有更多字符的单词按比例需要更多时间
    total_chars = sum(len(word) for word in words)
    timestamps = []
    current_time = 0
    
    for word in words:
        word_duration = (len(word) / total_chars) * duration
        timestamps.append((word, current_time, current_time + word_duration))
        current_time += word_duration
    
    return timestamps
```

### 5. 添加 CORS 支持

添加 CORS 中间件以允许跨源请求：

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)
```

### 6. 添加基本安全性

实现基本的 API 密钥身份验证：

```python
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, Depends, HTTPException

API_KEY = "your-api-key"  # 在生产环境中，使用环境变量
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="无法验证 API 密钥")
    return api_key

@app.post("/get_tts")
async def get_tts(request_data: TTSRequest, api_key: str = Depends(get_api_key)):
    # ... 现有代码 ...
```

### 7. 添加输入验证

增强 API 参数的输入验证：

```python
from pydantic import BaseModel, validator, Field

class TTSRequest(BaseModel):
    ref_wav_path: str
    prompt_text: str
    text: str
    temperature: Optional[float] = Field(1.0, ge=0.1, le=2.0)
    repetition_penalty: Optional[float] = Field(1.0, ge=0.1, le=2.0)
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0)
    scaling_factor: Optional[float] = Field(1.0, ge=0.5, le=2.0)
    
    @validator('ref_wav_path')
    def validate_ref_wav_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"参考音频文件未找到：{v}")
        return v
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("文本不能为空")
        return v
```

## 实施优先级

1. 修复初始化问题（关键）
2. 修复时间戳 API 的返回类型问题（关键）
3. 改进错误处理（高）
4. 添加 CORS 支持（中）
5. 添加输入验证（中）
6. 改进时间戳生成（中）
7. 添加基本安全性（低，取决于部署环境）

## 结论

当前的 API 实现存在几个需要解决的问题，以确保它能够正常工作并提供文档中描述的功能。所提出的修改将提高 API 的可靠性、安全性和可用性。

一旦实施了这些更改，应该进行额外的测试，以确保 API 在各种情况下按预期工作，包括边缘情况和错误条件。