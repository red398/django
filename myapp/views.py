import datetime
from platform import uname

from celery.bin.control import status
from django import forms
# 这是装饰器
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import Profile

from functools import wraps


# Create your views here.
# def index(request):
#   return HttpResponse("hello")


# 两个表单
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('gender', 'birth_date') # 书上url字段删掉，你模型没有url

# 登录才能修改的视图
@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('/myapp/profile/') # 自己写的展示页地址
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

# 新增：展示用户信息页面（对应书上模板代码）
def show_profile(request):
    return render(request, 'show_profile.html', {'user': request.user})


from .models import Order,OrderLine

# 函数1：查询用户一段时间订单
def get_order_list(user_id, start_date, end_date):
    order_list = Order.objects.filter(user_id=user_id).filter(
        created_date__gt=start_date,
        created_date__lt=end_date
    )
    return order_list

# 函数2：查询单个订单里所有商品
def get_order_detail(order_id):
    print(order_id)
    order_line_list = OrderLine.objects.filter(id=order_id)
    return order_line_list


# 我的订单列表页
def my_order(request):
    # 拿当前登录用户ID，随便填起止日期测试
    uid = request.user.id
    from datetime import date
    orders = get_order_list(uid, date(2020,1,1), date(2030,1,1))
    return render(request, "order_list.html", {"order_list":orders})

# 订单详情页
def order_detail(request,oid):
    print(oid)
    lines = get_order_detail(oid)
    print(lines)

    return render(request, "order_detail.html", {"order_line_list":lines})

#处理404
def handler404_views(request,exception):
    return render(request,"404.html",status=404)

#请求和响应对象
#还有一个模版请求对象
#可以在返回前修改
def test(request):
    print(request)
    print(type(request))
    print(request.method)
    return HttpResponse("这是一个测试界面")

#关于视图类
from django.views import View
class TestView(View):
    #这里是魔法，钩子方法，Django会自动判断请求类型
    def get(self,request):
        return HttpResponse("这是get请求")
    #
    def post(self,request):
        return HttpResponse("这是post请求")

#文件上传相关
from django.http import HttpResponseRedirect
from .forms import UploadFileForm


# ========== 书上核心：文件处理函数 ==========
def handle_uploaded_file(f):
    # 定义服务器保存路径（写死路径，书上原生写法）
    save_path = "upload_file.txt"
    # 二进制方式分块写入，适配大文件
    with open(save_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


# ========== 上传视图函数 ==========
def upload_file(request):
    if request.method == 'POST':
        # POST：接收表单 + 文件
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # 取出上传的文件对象，交给处理函数
            handle_uploaded_file(request.FILES['file'])
            # 跳转至成功页
            return HttpResponseRedirect('/myapp/success/')
    else:
        # GET：空表单，展示上传页面
        form = UploadFileForm()

    # 渲染上传页面
    return render(request, 'upload.html', {'form': form})


# 简单成功页视图
def success(request):
    return HttpResponse("文件上传成功！")

#csv文件生成
import csv
def export_student_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"]='attachment;filename="学生名单.csv"'
    writer=csv.writer(response)
    writer.writerow(["姓名","年龄","班级"])
    writer.writerow(["张三","18","高(三)"])
    writer.writerow(["李四","17","高(二)"])
    return response

#forms表单
from .forms import UserInfoForm
def get_user_info(request):
    if request.method=="POST":
        form=UserInfoForm(request.POST)
        if form.is_valid():
            #这里可以得到clean_data
            print(form.cleaned_data)
            return redirect('/myapp/welcome')
    form=UserInfoForm()
    return render(request,'user_forms_info.html',{'form':form})

def welcome(request):
    return HttpResponse("恭喜你，表单提交成功")



#ajax表单
from .forms import ProductForm
def is_ajax(request):
    return request.headers.get("x-requested-with")=="XMLHttpRequest"
def product(request):
    if request.method=="POST":
        form=ProductForm(request.POST)
        #数据校验
        if form.is_valid():
            #判断ajax
            if is_ajax(request):
                return render(request,'form.html',{'form':form})
            else:
                return HttpResponse("恭喜提交表单")
        #校验失败
        else:
            if is_ajax(request):
                return render(request,'form.html',{'form':form})
            else:
                return render(request,'product.html',{'form':form})

    #get提交

    else:
        form=ProductForm()
        return render(request,'product.html',{'form':form})

#view类和Ajax验证码
from .forms import ProductFormView
from django.views import View
class ProductView(View):
    def get(self,request):
        form=ProductFormView()
        return render(request,'product_view.html',{'form':form})

    def post(self, request):
        # 接收提交数据
        form = ProductFormView(request.POST)
        if form.is_valid():
            # 表单校验通过
            if is_ajax(request):
                return render(request, 'form_view.html', {'form': form})
            else:
                return HttpResponse("恭喜提交表单")
        else:
            # 表单/验证码校验失败
            if is_ajax(request):
                return render(request, 'form_view.html', {'form': form})
            else:
                return render(request, 'product_view.html', {'form': form})

#测试redis
from django.views.decorators.cache import cache_page

from .models import Product
@cache_page(60*10)
def product_redis(request):
    print("-----访问数据库查询-----")
    data_list=Product.objects.all()
    print(data_list)
    return render(request,'product_redis.html',{'data':data_list})

#自定义cache
from django.core.cache import cache

# 自定义函数缓存装饰器
def cached(expire=60):
    # 第二层：接收被装饰函数
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            # 拼接缓存key
            key = f"{func.__name__}_{args}_{kwargs}"
            # 查缓存
            result = cache.get(key)
            if result is not None:
                return result
            # 无缓存，执行原函数
            result = func(*args, **kwargs)
            # 写入redis缓存
            cache.set(key, result, expire)
            return result
        return inner
    return decorator

# 被缓存的业务函数
@cached(30)  # 缓存30秒
def get_username(uid):
    print('===正在执行数据库查询===')
    if uid == 1:
        return '张三'
    return '李四'

# 页面视图
def cache_test_view(request):
    name = get_username(1)
    return HttpResponse(f'用户姓名：{name}')

#vary验证
# 错误接口：/err/ 无Vary，全浏览器共用同一份Redis缓存
@cache_page(60*10)
def test_vary_err(request):
    ua = request.META["HTTP_USER_AGENT"]
    if "Firefox" in ua:
        return HttpResponse("🦊 Firefox专属页面")
    elif "Edg" in ua:
        return HttpResponse("🟦 Edge专属页面")
    elif "Chrome" in ua:
        return HttpResponse("🔵 Chrome专属页面")
    return HttpResponse("🟡 其他浏览器")

# 正确接口：/ok/ Vary拆分UA，Redis存多份缓存
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_control

#装饰器的执行顺序：1.进来是从上到下 2.运行是从里到外（从下到上）
#然后这个vary_on_headers没有实现在不同的浏览器有不同缓存
#看看cookie能不能做到
@cache_control(max_age=300)
@cache_page(60*10)
#不需要上面那个
@vary_on_headers("User-Agent")
def test_vary_ok(request):
    ua = request.META["HTTP_USER_AGENT"]
    if "Firefox" in ua:
        return HttpResponse("🦊 Firefox专属页面")
    elif "Edg" in ua:
        return HttpResponse("🟦 Edge专属页面")
    elif "Chrome" in ua:
        return HttpResponse("🔵 Chrome专属页面")
    return HttpResponse("🟡 其他浏览器")

#与cookie相关
from django.views.decorators.vary import vary_on_cookie

@cache_page(600)
@vary_on_cookie
def test_vary_cookie(request):
    if request.user.is_authenticated:
        return HttpResponse("登录页面")
    return HttpResponse("游客页面")


#cache-aside
from random import randint
def get_product_detail(product_id):
    cache_val=cache.get(product_id)
    if cache_val is not None:
        print("---从redis拿的---")
        return cache_val
    try:
        obj=Product.objects.get(pk=product_id)
        #随机过期时间，防止大量key同时过期，防止雪崩
        expire=600+randint(-300,300)
        cache.set(product_id,obj.name,timeout=expire)
        print("---从数据库拿的---")
        return obj.name
    #查不到加空值，防止穿透
    except Product.DoesNotExist:
        cache.set(product_id,None,timeout=60)
        print("---数据不存在---")
        return None

def product_one(request,pid):

    product_name=get_product_detail(pid)
    return render(request,"product_one.html",{"name":product_name})

#celery
from .tasks import handle_user_task

def celery_test(request):
    if request.method=='POST':
        user_name=request.POST.get("username","匿名")
        print('---开始执行异步---')
        print(user_name)
        handle_user_task.delay(user_name)
        return HttpResponse(f"提交成功！你输入的名字是{user_name},正在后台处理")

    return render(request,'celery_test.html')

#邮箱
from .forms import ProductSendEmailForm
from .tasks import notify_supplier
def product_send_email(request):
    if request.method=="POST":
        print('---这是POST请求---')
        form=ProductSendEmailForm(request.POST)
        print(form)

        if form.is_valid():
            #存入数据库
            data=form.save()
            print(data.id)
            notify_supplier.delay(data.id)
            return render(request,'product_send_email.html',{'form':ProductSendEmailForm(),'msg':'创建成功,邮件在发送中'})

    else:
        print('---GET请求---')
        form=ProductSendEmailForm()
        print(form)
        return render(request,'product_send_email.html',{'form':form})


#csrf漏洞
#在setting里关了csrf防御

def csrf_login(request):

    request.session['username']='普通用户'
    #HttpResponse可以直接写html标签
    return HttpResponse("登录成功！<a href='/myapp/csrf_profile'>进入个人中心</a>")

def csrf_profile(request):
    if request.method=="POST":
        new_name=request.POST.get("nickname","")
        if new_name:
            request.session["username"]=new_name

    name=request.session.get("username",'未登录')
    return render(request,"csrf_profile.html",{'name':name})


#sql
#由于冲突了
from django.db import connection as django_db_connection
def sql_injection(request):
    #默认为1
    id=request.GET.get('id',1)
    print(id)
    sql=f'SELECT * FROM sql_user WHERE id={id};'
    print(sql)
    #由于配置里面已经连接数据库了，所以直接写
    try:
        with django_db_connection.cursor() as cursor:
            cursor.execute(sql)
            result=cursor.fetchall()
            print(result)
            return HttpResponse(f'查询结果:{result}')

    except Exception as e:
        return HttpResponse(f'出错了:{str(e)}<br>执行的sql:{sql}')
    #这里和rabbitmq冲突了
    #出错了:'BlockingConnection' object has no attribute 'cursor'

#点击劫持
#加了装饰器就可以被劫持

from django.views.decorators.clickjacking import xframe_options_exempt
@xframe_options_exempt
def clickjacking(request):
    return render(request,'clickjacking.html')

#钓鱼curl

def forget_pwd(request):
    domain=request.get_host()
    token='reset_token_666'
    reset_url=f'http://{domain}/myapp/reset/{token}'
    mail_text=f"""
    【注意】疑似你的账号密码被盗
    请立即修改密码
    修改链接为<a href='{reset_url}'>这里<a/>         
    10分钟之类有效
    """
    return HttpResponse(mail_text)

def reset_pwd(request,token):
    print(token)
    return render(request,'reset_pwd.html',{"token":token})

#新的登录注册界面
from .models import MyUser
from .utils.password_hash import make_password, check_password

def register_view(request):
    """注册视图：生成PBKDF2哈希存入数据库"""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        raw_pwd = request.POST.get("password", "").strip()

        if not username or not raw_pwd:
            return HttpResponse("用户名和密码不能为空")
        if MyUser.objects.filter(username=username).exists():
            return HttpResponse("用户名已存在")

        # 生成密码哈希并存入数据库
        pwd_hash = make_password(raw_pwd)
        MyUser.objects.create(username=username, password_hash=pwd_hash)
        return redirect("/myapp/login")

    return render(request, "register.html")


def login_view(request):
    """登录视图：校验密码哈希"""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        raw_pwd = request.POST.get("password", "").strip()

        try:
            user = MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            # 为了防用户枚举，这里也可以统一返回“用户名或密码错误”
            return HttpResponse("用户名不存在")

        if check_password(raw_pwd, user.password_hash):
            request.session["uid"] = user.id
            return HttpResponse("登录成功！已写入session，可跳转到首页")
        else:
            return HttpResponse("密码错误")

    return render(request, "login.html")


#http basic auth
from functools import wraps
import base64
from django.contrib.auth import authenticate,login

#写装饰器
def http_basic_auth(func):
    @wraps(func)
    def _decorator(request,*args,**kwargs):
        auth_header=request.META.get("HTTP_AUTHORIZATION",'')
        if auth_header.startswith('Basic '):
            auth_token=auth_header.split(' ')[1]
            try:
                decoded_auth=base64.b64decode(auth_token).decode('utf-8')
                username,password=decoded_auth.split(':')
                user=authenticate(username=username,password=password)
                if user is not None:
                    login(request,user)
                    return func(request,*args,**kwargs)
            except Exception:
                pass
        return HttpResponse('Unauthorized',status=401)
    return _decorator

#受保护的视图
@http_basic_auth
def basic_protected(request):
    return HttpResponse(f'Basic Auth 验证成功！当前用户问为:{request.user.username}')

#jwt
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views import View
#增加过期时间
from datetime import datetime,timedelta


#这里还要加上csrf临时取消
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self,request):
        username=request.POST.get('username')
        password=request.POST.get('password')

        if not username or not password:
            return JsonResponse({'err':'缺少用户名或密码'},status=400)
        #用django的内部方法检查
        user=authenticate(username=username,password=password)
        if not user:
            return JsonResponse({'err':'用户名或密码错误'},status=401)

        print('---开始构造jwt---')
        #构造jwt
        payload={
            'id':user.id,
            'username':user.username,
            #防止令牌永久有效
            'exp':datetime.utcnow()+timedelta(hours=1)
        }
        print('---开始生成jwt---')
        #生成jwt
        token=jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256')

        print(token)
        return JsonResponse({'token':token})


class ProtectView(View):
    def get(self,request):
        auth_header=request.META.get('HTTP_AUTHORIZATION','')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'err':'请携带Bearer Token'},status=401)
        token=auth_header.split(' ')[1]
        try:
            payload=jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            return JsonResponse({'err':'Token已过期'},status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'err':'无效的Token'},status=401)

        #返回用户信息
        return JsonResponse({
            "msg":'jwt验证成功',
            "user_id":payload['id'],
            "username":payload['username'],
        })

#有关签名验证的
import hashlib
import hmac

AK_SK_MAP={
    "demo_ak_001":"demo_sk_123456abcdef"
}
SING_ALG="HMAC-SHA256"
AUTH_PREFIX='CANONICAL'
#照搬客户端
#自己的思考过程，其实这就是一个对称算法的真实实现
#客户端和服务端存着私钥
#然后客户端通过发请求，把自己的加密算法，公钥，和签名（也就是算出来的值）
#服务端在计算一遍
#所以正确的做法是服务端解析请求
#然后根据不同的请求做不同的算法，得到最终结果
def build_sign(alg,method,params,uri,sk):
    sorted_items=sorted(params.items(),key=lambda x:x[0])
    query_str="&".join([f"{k}={v}" for k,v in sorted_items])
    canonical_req=f"{method}\n{uri}\n{query_str}"
    sha_res=hashlib.sha256(canonical_req.encode('utf-8')).hexdigest()
    str_to_sign=f"{alg}\n\n{sha_res}"
    sign=hmac.new(sk.encode('utf-8'),str_to_sign.encode('utf-8'),hashlib.sha256).hexdigest()
    return sign

#签名校验的视图函数
def sign_verify(request):
    auth_str=request.META.get("HTTP_AUTHORIZATION",'')
    if not auth_str.startswith(AUTH_PREFIX):
        return HttpResponse("头部格式错误",status=401)
    #拆分 前缀，算法，AK，客户端的签名

    try:
        _,alg,ak,client_sign=auth_str.split(" ")
    except:
        return HttpResponse("Authorization拆分失败",status=401)

    #检验ak是否存在
    if alg != SING_ALG or ak not in AK_SK_MAP:
        return HttpResponse("非法AK或算法不支持",status=401)

    sk=AK_SK_MAP[ak]

    #服务器重新算
    server_sign=build_sign(
        alg=alg,
        method=request.method,
        params=request.GET.dict(),
        uri=request.path,
        sk=sk,
    )

    #对比签名
    print(f'客户端的{client_sign}')
    print(f"服务端的{server_sign}")
    if server_sign==client_sign:
        return HttpResponse("✅️签名验证通过，可以正常访问接口数据",status=200)
    else:
        return HttpResponse("❌️签名不一致，拒绝访问",status=401)

#测试session用redis+数据库缓存
def session_login(request):
    request.session["uid"]=100001
    request.session['username']='tset_user'
    request.session['is_login']=True
    #设置过期时间,30分钟过期
    request.session.set_expiry(1800)
    return HttpResponse('欢迎登录，session已存入redis+数据库')

#检查登录状态
def session_check_login(request):
    uid=request.session.get("uid")
    username=request.session.get("username")
    if not uid:
        return HttpResponse('未登录')
    return HttpResponse(f"登录正常,用户id:{uid},用户名:{username}")
#退出登录
def session_logout(request):
    request.session.flush()
    return HttpResponse("退出成功，session已清空")
#清理过期的session
def session_expire_clear(request):
    request.session.clear_expired()
    return HttpResponse("已清理Redis和数据库中过期的会话")

#CAL
@login_required()
def admin_user_list(request):
    print(f'当前用户名{request.user.username}')
    print(f'当前用户is_superuser:{request.user.is_superuser}')
    return HttpResponse('后台：全部用户数据列表')

@login_required()
def admin_data_export(request):
    print(f'当前用户名{request.user.username}')
    print(f'当前用户is_superuser:{request.user.is_superuser}')
    return HttpResponse('后台：导出全站统计数据')

def home(request):
    return HttpResponse('首页:所有用户都可以访问')

#rabc
from django.contrib.auth.models import User,Group,Permission
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from .models import Task

#1.初始化用户，分组，权限
def init_perm_data(request):
    #创建测试账号
    #解释：
    #1.get_or_create()返回两个参数，_表示后面一个参数不要
    #这是约定俗成的
    #2.直接写password说明吧明文存进数据库
    #这样只能用if之类的来判断
    #用authenticate的话要换一个方法，因为会自动加密
    user,_=User.objects.get_or_create(username='testuser')
    #这样写的话就能把密码变成密文
    user.set_password('123456')
    user.save()
    #创建角色分组
    staff_group,_=Group.objects.get_or_create(name='普通员工组')

    #获取模型对应权限
    task_ct=ContentType.objects.get_for_model(Task)
    view_perm=Permission.objects.get(codename='view_task',content_type=task_ct)
    close_perm=Permission.objects.get(codename='close_task',content_type=task_ct)

    #用户加入分组
    #这里指上面的user，就是那个testuser
    user.groups.add(staff_group)

    #分组分配查看权限
    #这个自定义‘普通员工组’加权限
    staff_group.permissions.add(view_perm)
    #单独给用户额外关闭权限
    #单独给人加权限
    user.user_permissions.add(close_perm)

    return HttpResponse('初始化完成，账号testuser 密码123456')

#方式1：视图内部手动判断权限
@login_required
def task_list_manual(request):
    if not request.user.has_perm('myapp.view_task'):
        return HttpResponse('403 无查看任务权限',status=403)
    tasks=Task.objects.all()
    return render(request,'task_list.html',{'task':tasks})

#方式2：装饰器快速校验权限
@login_required
@permission_required('myapp.close_task')
def close_task(request):
    #不需要自己写来判断有无权限
    return HttpResponse('操作成功，关闭任务接口')

def rbac_login(request):
    msg=''
    if request.method=="POST":
        uname=request.POST.get('username')
        pwd=request.POST.get('password')
        user=authenticate(username=uname,password=pwd)
        if user:
            #有了这个login(),就会自动存cookie，session
            login(request, user)
            return redirect('task_list')
        else:
            msg='账号密码错误'

    return render(request,'rbac_login.html',{'msg':msg})




#test
#如果只是测试，不需要写html
from .models import TestProduct

def test_test_home(request):
    return render(request,'test_home.html')

def test_test_login(request):
    if request.method=="POST":
        user=authenticate(username=request.POST.get('username'),password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('test_product_list')
    return render(request,'test_login.html')

def test_test_product_list(request):
    name=request.GET.get('name','')
    products=TestProduct.objects.all()
    if name:
        products=products.filter(title=name)
    return render(request,'test_product_list.html',{'products':products,'user':request.user})

def test_test_redirect_demo(request):
    return redirect('test_product_list')

def test_test_upload_view(request):
    if request.method=="POST":
        return render(request,'test_upload.html',{'msg':'上传成功'})
    return render(request,'test_upload.html')