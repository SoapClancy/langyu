from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.utils import timezone
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

PAYMENT_CHOICES = (
    ('pick_up', '到店自取'),
    ('delivery', '货到付款（£20镑以上免运费）')
)


class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone = PhoneNumberField()

    comments = forms.CharField(required=False, widget=forms.Textarea, max_length=1000)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES, required=True)
    old_cost_before_post = forms.CharField(max_length=32)


class AddressForm(forms.Form):
    shipping_address = forms.CharField(max_length=50, required=False)
    shipping_address_2 = forms.CharField(max_length=50, required=False)
    shipping_post_code = forms.CharField(max_length=10, required=False)

    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    old_cost_before_post = forms.CharField(max_length=32)
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox()
    )

    def clean(self):
        cleaned_data = super().clean()
        shipping_address = cleaned_data.get('shipping_address')
        shipping_address_2 = cleaned_data.get('shipping_address_2')
        shipping_post_code = cleaned_data.get('shipping_post_code')
        use_default_shipping = cleaned_data.get('use_default_shipping')
        if any((not shipping_address, not shipping_address_2, not shipping_post_code)) and (
                not use_default_shipping):
            raise forms.ValidationError('使用默认地址或者填写有效的地址')


def present_or_future_date(value):
    if value < timezone.now():
        raise forms.ValidationError("无法选择过去的时间")
    return value


class PickUpForm(forms.Form):
    pick_up_time = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M'], validators=[present_or_future_date])
    old_cost_before_post = forms.CharField(max_length=32)
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox()
    )
