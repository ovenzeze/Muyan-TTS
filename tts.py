from inference.inference import Inference
import asyncio
import os
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main(model_type, model_path):
    try:
        tts = Inference(model_type, model_path, enable_vllm_acc=False)
        logging.info("TTS实例化成功")
        
        wavs = await tts.generate(
            ref_wav_path="assets/Claire.wav",
            prompt_text="Although the campaign was not a complete success, it did provide Napoleon with valuable experience and prestige.",
            text="Welcome to the captivating world of podcasts, let's embark on this exciting journey together."
        )
        output_path = "logs/tts.wav"
        os.makedirs("logs", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(next(wavs))  
        logging.info(f"语音生成成功，保存在 {output_path}")
    except Exception as e:
        logging.error(f"TTS生成过程中出错: {str(e)}")
        raise

if __name__ == "__main__":
    model_type = "base"
    cnhubert_model_path = "pretrained_models/chinese-hubert-base"
    
    try:
        if model_type == "base":
            model_path = "pretrained_models/Muyan-TTS"
        elif model_type == "sft":
            model_path = "pretrained_models/Muyan-TTS-SFT"
        else:
            logging.error(f"无效的模型类型: '{model_type}'。请指定 'base' 或 'sft'。")
            raise ValueError(f"Invalid model type: '{model_type}'. Please specify either 'base' or 'sft'.")
        logging.info(f"模型成功下载到 {model_path}")
    except Exception as e:
        logging.error(f"下载模型时出错: {str(e)}")
        raise
    
    asyncio.run(main(model_type, model_path))
