from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from django.contrib import messages
from django.utils import timezone
from .models import Product, Customer, SalesOrder, SalesOrderItem, StockMovement
from .forms import OrderCreateForm, OrderItemFormSet

@login_required
def dashboard(request):
    low_stock_threshold = 10
    context = {
        'total_products': Product.objects.count(),
        'total_customers': Customer.objects.count(),
        'orders_today': SalesOrder.objects.filter(order_date=timezone.now().date()).count(),
        'low_stock_count': Product.objects.filter(stock_qty__lt=low_stock_threshold).count(),
        'low_stock_products': Product.objects.filter(stock_qty__lt=low_stock_threshold),
        'recent_logs': StockMovement.objects.order_by('-timestamp')[:5]
    }
    return render(request, 'erp/dashboard.html', context)

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'erp/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        cat = self.request.GET.get('category')
        
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(sku__icontains=q))
        if cat:
            queryset = queryset.filter(category__icontains=cat)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Product.objects.values_list('category', flat=True).distinct()
        return context

class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Product
    fields = '__all__'
    template_name = 'erp/product_form.html'
    success_url = reverse_lazy('product-list')
    permission_required = 'erp.add_product'

class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Product
    fields = '__all__'
    template_name = 'erp/product_form.html'
    success_url = reverse_lazy('product-list')
    permission_required = 'erp.change_product'

class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Product
    template_name = 'erp/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')
    permission_required = 'erp.delete_product'

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'erp/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10

class CustomerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Customer
    fields = '__all__'
    template_name = 'erp/customer_form.html'
    success_url = reverse_lazy('customer-list')
    permission_required = 'erp.add_customer'

class CustomerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Customer
    fields = '__all__'
    template_name = 'erp/customer_form.html'
    success_url = reverse_lazy('customer-list')
    permission_required = 'erp.change_customer'

class CustomerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Customer
    template_name = 'erp/customer_confirm_delete.html'
    success_url = reverse_lazy('customer-list')
    permission_required = 'erp.delete_customer'

class OrderListView(LoginRequiredMixin, ListView):
    model = SalesOrder
    template_name = 'erp/order_list.html'
    context_object_name = 'orders'
    ordering = ['-order_date', '-id']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        status = self.request.GET.get('status')
        
        if q:
            queryset = queryset.filter(
                Q(order_number__icontains=q) | 
                Q(customer__name__icontains=q)
            )
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-order_date', '-id')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = SalesOrder
    template_name = 'erp/order_detail.html'
    context_object_name = 'order'

@login_required
@permission_required('erp.add_salesorder', raise_exception=True)
def order_create_view(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.created_by = request.user
                order.save()
                
                items = formset.save(commit=False)
                total = 0
                for item in items:
                    item.order = order
                    item.price = item.product.selling_price
                    item.save()
                    total += item.total
                
                order.total_amount = total
                order.save()
                
            messages.success(request, 'Order created successfully.')
            return redirect('order-list')
    else:
        form = OrderCreateForm()
        formset = OrderItemFormSet()
    
    return render(request, 'erp/order_form.html', {'form': form, 'formset': formset})

@login_required
def order_status_change(request, pk, action):
    order = get_object_or_404(SalesOrder, pk=pk)
    
    if not request.user.has_perm('erp.change_salesorder'):
         messages.error(request, "You don't have permission to update orders.")
         return redirect('order-detail', pk=pk)

    if action == 'confirm' and order.status == 'PENDING':
        order.status = 'CONFIRMED'
        order.save()
        messages.success(request, f"Order {order.order_number} confirmed.")
    elif action == 'cancel' and order.status != 'CANCELLED':
        order.status = 'CANCELLED'
        order.save()
        messages.success(request, f"Order {order.order_number} cancelled.")
    
    return redirect('order-detail', pk=pk)

from django.db import transaction
