from transformers import pipeline
from home.models import Comment

# 감정분석 파이프라인 초기화 (영어 기반이라 한글은 정확도 낮을 수 있음)
sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_comments():
    comments = Comment.objects.filter(sentiment="")  # 분석 안 된 것만 처리
    for comment in comments:
        result = sentiment_analyzer(comment.content[:512])[0]  # 512자 이하만 분석
        label = result['label'].lower()

        if label == "positive":
            comment.sentiment = "긍정"
        elif label == "negative":
            comment.sentiment = "부정"
        else:
            comment.sentiment = "중립"

        comment.save()
        print(f"분석 완료: {comment.content[:30]}... -> {comment.sentiment}")
