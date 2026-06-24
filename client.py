#这是一个模拟客户端，为了验证签名认证
import hashlib
import hmac
import requests


#双方完全一致的秘钥对
ACCESS_KEY_ID='demo_ak_001'
SECRET_KEY='demo_sk_123456abcdef'
SING_ALG='HMAC-SHA256'

def build_sign(alg,method,params,uri,sk):
    sorted_items=sorted(params.items(),key=lambda x:x[0])
    query_str="&".join([f"{k}={v}" for k,v in sorted_items])
    canonical_req=f"{method}\n{uri}\n{query_str}"
    sha_res=hashlib.sha256(canonical_req.encode('utf-8')).hexdigest()
    str_to_sign=f"{alg}\n\n{sha_res}"
    sign=hmac.new(sk.encode('utf-8'),str_to_sign.encode('utf-8'),hashlib.sha256).hexdigest()
    return sign

if __name__=='__main__':
    req_method="GET"
    #这里要严格写/，必须和真实的一模一样。
    req_uri="/myapp/api/sign/demo"
    target_url="http://127.0.0.1:8000/myapp/api/sign/demo"
    req_params={"action":"get_goods","name":"apple","num":"10"}

    #生成签名
    final_sign=build_sign(SING_ALG,req_method,req_params,req_uri,SECRET_KEY)
    print(f"最后签名{final_sign}")
    #拼接Authorization请求头，格式固定：CANONICAL 算法AK 签名
    auth_header=f"CANONICAL {SING_ALG} {ACCESS_KEY_ID} {final_sign}"
    headers={"Authorization":auth_header}

    #发起请求
    resp=requests.get(target_url,headers=headers,params=req_params)
    print("状态码",resp.status_code)
    print("返回内容",resp.text)