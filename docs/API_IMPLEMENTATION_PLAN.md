# Muyan-TTS API Implementation Plan

This document provides a detailed implementation plan for addressing the issues identified in the API_REPORT.md. It includes specific code changes and examples for each modification.

## 1. Fix Initialization Issue

### Current Code (api.py):
```python
# ... existing code ...

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

### Modified Code:
```python
# ... existing code ...

# Initialize TTS model at module level
model_type = "base"
cnhubert_model_path = "pretrained_models/chinese-hubert-base"

try:
    if model_type == "base":
        model_path = "pretrained_models/Muyan-TTS"
    elif model_type == "sft":
        model_path = "pretrained_models/Muyan-TTS-SFT"
    else:
        print(f"Invalid model type: '{model_type}'. Please specify either 'base' or 'sft'.")
        model_path = "pretrained_models/Muyan-TTS"  # Default to base model
    print(f"Model path: {model_path}")
except Exception as e:
    print(f"Error setting model path: {str(e)}")
    model_path = "pretrained_models/Muyan-TTS"  # Default to base model

# Initialize TTS model
tts = Inference(model_type, model_path, enable_vllm_acc=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=TTS_PORT)
```

## 2. Fix Return Type Issue for Timestamps API

### Current Code (api.py):
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

### Modified Code (Option 1 - File-based approach):
```python
import os
import time
from fastapi.responses import FileResponse

# Create a directory for temporary audio files
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
        
        # Save audio to a temporary file
        timestamp = int(time.time())
        filename = f"tts_{timestamp}.wav"
        file_path = os.path.join("temp_audio", filename)
        
        with open(file_path, "wb") as f:
            f.write(audio_data)
        
        # Return JSON with file URL and timestamps
        return {
            "audio_url": f"/audio/{filename}",
            "timestamps": timestamps
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Add a route to serve audio files
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join("temp_audio", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/wav")
```

### Modified Code (Option 2 - Base64 approach):
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
        
        # Encode audio as base64
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        
        # Return JSON with base64 audio and timestamps
        return JSONResponse({
            "audio_base64": audio_base64,
            "timestamps": timestamps
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

## 3. Improve Error Handling

### Current Code (api.py):
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

### Modified Code:
```python
@app.post("/get_tts")
async def get_tts(request_data: TTSRequest):
    try:
        logging.info(f"req: {request_data}")
        
        # Check if reference audio file exists
        if not os.path.exists(request_data.ref_wav_path):
            raise HTTPException(status_code=404, detail=f"Reference audio file not found: {request_data.ref_wav_path}")
        
        # Check if text is empty
        if not request_data.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
            
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
        logging.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logging.error(f"Invalid input: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logging.error(f"Error during TTS generation: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

## 4. Add CORS Support

### Modified Code (api.py):
```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# ... rest of the code ...
```

## 5. Add Input Validation

### Current Code (api.py):
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

### Modified Code:
```python
from pydantic import BaseModel, validator, Field
from typing import Optional
import os

class TTSRequest(BaseModel):
    ref_wav_path: str
    prompt_text: str
    text: str
    temperature: Optional[float] = Field(1.0, ge=0.1, le=2.0, description="Temperature parameter (0.1-2.0)")
    repetition_penalty: Optional[float] = Field(1.0, ge=0.1, le=2.0, description="Repetition penalty (0.1-2.0)")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")
    scaling_factor: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Scaling factor (0.5-2.0)")
    
    @validator('ref_wav_path')
    def validate_ref_wav_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"Reference audio file not found: {v}")
        return v
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        if len(v) > 1000:
            raise ValueError("Text is too long (maximum 1000 characters)")
        return v
```

## 6. Improve Timestamp Generation

### Current Code (inference.py):
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

### Modified Code:
```python
def generate_timestamps(self, text, synthesized_audio, sample_rate=16000):
    """
    Generate more accurate word-level timestamps using character-based duration estimation.
    
    Args:
        text (str): The input text
        synthesized_audio (bytes): The synthesized audio data
        sample_rate (int): The audio sample rate
        
    Returns:
        list: A list of tuples (word, start_time, end_time)
    """
    words = text.split()
    if not words:
        return []
        
    # Calculate total duration
    duration = len(synthesized_audio) / sample_rate
    
    # Calculate character-based durations
    total_chars = sum(len(word) for word in words)
    
    # Add spaces between words (except for the last word)
    total_chars += len(words) - 1
    
    timestamps = []
    current_time = 0
    
    for i, word in enumerate(words):
        # Calculate word duration based on character count
        # Add 1 for the space after the word (except for the last word)
        char_count = len(word) + (0 if i == len(words) - 1 else 1)
        word_duration = (char_count / total_chars) * duration
        
        # Add timestamp
        timestamps.append({
            "word": word,
            "start_time": round(current_time, 3),
            "end_time": round(current_time + word_duration, 3)
        })
        
        # Update current time
        current_time += word_duration
    
    return timestamps
```

## 7. Add Basic Security

### Modified Code (api.py):
```python
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, Depends, HTTPException
import os

# Get API key from environment variable or use a default for development
API_KEY = os.getenv("MUYAN_TTS_API_KEY", "dev-api-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=403, detail="API key is required")
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/get_tts")
async def get_tts(request_data: TTSRequest, api_key: str = Depends(get_api_key)):
    # ... existing code ...

@app.post("/get_tts_with_timestamps")
async def get_tts_with_timestamps(request_data: TimestampRequest, api_key: str = Depends(get_api_key)):
    # ... existing code ...
```

## Complete Modified API Implementation

Here's a complete implementation of the modified `api.py` file incorporating all the changes:

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
              description="API for text-to-speech synthesis using Muyan-TTS",
              version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create a directory for temporary audio files
os.makedirs("temp_audio", exist_ok=True)

# API key authentication (optional)
# Uncomment to enable API key authentication
# API_KEY = os.getenv("MUYAN_TTS_API_KEY", "dev-api-key")
# api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
# 
# async def get_api_key(api_key: str = Security(api_key_header)):
#     if not api_key:
#         raise HTTPException(status_code=403, detail="API key is required")
#     if api_key != API_KEY:
#         raise HTTPException(status_code=403, detail="Invalid API key")
#     return api_key


class TTSRequest(BaseModel):
    ref_wav_path: str
    prompt_text: str
    text: str
    temperature: Optional[float] = Field(1.0, ge=0.1, le=2.0, description="Temperature parameter (0.1-2.0)")
    repetition_penalty: Optional[float] = Field(1.0, ge=0.1, le=2.0, description="Repetition penalty (0.1-2.0)")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")
    scaling_factor: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Scaling factor (0.5-2.0)")
    
    @validator('ref_wav_path')
    def validate_ref_wav_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"Reference audio file not found: {v}")
        return v
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        if len(v) > 1000:
            raise ValueError("Text is too long (maximum 1000 characters)")
        return v


class TimestampRequest(TTSRequest):
    # Inherits all fields and validators from TTSRequest
    pass


@app.post("/get_tts", summary="Generate speech from text", 
          description="Converts text to speech using the specified reference audio and parameters")
async def get_tts(request_data: TTSRequest):  # Add api_key: str = Depends(get_api_key) to enable API key auth
    try:
        logging.info(f"req: {request_data}")
        
        # Validation is handled by Pydantic validators
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
        logging.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logging.error(f"Invalid input: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logging.error(f"Error during TTS generation: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_tts_with_timestamps", summary="Generate speech with timestamps", 
          description="Converts text to speech and returns word-level timestamps")
async def get_tts_with_timestamps(request_data: TimestampRequest):  # Add api_key: str = Depends(get_api_key) to enable API key auth
    try:
        logging.info(f"req: {request_data}")
        
        # Validation is handled by Pydantic validators
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
        
        # Save audio to a temporary file
        timestamp = int(time.time())
        filename = f"tts_{timestamp}.wav"
        file_path = os.path.join("temp_audio", filename)
        
        with open(file_path, "wb") as f:
            f.write(audio_data)
        
        # Return JSON with file URL and timestamps
        return {
            "audio_url": f"/audio/{filename}",
            "timestamps": timestamps
        }
    except FileNotFoundError as e:
        logging.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logging.error(f"Invalid input: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logging.error(f"Error during TTS generation: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audio/{filename}", summary="Get audio file", 
         description="Returns the audio file generated by the TTS API")
async def get_audio(filename: str):
    file_path = os.path.join("temp_audio", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/wav")


@app.get("/", summary="API root", description="Returns basic API information")
async def root():
    return {
        "name": "Muyan-TTS API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/get_tts", "method": "POST", "description": "Generate speech from text"},
            {"path": "/get_tts_with_timestamps", "method": "POST", "description": "Generate speech with timestamps"},
            {"path": "/audio/{filename}", "method": "GET", "description": "Get audio file"}
        ]
    }


# Initialize TTS model at module level
model_type = "base"
cnhubert_model_path = "pretrained_models/chinese-hubert-base"

try:
    if model_type == "base":
        model_path = "pretrained_models/Muyan-TTS"
    elif model_type == "sft":
        model_path = "pretrained_models/Muyan-TTS-SFT"
    else:
        logging.warning(f"Invalid model type: '{model_type}'. Using default 'base' model.")
        model_path = "pretrained_models/Muyan-TTS"  # Default to base model
    logging.info(f"Model path: {model_path}")
except Exception as e:
    logging.error(f"Error setting model path: {str(e)}")
    model_path = "pretrained_models/Muyan-TTS"  # Default to base model

# Initialize TTS model
tts = Inference(model_type, model_path, enable_vllm_acc=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=TTS_PORT)
```

## Implementation Timeline

1. **Day 1**: Fix critical issues
   - Fix initialization issue
   - Fix return type issue for timestamps API
   - Add basic error handling

2. **Day 2**: Implement medium-priority improvements
   - Add CORS support
   - Add input validation
   - Improve timestamp generation

3. **Day 3**: Add security and finalize
   - Add basic security (if needed)
   - Test all API endpoints
   - Document changes

## Testing Plan

After implementing the changes, the following tests should be performed:

1. **Basic Functionality Tests**:
   - Test `/get_tts` with valid parameters
   - Test `/get_tts_with_timestamps` with valid parameters
   - Test `/audio/{filename}` endpoint

2. **Error Handling Tests**:
   - Test with non-existent reference audio file
   - Test with empty text
   - Test with invalid parameters (out of range)

3. **Edge Case Tests**:
   - Test with very long text
   - Test with text containing special characters
   - Test with different languages

4. **Security Tests** (if implemented):
   - Test with missing API key
   - Test with invalid API key

## Conclusion

This implementation plan provides a comprehensive approach to addressing the issues identified in the API_REPORT.md. By following this plan, the Muyan-TTS API will be more robust, secure, and user-friendly.