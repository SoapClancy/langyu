from django.urls import path
from .views import add_to_cart, remove_from_cart, remove_single_item_from_cart, OrderSummaryView, admin_order_pdf

app_name = 'order'

urlpatterns = [
    path('add-to-cart/<slug>/<int:number>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('admin/order/<int:order_id>/pdf/',
         admin_order_pdf,
         name='admin_order_pdf'),
]
