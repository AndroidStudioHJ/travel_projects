from django.shortcuts import render
from django.views.generic import TemplateView
from .utils import build_search_url, fetch_html, parse_posts, split_by_sentiment
from .models import BlogPost

# Create your views here.

class SentimentAnalysisView(TemplateView):
    template_name = 'blog/sentiment_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '')
        
        if query:
            url = build_search_url(query)
            html = fetch_html(url)
            posts = parse_posts(html)
            positive, negative, neutral = split_by_sentiment(posts)
            
            # 결과를 데이터베이스에 저장
            for post in posts:
                sentiment = 'positive' if post in positive else 'negative' if post in negative else 'neutral'
                BlogPost.objects.create(
                    title=post['title'],
                    link=post['link'],
                    summary=post['summary'],
                    date=post['date'],
                    sentiment=sentiment
                )
            
            context.update({
                'query': query,
                'total_count': len(posts),
                'positive_count': len(positive),
                'negative_count': len(negative),
                'neutral_count': len(neutral),
                'positive_posts': positive[:5],
                'negative_posts': negative[:5],
                'neutral_posts': neutral[:5] if not positive and not negative else [],
            })
        
        return context
