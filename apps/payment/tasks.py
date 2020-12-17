from celery import task
from django.core.mail import EmailMessage
from ..order.models import Order
import weasyprint
from io import BytesIO
from django.template.loader import render_to_string
from Langyu import settings

@task
def order_created(request, order_id):
    """
    用celery发异步邮件
    """
    order = Order.objects.get(id=order_id)
    subject = '朗御Langyu订单号. {}'.format(order.order_id)
    if not order.paid:
        message = '尊敬的 {},\n\n您已经成功在朗御Langyu下单。您的订单号是 {}.\n\n祝您生活愉快，\n朗御Langyu'.format(
            order.first_name,
            order.order_id)
    else:
        message = '尊敬的 {},\n\n您已完成该订单.\n\n祝您生活愉快，\n朗御Langyu'.format(
            order.first_name,
            order.order_id)
    email = EmailMessage(subject,
                         message,
                         'langyu2020@gmail.com',
                         [order.email], cc=['langyu2020@gmail.com'])
    # 生成PDF
    html = render_to_string('pdf.html', {'order': order})
    out = BytesIO()
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(out, stylesheets=[
        weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')])
    # attach PDF file
    email.attach('order_{}.pdf'.format(order.order_id),
                 out.getvalue(),
                 'application/pdf')
    mail_sent = email.send()
    # mail_sent = send_mail(subject,
    #                       message,
    #                       'admin@LangyuDev0.com',
    #                       [order.email])
    return mail_sent
