from django.db import models
from django.core.validators import MinValueValidator
from django.shortcuts import reverse, redirect
from decimal import Decimal
from .category_choices import MAIN_CATEGORY_CHOICES, SUB_CATEGORY_CHOICES
from django.core.exceptions import ValidationError

# Create your models here.
LABEL_CHOICES = (
    ('Normal', '其它'),
    ('Sale', '打折'),
    ('New', '新品'),
    ('Populate', '热销')
)


class MainCategory(models.Model):
    name = models.CharField(choices=MAIN_CATEGORY_CHOICES,
                            max_length=32,
                            db_index=True)
    slug = models.SlugField(max_length=32,
                            unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = '父类'
        verbose_name_plural = '父类'

    def __str__(self):
        return self.get_name_display()

    def get_absolute_url(self):
        return reverse('item:product_list_by_main_category',
                       args=[self.slug])


class SubCategory(models.Model):
    name = models.CharField(choices=SUB_CATEGORY_CHOICES,
                            max_length=64,
                            db_index=True)
    slug = models.SlugField(max_length=64,
                            unique=True)
    main_category = models.ForeignKey(MainCategory,
                                      related_name='sub_categories',
                                      on_delete=models.CASCADE)

    class Meta:
        ordering = ('name',)
        verbose_name = '子类'
        verbose_name_plural = '子类'

    def __str__(self):
        return self.main_category.__str__() + ' - ' + self.get_name_display()

    def clean(self):
        if self.main_category.name not in self.name:
            raise ValidationError("检查main category的选择")

    def get_absolute_url(self):
        return reverse('item:product_list_by_sub_category',
                       args=[self.main_category.slug, self.slug])


class Label(models.Model):
    name = models.CharField(choices=LABEL_CHOICES,
                            max_length=16,
                            db_index=True)
    slug = models.SlugField(max_length=64,
                            unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = '标签'
        verbose_name_plural = '标签'

    def __str__(self):
        return self.get_name_display()


class Item(models.Model):
    sub_category = models.ForeignKey(SubCategory,
                                     related_name='items',
                                     on_delete=models.CASCADE)

    name = models.CharField(max_length=100,
                            db_index=True)
    slug = models.SlugField(max_length=100,
                            db_index=True,
                            unique=True)
    description = models.TextField(blank=True)
    available_number = models.IntegerField(default=10,
                                           validators=[MinValueValidator(0)])

    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                validators=[MinValueValidator(Decimal('0.01'))])
    discount_price = models.DecimalField(blank=True, null=True,
                                         max_digits=10, decimal_places=2,
                                         validators=[MinValueValidator(Decimal('0.01'))])
    sales_volume = models.PositiveIntegerField(default=0)

    label = models.ManyToManyField(Label,
                                   related_name='items',
                                   default=1)  # 设置M2M字段的default巨坑！只要设置default对应的pk就行，第一个从1开始而不是0
    image = models.ImageField(upload_to='item/%Y/%m/%d',
                              blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)
        verbose_name = '商品'
        verbose_name_plural = '商品'

    def clean(self):
        if (self.discount_price is not None) and (self.discount_price >= self.price):
            raise ValidationError("打折后的价格应该低于原价")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("item:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("order:add-to-cart", kwargs={
            'slug': self.slug,
            'number': 1
        })

    def get_remove_from_cart_url(self):
        return reverse("order:remove-from-cart", kwargs={
            'slug': self.slug
        })
