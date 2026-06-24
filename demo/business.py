#业务代码（依赖接口，网络接口）
from requests.exceptions import Timeout
from datetime import datetime
import requests

#1.判断是否工作日（依赖系统时间）
def is_workday():
    today=datetime.today()
    #周一0~周五4=工作日
    return 0<=today.weekday()<5

#2.调用外部HTTP接口获取节假日（依赖真实网络服务）
def get_holiday():
    try:
        resp=requests.get('http://test-server/api/holiday')
        if resp.status_code==200:
            return resp.json()
        return None
    except Timeout:
        return None