from django.db import migrations, models
import django.db.models.deletion
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='Oursolve', max_length=200)),
                ('site_description', models.TextField(default='Free online tools for everyday tasks.', help_text='Used in the site-wide meta description.')),
                ('google_analytics_id', models.CharField(blank=True, help_text='Google Analytics measurement ID, e.g. G-XXXXXXXXXX', max_length=50)),
                ('footer_text', models.TextField(blank=True, help_text='HTML allowed. Shown in the site footer.')),
            ],
            options={
                'verbose_name': 'Site Settings',
                'verbose_name_plural': 'Site Settings',
            },
        ),
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True)),
                ('description', models.TextField()),
                ('icon', models.CharField(blank=True, help_text='Emoji icon, e.g. 📱', max_length=10)),
                ('url', models.CharField(help_text='Relative URL path, e.g. /tools/qr-generator/', max_length=200)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('slug', models.SlugField(blank=True, max_length=320, unique=True)),
                ('content', ckeditor_uploader.fields.RichTextUploadingField()),
                ('excerpt', models.TextField(blank=True, help_text='Short summary shown in post listings. Leave blank to auto-generate from content.')),
                ('featured_image_url', models.URLField(blank=True, help_text='Full URL of the featured image (e.g. https://...)')),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags, e.g. "python, django, tutorial"', max_length=500)),
                ('status', models.CharField(
                    choices=[('draft', 'Draft'), ('published', 'Published')],
                    db_index=True,
                    default='draft',
                    max_length=20,
                )),
                ('author', models.CharField(default='Oursolve Team', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('meta_title', models.CharField(blank=True, help_text='Override the default title for search engines (max 60 chars recommended).', max_length=300)),
                ('meta_description', models.CharField(blank=True, help_text='Summary for search engines (max 160 chars recommended).', max_length=500)),
                ('category', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='posts',
                    to='blog.category',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
