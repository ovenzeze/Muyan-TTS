import requests
import time
import logging
import os
import base64
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
async def get_tts(request_data: TTSRequest):
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
async def get_tts_with_timestamps(request_data: TimestampRequest):
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
