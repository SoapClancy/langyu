from django.contrib import admin
from .models import OrderItem, Order
from django.utils.safestring import mark_safe
from django.urls import reverse
from ..payment.tasks import order_created


def order_total_cost(obj):
    return str(obj.get_total())


# Register your models here.
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['item']


def order_pdf(obj):
    return mark_safe('<a href="{}">PDF</a>'.format(
        reverse('order:admin_order_pdf', args=[obj.id])))


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'first_name', 'last_name', 'email', 'phone', 'shipping_address', 'ordered',
                    'paid', order_total_cost, order_pdf]
    inlines = [OrderItemInline]
    list_filter = ['first_name', 'email', 'phone', 'shipping_address']

    list_editable = ['paid']
    search_fields = ['order_id', 'email', 'phone', 'shipping_address']

    def save_model(self, request, obj, form, change):
        if change:
            if form.cleaned_data.get('paid') is True:
                order = Order.objects.get(pk=obj.id)
                order.paid = True
                order.save()
                order_created(request, order.id)
        return super().save_model(request, obj, form, change)
