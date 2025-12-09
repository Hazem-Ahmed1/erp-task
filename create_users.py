import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_erp.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_users():
    # Admin User
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        admin_group = Group.objects.get(name='Admin')
        admin.groups.add(admin_group)
        print("User 'admin' created with password 'admin'.")
    else:
        print("User 'admin' already exists.")

    # Sales User
    if not User.objects.filter(username='sales').exists():
        sales = User.objects.create_user('sales', 'sales@example.com', 'sales')
        sales_group = Group.objects.get(name='Sales User')
        sales.groups.add(sales_group)
        print("User 'sales' created with password 'sales'.")
    else:
        print("User 'sales' already exists.")

if __name__ == '__main__':
    create_users()
