from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('create/', views.project_create, name='create'),
    path('<int:pk>/', views.project_detail, name='detail'),
    path('<int:pk>/donate/', views.project_donate, name='donate'),
    path('<int:pk>/comment/', views.project_comment, name='comment'),
    path('<int:pk>/comment/<int:comment_id>/reply/', views.comment_reply, name='comment_reply'),
    path('<int:pk>/rate/', views.project_rate, name='rate'),
    path('<int:pk>/cancel/', views.project_cancel, name='cancel'),
    path('<int:pk>/report/', views.project_report, name='report'),
    path('comment/<int:comment_id>/report/', views.comment_report, name='comment_report'),
    path('search/', views.search, name='search'),
    path('category/<int:pk>/', views.category_projects, name='category'),
]