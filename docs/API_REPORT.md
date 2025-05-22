# Muyan-TTS API Implementation Report

## Overview

This report evaluates the current HTTP API implementation in the Muyan-TTS project, comparing it with the documented API specifications, and provides a modification plan to address identified issues.

## Current API Documentation

According to the documentation in `INTRODUCTION.md`, the Muyan-TTS project provides two main API endpoints:

1. `/get_tts`: Generates speech from text
2. `/get_tts_with_timestamps`: Generates speech with word-level timestamps

Both endpoints accept the following parameters:
- `ref_wav_path`: Reference audio file path (required)
- `prompt_text`: Prompt text (required)
- `text`: Text to synthesize (required)
- `temperature`: Temperature parameter (optional, default: 1.0)
- `repetition_penalty`: Repetition penalty parameter (optional, default: 1.0)
- `speed`: Speech speed (optional, default: 1.0)
- `scaling_factor`: Scaling factor (optional, default: 1.0)

## Current Implementation Analysis

The API is implemented in `api.py` using FastAPI. The implementation includes:

- Two Pydantic models: `TTSRequest` and `TimestampRequest`
- Two API endpoints: `/get_tts` and `/get_tts_with_timestamps`
- Initialization of the TTS model in the main block

### Issues Identified

1. **Initialization Issue**: The `tts` variable is only initialized in the `if __name__ == "__main__":` block, but it's used in the API endpoints. This means the API endpoints won't work when imported as a module.

2. **Return Type Issue**: The `get_tts_with_timestamps` function returns a dictionary containing a `StreamingResponse` object, which is not serializable and will cause runtime errors.

3. **Error Handling**: There's no specific error handling for missing files in the `ref_wav_path` parameter or other common errors.

4. **Timestamp Generation**: The timestamp generation in the `generate_timestamps` function is simplistic and doesn't provide accurate word-level timestamps. It just divides the audio duration evenly among all words.

5. **CORS Handling**: There's no CORS handling in the API, which might cause issues when calling the API from a web application.

6. **Security Concerns**: The API doesn't have any authentication or rate limiting mechanisms.

7. **Documentation Discrepancy**: The API documentation mentions that parameters are optional, and the implementation correctly sets them as optional, but there's no validation or handling for edge cases.

## Modification Plan

### 1. Fix Initialization Issue

Move the TTS model initialization outside the `if __name__ == "__main__":` block to ensure it's available when the module is imported.

```python
# Initialize TTS model at module level
model_type = "base"
model_path = "pretrained_models/Muyan-TTS"
tts = Inference(model_type, model_path, enable_vllm_acc=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=TTS_PORT)
```

### 2. Fix Return Type Issue for Timestamps API

Modify the `get_tts_with_timestamps` endpoint to return both audio and timestamps correctly:

Option 1: Return a JSON response with a URL to the audio file and the timestamps:
```python
@app.post("/get_tts_with_timestamps")
async def get_tts_with_timestamps(request_data: TimestampRequest):
    # ... existing code ...
    
    # Save audio to a temporary file
    audio_file_path = f"temp/{int(time.time())}.wav"
    os.makedirs("temp", exist_ok=True)
    with open(audio_file_path, "wb") as f:
        f.write(tts_response)
    
    # Return JSON with file URL and timestamps
    return {
        "audio_url": f"/audio/{os.path.basename(audio_file_path)}",
        "timestamps": timestamps
    }

# Add a route to serve audio files
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    return FileResponse(f"temp/{filename}", media_type="audio/wav")
```

Option 2: Use a custom response class that can handle both binary data and JSON:
```python
from fastapi.responses import JSONResponse
import base64

@app.post("/get_tts_with_timestamps")
async def get_tts_with_timestamps(request_data: TimestampRequest):
    # ... existing code ...
    
    # Encode audio as base64
    audio_base64 = base64.b64encode(tts_response).decode("utf-8")
    
    # Return JSON with base64 audio and timestamps
    return JSONResponse({
        "audio_base64": audio_base64,
        "timestamps": timestamps
    })
```

### 3. Improve Error Handling

Add more specific error handling for common issues:

```python
@app.post("/get_tts")
async def get_tts(request_data: TTSRequest):
    try:
        # Check if reference audio file exists
        if not os.path.exists(request_data.ref_wav_path):
            raise HTTPException(status_code=404, detail=f"Reference audio file not found: {request_data.ref_wav_path}")
        
        # ... existing code ...
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

### 4. Improve Timestamp Generation

Implement a more accurate timestamp generation method:

```python
def generate_timestamps(self, text, synthesized_audio, sample_rate=16000):
    """
    Generate more accurate word-level timestamps using a phoneme-based approach.
    This is a placeholder for a more sophisticated implementation.
    """
    # For a real implementation, consider using a forced alignment tool like:
    # - Montreal Forced Aligner
    # - Gentle
    # - DeepSpeech's alignment capabilities
    
    words = text.split()
    num_words = len(words)
    duration = len(synthesized_audio) / sample_rate
    
    # Simple implementation (improved version)
    # Assume words with more characters take proportionally more time
    total_chars = sum(len(word) for word in words)
    timestamps = []
    current_time = 0
    
    for word in words:
        word_duration = (len(word) / total_chars) * duration
        timestamps.append((word, current_time, current_time + word_duration))
        current_time += word_duration
    
    return timestamps
```

### 5. Add CORS Support

Add CORS middleware to allow cross-origin requests:

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
```

### 6. Add Basic Security

Implement basic API key authentication:

```python
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, Depends, HTTPException

API_KEY = "your-api-key"  # In production, use environment variables
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate API key")
    return api_key

@app.post("/get_tts")
async def get_tts(request_data: TTSRequest, api_key: str = Depends(get_api_key)):
    # ... existing code ...
```

### 7. Add Input Validation

Enhance input validation for the API parameters:

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
            raise ValueError(f"Reference audio file not found: {v}")
        return v
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v
```

## Implementation Priority

1. Fix Initialization Issue (Critical)
2. Fix Return Type Issue for Timestamps API (Critical)
3. Improve Error Handling (High)
4. Add CORS Support (Medium)
5. Add Input Validation (Medium)
6. Improve Timestamp Generation (Medium)
7. Add Basic Security (Low, depending on deployment context)

## Conclusion

The current API implementation has several issues that need to be addressed to ensure it works correctly and provides the functionality described in the documentation. The proposed modifications will improve the reliability, security, and usability of the API.

Once these changes are implemented, additional testing should be performed to ensure the API works as expected in various scenarios, including edge cases and error conditions.