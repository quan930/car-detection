# encoding:utf-8
import urllib.request
import urllib.parse
import base64
import json

request_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/detection/car0101"
access_token = '24.dcdc4fdcf38dd472c5566b9e97a73adb.2592000.1599453251.282335-21865104'

# 图片转base64
with open("abc.jpg", 'rb') as f:
    base64_data = base64.b64encode(f.read())
    s = base64_data.decode('UTF8')

params = {"image": s}
data = bytes(json.dumps(params), 'utf8')

request_url = request_url + "?access_token=" + access_token

request = urllib.request.Request(request_url, data)
request.add_header('Content-Type', 'application/json')

response = urllib.request.urlopen(request)
content = json.loads(response.read().decode())
if content:
    # 结果
    print(content)
