from rest_framework import serializers
from .models import BlogPost, Category, Tool, SiteSettings


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class BlogPostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for post listings — no full content."""
    category = CategorySerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    meta_title = serializers.SerializerMethodField()
    meta_description = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image_url',
            'category', 'tags', 'author',
            'published_at', 'updated_at',
            'meta_title', 'meta_description',
        ]

    def get_tags(self, obj):
        return obj.get_tags_list()

    def get_meta_title(self, obj):
        return obj.effective_meta_title

    def get_meta_description(self, obj):
        return obj.meta_description or obj.effective_excerpt[:160]

    def get_excerpt(self, obj):
        return obj.effective_excerpt


class BlogPostDetailSerializer(BlogPostListSerializer):
    """Full serializer for a single post — includes HTML content."""

    class Meta(BlogPostListSerializer.Meta):
        fields = BlogPostListSerializer.Meta.fields + ['content']


class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'slug', 'description', 'icon', 'url', 'order']


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['site_name', 'site_description', 'google_analytics_id', 'footer_text']
