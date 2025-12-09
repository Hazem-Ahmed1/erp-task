import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_erp.settings')
django.setup()

from django.contrib.auth.models import User
from erp.models import Product, Customer, SalesOrder, SalesOrderItem

def populate():
    print("Populating data...")
    
    # Users
    admin = User.objects.get(username='admin')
    sales_user = User.objects.get(username='sales')

    # 1. Products
    products_data = [
        {'sku': 'DELL-XPS', 'name': 'Dell XPS 13 Laptop', 'cat': 'Electronics', 'cost': 900, 'price': 1200, 'stock': 50},
        {'sku': 'LOGI-MX', 'name': 'Logitech MX Master 3', 'cat': 'Accessories', 'cost': 60, 'price': 100, 'stock': 200},
        {'sku': 'SAM-S24', 'name': 'Samsung Galaxy S24', 'cat': 'Electronics', 'cost': 700, 'price': 950, 'stock': 30},
        {'sku': 'HP-MON', 'name': 'HP 27 inch Monitor', 'cat': 'Electronics', 'cost': 150, 'price': 250, 'stock': 5}, # Low stock test (Threshold 10)
        {'sku': 'USB-C', 'name': 'USB-C Cable', 'cat': 'Accessories', 'cost': 2, 'price': 10, 'stock': 500},
    ]

    products = []
    for p in products_data:
        prod, created = Product.objects.get_or_create(
            sku=p['sku'],
            defaults={
                'name': p['name'], 'category': p['cat'],
                'cost_price': p['cost'], 'selling_price': p['price'],
                'stock_qty': p['stock']
            }
        )
        if created:
            print(f"Created Product: {prod.name}")
        else:
            prod.stock_qty = p['stock']
            prod.save()
            print(f"Updated Product: {prod.name}")
        products.append(prod)

    # 2. Customers
    customers_data = [
        {'code': 'Cust-001', 'name': 'Tech Solutions Inc', 'phone': '555-0100', 'email': 'contact@techsol.com'},
        {'code': 'Cust-002', 'name': 'Global Trading Ltd', 'phone': '555-0101', 'email': 'info@globaltrading.com'},
        {'code': 'Cust-003', 'name': 'John Doe (Individual)', 'phone': '555-0999', 'email': 'john@example.com'},
    ]

    customers = []
    for c in customers_data:
        cust, created = Customer.objects.get_or_create(
            code=c['code'],
            defaults={'name': c['name'], 'phone': c['phone'], 'email': c['email'], 'address': '123 Fake St'}
        )
        if created:
            print(f"Created Customer: {cust.name}")
        customers.append(cust)

    # 3. Sales Orders
    order1, created = SalesOrder.objects.get_or_create(
        customer=customers[0],
        status='CONFIRMED',
        defaults={'created_by': sales_user}
    )
    if created:
        # Create items
        SalesOrderItem.objects.create(order=order1, product=products[0], qty=5, price=products[0].selling_price) # Dell XPS
        
        # Now Confirm it
        order1.status = 'CONFIRMED'
        order1.save() 
        print(f"Created Confirmed Order {order1.order_number} (Dell XPS x5)")

    # Case B: Pending Order (No stock change)
    order2 = SalesOrder.objects.create(
        customer=customers[1],
        status='PENDING',
        created_by=sales_user
    )
    SalesOrderItem.objects.create(order=order2, product=products[1], qty=10, price=products[1].selling_price) # Mouse
    print(f"Created Pending Order {order2.order_number} (Mouse x10)")

    # Case C: Cancelled Order (Stock reduced then restored)
    order3 = SalesOrder.objects.create(
        customer=customers[2],
        status='PENDING',
        created_by=admin
    )
    SalesOrderItem.objects.create(order=order3, product=products[2], qty=2, price=products[2].selling_price) # S24 Phone
    
    # Confirm first (Stock -2)
    order3.status = 'CONFIRMED'
    order3.save()
    
    # Then Cancel (Stock +2)
    order3.status = 'CANCELLED'
    order3.save()
    print(f"Created Cancelled Order {order3.order_number} (S24 x2) - Stock should be unchanged net")

    print("Data population complete.")

if __name__ == '__main__':
    populate()
