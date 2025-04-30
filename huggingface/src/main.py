from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sentiment_analysis():
    try:
        # 初始化情感分析pipeline
        logger.info("正在初始化情感分析模型...")
        model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
        
        # 测试文本
        test_texts = [
            "I love this movie!",
            "This is terrible.",
            "I'm not sure how I feel about this.",
            "Nous sommes très heureux de vous présenter la bibliothèque 🤗 Transformers."
        ]
        
        logger.info("开始情感分析...")
        results = classifier(test_texts)
        
        # 打印结果
        for text, result in zip(test_texts, results):
            print(f"文本: {text}")
            print(f"情感: {result['label']}")
            print(f"置信度: {result['score']:.4f}")
            print("-" * 50)
            
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        raise

def main():
    passspeech_recognizer = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h")

if __name__ == "__main__":
    sentiment_analysis()