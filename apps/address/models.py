from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    address = models.CharField(_('address'), max_length=100)
    address_2 = models.CharField(_('address_2'), max_length=100)
    post_code = models.CharField(_('post_code'), max_length=16)
    default = models.BooleanField(_('default'), default=False)

    def __str__(self):
        return "address='{}' address_2='{}' post_code='{}' default={}".format(
            self.address, self.address_2, self.post_code, self.default)

    class Meta:
        verbose_name = '地址'
        verbose_name_plural = '地址'
