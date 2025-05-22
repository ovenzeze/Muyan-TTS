# Muyan-TTS API 实施计划

本文档提供了一个详细的实施计划，用于解决 API_REPORT.md 中确定的问题。它包括每个修改的具体代码更改和示例。

## 1. 修复初始化问题

### 当前代码 (api.py):
```python
# ... 现有代码 ...

if __name__ == "__main__":
    model_type = "base"
    cnhubert_model_path = "pretrained_models/chinese-hubert-base"
    
    try:
        if model_type == "base":
            model_path = "pretrained_models/Muyan-TTS"
        elif model_type == "sft":
            model_path = "pretrained_models/Muyan-TTS-SFT"
        else:
            print(f"Invalid model type: '{model_type}'. Please specify either 'base' or 'sft'.")
        print(f"Model downloaded successfully to {model_path}")
    except Exception as e:
        print(f"Error downloading model: {str(e)}")
    
    tts = Inference(model_type, model_path, enable_vllm_acc=True)
    uvicorn.run(app, host="0.0.0.0", port=TTS_PORT)
```

### 修改后的代码:
```python
# ... 现有代码 ...

# 在模块级别初始化 TTS 模型
model_type = "base"
cnhubert_model_path = "pretrained_models/chinese-hubert-base"

try:
    if model_type == "base":
        model_path = "pretrained_models/Muyan-TTS"
    elif model_type == "sft":
        model_path = "pretrained_models/Muyan-TTS-SFT"
    else:
        print(f"无效的模型类型: '{model_type}'。请指定 'base' 或 'sft'。")
        model_path = "pretrained_models/Muyan-TTS"  # 默认使用基础模型
    print(f"模型路径: {model_path}")
except Exception as e:
    print(f"设置模型路径时出错: {str(e)}")
    model_path = "pretrained_models/Muyan-TTS"  # 默认使用基础模型

# 初始化 TTS 模型
tts = Inference(model_type, model_path, enable_vllm_acc=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=TTS_PORT)
```

## 2. 修复时间戳 API 的返回类型问题

### 当前代码 (api.py):
```python
@app.post("/get_tts_with_timestamps")
async def get_tts_with_timestamps(request_data: TimestampRequest):
    try:
        logging.info(f"req: {request_data}")
        ref_wav_path = request_data.ref_wav_path
        prompt_text = request_data.prompt_text
        text = request_data.text
        temperature = request_data.temperature
        repetition_penalty = request_data.repetition_penalty
        speed = request_data.speed
        scaling_factor = request_data.scaling_factor

        tts_response, timestamps = await tts.generate_with_timestamps(ref_wav_path, prompt_text, text, temperature=temperature,
                                                                      repetition_penalty=repetition_penalty, speed=speed,
                                                                      scaling_factor=scaling_factor)
        return {"audio": StreamingResponse(tts_response, media_type="audio/wav"), "timestamps": timestamps}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

### 修改后的代码 (选项 1 - 基于文件的方法):
```python
import os
import time
from fastapi.responses import FileResponse

# 创建临时音频文件目录
os.makedirs("temp_audio", exist_ok=True)

@app.post("/get_tts_with_timestamps")
async def get_tts_with_timestamps(request_data: TimestampRequest):
    try:
        logging.info(f"req: {request_data}")
        ref_wav_path = request_data.ref_wav_path
        prompt_text = request_data.prompt_text
        text = request_data.text
        temperature = request_data.temperature
        repetition_penalty = request_data.repetition_penalty
        speed = request_data.speed
        scaling_factor = request_data.scaling_factor

        audio_data, timestamps = await tts.generate_with_timestamps(ref_wav_path, prompt_text, text, temperature=temperature,
                                                                   repetition_penalty=repetition_penalty, speed=speed,
                                                                   scaling_factor=scaling_factor)
        
        # 将音频保存到临时文件
        timestamp = int(time.time())
        filename = f"tts_{timestamp}.wav"
        file_path = os.path.join("temp_audio", filename)
        
        with open(file_path, "wb") as f:
            f.write(audio_data)
        
        # 返回包含文件 URL 和时间戳的 JSON
        return {
            "audio_url": f"/audio/{filename}",
            "timestamps": timestamps
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# 添加一个路由来提供音频文件
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join("temp_audio", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="音频文件未找到")
    return FileResponse(file_path, media_type="audio/wav")
```

### 修改后的代码 (选项 2 - Base64 方法):
```python
import base64
from fastapi.responses import JSONResponse

@app.post("/get_tts_with_timestamps")
async def get_tts_with_timestamps(request_data: TimestampRequest):
    try:
        logging.info(f"req: {request_data}")
        ref_wav_path = request_data.ref_wav_path
        prompt_text = request_data.prompt_text
        text = request_data.text
        temperature = request_data.temperature
        repetition_penalty = request_data.repetition_penalty
        speed = request_data.speed
        scaling_factor = request_data.scaling_factor

        audio_data, timestamps = await tts.generate_with_timestamps(ref_wav_path, prompt_text, text, temperature=temperature,
                                                                   repetition_penalty=repetition_penalty, speed=speed,
                                                                   scaling_factor=scaling_factor)
        
        # 将音频编码为 base64
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        
        # 返回包含 base64 音频和时间戳的 JSON
        return JSONResponse({
            "audio_base64": audio_base64,
            "timestamps": timestamps
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

## 3. 改进错误处理

### 当前代码 (api.py):
```python
@app.post("/get_tts")
async def get_tts(request_data: TTSRequest):
    try:
        logging.info(f"req: {request_data}")
        ref_wav_path = request_data.ref_wav_path
        prompt_text = request_data.prompt_text
        text = request_data.text
        temperature = request_data.temperature
        repetition_penalty = request_data.repetition_penalty
        speed = request_data.speed
        scaling_factor = request_data.scaling_factor
        
        tts_response = await tts.generate(ref_wav_path, prompt_text, text, temperature=temperature,
                                          repetition_penalty=repetition_penalty, speed=speed,
                                          scaling_factor=scaling_factor)
        return StreamingResponse(tts_response, media_type="audio/wav")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

### 修改后的代码:
```python
@app.post("/get_tts")
async def get_tts(request_data: TTSRequest):
    try:
        logging.info(f"req: {request_data}")
        
        # 检查参考音频文件是否存在
        if not os.path.exists(request_data.ref_wav_path):
            raise HTTPException(status_code=404, detail=f"参考音频文件未找到：{request_data.ref_wav_path}")
        
        # 检查文本是否为空
        if not request_data.text.strip():
            raise HTTPException(status_code=400, detail="文本不能为空")
            
        ref_wav_path = request_data.ref_wav_path
        prompt_text = request_data.prompt_text
        text = request_data.text
        temperature = request_data.temperature
        repetition_penalty = request_data.repetition_penalty
        speed = request_data.speed
        scaling_factor = request_data.scaling_factor
        
        tts_response = await tts.generate(ref_wav_path, prompt_text, text, temperature=temperature,
                                          repetition_penalty=repetition_penalty, speed=speed,
                                          scaling_factor=scaling_factor)
        return StreamingResponse(tts_response, media_type="audio/wav")
    except FileNotFoundError as e:
        logging.error(f"文件未找到: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logging.error(f"无效输入: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logging.error(f"TTS 生成过程中出错: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

## 4. 添加 CORS 支持

### 修改后的代码 (api.py):
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

# ... 代码的其余部分 ...
```

## 5. 添加输入验证

### 当前代码 (api.py):
```python
class TTSRequest(BaseModel):
    ref_wav_path: str
    prompt_text: str
    text: str
    temperature: Optional[float]=1.0
    repetition_penalty: Optional[float]=1.0
    speed: Optional[float]=1.0
    scaling_factor: Optional[float]=1.0
```

### 修改后的代码:
```python
from pydantic import BaseModel, validator, Field
from typing import Optional
import os

class TTSRequest(BaseModel):
    ref_wav_path: str
    prompt_text: str
    text: str
    temperature: Optional[float] = Field(1.0, ge=0.1, le=2.0, description="温度参数 (0.1-2.0)")
    repetition_penalty: Optional[float] = Field(1.0, ge=0.1, le=2.0, description="重复惩罚 (0.1-2.0)")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="语速 (0.5-2.0)")
    scaling_factor: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="缩放因子 (0.5-2.0)")
    
    @validator('ref_wav_path')
    def validate_ref_wav_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"参考音频文件未找到：{v}")
        return v
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("文本不能为空")
        if len(v) > 1000:
            raise ValueError("文本太长（最多1000个字符）")
        return v
```

## 6. 改进时间戳生成

### 当前代码 (inference.py):
```python
def generate_timestamps(self, text, synthesized_audio):
    words = text.split()
    num_words = len(words)
    duration = len(synthesized_audio) / 16000  # Assuming 16kHz sample rate
    timestamps = []
    for i, word in enumerate(words):
        start_time = (i / num_words) * duration
        end_time = ((i + 1) / num_words) * duration
        timestamps.append((word, start_time, end_time))
    return timestamps
```

### 修改后的代码:
```python
def generate_timestamps(self, text, synthesized_audio, sample_rate=16000):
    """
    使用基于字符的持续时间估计生成更准确的词级时间戳。
    
    参数:
        text (str): 输入文本
        synthesized_audio (bytes): 合成的音频数据
        sample_rate (int): 音频采样率
        
    返回:
        list: 包含元组 (word, start_time, end_time) 的列表
    """
    words = text.split()
    if not words:
        return []
        
    # 计算总持续时间
    duration = len(synthesized_audio) / sample_rate
    
    # 计算基于字符的持续时间
    total_chars = sum(len(word) for word in words)
    
    # 在单词之间添加空格（最后一个单词除外）
    total_chars += len(words) - 1
    
    timestamps = []
    current_time = 0
    
    for i, word in enumerate(words):
        # 根据字符计数计算单词持续时间
        # 为单词后的空格添加1（最后一个单词除外）
        char_count = len(word) + (0 if i == len(words) - 1 else 1)
        word_duration = (char_count / total_chars) * duration
        
        # 添加时间戳
        timestamps.append({
            "word": word,
            "start_time": round(current_time, 3),
            "end_time": round(current_time + word_duration, 3)
        })
        
        # 更新当前时间
        current_time += word_duration
    
    return timestamps
```

## 7. 添加基本安全性

### 修改后的代码 (api.py):
```python
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, Depends, HTTPException
import os

# 从环境变量获取 API 密钥或使用开发默认值
API_KEY = os.getenv("MUYAN_TTS_API_KEY", "dev-api-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=403, detail="需要 API 密钥")
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="无效的 API 密钥")
    return api_key

@app.post("/get_tts")
async def get_tts(request_data: TTSRequest, api_key: str = Depends(get_api_key)):
    # ... 现有代码 ...

@app.post("/get_tts_with_timestamps")
async def get_tts_with_timestamps(request_data: TimestampRequest, api_key: str = Depends(get_api_key)):
    # ... 现有代码 ...
```

## 完整的修改后 API 实现

以下是包含所有更改的修改后 `api.py` 文件的完整实现：

```python
import requests
import time
import logging
import os
import base64
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, validator, Field
import uvicorn
from inference.inference import Inference

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TTS_PORT = 8020
app = FastAPI(title="Muyan-TTS API", 
              description="使用 Muyan-TTS 进行文本到语音合成的 API",
              version="1.0.0")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 创建临时音频文件目录
os.makedirs("temp_audio", exist_ok=True)

# API 密钥认证（可选）
# 取消注释以启用 API 密钥认证
# API_KEY = os.getenv("MUYAN_TTS_API_KEY", "dev-api-key")
# api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
# 
# async def get_api_key(api_key: str = Security(api_key_header)):
#     if not api_key:
#         raise HTTPException(status_code=403, detail="需要 API 密钥")
#     if api_key != API_KEY:
#         raise HTTPException(status_code=403, detail="无效的 API 密钥")
#     return api_key


class TTSRequest(BaseModel):
    ref_wav_path: str
    prompt_text: str
    text: str
    temperature: Optional[float] = Field(1.0, ge=0.1, le=2.0, description="温度参数 (0.1-2.0)")
    repetition_penalty: Optional[float] = Field(1.0, ge=0.1, le=2.0, description="重复惩罚 (0.1-2.0)")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="语速 (0.5-2.0)")
    scaling_factor: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="缩放因子 (0.5-2.0)")
    
    @validator('ref_wav_path')
    def validate_ref_wav_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"参考音频文件未找到：{v}")
        return v
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("文本不能为空")
        if len(v) > 1000:
            raise ValueError("文本太长（最多1000个字符）")
        return v


class TimestampRequest(TTSRequest):
    # 继承 TTSRequest 的所有字段和验证器
    pass


@app.post("/get_tts", summary="从文本生成语音", 
          description="使用指定的参考音频和参数将文本转换为语音")
async def get_tts(request_data: TTSRequest):  # 添加 api_key: str = Depends(get_api_key) 以启用 API 密钥认证
    try:
        logging.info(f"req: {request_data}")
        
        # 验证由 Pydantic 验证器处理
        ref_wav_path = request_data.ref_wav_path
        prompt_text = request_data.prompt_text
        text = request_data.text
        temperature = request_data.temperature
        repetition_penalty = request_data.repetition_penalty
        speed = request_data.speed
        scaling_factor = request_data.scaling_factor
        
        tts_response = await tts.generate(ref_wav_path, prompt_text, text, temperature=temperature,
                                          repetition_penalty=repetition_penalty, speed=speed,
                                          scaling_factor=scaling_factor)
        return StreamingResponse(tts_response, media_type="audio/wav")
    except FileNotFoundError as e:
        logging.error(f"文件未找到: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logging.error(f"无效输入: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logging.error(f"TTS 生成过程中出错: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_tts_with_timestamps", summary="生成带时间戳的语音", 
          description="将文本转换为语音并返回词级时间戳")
async def get_tts_with_timestamps(request_data: TimestampRequest):  # 添加 api_key: str = Depends(get_api_key) 以启用 API 密钥认证
    try:
        logging.info(f"req: {request_data}")
        
        # 验证由 Pydantic 验证器处理
        ref_wav_path = request_data.ref_wav_path
        prompt_text = request_data.prompt_text
        text = request_data.text
        temperature = request_data.temperature
        repetition_penalty = request_data.repetition_penalty
        speed = request_data.speed
        scaling_factor = request_data.scaling_factor

        audio_data, timestamps = await tts.generate_with_timestamps(ref_wav_path, prompt_text, text, temperature=temperature,
                                                                   repetition_penalty=repetition_penalty, speed=speed,
                                                                   scaling_factor=scaling_factor)
        
        # 将音频保存到临时文件
        timestamp = int(time.time())
        filename = f"tts_{timestamp}.wav"
        file_path = os.path.join("temp_audio", filename)
        
        with open(file_path, "wb") as f:
            f.write(audio_data)
        
        # 返回包含文件 URL 和时间戳的 JSON
        return {
            "audio_url": f"/audio/{filename}",
            "timestamps": timestamps
        }
    except FileNotFoundError as e:
        logging.error(f"文件未找到: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logging.error(f"无效输入: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logging.error(f"TTS 生成过程中出错: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audio/{filename}", summary="获取音频文件", 
         description="返回由 TTS API 生成的音频文件")
async def get_audio(filename: str):
    file_path = os.path.join("temp_audio", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="音频文件未找到")
    return FileResponse(file_path, media_type="audio/wav")


@app.get("/", summary="API 根路径", description="返回基本 API 信息")
async def root():
    return {
        "name": "Muyan-TTS API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/get_tts", "method": "POST", "description": "从文本生成语音"},
            {"path": "/get_tts_with_timestamps", "method": "POST", "description": "生成带时间戳的语音"},
            {"path": "/audio/{filename}", "method": "GET", "description": "获取音频文件"}
        ]
    }


# 在模块级别初始化 TTS 模型
model_type = "base"
cnhubert_model_path = "pretrained_models/chinese-hubert-base"

try:
    if model_type == "base":
        model_path = "pretrained_models/Muyan-TTS"
    elif model_type == "sft":
        model_path = "pretrained_models/Muyan-TTS-SFT"
    else:
        logging.warning(f"无效的模型类型: '{model_type}'。使用默认的 'base' 模型。")
        model_path = "pretrained_models/Muyan-TTS"  # 默认使用基础模型
    logging.info(f"模型路径: {model_path}")
except Exception as e:
    logging.error(f"设置模型路径时出错: {str(e)}")
    model_path = "pretrained_models/Muyan-TTS"  # 默认使用基础模型

# 初始化 TTS 模型
tts = Inference(model_type, model_path, enable_vllm_acc=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=TTS_PORT)
```

## 实施时间表

1. **第 1 天**：修复关键问题
   - 修复初始化问题
   - 修复时间戳 API 的返回类型问题
   - 添加基本错误处理

2. **第 2 天**：实施中等优先级的改进
   - 添加 CORS 支持
   - 添加输入验证
   - 改进时间戳生成

3. **第 3 天**：添加安全性并完成
   - 添加基本安全性（如需要）
   - 测试所有 API 端点
   - 记录更改

## 测试计划

实施更改后，应执行以下测试：

1. **基本功能测试**：
   - 使用有效参数测试 `/get_tts`
   - 使用有效参数测试 `/get_tts_with_timestamps`
   - 测试 `/audio/{filename}` 端点

2. **错误处理测试**：
   - 使用不存在的参考音频文件进行测试
   - 使用空文本进行测试
   - 使用无效参数（超出范围）进行测试

3. **边缘情况测试**：
   - 使用非常长的文本进行测试
   - 使用包含特殊字符的文本进行测试
   - 使用不同语言进行测试

4. **安全测试**（如已实施）：
   - 使用缺少 API 密钥进行测试
   - 使用无效 API 密钥进行测试

## 结论

本实施计划提供了一种全面的方法来解决 API_REPORT.md 中确定的问题。通过遵循此计划，Muyan-TTS API 将更加健壮、安全和用户友好。