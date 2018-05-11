# coding=utf-8

import base64
import datetime
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import requests



class Client(object):
    # 此处填写APIKEY

    ACCESS_KEY = " "
    SECRET_KEY = " "

    # API 请求地址
    MARKET_URL = "https://api.huobi.pro"
    TRADE_URL = "https://api.huobi.pro"

    # 首次运行可通过get_accounts()获取acct_id,然后直接赋值,减少重复获取。
    ACCOUNT_ID = None

    # 'Timestamp': '2017-06-02T06:13:49'

    def http_get_request(self,url, params, add_to_headers=None):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        }
        if add_to_headers:
            headers.update(add_to_headers)
        postdata = urllib.parse.urlencode(params)
        response = requests.get(url, postdata, headers=headers, timeout=5)
        try:

            if response.status_code == 200:
                return response.json()
            else:
                return
        except BaseException as e:
            print("httpGet failed, detail is:%s,%s" % (response.text, e))
            return

    def http_post_request(self,url, params, add_to_headers=None):
        headers = {
            "Accept": "application/json",
            'Content-Type': 'application/json'
        }
        if add_to_headers:
            headers.update(add_to_headers)
        postdata = json.dumps(params)
        response = requests.post(url, postdata, headers=headers, timeout=10)
        try:

            if response.status_code == 200:
                return response.json()
            else:
                return
        except BaseException as e:
            print("httpPost failed, detail is:%s,%s" % (response.text, e))
            return

    def api_key_get(self,params, request_path):
        method = 'GET'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params.update({'AccessKeyId': self.ACCESS_KEY,
                       'SignatureMethod': 'HmacSHA256',
                       'SignatureVersion': '2',
                       'Timestamp': timestamp})

        host_url = self.TRADE_URL
        host_name = urllib.parse.urlparse(host_url).hostname
        host_name = host_name.lower()
        params['Signature'] = self.createSign(params, method, host_name, request_path, self.SECRET_KEY)

        url = host_url + request_path
        return self.http_get_request(url, params)

    def api_key_post(self,params, request_path):
        method = 'POST'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params_to_sign = {'AccessKeyId': self.ACCESS_KEY,
                          'SignatureMethod': 'HmacSHA256',
                          'SignatureVersion': '2',
                          'Timestamp': timestamp}

        host_url = self.TRADE_URL
        host_name = urllib.parse.urlparse(host_url).hostname
        host_name = host_name.lower()
        params_to_sign['Signature'] = self.createSign(params_to_sign, method, host_name, request_path, self.SECRET_KEY)

        url = host_url + request_path + '?' + urllib.parse.urlencode(params_to_sign)
        return self.http_post_request(url, params)

    def createSign(self,pParams, method, host_url, request_path, secret_key):
        # [(AccessKeyID, xxxx-aaaa),(SignatureMethod,xxxx-aaaaa) ....]
        sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)

        # AccessKeyId=e2xxxxxx-99xxxxxx-84xxxxxx-7xxx
        # x&SignatureMethod=HmacSHA256&SignatureVersion=2&Timestamp=2017-05-11T15%3A19%3A30&order-id=1234567890
        encode_params = urllib.parse.urlencode(sorted_params)
        #GET\n
        #api.huobi.pro\n
        #/v1/order/orders\n
        #AccessKeyId=e2xxxxxx-99x
        payload = [method, host_url, request_path, encode_params]
        payload = '\n'.join(payload)

        payload = payload.encode(encoding='UTF8')
        secret_key = secret_key.encode(encoding='UTF8')
        # Using secret key to sign it
        digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
        # Base64 update
        signature = base64.b64encode(digest)
        # URI decode
        signature = signature.decode()
        return signature
