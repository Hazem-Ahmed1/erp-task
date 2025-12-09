from django import forms
from django.forms import inlineformset_factory
from .models import SalesOrder, SalesOrderItem

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['customer', 'status']
        exclude = ['order_number', 'order_date', 'created_by', 'total_amount', 'status']

SalesOrderItemFormSet = inlineformset_factory(
    SalesOrder, SalesOrderItem,
    fields=['product', 'qty'],
    extra=1,
    can_delete=True
)

OrderItemFormSet = SalesOrderItemFormSet
