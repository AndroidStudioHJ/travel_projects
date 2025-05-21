import openai
from openai import OpenAI
from django.conf import settings
from django.shortcuts import render
from .forms import PetTravelForm

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def home(request):
    return render(request, 'main/home.html')

def recommend_travel(request):
    recommendation = None
    food_recommendation = None
    error_message = None

    if request.method == 'POST':
        form = PetTravelForm(request.POST)
        if form.is_valid():
            pet_type = form.cleaned_data['pet_type']
            activity_level = form.cleaned_data['activity_level']
            season = form.cleaned_data['season']

            # 여행지 추천 프롬프트
            travel_prompt = (
                f"반려동물 종류: {pet_type}\n"
                f"활동 수준: {activity_level}\n"
                f"여행 시기: {season}\n"
                "위 조건을 기반으로 추천 여행지를 한국어로 1~2문장으로 추천해줘."
            )

            try:
                # 여행지 추천
                travel_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "당신은 친절한 반려동물 여행 가이드입니다."},
                        {"role": "user", "content": travel_prompt}
                    ],
                    max_tokens=100,
                    temperature=0.7,
                )
                recommendation = travel_response.choices[0].message.content.strip()

                # 먹거리 추천 프롬프트에 여행지 포함 (반려동물로 변경)
                food_prompt = (
                    f"반려동물 종류: {pet_type}\n"
                    f"추천 여행지: {recommendation}\n"
                    f"이 여행지에서 반려동물도 안전하게 먹을 수 있는 먹거리 중 추천할 만한 것을 1~2문장으로 한국어로 알려줘."
                )

                # 먹거리 추천
                food_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "당신은 친절한 반려동물 영양사입니다."},
                        {"role": "user", "content": food_prompt}
                    ],
                    max_tokens=100,
                    temperature=0.7,
                )
                food_recommendation = food_response.choices[0].message.content.strip()

            except Exception as e:
                error_message = f"추천 오류: {str(e)}"
    else:
        form = PetTravelForm()

    return render(request, 'main/recommend.html', {
        'form': form,
        'recommendation': recommendation,
        'food_recommendation': food_recommendation,
        'error_message': error_message
    })
