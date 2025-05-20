from .models import City

def cities(request):
    return {
        'cities': City.objects.filter(is_active=True).order_by('order', 'name')
    } 