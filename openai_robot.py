from transformers import pipeline


def improved_chinese_chatbot():
    try:
        # 使用文本生成管道
        generator = pipeline(
            "text-generation",
            model="uer/gpt2-chinese-cluecorpussmall",
            tokenizer="uer/gpt2-chinese-cluecorpussmall",
            truncation=True  # 明确启用截断
        )

        # 更明确的提示
        prompt = "问题：请回复'测试成功'\n回答："

        result = generator(
            prompt,
            max_length=50,
            num_return_sequences=1,
            temperature=0.3,  # 降低随机性
            do_sample=True,
            pad_token_id=generator.tokenizer.eos_token_id
        )

        response = result[0]['generated_text']
        # 提取回答部分（去掉问题）
        if "回答：" in response:
            answer = response.split("回答：")[1].strip()
        else:
            answer = response.replace(prompt, "").strip()

        print("AI 回复:", answer)

    except Exception as e:
        print(f"错误: {e}")


improved_chinese_chatbot()