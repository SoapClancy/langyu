from django.db import models
from django.conf import settings
from apps.item.models import Item
from apps.address.models import Address
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
import datetime
import random
import string


# Create your models here.
class Order(models.Model):
    order_id = models.CharField(max_length=64)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='orders',
                             on_delete=models.CASCADE)
    first_name = models.CharField(_('first name'),
                                  max_length=50)
    last_name = models.CharField(_('last name'),
                                 max_length=50)
    email = models.EmailField(_('e-mail'))
    phone = PhoneNumberField(help_text="UK电话号码，格式是: 0111 222 3333或111 222 3333")
    comments = models.TextField(blank=True)

    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    shipping_address = models.ForeignKey(
        Address, related_name='orders', on_delete=models.SET_NULL, blank=True, null=True)
    pick_up_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.order_id

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'

    @staticmethod
    def create_ref_code(name: str):
        return str(datetime.datetime.now())[:-7] + '+' + name + '_' + ''.join(
            (random.choices(string.ascii_lowercase + string.digits, k=4)))

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.create_ref_code(self.user.username)
        super().save(*args, **kwargs)

    def get_total(self):
        total = 0
        for order_item in self.order_items.all():
            total += order_item.get_final_price()
        return total

    # def save(self, *args, **kwargs):
    #     old = Order.objects.filter(pk=getattr(self, 'pk', None)).first()
    #     if old:
    #         if old.attr != self.attr:
    #             # attr changed
    #             pass
    #     super(Order, self).save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              related_name='order_items',
                              on_delete=models.CASCADE)

    item = models.ForeignKey(Item,
                             related_name='order_items',
                             on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = '订单商品'

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
