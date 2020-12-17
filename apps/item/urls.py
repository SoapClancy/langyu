from django.urls import path
from .views import ItemDetailView, HomeView, contact_view

app_name = 'item'

urlpatterns = [
    path('', HomeView.as_view(), name='item-list'),
    path('contact/', contact_view, name='contact_view'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('<slug:main_category_slug>/', HomeView.as_view(),
         name='product_list_by_main_category'),
    path('<slug:main_category_slug>/<slug:sub_category_slug>/', HomeView.as_view(),
         name='product_list_by_sub_category'),
]
