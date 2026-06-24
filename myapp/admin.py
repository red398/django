from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Profile, Basket, Line, Product,
    Order, OrderLine, OrderNote,
    OrderStatusChange, CommunicationEvent
)

# 逐个注册模型
admin.site.register(Profile)
admin.site.register(Basket)
admin.site.register(Line)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(OrderNote)
admin.site.register(OrderStatusChange)
admin.site.register(CommunicationEvent)