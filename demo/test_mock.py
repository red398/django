#全套mock测试
import unittest
from unittest.mock import Mock,patch
from datetime import datetime
from requests.exceptions import Timeout
from business import is_workday,get_holiday

class TestMockFull(unittest.TestCase):
    #1.基础Mock测试创建假对象，校验调用次数、传参
    def test_basic_mock_assert(self):
        mock_json=Mock()
        mock_json.loads('{"date":"2026-06-22"}')

        #断言方法被调用1次，参数完全匹配
        mock_json.loads.assert_called_once_with('{"date":"2026-06-22"}')
        print('全部调用记录：',mock_json.loads.call_args_list)

    #2.return_value固定返回值：模拟系统时间
    @patch('business.datetime')
    #这里@patch会替换requests.get，伪造返回接口
    def test_mock_fixed_time(self,mock_dt):
        #模拟周二（工作日）
        tues=datetime(2026,6,23)
        mock_dt.today.return_value=tues
        self.assertEqual(is_workday(),True)
        #模拟周六（休息日）
        sat=datetime(2026,6,27)
        mock_dt.today.return_value=sat
        self.assertEqual(is_workday(),False)

    #3.side_effect用法1：手动制造超时异常，测试异常分支
    @patch('business.requests')
    def test_mock_raise_exception(self,mock_req):
        #强制接口抛出超时故障
        mock_req.get.side_effect=Timeout
        #业务捕获异常
        self.assertEqual(get_holiday(),None)

    #4.side_effect用户2：多次调用一次返回异常、正常数据
    @patch('business.requests')
    def test_mock_multi_result(self,mock_req):
        mock_response=Mock()
        mock_response.status_code=200
        mock_response.json.return_value={"10/1":"国庆节"}
        #第一次调用超时，第二次正常返回节日数据
        mock_req.get.side_effect=[Timeout,mock_response]
        self.assertEqual(get_holiday(),None)
        self.assertEqual(get_holiday()["10/1"],"国庆节")

    #5.path with上下文：仅代码块内生效，局部模拟
    def test_mock_scope_control(self):
        #仅with内部替换requests,出代码块自动恢复原始库
        with patch('business.requests') as mock_req:
            resp=Mock(status_code=200)
            resp.json.return_value={}
            mock_req.get.return_value=resp
            self.assertIsNotNone(get_holiday())

if __name__=='__main__':
    unittest.main(verbosity=2)