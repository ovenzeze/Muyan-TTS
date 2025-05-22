import unittest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestTTS(unittest.TestCase):
    
    @patch('tts.Inference')
    @patch('tts.logging')
    @patch('tts.os.makedirs')
    async def test_main_function(self, mock_makedirs, mock_logging, mock_inference):
        """Test the main function in tts.py"""
        from tts import main
        
        # Mock the Inference class
        mock_inference_instance = MagicMock()
        mock_inference.return_value = mock_inference_instance
        
        # Mock the generate method
        mock_inference_instance.generate = AsyncMock()
        mock_inference_instance.generate.return_value = [b'audio_data']
        
        # Call the main function
        await main("base", "/path/to/model")
        
        # Check that the Inference class was initialized correctly
        mock_inference.assert_called_once_with("base", "/path/to/model", enable_vllm_acc=False)
        
        # Check that the generate method was called with the correct parameters
        mock_inference_instance.generate.assert_called_once_with(
            ref_wav_path="assets/Claire.wav",
            prompt_text="Although the campaign was not a complete success, it did provide Napoleon with valuable experience and prestige.",
            text="Welcome to the captivating world of podcasts, let's embark on this exciting journey together."
        )
        
        # Check that the logs directory was created
        mock_makedirs.assert_called_once_with("logs", exist_ok=True)
        
        # Check that the success message was logged
        mock_logging.info.assert_any_call("TTS实例化成功")
        mock_logging.info.assert_any_call("语音生成成功，保存在 logs/tts.wav")
    
    @patch('tts.asyncio.run')
    @patch('tts.logging')
    def test_main_script(self, mock_logging, mock_asyncio_run):
        """Test the main script execution in tts.py"""
        # We need to import the module in a way that doesn't execute the main script
        import importlib.util
        spec = importlib.util.spec_from_file_location("tts_module", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tts.py"))
        tts_module = importlib.util.module_from_spec(spec)
        
        # Mock the asyncio.run function
        mock_asyncio_run.return_value = None
        
        # Execute the module
        spec.loader.exec_module(tts_module)
        
        # Check that asyncio.run was called with the main function
        mock_asyncio_run.assert_called_once()
        
        # Check that the model paths were set correctly
        self.assertEqual(tts_module.model_type, "base")
        self.assertEqual(tts_module.cnhubert_model_path, "pretrained_models/chinese-hubert-base")
        
        # Check that the model path was set correctly
        mock_logging.info.assert_any_call("模型成功下载到 pretrained_models/Muyan-TTS")


if __name__ == "__main__":
    unittest.main()