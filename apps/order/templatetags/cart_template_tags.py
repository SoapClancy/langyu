from django import template
from ..models import Order

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            count_ = 0
            for order_item in qs[0].order_items.all():
                count_ = count_ + order_item.quantity
            return count_
    return 0



