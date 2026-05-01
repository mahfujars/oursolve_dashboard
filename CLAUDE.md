# oursolve_dashboard — Claude Context

## What Is This
Django 4.x REST API + admin dashboard for oursolve.com. Runs under `/dashboard/` on cPanel shared hosting via Passenger/WSGI. The static frontend (`oursolve_tools`) calls this API for blog posts and tools data.

- **Live URL:** https://oursolve.com/dashboard/
- **API base:** https://oursolve.com/dashboard/api/
- **GitHub:** https://github.com/mahfujars/oursolve_dashboard
- **Python:** 3.11 (virtualenv at `/home/oursolve/virtualenv/oursolve_dashboard/3.11/`)
- **Deploy target:** `/home/oursolve/oursolve_dashboard/`

---

## Hosting Constraints — CRITICAL

**No SSH or terminal access on cPanel.** All server-side operations must be done via:
- **File Manager** — browse/edit/delete files directly
- **Setup Python App** — pip install packages, set env vars, restart app
- **Git Version Control** — "Update from Remote" (hard reset to origin), "Deploy HEAD Commit" (runs `.cpanel.yml`)

Never suggest `ssh`, `git stash`, `git clean`, shell scripts run manually, or any CLI command requiring terminal. Always provide the cPanel equivalent.

---

## Deploy Workflow

1. Edit files locally
2. `git push` to GitHub (account: `mahfujars`)
3. cPanel **Git Version Control** → `oursolve_dashboard` → **Update from Remote** (pulls latest)
4. cPanel **Git Version Control** → **Deploy HEAD Commit** (runs `.cpanel.yml`: pip install → migrate → collectstatic → restart)
5. cPanel **Setup Python App** → **Restart** if `.cpanel.yml` changes were not enough

### Deploy Blocker: "Uncommitted Changes" Error
If Deploy HEAD Commit shows "uncommitted changes on server", the server's git working tree is dirty (migrate/collectstatic created files). Fix:
1. Click **Update from Remote** first (hard-resets to origin/main)
2. Then retry **Deploy HEAD Commit**

### `.cpanel.yml` Pipeline (exact order matters)
```yaml
deployment:
  tasks:
    - export DEPLOYPATH=/home/oursolve/oursolve_dashboard/
    - export PYTHON=/home/oursolve/virtualenv/oursolve_dashboard/3.11/bin/python3.11
    - /bin/cp -r * $DEPLOYPATH
    - mkdir -p $DEPLOYPATH/tmp $DEPLOYPATH/logs $DEPLOYPATH/media $DEPLOYPATH/staticfiles
    - mkdir -p /home/oursolve/public_html/dashboard
    - $PYTHON -m pip install -r $DEPLOYPATH/requirements.txt --quiet
    - $PYTHON $DEPLOYPATH/manage.py migrate --noinput
    - $PYTHON $DEPLOYPATH/manage.py collectstatic --noinput
    - touch $DEPLOYPATH/tmp/restart.txt
```
pip install MUST run before collectstatic. If a new package adds static files (e.g. jazzmin), they won't appear until both run in sequence.

---

## LiteSpeed Caching Problem

LiteSpeed (the cPanel web server) independently caches HTML responses from the Python app. Changes can take minutes–hours to appear even after restart.

**Fix applied:** `oursolve_dashboard/middleware.py` — `NoCacheMiddleware` sets:
- `Cache-Control: no-store, no-cache, must-revalidate, max-age=0`
- `X-LiteSpeed-Cache-Control: no-cache`

Also add to `/home/oursolve/public_html/dashboard/.htaccess` (server-side only, NOT in git):
```apache
<IfModule LiteSpeed>
CacheLookup off
</IfModule>
```

---

## URL Routing — Critical Rule

`path('', admin.site.urls)` **MUST be last** in `urlpatterns`. Admin's URL patterns match `^<app_label>/<model_name>/` and will silently catch API routes (e.g. `api/posts/` gets matched as app_label=api) if placed first.

Correct order in `urls.py`:
```python
urlpatterns = [
    path('api/', include('blog.urls')),          # API first
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', admin.site.urls),                   # admin LAST
]
```

---

## Key Settings

| Setting | Value | Why |
|---------|-------|-----|
| `FORCE_SCRIPT_NAME` | `/dashboard` | App runs at /dashboard/ subpath |
| `STATIC_URL` | `/dashboard/static/` | Matches subpath |
| `STATIC_ROOT` | `BASE_DIR / 'staticfiles'` | collectstatic target |
| `STATICFILES_STORAGE` | `whitenoise.storage.CompressedStaticFilesStorage` | NOT ManifestStaticFilesStorage — no terminal to run collectstatic manually |
| `DATABASE` | SQLite at `BASE_DIR / 'db.sqlite3'` | No MySQL setup needed |
| `SECRET_KEY` | env var `DJANGO_SECRET_KEY` | Set in cPanel Setup Python App → env vars |
| `DEBUG` | env var `DJANGO_DEBUG=True` for dev | False in production |

---

## Admin Theme — Jazzmin

`django-jazzmin` provides the WordPress-like admin interface. Key rules:
- `'jazzmin'` must be **first** in `INSTALLED_APPS`, before `'django.contrib.admin'`
- After any pip install that adds static files, run collectstatic (Deploy HEAD Commit handles this)
- Config lives in `JAZZMIN_SETTINGS` and `JAZZMIN_UI_TWEAKS` in `settings.py`
- Theme: dark purple sidebar, navbar-dark, horizontal_tabs changeform

---

## Blog Admin — SEO Editor

Custom admin template at `blog/templates/admin/blog/blogpost/change_form.html` adds:
- Live Google SERP preview box (shows title/URL/description as Google would)
- Character counters on `meta_title` (60 char limit) and `meta_description` (160 char limit)
- Color-coded counter badges: green (ok) → yellow (warn) → red (over)
- Fieldsets organized as horizontal tabs: Content / Organisation / Publishing / SEO

---

## Models

### BlogPost
| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField(300) | |
| `slug` | SlugField(320, unique) | Auto-generated from title, collision-safe |
| `content` | RichTextUploadingField | CKEditor with code snippet plugin |
| `excerpt` | TextField | Auto-generated from content if blank |
| `featured_image_url` | URLField | External URL, not uploaded file |
| `category` | FK → Category | SET_NULL on delete |
| `tags` | CharField(500) | Comma-separated string |
| `status` | CharField | `draft` / `published` |
| `author` | CharField | Default: "Oursolve Team" |
| `published_at` | DateTimeField | Auto-set on first publish |
| `meta_title` | CharField(300) | SEO override, 60 chars recommended |
| `meta_description` | CharField(500) | SEO, 160 chars recommended |

### Category
`name`, `slug` (auto from name)

### Tool
`name`, `slug`, `description`, `icon` (emoji), `url` (relative path), `is_active`, `order`

### SiteSettings
Singleton model. Use `SiteSettings.get()` classmethod to access. Fields: `site_name`, `site_description`, `google_analytics_id`, `footer_text`.

---

## API Endpoints

Base: `https://oursolve.com/dashboard/api/`

| Endpoint | Method | Returns |
|----------|--------|---------|
| `api/posts/` | GET | Paginated published posts (page_size=10) |
| `api/posts/<slug>/` | GET | Single post detail |
| `api/categories/` | GET | All categories |
| `api/tools/` | GET | Active tools ordered by `order` |
| `api/settings/` | GET | SiteSettings singleton |

- Read-only public access (`IsAuthenticatedOrReadOnly`)
- Rate-limited: 60 req/min for anonymous
- CORS allowed from `oursolve.com` only

---

## File Structure

```
oursolve_dashboard/
├── manage.py
├── passenger_wsgi.py              # Passenger WSGI entry point
├── requirements.txt
├── .cpanel.yml                    # Deploy pipeline
├── .htaccess                      # DO NOT EDIT — cPanel managed, not in git
├── oursolve_dashboard/
│   ├── settings.py                # All config including jazzmin
│   ├── urls.py                    # api/ first, admin LAST
│   ├── middleware.py              # NoCacheMiddleware (LiteSpeed fix)
│   └── wsgi.py
├── blog/
│   ├── models.py                  # BlogPost, Category, Tool, SiteSettings
│   ├── admin.py                   # Jazzmin fieldsets, SEO tab
│   ├── views.py                   # DRF APIViews
│   ├── serializers.py
│   ├── urls.py
│   ├── migrations/
│   └── templates/
│       └── admin/blog/blogpost/
│           └── change_form.html   # Live SEO preview + char counters
└── templates/                     # Global templates dir
```

---

## public_html/dashboard/.htaccess (server-only, NOT in git)

This file lives at `/home/oursolve/public_html/dashboard/.htaccess` on the server. It is managed by cPanel and should not be committed. Required contents:

```apache
PassengerAppRoot "/home/oursolve/oursolve_dashboard"
PassengerBaseURI "/dashboard"
PassengerPython "/home/oursolve/virtualenv/oursolve_dashboard/3.11/bin/python"
PassengerAppType wsgi
PassengerStartupFile passenger_wsgi.py
<IfModule Litespeed>
SetEnv DJANGO_SECRET_KEY <secret-key-here>
</IfModule>
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^ - [L]
<IfModule LiteSpeed>
CacheLookup off
</IfModule>
```

`RewriteEngine On` + the RewriteRule are required for sub-paths under `/dashboard/` to route to Passenger. Without them, only the base URI `/dashboard/` works.

---

## Known Bugs / Lessons Learned

1. **URL ordering bug**: `path('', admin.site.urls)` first → API routes return 404 because admin matches them as app_label. Always put `api/` before admin.

2. **LiteSpeed caching**: Even after app restart, old HTML is served for minutes. NoCacheMiddleware + `CacheLookup off` in .htaccess fixes this. The middleware is in git; the .htaccess line must be added manually via File Manager.

3. **jazzmin CSS/JS 404 after install**: collectstatic must run after pip install. The `.cpanel.yml` pipeline handles this, but only if you do a full Deploy HEAD Commit (not just Restart).

4. **Deploy blocked by "uncommitted changes"**: Server git tree is dirty from migrate/collectstatic output files. Fix: Update from Remote (resets to origin), then Deploy HEAD Commit.

5. **Passenger restart is async**: `touch tmp/restart.txt` triggers restart on next request after a cold Python startup delay (10–30s). If the site shows an error immediately after deploy, wait and retry.

6. **ManifestStaticFilesStorage breaks without terminal**: It hashes static filenames and needs to be run fresh each time. Without terminal access, you can't run collectstatic manually if it fails. Use `CompressedStaticFilesStorage` instead — it works correctly from `.cpanel.yml`.
