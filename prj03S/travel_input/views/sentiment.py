from django.shortcuts import redirect

def sentiment_search(request):
    """
    네이버 블로그 검색 뷰 - sentiment_analysis로 리다이렉트
    """
    return redirect('home:sentiment_analysis') 