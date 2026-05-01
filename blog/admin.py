from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse

from .models import BlogPost, Category, Tool, SiteSettings


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def post_count(self, obj):
        count = obj.posts.count()
        url = reverse('admin:blog_blogpost_changelist') + f'?category__id__exact={obj.pk}'
        return format_html('<a href="{}">{} post{}</a>', url, count, 's' if count != 1 else '')
    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'status_badge', 'category', 'author',
        'created_at', 'published_at', 'preview_link',
    ]
    list_filter = ['status', 'category', 'author', 'created_at']
    search_fields = ['title', 'excerpt', 'content', 'author', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    actions = ['publish_posts', 'unpublish_posts']
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    list_per_page = 25

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image_url'),
        }),
        ('Organisation', {
            'fields': ('category', 'tags', 'author'),
        }),
        ('Publishing', {
            'fields': ('status', 'created_at', 'updated_at', 'published_at'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'description': (
                'Customise how this post appears in Google. '
                'Title: aim for 50–60 chars · Description: aim for 120–160 chars.'
            ),
        }),
    )

    def status_badge(self, obj):
        if obj.status == BlogPost.STATUS_PUBLISHED:
            colour, label = '#22c55e', 'Published'
        else:
            colour, label = '#f97316', 'Draft'
        return format_html(
            '<span style="display:inline-block;padding:2px 10px;border-radius:20px;'
            'font-size:.78rem;font-weight:700;color:#fff;background:{}">{}</span>',
            colour, label,
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def preview_link(self, obj):
        if obj.status == BlogPost.STATUS_PUBLISHED and obj.slug:
            url = f'{settings.SITE_URL}/blog/{obj.slug}/'
            return format_html('<a href="{}" target="_blank" rel="noopener">↗ Preview</a>', url)
        return format_html('<span style="color:#94a3b8">—</span>')
    preview_link.short_description = 'Preview'

    @admin.action(description='Publish selected posts')
    def publish_posts(self, request, queryset):
        now = timezone.now()
        updated = 0
        for post in queryset.filter(status=BlogPost.STATUS_DRAFT):
            post.status = BlogPost.STATUS_PUBLISHED
            if post.published_at is None:
                post.published_at = now
            post.save(update_fields=['status', 'published_at'])
            updated += 1
        self.message_user(request, f'{updated} post(s) published.')

    @admin.action(description='Unpublish selected posts (revert to draft)')
    def unpublish_posts(self, request, queryset):
        updated = queryset.filter(status=BlogPost.STATUS_PUBLISHED).update(
            status=BlogPost.STATUS_DRAFT
        )
        self.message_user(request, f'{updated} post(s) moved back to draft.')


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['order', 'icon', 'name', 'url', 'active_badge']
    list_display_links = ['name']
    list_editable = ['order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#22c55e;font-weight:700">● Active</span>')
        return format_html('<span style="color:#94a3b8;font-weight:700">○ Inactive</span>')
    active_badge.short_description = 'Status'
    active_badge.admin_order_field = 'is_active'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('site_name', 'site_description', 'footer_text'),
        }),
        ('Analytics', {
            'fields': ('google_analytics_id',),
            'description': 'Google Analytics Measurement ID, e.g. G-XXXXXXXXXX.',
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
