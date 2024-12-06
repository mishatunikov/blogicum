from django.urls import path
from django.views.generic import TemplateView, ListView

from blog import views
from .models import Post

app_name = 'blog'


urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/',
         views.category_posts,
         name='category_posts'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('profile/<slug:username>/', views.profile, name='profile'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
]
