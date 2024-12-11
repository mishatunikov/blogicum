from django.urls import path, include

from blog import views

app_name = 'blog'


post_endpoints = [
    path('create/', views.PostCreateView.as_view(), name='create_post'),

    path('<int:post_id>/', views.detail_post, name='post_detail'),

    path('<int:post_id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),

    path('<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),

    path('<int:post_id>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),

    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),

    path('<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment')
]

profile_endpoint = [
    path('edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('<slug:username>/', views.ProfileListView.as_view(), name='profile')
]

category_endpoint = [
    path('<slug:category_slug>/', views.CategoryPostsListView.as_view(),
         name='category_posts'),
]


urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('category/', include(category_endpoint)),
    path('posts/', include(post_endpoints)),
    path('profile/', include(profile_endpoint)),
]
