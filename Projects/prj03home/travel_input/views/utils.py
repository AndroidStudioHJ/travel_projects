import os
import openai

def summarize_text_with_openai(text):
    """
    OpenAI API를 사용해 입력 텍스트를 한국어로 3줄로 요약합니다.
    환경변수 OPENAI_API_KEY 필요.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return 'OpenAI API 키가 설정되어 있지 않습니다.'
    openai.api_key = api_key
    prompt = (
        "아래 내용을 한국어로 3줄로 요약해줘. "
        "각 줄은 줄바꿈(\\n)으로 구분해서 출력해줘. "
        "반드시 3줄로 만들어줘.\n"
        f"{text}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"요약 실패: {e}" 