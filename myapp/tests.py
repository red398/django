from django.template.defaultfilters import title
from django.test import TestCase

# Create your tests here.
import datetime
from django.utils import timezone
from .models import TestProduct

class ProducutMethodTests(TestCase):
    #测试场景，30天后
    def test_was_created_recently_with_future_product(self):
        future_time=timezone.now()+datetime.timedelta(days=30)
        future_product=TestProduct(date_created=future_time)
        #预计出现false，但实际会报错
        self.assertEqual(future_product.was_created_recently(),False)

    #补充正常场景：12小时内创建，应该返回True
    def test_was_created_recently_with_recent_product(self):
        recent_time=timezone.now()-datetime.timedelta(hours=12)
        recent_product=TestProduct(date_created=recent_time)
        self.assertEqual(recent_product.was_created_recently(),True)

    #刚好创建为1天，应该返回False
    def test_was_created_recently_with_one_day_ago(self):
        old_time=timezone.now()-datetime.timedelta(days=1)
        old_product=TestProduct(date_created=old_time)
        self.assertEqual(old_product.was_created_recently(),False)

#client测试客户端，django四类测试
from django.test import (
    TestCase,
    SimpleTestCase,
    TransactionTestCase,
    LiveServerTestCase,
    Client,
)
from django.urls import reverse
import tempfile

#---第一部分：测试客户端Client---
class ClientFullTest(TestCase):
    #初始化：自动生成client，测试数据，用户账号
    def setUp(self):
        #创建测试浏览器客户端
        self.c=Client()
        #创建测试用户(用户登录测试)
        from django.contrib.auth.models import User
        self.user=User.objects.create_user(username='test001',password='test123')
        #创建测试商品数据
        self.product=TestProduct.objects.create(title='手机',date_created='2026-06-20 10:00:00')
        #路由别名
        self.login_url=reverse('test_login')
        self.product_list=reverse('test_product_list')
        self.redirect_url=reverse('test_redirect_demo')
        self.upload_url=reverse('test_upload_file')

    #1.GET 请求 带查询参数
    def test_get_with_params(self):
        #等价访问/product/list/?name=手机
        res=self.c.get(self.product_list,{'name':'手机'})
        #校验页面正常返回
        self.assertEqual(res.status_code,200)
        #检验页面渲染出商品名称
        self.assertContains(res,'手机')

    #2.POST 登录表单(默认关闭csrf，不用传Token)
    def test_post_login_no_csrf(self):
        post_data={
            'username':'test001',
            'password':'test123',
        }
        #follow=True,自动跟踪重定向
        res=self.c.post(self.login_url,post_data,follow=True)

        #登录成功，页面展示用户
        self.assertContains(res,'test001')
        #查看重定向链路[(跳转地址，状态码)]
        print('重定向链路',res.redirect_chain)

    #3.强制开启csrf校验的客户端
    def test_client_enforce_csrf(self):
        csrf_client=Client(enforce_csrf_checks=True)
        post_data={'username':'test001','password':'test123'}
        #无csrf_token直接POST，返回403禁止访问
        res=csrf_client.post(self.login_url,post_data)
        self.assertEqual(res.status_code,403)

    #4.自定义请求头（模拟浏览器UA）
    def test_custom_header_client(self):
        #全局携带请求头
        header_client=Client(HTTP_USER_AGENT='Mozilla/5.0 Windows')
        #res=header_client.get(self.product_list)
        #读取请求头
        self.assertEqual(header_client.defaults['HTTP_USER_AGENT'],'Mozilla/5.0 Windows')

    #5.跟随重定向 follow=True
    def test_follow_redirect(self):
        res=self.c.get(self.redirect_url,follow=True)
        #重定向链，demo页→商品列表页
        #解释
        #redirect_chain是响应对象自带的列表属性
        #是一个二维元祖列表

        #一个发生了几次跳转
        self.assertEqual(len(res.redirect_chain),1)
        #最后一次的状态码
        self.assertEqual(res.redirect_chain[-1][1],302)

    #6.文件上传测试
    def test_post_upload_file(self):
        #临时生成测试文件
        with tempfile.NamedTemporaryFile() as fp:
            fp.write('测试文件内容'.encode('utf-8'))
            #解释读取文件是从文件开头开始
            #因为with之后会自动关闭
            #并且从头开始
            #但由于是临时文件，使用只能手动从头开始
            fp.seek(0)
            post_data={
                'name':'测试附件',
                'attachment':fp
            }

            res=self.c.post(self.upload_url,post_data)
            self.assertEqual(res.status_code,200)
            self.assertContains(res,'上传成功')

    #7.cookie会话自动携带(登录后持久会话)
    def test_client_cookie_session(self):
        #先登录
        self.c.post(self.login_url,{'username':'test001','password':'test123'})
        #再次访问需要登录的界面，自动携带登录cookie
        res=self.c.get(self.product_list)
        self.assertContains(res,'test001')

#---第二部分：四类测试基类---
#基类是django官方自带，提供内置工具
#上面6个就是基于TestCase类

#1.SimpleTestCase:不操作数据库，只测试模版，视图渲染（无DB开销）
class SimpleTestDemo(SimpleTestCase):
    def test_template_render(self):
        c=Client()
        #reverse根据别名解析URL
        res=c.get(reverse("test_home"))
        #校验使用指定模版
        self.assertTemplateUsed(res,'test_home.html')
        #检验页面包含文字
        self.assertContains(res,'首页欢迎')

#2.TestCase：日常业务首选，自动隔离测试数据库-
class TestCaseDemo(TestCase):
    def test_model_create(self):
        #自动创建干净数据库
        p=TestProduct.objects.create(title='测试商品')
        #count()查询当前测试库商品总数
        self.assertEqual(TestProduct.objects.count(),1)

#3.TransactionTest:支持数据库事务，行锁 select_for_update
class TransactionTestDemo(TransactionTestCase):
    def test_transaction_lock(self):
        from django.db import transaction
        with transaction.atomic():
            p=TestProduct.objects.create(title='锁测试商品')
            #可测试悲观锁，普通TestCase无法测试事务场景
            item=TestProduct.objects.select_for_update().first()
            self.assertEqual(item.title,'锁测试商品')

#4.LiveServerTestCase,启动真实Django服务，配合selenium浏览器自动化
class LiveServerDemo(LiveServerTestCase):
    def test_live_server(self):
        #self.live_server_url自动获取本地运行真实服务地址
        url=f"{self.live_server_url}{reverse('test_home')}"
        print('真实服务地址：',url)
        #可接入selenium webdriver操作浏览器
