import re

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    content = RichTextUploadingField()
    excerpt = models.TextField(
        blank=True,
        help_text='Short summary shown in post listings. Leave blank to auto-generate from content.'
    )
    featured_image_url = models.URLField(
        blank=True,
        help_text='Full URL of the featured image (e.g. https://...)'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated tags, e.g. "python, django, tutorial"'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    author = models.CharField(max_length=100, default='Oursolve Team')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # SEO
    meta_title = models.CharField(
        max_length=300,
        blank=True,
        help_text='Override the default title for search engines (max 60 chars recommended).'
    )
    meta_description = models.CharField(
        max_length=500,
        blank=True,
        help_text='Summary for search engines (max 160 chars recommended).'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug from title
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug

        # Set published_at when first published
        if self.status == self.STATUS_PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_tags_list(self):
        """Return tags as a clean list."""
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def effective_meta_title(self):
        return self.meta_title or self.title

    @property
    def effective_excerpt(self):
        if self.excerpt:
            return self.excerpt
        text = re.sub(r'<[^>]+>', '', self.content)
        return text[:200].strip() + ('…' if len(text) > 200 else '')


class Tool(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    icon = models.CharField(
        max_length=10,
        blank=True,
        help_text='Emoji icon, e.g. 📱'
    )
    url = models.CharField(
        max_length=200,
        help_text='Relative URL path, e.g. /tools/qr-generator/'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers appear first.'
    )

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SiteSettings(models.Model):
    """Singleton model — only one row should ever exist."""

    site_name = models.CharField(max_length=200, default='Oursolve')
    site_description = models.TextField(
        default='Free online tools for everyday tasks.',
        help_text='Used in the site-wide meta description.'
    )
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text='Google Analytics measurement ID, e.g. G-XXXXXXXXXX'
    )
    footer_text = models.TextField(
        blank=True,
        help_text='HTML allowed. Shown in the site footer.'
    )

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def clean(self):
        from django.core.exceptions import ValidationError
        if SiteSettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError('Only one Site Settings instance is allowed. Edit the existing one.')

    @classmethod
    def get(cls):
        """Return the singleton instance, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
