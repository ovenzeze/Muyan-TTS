import sys
import os
from sovits.process import Processor
from sovits.utils import *
from fastapi.responses import StreamingResponse
import re, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
MIN_SENTENCE_LENGTH = 12


class Inference():
    def __init__(self, 
                 model_type, model_path, ref_wav_path="assets/Claire.wav", 
                 prompt_text="Although the campaign was not a complete success, it did provide Napoleon with valuable experience and prestige.",
                 enable_vllm_acc=False):
        # ref_wav_path and prompt_text are used here only to initialize sovits (otherwise the first run would be slow)
        # new ref_wav_path and prompt_text can still be specified later using call_tts
        self.sovits_processor = Processor(sovits_path=os.path.join(model_path, "sovits.pth"))
        self.sovits_processor.generate_audio_token(ref_wav_path)
        clean_text_inf_normed_text(prompt_text, 'en', 'v1') 
        logging.info("init vits finish")

        # Used to distinguish between API mode and regular TTS mode
        self.enable_vllm_acc = enable_vllm_acc
        if self.enable_vllm_acc == True:
            from inference.inference_llama import InferenceLlamaVllm
            self.llama = InferenceLlamaVllm(model_path, model_type)
        else:
            from inference.inference_llama import InferenceLlamaHf
            self.llama = InferenceLlamaHf(model_path, model_type)
            
        self.model_type = model_type
        
    def _create_prompt(self, prompt_text, text, audio_tokens):
        if self.model_type == "base":
            return " " + prompt_text.strip() + " " + text.strip() + " " + audio_tokens.strip()
            
        elif self.model_type == "sft":
            return "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"\
                    + " "\
                    + text.strip()\
                    + "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

        else:
            raise ValueError(f"Error model type: {self.model_type}")    
        
    def _process_prompt(self, ref_wav_path, prompt_text, text):
        audio_tokens = self.sovits_processor.generate_audio_token(ref_wav_path)
        prompt_text = get_normed_text(prompt_text, 'en', 'v1')
        text = get_normed_text(text, 'en', 'v1')
        
        # Used to handle overly long sentences by splitting them into multiple shorter sentences
        batch_texts = clean_and_split_text(text)
        batch_texts = merge_sentences_minimum_n(batch_texts, MIN_SENTENCE_LENGTH) 
        
        batch_prompts = []
        for i in range(len(batch_texts)):
            batch_prompts.append(self._create_prompt(prompt_text, batch_texts[i], audio_tokens))
            
        return batch_prompts
        
    async def generate(self, ref_wav_path, prompt_text, text, temperature=1.0, 
                 repetition_penalty=1.0, cut_punc=None,
                 speed=1.0, scaling_factor=1.0):
        try:
            logging.info(f"Generating TTS for text: {text}")
            batch_prompts = self._process_prompt(ref_wav_path, prompt_text, text)
            
            results = await self.llama.cal_tts(batch_prompts, temperature, repetition_penalty)
            pred_semantic = "".join(results)
            wavs = self.sovits_processor.handle(pred_semantic, ref_wav_path, prompt_text, 'en', text, 'en', cut_punc, speed, [], scaling_factor)
            logging.info("TTS generation successful")
            return wavs
        except Exception as e:
            logging.error(f"Error during TTS generation: {str(e)}")
            raise

    def init_vits(self, ref_wav_path, prompt_text):
        logging.info("init vits...")
        self.sovits_processor.generate_audio_token(ref_wav_path)
        clean_text_inf_normed_text(prompt_text, 'en', 'v1') 
        logging.info("init vits finish")

    def generate_timestamps(self, text, synthesized_audio, sample_rate=16000):
        """
        使用基于字符的持续时间估计生成更准确的词级时间戳。
        
        参数:
            text (str): 输入文本
            synthesized_audio (bytes): 合成的音频数据
            sample_rate (int): 音频采样率
            
        返回:
            list: 包含词级时间戳的列表
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

    async def generate_with_timestamps(self, ref_wav_path, prompt_text, text, temperature=1.0, 
                 repetition_penalty=1.0, cut_punc=None,
                 speed=1.0, scaling_factor=1.0):
        try:
            logging.info(f"Generating TTS with timestamps for text: {text}")
            batch_prompts = self._process_prompt(ref_wav_path, prompt_text, text)
            
            results = await self.llama.cal_tts(batch_prompts, temperature, repetition_penalty)
            pred_semantic = "".join(results)
            wavs = self.sovits_processor.handle(pred_semantic, ref_wav_path, prompt_text, 'en', text, 'en', cut_punc, speed, [], scaling_factor)
            synthesized_audio = b''.join([chunk for chunk in wavs])
            timestamps = self.generate_timestamps(text, synthesized_audio)
            logging.info("TTS with timestamps generation successful")
            return synthesized_audio, timestamps
        except Exception as e:
            logging.error(f"Error during TTS with timestamps generation: {str(e)}")
            raise
