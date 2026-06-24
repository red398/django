#这是celery

from celery import shared_task
import time





@shared_task()
def handle_user_task(name):

    print('---开始处理异步任务---')
    print(f'---收到参数{name}---')

    #模拟耗时
    time.sleep(3)

    print(f'任务完成，欢迎{name}访问')
    return f"处理完成->{name}"





#实现发送邮件
#不叫装饰器不能调用delay()
from .models import  ProductSendEmail
from django.core.mail import send_mail
@shared_task()
def notify_supplier(product_id):
    try:
        product=ProductSendEmail.objects.get(pk=product_id)

        email_list=[product.supplier_email]
        send_mail(
            subject='新商品创建了',
            message=f'商品:{product.title}\n'
                     f'商品描述:{product.description}',
        from_email='2020724436@qq.com',
            #和上面的email_list关联
            recipient_list=email_list,
            fail_silently=False,
        )
        return f"邮件已发送{product.supplier_email}"
    except ProductSendEmail.DoesNotExist:
        return "商品不存在，邮件发送失败"

#celery定时任务
from datetime import datetime
@shared_task()
def print_time_task():
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'定时任务执行成功|当前时间{now}')
    return '执行完成！'
