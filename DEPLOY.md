# Deploying oursolve_dashboard to cPanel

The dashboard runs at **https://oursolve.com/dashboard/** using cPanel's
Python App feature (Passenger/WSGI).

---

## 1. Create the Python App in cPanel

1. Log into cPanel → **Setup Python App**
2. Click **Create Application**
3. Fill in:
   - **Python version:** 3.9 or higher
   - **Application root:** `oursolve_dashboard`
     *(this maps to `/home/oursolve/oursolve_dashboard/` on the server)*
   - **Application URL:** `oursolve.com/dashboard`
   - **Application startup file:** `passenger_wsgi.py`
   - **Application Entry point:** `application`
4. Click **Create** — cPanel will create the virtual environment automatically.

---

## 2. Upload the project files

Upload the entire `oursolve_dashboard/` folder to:
```
/home/oursolve/oursolve_dashboard/
```

You can use cPanel File Manager, FTP, or Git (recommended).

**Using Git (recommended):**
```bash
# SSH into the server
ssh oursolve@oursolve.com

cd ~
git clone https://github.com/mahfujars/oursolve_tools.git
# The dashboard lives at ~/oursolve_tools/oursolve_dashboard/
# Symlink or copy it to the app root:
cp -r ~/oursolve_tools/oursolve_dashboard ~/oursolve_dashboard
```

---

## 3. Install dependencies

In cPanel → Python App, click **Enter to the virtual environment** to get the
activation command. Then SSH in and run:

```bash
# Activate the virtual environment (copy the command from cPanel)
source /home/oursolve/virtualenv/oursolve_dashboard/3.x/bin/activate

cd ~/oursolve_dashboard

pip install -r requirements.txt
```

---

## 4. Set environment variables

In cPanel → Python App → **Environment Variables**, add:

| Key | Value |
|-----|-------|
| `DJANGO_SECRET_KEY` | A long random string (generate one below) |
| `DJANGO_DEBUG` | `False` |

**Generate a secret key (run locally or via SSH):**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 5. Initialise the database

```bash
# (virtual environment still active)
cd ~/oursolve_dashboard

python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## 6. Configure the .htaccess routing

cPanel's Python App creates a `public_html/dashboard/` directory automatically.
Place (or confirm) the `.htaccess` file there:

```
/home/oursolve/public_html/dashboard/.htaccess
```

The file is included in this repo at `oursolve_dashboard/.htaccess`.
Copy it:
```bash
cp ~/oursolve_dashboard/.htaccess ~/public_html/dashboard/.htaccess
```

---

## 7. Restart the app

In cPanel → Python App, click **Restart** after any code or dependency change.

Alternatively via SSH (faster):
```bash
touch ~/oursolve_dashboard/tmp/restart.txt
# or: kill -USR1 $(cat /var/run/passenger.pid)
```

---

## 8. Verify

- Admin: **https://oursolve.com/dashboard/admin/**
- API posts: **https://oursolve.com/dashboard/api/posts/**
- API tools: **https://oursolve.com/dashboard/api/tools/**
- API settings: **https://oursolve.com/dashboard/api/settings/**

---

## Day-to-day deployment (code updates)

```bash
ssh oursolve@oursolve.com
cd ~/oursolve_dashboard

git pull origin main          # pull latest code

# If models changed:
python manage.py migrate

# If static files changed:
python manage.py collectstatic --noinput

touch tmp/restart.txt         # restart Passenger
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| 500 error on all pages | Check `DJANGO_SECRET_KEY` is set; run `migrate` |
| Static files (CSS/JS) not loading | Run `collectstatic`; check `STATIC_ROOT` is writable |
| Admin login redirects to wrong URL | Confirm `FORCE_SCRIPT_NAME = '/dashboard'` in settings |
| CORS errors from oursolve.com | Check `CORS_ALLOWED_ORIGINS` in settings |
| CKEditor images not uploading | Ensure `media/` directory is writable by the app user |

---

## API Usage from the static site

Fetch tools from JavaScript (no auth needed):

```js
// List all active tools
fetch('https://oursolve.com/dashboard/api/tools/')
  .then(r => r.json())
  .then(tools => console.log(tools));

// List published posts (paginated, 10/page)
fetch('https://oursolve.com/dashboard/api/posts/?page=1')
  .then(r => r.json())
  .then(data => console.log(data.results));

// Single post
fetch('https://oursolve.com/dashboard/api/posts/my-post-slug/')
  .then(r => r.json())
  .then(post => console.log(post));

// Filter by category
fetch('https://oursolve.com/dashboard/api/posts/?category=tutorials')

// Search
fetch('https://oursolve.com/dashboard/api/posts/?search=password')
```

All API responses are JSON. Post listings are paginated:
```json
{
  "count": 42,
  "next": "https://oursolve.com/dashboard/api/posts/?page=2",
  "previous": null,
  "results": [ ... ]
}
```
