from django import forms
from .models import Item
from django.core.exceptions import ValidationError


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['sub_category', 'name', 'slug', 'description',
                  'available_number', 'price', 'discount_price',
                  'label', 'image']

    def clean(self):
        if self.cleaned_data.get('label') is None:
            raise ValidationError("必须选择label")

        if all((self.cleaned_data.get('discount_price') is not None,
                not self.cleaned_data.get('label').filter(name__contains='Sale'))):
            raise ValidationError("如果给定了折扣价钱（discount price），那么label必须包含“打折”")

        if all((self.cleaned_data.get('label').filter(name__contains='Sale'),
                (self.cleaned_data.get('discount_price') is None))):
            raise ValidationError("如果label包含“打折”，那么必须给定折扣价钱（discount price）")

        if all((self.cleaned_data.get('label').filter(name__contains='Normal'),
                (self.cleaned_data.get('label').count() > 1))):
            raise ValidationError("选择了Normal就不可以选择其它的label")
