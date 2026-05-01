from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import BlogPost, Category, Tool, SiteSettings
from .serializers import (
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    CategorySerializer,
    ToolSerializer,
    SiteSettingsSerializer,
)


class PostListView(generics.ListAPIView):
    """
    GET /api/posts/
    Returns paginated list of published posts, newest first.

    Query params:
      ?category=<slug>   filter by category
      ?tag=<tag>         filter posts containing this tag
      ?search=<q>        search title and excerpt
    """
    serializer_class = BlogPostListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = (
            BlogPost.objects
            .filter(status=BlogPost.STATUS_PUBLISHED)
            .select_related('category')
            .order_by('-published_at')
        )

        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)

        tag = self.request.query_params.get('tag')
        if tag:
            qs = qs.filter(tags__icontains=tag)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(excerpt__icontains=search)

        return qs


class PostDetailView(APIView):
    """
    GET /api/posts/<slug>/
    Returns a single published post by slug.
    """
    permission_classes = [AllowAny]

    def get(self, request, slug):
        post = get_object_or_404(
            BlogPost,
            slug=slug,
            status=BlogPost.STATUS_PUBLISHED,
        )
        serializer = BlogPostDetailSerializer(post)
        return Response(serializer.data)


class ToolListView(generics.ListAPIView):
    """
    GET /api/tools/
    Returns all active tools ordered by their display order.
    """
    serializer_class = ToolSerializer
    permission_classes = [AllowAny]
    pagination_class = None  # return all tools without pagination

    def get_queryset(self):
        return Tool.objects.filter(is_active=True).order_by('order', 'name')


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Category.objects.all().order_by('name')


class SiteSettingsView(APIView):
    """
    GET /api/settings/
    Returns site-wide settings for the frontend.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        settings = SiteSettings.get()
        serializer = SiteSettingsSerializer(settings)
        return Response(serializer.data)
