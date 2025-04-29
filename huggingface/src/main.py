from transformers import pipeline
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # 初始化情感分析pipeline
        logger.info("正在初始化情感分析模型...")
        classifier = pipeline("sentiment-analysis")
        
        # 测试文本
        test_texts = [
            "I love this movie!",
            "This is terrible.",
            "I'm not sure how I feel about this."
        ]
        
        # 进行情感分析
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

if __name__ == "__main__":
    main()