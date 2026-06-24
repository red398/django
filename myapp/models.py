from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
# 信号导入
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)

# 新建用户自动创建profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created,**kwargs):
    if created:
        Profile.objects.create(user=instance)



from django.conf import settings
AUTH_USER_MODEL = settings.AUTH_USER_MODEL

class Basket(models.Model):
    STATUS_CHOICES = (
        ("Open", "Open"),
        ("Ordered", "Ordered")
    )
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)
    date_created = models.DateTimeField(auto_now_add=True)
    date_ordered = models.DateTimeField(blank=True, null=True)


class Line(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_created = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Order(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=10)


class OrderNote(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class OrderStatusChange(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now_add=True)

class CommunicationEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now_add=True)

class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    event_type = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now_add=True)

#发email
class ProductSendEmail(models.Model):
    title=models.CharField(max_length=100,verbose_name='商品标题')
    description=models.TextField(verbose_name='商品描述')
    supplier_email=models.EmailField(verbose_name='供应商邮件')
    create_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

#新的注册登录界面
class MyUser(models.Model):
    username = models.CharField(max_length=50, unique=True, verbose_name="用户名")
    password_hash = models.CharField(max_length=256, verbose_name="加密密码")

    def __str__(self):
        return self.username

    class Meta:
        db_table = "my_user"
        verbose_name = "用户"
        verbose_name_plural = "用户"

#RBAC
class Task(models.Model):
    title=models.CharField(max_length=100,verbose_name='任务标题')
    status=models.CharField(max_length=20,default='open')

    class Meta:
        verbose_name='任务'
        verbose_name_plural='任务表'
        #自定义业务权限，migrate自动入库
        permissions=[
            #django自带('view_task','查看全部任务'),
            ('close_task','关闭任务'),
        ]

#test相关，使用test

from django.utils import timezone
import datetime
class TestProduct(models.Model):
    title=models.CharField(max_length=100,verbose_name='商品名称')
    date_created=models.DateTimeField(default=timezone.now,verbose_name='创建时间')

    def was_created_recently(self):
        #原bug:未来时间也返回True
        #return self.date_created >= timezone.now()-datetime.timedelta(days=1)

        #这是正确的✅️
        now=timezone.now()
        one_day_ago=now-datetime.timedelta(days=1)
        #必须晚于1天，且不能超过当时时间
        return one_day_ago<self.date_created<=now

    #这里在后台打开会显示中文名字
    class Meta:
        verbose_name='Product'
        verbose_name_plural='Products'
        def __str__(self):
            return self.title