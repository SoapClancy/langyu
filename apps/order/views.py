from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from apps.item.models import Item
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
import weasyprint
from django.template.loader import render_to_string
from Langyu import settings

# Create your views here.
@login_required
def add_to_cart(request, slug, number=1):
    def add_new_item_to_current_order():
        nonlocal order_item, order, item
        order_item = OrderItem(order=order, item=item, quantity=number)
        # 如果库存不足
        if order_item.quantity > item.available_number:
            messages.warning(request, f"“{item.name}”库存不足，加入购物车失败")
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        order_item.save()
        order.order_items.add(order_item)
        messages.info(request, f"已将“{item.name}”加入购物车")

    # 如果存在3笔以上的unpaid的订单，则不允许下单
    if Order.objects.filter(user=request.user, paid=False).count() >= 3:
        messages.warning(request, "“未支付”订单数超过3笔，无法创建新的订单")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    item = get_object_or_404(Item, slug=slug)
    # 如果库存不足
    if item.available_number == 0:
        messages.warning(request, f"“{item.name}”库存不足，加入购物车失败")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    # 如果存在未完成的订单
    if order_qs.exists():
        # 选取最近一个未完成的订单
        order = order_qs[0]
        # 如果订单中存在这个item
        if order.order_items.filter(item__slug=item.slug).exists():
            order_item = order.order_items.get(item__slug=item.slug)
            # 如果库存不足
            if order_item.quantity + number > item.available_number:
                messages.warning(request, f"“{item.name}”库存不足，加入购物车失败")
                return HttpResponseRedirect(request.META['HTTP_REFERER'])

            order_item.quantity += number
            order_item.save()
            messages.info(request, f"“{item.name}”数量已更新")
        # 如果订单中不存在这个item
        else:
            add_new_item_to_current_order()

    # 如果不存在未完成的订单，就新开启一个订单
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        add_new_item_to_current_order()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    # 如果存在未完成的订单
    if order_qs.exists():
        # 选取最近一个未完成的订单
        order = order_qs[0]
        # 如果订单中存在这个item
        if order.order_items.filter(item__slug=item.slug).exists():
            order_item = order.order_items.get(item__slug=item.slug)
            order_item.delete()
            messages.info(request, f"已将“{item.name}”移出购物车")
        else:
            messages.info(request, f"“{item.name}”不在购物车中")
    else:
        messages.info(request, '您还没有未完成的订单')
    return redirect("order:order-summary")


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    # 如果存在未完成的订单
    if order_qs.exists():
        # 选取最近一个未完成的订单
        order = order_qs[0]
        # 如果订单中存在这个item
        if order.order_items.filter(item__slug=item.slug).exists():
            order_item = order.order_items.get(item__slug=item.slug)
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, f"“{item.name}”数量已更新")
            else:
                order_item.delete()
                messages.info(request, f"已将“{item.name}”移出购物车")
            return redirect("order:order-summary")
        else:
            messages.info(request, f"“{item.name}”不在购物车中")
            return redirect("item:product", slug=slug)
    else:
        messages.info(request, '您还没有未完成的订单')
        return redirect("item:product", slug=slug)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.filter(user=self.request.user, ordered=False)[0]
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except IndexError:
            messages.warning(self.request, "购物车为空")
            return HttpResponseRedirect(self.request.META['HTTP_REFERER'])


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('pdf.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="order_{}.pdf"'.format(order.id)
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        response,
        stylesheets=[weasyprint.CSS(
            settings.STATIC_ROOT + 'css/pdf.css')])
    return response
