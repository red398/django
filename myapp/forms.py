#文件上传功能
from cProfile import label

from django import forms

class UploadFileForm(forms.Form):
    # 普通文本输入（示例字段）
    title = forms.CharField(max_length=50)
    # 文件上传核心字段
    file = forms.FileField()


#forms表单
#验证码
from captcha.fields import CaptchaField
class UserInfoForm(forms.Form):
    gender_choices=[
        ('male','男'),
        ('female','女'),
        ('other','其他'),
    ]
    color_choices=[
        ('red','红色'),
        ('yellow','黄色'),
        ('blue','蓝色'),
    ]
    name=forms.CharField(label='姓名',max_length=100)
    gender=forms.CharField(label='性别',widget=forms.RadioSelect(choices=gender_choices))
    color=forms.CharField(label='颜色',widget=forms.RadioSelect(choices=color_choices))
    other=forms.CharField(label='其他',widget=forms.Textarea)
    #验证码
    captcha=CaptchaField(label='验证码')


#ajax
class ProductForm(forms.Form):
    product=forms.CharField(label="商品名称",max_length=20)
    price=forms.DecimalField(label='商品价格',max_digits=10,decimal_places=2)

#ajax_view
class ProductFormView(forms.Form):
    product=forms.CharField(label="商品名称",max_length=20)
    price=forms.DecimalField(label='商品价格',max_digits=10,decimal_places=2)

    captcha = CaptchaField(label="ajax验证码")

#发邮件
from .models import ProductSendEmail


class ProductSendEmailForm(forms.ModelForm):
    class Meta:
        model=ProductSendEmail
        fields=['title','description','supplier_email']
