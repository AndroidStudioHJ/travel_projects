def cities(request):
    from .models import City
    return {
        'cities': City.objects.filter(is_active=True).order_by('order', 'name')
    }