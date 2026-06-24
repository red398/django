from django.urls import path
from . import views

#视图类的路由
from .views import TestView, product_one, celery_test, product_send_email, csrf_login, csrf_profile, sql_injection, \
    clickjacking, forget_pwd, reset_pwd, register_view, login_view, basic_protected, LoginView, ProtectView, \
    sign_verify, session_login, session_check_login, session_logout, session_expire_clear, admin_user_list

urlpatterns=[
    #path('',views.index),
    path('profile/', views.show_profile),  # 展示信息
    path('update/', views.update_profile),  # 修改信息
    path('myorder/', views.my_order, name="my_order"),
    path('order/<int:oid>/', views.order_detail, name="order_detail"),
    path('test',views.test),
    #必须要写.as_view()
    path('test_views_class',TestView.as_view()),

    #这是文件上传
    # 上传页面路由
    path('upload/', views.upload_file, name='upload'),
    # 上传成功页路由
    path('success/', views.success, name='success'),

    #csv
    path('csv',views.export_student_csv),

    #forms
    path('welcome',views.welcome),
    path('user/info',views.get_user_info),

    #ajax
    path('product',views.product),
    #ajax_view
    path('product_view',views.ProductView.as_view()),

    #redis
    path('product_redis',views.product_redis),
    #自定义cache
    path('test_redis',views.cache_test_view),

    #测试vary
    path('test_vary_err',views.test_vary_err),
    path('test_vary_ok',views.test_vary_ok),
    path('test_vary_cookie',views.test_vary_cookie),

    #测试cache-aside
    path('product_one/<int:pid>/',product_one),

    #测试celery
    path('celery_test',celery_test),

    #测试邮件
    path('test_email',product_send_email),

    #csrf
    path('csrf_login',csrf_login),
    path('csrf_profile',csrf_profile),

    #sql
    path('sql',sql_injection),

    #点击劫持
    path('clickjacking',clickjacking),

    #白名单和http的host
    path('forget_pwd',forget_pwd),
    path('reset/<str:token>',reset_pwd),

    #注册登录界面
    path("register",register_view, name="register"),
    path("login",login_view, name="login"),

    #auth basic
    path('auth_basic',basic_protected),

    #jwt
    path('api/login',LoginView.as_view()),
    path('api/protected',ProtectView.as_view()),

    #验证签名
    path("api/sign/demo",sign_verify,name="sign_demo"),

    #session+数据库
    path('session/login',session_login),
    path('session/check_login',session_check_login),
    path('session/logout',session_logout),
    path('session/expire',session_expire_clear),

    #ACL
    path('admin/user',admin_user_list,name='admin_user_list'),
    path('admin/export',views.admin_data_export,name='admin_data_export'),

    #rbac
    path('rbac/init',views.init_perm_data,name='init_perm'),
    path('rbac/login',views.rbac_login,name='rbac_login'),
    path('rbac/task_list',views.task_list_manual,name='task_list'),
    path('rbac/task_close',views.close_task,name='task_close'),

    #test
    path('test/login',views.test_test_login,name='test_login'),
    path('test/product/list',views.test_test_product_list,name='test_product_list'),
    path('test/upload',views.test_test_upload_view,name='test_upload_file'),
    path('test/redirect_demo',views.test_test_redirect_demo,name='test_redirect_demo'),
    path('test/home',views.test_test_home,name='test_home'),

]