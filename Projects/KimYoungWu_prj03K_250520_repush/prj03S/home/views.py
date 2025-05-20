from django.shortcuts import render, redirect
from .models import Destination, Comment
from .utils import analyze_sentiment, recommend_destinations
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')  # 홈 페이지 템플릿 렌더링

@login_required
def write_comment(request, dest_id):
    destination = Destination.objects.get(id=dest_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        sentiment = analyze_sentiment(content)

        Comment.objects.create(
            user=request.user,
            destination=destination,
            content=content,
            sentiment=sentiment,
        )
        return redirect('destination_detail', dest_id=dest_id)

    return render(request, 'home/write_comment.html', {'destination': destination})

@login_required
def recommend(request):
    user_comments = Comment.objects.filter(user=request.user)
    all_destinations = Destination.objects.all()
    recommended_list = recommend_destinations(user_comments, all_destinations)

    return render(request, 'home/recommend.html', {'recommendations': recommended_list})
