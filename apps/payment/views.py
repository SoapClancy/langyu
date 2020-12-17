from django.shortcuts import render, redirect
from ..address.models import Address
from ..order.models import Order
from django.views.generic import View
from .forms import CheckoutForm, AddressForm, PickUpForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from .tasks import order_created


# Create your views here.
def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm(initial={'old_cost_before_post': str(order.get_total())})
            context = {
                'form': form,
                'order': order,
            }
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "未找到未完成的订单")
            return redirect("payment:checkout")

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm(self.request.POST or None)

            if form.is_valid():
                if form.cleaned_data.get('old_cost_before_post') != order.get_total().__str__():
                    messages.warning(self.request, "购物车中有商品的价格在刚才恰好发生了改变，请刷新后重试")
                    return HttpResponseRedirect(self.request.META['HTTP_REFERER'])
                # 从form中得到额外的信息（比如名字，phone等）
                order.first_name = form.cleaned_data.get('first_name')
                order.last_name = form.cleaned_data.get('last_name')
                order.email = form.cleaned_data.get('email')
                order.phone = form.cleaned_data.get('phone')
                order.comments = form.cleaned_data.get('comments')
                order.save()

                if form.cleaned_data.get('payment_option') == 'pick_up':
                    return redirect('payment:payment', payment_option='pick_up')
                elif form.cleaned_data.get('payment_option') == 'delivery':
                    return redirect('payment:payment', payment_option='delivery')
                else:
                    messages.warning(self.request, "选择了不支持的付款方式")
                    return redirect('payment:checkout')
            else:
                errors = form.errors.as_data()
                if 'phone' in errors:
                    messages.warning(self.request, "检查电话号码的输入。英国电话号码的格式是: 0111 222 3333或111 222 3333")
                if 'email' in errors:
                    messages.warning(self.request, "检查Email的输入")
                if 'first_name' in errors:
                    messages.warning(self.request, "检查名字的输入")
                if 'last_name' in errors:
                    messages.warning(self.request, "检查姓氏的输入")
                if 'payment_option' in errors:
                    messages.warning(self.request, "选择一种送货方式")
                print(errors)
                return HttpResponseRedirect(self.request.META['HTTP_REFERER'])
        except ObjectDoesNotExist:
            messages.info(self.request, "未找到未完成的订单")
            return redirect("order:order-summary")


class PaymentView(LoginRequiredMixin, View):
    def get_corresponding_form(self, order, post_=False):
        if 'pick_up' in self.request.get_full_path():
            if post_:
                form = PickUpForm(self.request.POST or None, initial={'old_cost_before_post': str(order.get_total())})
            else:
                form = PickUpForm(initial={'old_cost_before_post': str(order.get_total())})
        elif 'delivery' in self.request.get_full_path():
            if post_:
                form = AddressForm(self.request.POST or None, initial={'old_cost_before_post': str(order.get_total())})
            else:
                form = AddressForm(initial={'old_cost_before_post': str(order.get_total())})
        else:
            messages.warning(self.request, "无效的dispatch方式")
            return None
        return form

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            get_form = self.get_corresponding_form(order)
            if get_form:
                form = get_form
            else:
                return redirect("payment:checkout")
            context = {
                'form': form,
                'order': order,
            }
            # 如果有默认地址的记录就允许去使用
            default_shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                default=True
            )

            if default_shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': default_shipping_address_qs[0]})

            return render(self.request, "payment.html", context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "未找到未完成的订单")
            return redirect("payment:checkout")

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            post_form = self.get_corresponding_form(order, post_=True)
            if post_form:
                form = post_form
            else:
                return redirect("payment:checkout")

            if form.is_valid():
                if form.cleaned_data.get('old_cost_before_post') != order.get_total().__str__():
                    messages.warning(self.request, "购物车中有商品的价格在刚才恰好发生了改变，请刷新后重试")
                    return HttpResponseRedirect(self.request.META['HTTP_REFERER'])

                # 两种取货方式
                if 'pick_up' in self.request.get_full_path():
                    order.pick_up_time = form.cleaned_data.get('pick_up_time')

                elif 'delivery' in self.request.get_full_path():
                    # 如果说了要用默认地址，那就用默认地址
                    if form.cleaned_data.get('use_default_shipping'):
                        shipping_address = Address.objects.filter(
                            user=self.request.user,
                            default=True
                        )[0]
                    # 如果没有默认地址，就新建地址，并且考虑是不是要将其设为默认
                    else:
                        shipping_address = Address(user=self.request.user,
                                                   address=form.cleaned_data.get('shipping_address'),
                                                   address_2=form.cleaned_data.get('shipping_address_2'),
                                                   post_code=form.cleaned_data.get('shipping_post_code'))
                        if form.cleaned_data.get('set_default_shipping'):
                            shipping_address.default = True
                            # 只允许有一个默认地址，其它一律设为非默认
                            previous_default_qs = Address.objects.filter(
                                user=self.request.user,
                                default=True
                            )
                            if previous_default_qs.exists():
                                previous_default = previous_default_qs[0]
                                previous_default.default = False
                                previous_default.save()

                        shipping_address.save()
                    order.shipping_address = shipping_address
                else:
                    messages.warning(self.request, "无效的dispatch方式")
                    return redirect("payment:checkout")
                # 最后再查一遍库存
                for order_item in order.order_items.all():
                    if order_item.quantity > order_item.item.available_number:
                        messages.warning(self.request, "“{}”的库存刚才已更新，目前库存不足，请更新购物车并重试".format(order_item.item.name))
                        return redirect("order:order-summary")
                    else:
                        order_item.item.available_number -= order_item.quantity
                        order_item.item.sales_volume += order_item.quantity

                        order_item.item.save()
                # 完成订单
                order.ordered = True
                order.save()
                order_created(self.request, order.id)
                return render(self.request, "confirmation.html", {'order': order})

            else:
                if 'pick_up_time' in form.errors.as_data():
                    messages.warning(self.request, "无法选择过去的时间")
                else:
                    print(form.errors.as_data())
                    messages.warning(self.request, "检查表单输入")
                return HttpResponseRedirect(self.request.META['HTTP_REFERER'])
        except ObjectDoesNotExist:
            messages.warning(self.request, "未找到未完成的订单")
            return redirect("order:order-summary")
