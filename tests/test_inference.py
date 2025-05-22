import unittest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We'll test the Inference class methods that don't require the actual models
class TestInference(unittest.TestCase):
    
    @patch('inference.inference.Processor')
    @patch('inference.inference.clean_text_inf_normed_text')
    @patch('inference.inference.InferenceLlamaHf')
    def test_inference_init(self, mock_llama, mock_clean_text, mock_processor):
        """Test the Inference class initialization"""
        from inference.inference import Inference
        
        # Mock the processor
        mock_processor_instance = MagicMock()
        mock_processor.return_value = mock_processor_instance
        
        # Mock the LLM
        mock_llama_instance = MagicMock()
        mock_llama.return_value = mock_llama_instance
        
        # Initialize the Inference class
        inference = Inference(
            model_type="base",
            model_path="/path/to/model",
            ref_wav_path="test.wav",
            prompt_text="This is a prompt",
            enable_vllm_acc=False
        )
        
        # Check that the processor was initialized correctly
        mock_processor.assert_called_once_with(sovits_path="/path/to/model/sovits.pth")
        mock_processor_instance.generate_audio_token.assert_called_once_with("test.wav")
        
        # Check that the text cleaner was called
        mock_clean_text.assert_called_once_with("This is a prompt", 'en', 'v1')
        
        # Check that the LLM was initialized correctly
        mock_llama.assert_called_once_with("/path/to/model", "base")
        
        # Check that the model type was set correctly
        self.assertEqual(inference.model_type, "base")
    
    def test_create_prompt_base(self):
        """Test the _create_prompt method with base model type"""
        from inference.inference import Inference
        
        # Mock the Inference class
        inference = MagicMock(spec=Inference)
        inference.model_type = "base"
        
        # Call the actual method
        result = Inference._create_prompt(
            inference,
            prompt_text="This is a prompt",
            text="This is the text",
            audio_tokens="<|audio_token_1|>"
        )
        
        # Check the result
        expected = " This is a prompt This is the text <|audio_token_1|>"
        self.assertEqual(result, expected)
    
    def test_create_prompt_sft(self):
        """Test the _create_prompt method with sft model type"""
        from inference.inference import Inference
        
        # Mock the Inference class
        inference = MagicMock(spec=Inference)
        inference.model_type = "sft"
        
        # Call the actual method
        result = Inference._create_prompt(
            inference,
            prompt_text="This is a prompt",
            text="This is the text",
            audio_tokens="<|audio_token_1|>"
        )
        
        # Check the result
        expected = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n This is the text<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        self.assertEqual(result, expected)
    
    def test_create_prompt_invalid(self):
        """Test the _create_prompt method with invalid model type"""
        from inference.inference import Inference
        
        # Mock the Inference class
        inference = MagicMock(spec=Inference)
        inference.model_type = "invalid"
        
        # Call the actual method and check that it raises an error
        with self.assertRaises(ValueError):
            Inference._create_prompt(
                inference,
                prompt_text="This is a prompt",
                text="This is the text",
                audio_tokens="<|audio_token_1|>"
            )
    
    @patch('inference.inference.get_normed_text')
    @patch('inference.inference.clean_and_split_text')
    @patch('inference.inference.merge_sentences_minimum_n')
    def test_process_prompt(self, mock_merge, mock_split, mock_norm):
        """Test the _process_prompt method"""
        from inference.inference import Inference
        
        # Mock the Inference class
        inference = MagicMock(spec=Inference)
        inference._create_prompt.return_value = "prompt"
        inference.sovits_processor.generate_audio_token.return_value = "<|audio_token_1|>"
        
        # Mock the text processing functions
        mock_norm.side_effect = ["normed_prompt", "normed_text"]
        mock_split.return_value = ["sentence1", "sentence2"]
        mock_merge.return_value = ["merged_sentence"]
        
        # Call the actual method
        result = Inference._process_prompt(
            inference,
            ref_wav_path="test.wav",
            prompt_text="This is a prompt",
            text="This is the text"
        )
        
        # Check the result
        inference.sovits_processor.generate_audio_token.assert_called_once_with("test.wav")
        mock_norm.assert_any_call("This is a prompt", 'en', 'v1')
        mock_norm.assert_any_call("This is the text", 'en', 'v1')
        mock_split.assert_called_once_with("normed_text")
        mock_merge.assert_called_once_with(["sentence1", "sentence2"], 12)  # 12 is MIN_SENTENCE_LENGTH
        inference._create_prompt.assert_called_once_with("normed_prompt", "merged_sentence", "<|audio_token_1|>")
        self.assertEqual(result, ["prompt"])
    
    def test_generate_timestamps(self):
        """Test the generate_timestamps method"""
        from inference.inference import Inference
        
        # Mock the Inference class
        inference = MagicMock(spec=Inference)
        
        # Call the actual method
        result = Inference.generate_timestamps(
            inference,
            text="This is a test",
            synthesized_audio=bytes([0] * 32000)  # 2 seconds of audio at 16kHz
        )
        
        # Check the result
        expected = [
            ("This", 0.0, 0.5),
            ("is", 0.5, 1.0),
            ("a", 1.0, 1.5),
            ("test", 1.5, 2.0)
        ]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()