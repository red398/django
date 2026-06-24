"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from tkinter.font import names

from django.contrib import admin
from django.urls import path,include


#写一个主页
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,login,authenticate
#首页
def home(request):

    return render(request,'home.html')
#登录后界面
@login_required()
def index(request):
    return render(request,"index.html",{"user":request.user})

#新增账号密码登录
def login_page(request):
    if request.user.is_authenticated:
        return redirect('index')
    msg=''
    if request.method=="POST":
        uname=request.POST.get('username')
        pwd=request.POST.get('password')

        user=authenticate(username=uname,password=pwd)
        if user:
            login(request, user)
            return redirect('index')
        else:
            msg='用户名或者密码错误'
    return render(request,'login.html',{'msg':msg})


def user_logout(request):
    logout(request)
    return render(request,'home.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('myapp/',include('myapp.urls')),
    #验证码,记得后面加上/
    path('captcha/',include('captcha.urls')),

    #记得要数据库迁移
    path('social/',include('social_django.urls',namespace='social')),
    path('',home,name='home'),
    path('index/',index,name='index'),
    path('logout/',user_logout,name='logout'),

    #账号密码登录
    path('login/',login_page,name='login'),
]

handler404 = 'myapp.views.handler404_views'