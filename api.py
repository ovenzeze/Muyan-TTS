import requests
import time
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

import os
from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import uvicorn
from inference.inference import Inference

TTS_PORT=8020
app = FastAPI()


class TTSRequest(BaseModel):
    ref_wav_path: str
    prompt_text: str
    text: str
    temperature: Optional[float]=1.0
    repetition_penalty: Optional[float]=1.0
    speed: Optional[float]=1.0
    scaling_factor: Optional[float]=1.0
    
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

class TimestampRequest(BaseModel):
    ref_wav_path: str
    prompt_text: str
    text: str
    temperature: Optional[float] = 1.0
    repetition_penalty: Optional[float] = 1.0
    speed: Optional[float] = 1.0
    scaling_factor: Optional[float] = 1.0

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
