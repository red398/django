#设置一个中间件
#记得去settings注册
from django.http import HttpResponse
from django.urls import resolve
class ACLMiddleware:
    def __init__(self,get_response):
        self.get_response=get_response
        #ACL配置，所有需要管理员权限的接口路由名
        self.ACL_ADMIN_ROUTES=[
            "admin_user_list",
            "admin_data_export",
        ]

    def __call__(self,request):
        #先执行视图逻辑拿到响应
        response=self.get_response(request)

        #1.未登录用户直接放行，交给@login_required拦截
        if not request.user.is_authenticated:
            return response

        #获取当前访问接口的路由名称
        current_route=resolve(request.path_info).url_name

        #2.ACL核心校验，管理员接口只能超级用户访问
        if current_route in self.ACL_ADMIN_ROUTES:
            if not request.user.is_superuser:
                return HttpResponse("403 Forbidden:仅管理员账号可以访问",status=403)

        return response