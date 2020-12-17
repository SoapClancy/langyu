from django.urls import path
from .views import CheckoutView, PaymentView

app_name = 'payment'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<str:payment_option>/', PaymentView.as_view(), name='payment')
]
