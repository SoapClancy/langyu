from django.contrib import admin
from .models import MainCategory, SubCategory, Item, Label
from .forms import ItemForm


# Register your models here.
@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['main_category', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    form = ItemForm

    list_display = ['name', 'sub_category', 'slug', 'price', 'discount_price', 'get_labels',
                    'available_number', 'sales_volume', 'created', 'updated']
    list_filter = ['available_number', 'label', 'created', 'updated']

    list_editable = ['price', 'available_number']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def get_labels(self, obj):
        return "\n".join([p.get_name_display() for p in obj.label.all()])
