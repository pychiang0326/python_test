import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

os.environ["BITSANDBYTES_NOWELCOME"] = "1"
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

# 显存优化配置（2GB专用）
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True  # 二次量化进一步压缩
)

# 加载微软Phi-3-mini（更适合低显存）
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/phi-3-mini-4k-instruct",
    device_map="auto",
    quantization_config=bnb_config,
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-3-mini-4k-instruct")

# 测试生成（添加流式输出避免显存溢出）
input_text = "用Python写一个快速排序算法"
inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).to(model.device)

# 流式生成节省显存
from transformers import TextStreamer
streamer = TextStreamer(tokenizer)
outputs = model.generate(**inputs, max_new_tokens=200, streamer=streamer)