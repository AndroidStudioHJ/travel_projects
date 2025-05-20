# home/utils.py

from textblob import TextBlob

def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return '긍정'
    elif analysis.sentiment.polarity == 0:
        return '중립'
    else:
        return '부정'

def extract_keywords(text):
    # 간단 예시: 공백 단위 단어 리스트 반환 (실제론 NLP 패키지 활용 추천)
    return text.lower().split()

def recommend_destinations(user_comments, all_destinations):
    user_keywords = []
    for comment in user_comments:
        user_keywords.extend(extract_keywords(comment))

    recommended = []
    for dest in all_destinations:
        if any(k in user_keywords for k in dest.tags):
            recommended.append(dest)
    return recommended
