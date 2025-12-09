import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_erp.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from erp.models import Product, Customer, SalesOrder, SalesOrderItem, StockMovement

def create_roles():
    admin_group, created = Group.objects.get_or_create(name='Admin')
    sales_group, created = Group.objects.get_or_create(name='Sales User')
    ct_product = ContentType.objects.get_for_model(Product)
    sales_group.permissions.add(Permission.objects.get(codename='view_product', content_type=ct_product))
    
    # 2. Customer: Add, View, Change (No Delete)
    ct_customer = ContentType.objects.get_for_model(Customer)
    sales_group.permissions.add(
        Permission.objects.get(codename='add_customer', content_type=ct_customer),
        Permission.objects.get(codename='view_customer', content_type=ct_customer),
        Permission.objects.get(codename='change_customer', content_type=ct_customer),
    )
    
    ct_order = ContentType.objects.get_for_model(SalesOrder)
    sales_group.permissions.add(
        Permission.objects.get(codename='add_salesorder', content_type=ct_order),
        Permission.objects.get(codename='view_salesorder', content_type=ct_order),
    )
    # Sales User needs to add items too
    ct_item = ContentType.objects.get_for_model(SalesOrderItem)
    sales_group.permissions.add(
        Permission.objects.get(codename='add_salesorderitem', content_type=ct_item),
        Permission.objects.get(codename='view_salesorderitem', content_type=ct_item),
        Permission.objects.get(codename='change_salesorderitem', content_type=ct_item),
    )

    print("Roles 'Admin' and 'Sales User' created/updated.")

if __name__ == '__main__':
    create_roles()
