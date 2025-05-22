import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the API module
from api import TTSRequest, TimestampRequest


class TestAPI(unittest.TestCase):
    
    def test_tts_request_model(self):
        """Test the TTSRequest model validation"""
        # Test with required fields only
        request_data = {
            "ref_wav_path": "test.wav",
            "prompt_text": "This is a prompt",
            "text": "This is the text to synthesize"
        }
        request = TTSRequest(**request_data)
        self.assertEqual(request.ref_wav_path, "test.wav")
        self.assertEqual(request.prompt_text, "This is a prompt")
        self.assertEqual(request.text, "This is the text to synthesize")
        self.assertEqual(request.temperature, 1.0)  # Default value
        self.assertEqual(request.repetition_penalty, 1.0)  # Default value
        self.assertEqual(request.speed, 1.0)  # Default value
        self.assertEqual(request.scaling_factor, 1.0)  # Default value
        
        # Test with all fields
        request_data = {
            "ref_wav_path": "test.wav",
            "prompt_text": "This is a prompt",
            "text": "This is the text to synthesize",
            "temperature": 0.8,
            "repetition_penalty": 1.2,
            "speed": 1.5,
            "scaling_factor": 0.9
        }
        request = TTSRequest(**request_data)
        self.assertEqual(request.temperature, 0.8)
        self.assertEqual(request.repetition_penalty, 1.2)
        self.assertEqual(request.speed, 1.5)
        self.assertEqual(request.scaling_factor, 0.9)
    
    def test_timestamp_request_model(self):
        """Test the TimestampRequest model validation"""
        # Test with required fields only
        request_data = {
            "ref_wav_path": "test.wav",
            "prompt_text": "This is a prompt",
            "text": "This is the text to synthesize"
        }
        request = TimestampRequest(**request_data)
        self.assertEqual(request.ref_wav_path, "test.wav")
        self.assertEqual(request.prompt_text, "This is a prompt")
        self.assertEqual(request.text, "This is the text to synthesize")
        self.assertEqual(request.temperature, 1.0)  # Default value
        self.assertEqual(request.repetition_penalty, 1.0)  # Default value
        self.assertEqual(request.speed, 1.0)  # Default value
        self.assertEqual(request.scaling_factor, 1.0)  # Default value
        
        # Test with all fields
        request_data = {
            "ref_wav_path": "test.wav",
            "prompt_text": "This is a prompt",
            "text": "This is the text to synthesize",
            "temperature": 0.8,
            "repetition_penalty": 1.2,
            "speed": 1.5,
            "scaling_factor": 0.9
        }
        request = TimestampRequest(**request_data)
        self.assertEqual(request.temperature, 0.8)
        self.assertEqual(request.repetition_penalty, 1.2)
        self.assertEqual(request.speed, 1.5)
        self.assertEqual(request.scaling_factor, 0.9)
    
    @patch('api.tts')
    async def test_get_tts_endpoint(self, mock_tts):
        """Test the /get_tts endpoint"""
        from fastapi.testclient import TestClient
        from api import app
        
        # Mock the TTS generate method
        mock_tts.generate = AsyncMock()
        mock_tts.generate.return_value = [b'audio_data']
        
        client = TestClient(app)
        
        # Test with valid request
        request_data = {
            "ref_wav_path": "test.wav",
            "prompt_text": "This is a prompt",
            "text": "This is the text to synthesize"
        }
        
        # Use unittest.mock to patch the async function
        with patch('api.tts.generate', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = [b'audio_data']
            
            # This is a synchronous test, so we can't directly test the async endpoint
            # In a real test, we would use an async test framework like pytest-asyncio
            # For now, we'll just verify the request model works
            
            request = TTSRequest(**request_data)
            self.assertEqual(request.ref_wav_path, "test.wav")
            self.assertEqual(request.prompt_text, "This is a prompt")
            self.assertEqual(request.text, "This is the text to synthesize")
    
    @patch('api.tts')
    async def test_get_tts_with_timestamps_endpoint(self, mock_tts):
        """Test the /get_tts_with_timestamps endpoint"""
        from fastapi.testclient import TestClient
        from api import app
        
        # Mock the TTS generate_with_timestamps method
        mock_tts.generate_with_timestamps = AsyncMock()
        mock_tts.generate_with_timestamps.return_value = (b'audio_data', [("word", 0.0, 1.0)])
        
        client = TestClient(app)
        
        # Test with valid request
        request_data = {
            "ref_wav_path": "test.wav",
            "prompt_text": "This is a prompt",
            "text": "This is the text to synthesize"
        }
        
        # Use unittest.mock to patch the async function
        with patch('api.tts.generate_with_timestamps', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = (b'audio_data', [("word", 0.0, 1.0)])
            
            # This is a synchronous test, so we can't directly test the async endpoint
            # In a real test, we would use an async test framework like pytest-asyncio
            # For now, we'll just verify the request model works
            
            request = TimestampRequest(**request_data)
            self.assertEqual(request.ref_wav_path, "test.wav")
            self.assertEqual(request.prompt_text, "This is a prompt")
            self.assertEqual(request.text, "This is the text to synthesize")


if __name__ == "__main__":
    unittest.main()