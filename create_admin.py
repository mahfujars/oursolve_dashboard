import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oursolve_dashboard.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@oursolve.com', 'Admin1234!')
    print('Superuser created: admin / Admin1234!')
else:
    print('Admin user already exists')
