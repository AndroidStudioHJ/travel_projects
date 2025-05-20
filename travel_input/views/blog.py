from django.shortcuts import render
from ..sentiment import build_search_url, fetch_html, parse_posts, split_by_sentiment

def blog_search(request):
    query = request.GET.get("q", "")
    view_type = request.GET.get("view", "")  # 전체 보기 타입 (positive, negative, neutral)
    results = None

    if query:
        url = build_search_url(query)
        html = fetch_html(url)
        posts = parse_posts(html)
        positive, negative, neutral = split_by_sentiment(posts)

        # 전체 보기 타입에 따라 표시할 포스트 선택
        if view_type == "positive":
            display_posts = positive
        elif view_type == "negative":
            display_posts = negative
        elif view_type == "neutral":
            display_posts = neutral
        else:
            # 기본적으로 상위 5개씩만 표시
            display_posts = None
            pos_sel = positive[:5] if positive else neutral[:5]
            neg_sel = negative[:5] if negative else neutral[:5]
            neu_sel = neutral[:5]

        results = {
            "total": len(posts),
            "positive_count": len(positive),
            "negative_count": len(negative),
            "neutral_count": len(neutral),
            "positive_list": pos_sel if not view_type else positive,
            "negative_list": neg_sel if not view_type else negative,
            "neutral_list": neu_sel if not view_type else neutral,
            "all_posts": posts,
            "positive_posts": positive,
            "negative_posts": negative,
            "neutral_posts": neutral,
            "view_type": view_type,  # 현재 보기 타입
        }

    return render(request, "travel_input/blog_search.html", {
        "query": query,
        "results": results
    }) 