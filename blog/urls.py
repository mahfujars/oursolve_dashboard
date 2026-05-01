from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostListView.as_view(), name='api-post-list'),
    path('posts/<slug:slug>/', views.PostDetailView.as_view(), name='api-post-detail'),
    path('categories/', views.CategoryListView.as_view(), name='api-category-list'),
    path('tools/', views.ToolListView.as_view(), name='api-tool-list'),
    path('settings/', views.SiteSettingsView.as_view(), name='api-site-settings'),
]
