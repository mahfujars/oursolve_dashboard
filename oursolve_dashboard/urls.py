from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customise the admin site header/title
admin.site.site_header = 'Oursolve Dashboard'
admin.site.site_title = 'Oursolve Admin'
admin.site.index_title = 'Content Management'

urlpatterns = [
    path('api/', include('blog.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', admin.site.urls),
]

# Serve media files through Django in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
