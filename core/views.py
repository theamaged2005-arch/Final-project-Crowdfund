from django.db.models import Avg
from django.shortcuts import render
from django.utils import timezone

from projects.models import Project, Category


def home(request):
    now = timezone.now()

    running_projects = Project.objects.filter(
        start_time__lte=now, end_time__gte=now, is_cancelled=False
    )

    top_rated = (
        running_projects
        .annotate(avg_rating=Avg('ratings__stars'))
        .filter(avg_rating__isnull=False)
        .order_by('-avg_rating')[:5]
    )

    latest_projects = Project.objects.filter(is_cancelled=False).order_by('-created_at')[:5]
    featured_projects = Project.objects.filter(is_featured=True, is_cancelled=False).order_by('-created_at')[:5]
    categories = Category.objects.all()

    context = {
        'top_rated': top_rated,
        'latest_projects': latest_projects,
        'featured_projects': featured_projects,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)