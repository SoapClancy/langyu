import django_filters
from .models import Item, Label

CHOICES = (
    ('ascending', 'Ascending'),
    ('descending', 'Descending')
)


class ItemFilter(django_filters.FilterSet):
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='不低于')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='不高于')
    label = django_filters.ModelMultipleChoiceFilter(field_name='label', label='标签', queryset=Label.objects.all())
    name = django_filters.CharFilter(field_name='name', lookup_expr='contains', label='名称')
    o = django_filters.OrderingFilter(
        fields=(
            ('created', '上架时间'),
            ('price', '价格'),
        ),
        label='排序',
    )

    class Meta:
        model = Item
        fields = ('label',)
