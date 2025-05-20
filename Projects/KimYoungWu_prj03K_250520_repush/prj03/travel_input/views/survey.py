# travel_input/views/survey.py

from django.shortcuts import render, redirect
from travel_input.forms import TravelSurveyForm

def travel_survey(request):
    result = None
    if request.method == 'POST':
        form = TravelSurveyForm(request.POST)
        if form.is_valid():
            result = form.cleaned_data  # 여기에 AI 추천 로직 연결 가능

            # ✅ 결과를 포함하여 thank you 페이지로 이동
            return render(request, 'travel_input/ai_thank_you.html', {
                'form': form,
                'result': result
            })
    else:
        form = TravelSurveyForm()

    return render(request, 'travel_input/survey_form.html', {
        'form': form,
        'result': result
    })
