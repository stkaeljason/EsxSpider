# coding: utf8

import time,datetime,json,string,requests,hashlib,random,pprint
from math import radians, cos, sin, asin, sqrt
from pymongo import MongoClient
import configparser
import urllib
import os,base64
import random

def get_out_ip():
	url = 'http://www.trackip.net/ip'
	r = requests.get(url = url,timeout = 60.0)
	return r.text

def is_product():
	return True if os.getenv('ENV') == 'production' else False

conf = configparser.ConfigParser()

if is_product() is True:
	conf.read('./config.conf')
else:
	conf.read('./config.stage.conf')

appid = conf['WX']['appid']
app_secret = conf['WX']['app_secret']
template_id = conf['WX']['template_id']

mongo_url = conf['MONGO']['MONGO_URL']

def request(url,method,data = {},headers = {},cookies = None,timeout=60):
	# print(url)
	method = method.lower()
	methods = ['get','post','delete','put','head','options','patch']
	
	if method not in methods:
		return errorReport('参数错误,method:' + method)
	
	try:
		# request
		if method == 'get':
			response = requests.get(url,params = data,headers = headers , cookies = cookies,timeout = timeout)
		if method == 'post':
			response = requests.post(url,data = data,headers = headers, cookies = cookies,timeout = timeout)
		if method == 'put':
			response = requests.put(url,data = data,headers = headers,timeout = timeout)
		if method == 'patch':
			response = requests.patch(url,data = data,headers = headers,timeout = timeout)
		if method == 'delete':
			response = requests.delete(url,data = data,headers = headers,timeout = timeout)

		try:
			# print(response.status_code)
			res = response.json()
		except:
			res = response.text if isinstance(response.text,unicode) is True else unicode(response.text, "utf-8")
		api_logs = {'client':getDomain(response.url),
					'method':method,
					'url':url,
					'status_code':response.status_code,
					'request_headers':response.request.headers,
					'request_data':data,
					'response_headers':response.headers,
					'response_data':response.text,
					'user_id':'system',#system
					'date':time.time()}
		# save logs to dm_api_logs collection
		if is_product() is True:
			MongoClient(mongo_url).ershixiong_anzhuang.dm_api_logs.insert_one(api_logs)

	except requests.exceptions.HTTPError as e:
		return errorReport(str(e) + str(response.status_code)+'url:' + url)
	
	except requests.exceptions.ConnectionError as e:
		return errorReport(str(e) + str(response.status_code)+'url:' + url)
	
	except requests.exceptions.Timeout as e:
		return errorReport(str(e) + str(response.status_code)+'url:' + url)
	
	except requests.exceptions.URLRequired as e:
		return errorReport(str(e) + str(response.status_code)+'url:' + url)
	
	except requests.exceptions.TooManyRedirects as e:
		return errorReport(str(e) + str(response.status_code)+'url:' + url)
	return res

def getDomain(url):
	proto,rest = urllib.splittype(url)
	res,rest = urllib.splithost(rest)
	return 'Unkonw' if not res else res.replace('www.','')

def getMd5(password):
	m = hashlib.md5()
	m.update(password)
	return m.hexdigest()

def errorReport(message,system_name = 'api bot',link = ''):
	if is_product() is False:
		system_name = system_name + " -local env"
	"""error report with wechat template message"""
	token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+appid+'&secret='+ app_secret
	token = request(url = token_url,method = 'get')
	touser = ['oJFSKw3iXFn3o7OZWQeunx5SZ7ms','oJFSKw2AGvKpiUIfZYkU6po-0L4E']
	url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token='+token['access_token']
	headers = {'Content-Type': 'application/json'}
	for openid in touser:
		data = dict()
		data = {
			"touser":openid,
			"template_id":template_id,
			"url":link,
			"data":{"first":{"value":"系统错误报告"},
				"keyword1":{"value":system_name},
				"keyword2":{"value":message},
				"remark":{"value":"请通知技术同学及时处理"}}
		}
		request(url = url,method = 'post', data = json.dumps(data),headers = headers)
	return False

def getRandomStr(len = 6):
	return ''.join(random.sample(string.ascii_letters + string.digits, len))

def saveApiLogs(data):
	if is_product() is True:
		return  MongoClient(mongo_url).ershixiong_anzhuang.dm_api_logs.insert_one(data)

def findall():
	for data in MongoClient(mongo_url).ershixiong_anzhuang.dm_api_logs.find():
		pprint.pprint(data)

def lnglat(address = '四川省成都市武侯区桂溪街道老成仁路8号育才竹岛1栋2506'):
	print(address)
	'''高德接口获取地址信息'''
	url = 'http://restapi.amap.com/v3/geocode/geo?key=e06375c81f3c371c5e0c4a31cb684f7d&address='+address+'&city='
	r = request(url = url,method = 'get')
	print(json.dumps(r))
	if r['count'] != '1':
		return errorReport('地址解析失败,by高德:' + address)
	location = r['geocodes'][0]['location'].split(',') #["104.507115", "30.493183"]
	res = dict()
	res['lng'] = location[0]
	res['lat'] = location[1]
	print('lnglat',res)
	return res

def regeo(location = '104.074389,30.533006'):
	'''反解经纬度'''
	url = 'http://restapi.amap.com/v3/geocode/regeo'
	data = {'extensions':'base','key':'e06375c81f3c371c5e0c4a31cb684f7d','location':location}
	ret = request(url = url,data = data,method = 'get')
	if HasAttrVar(ret,'status','0'):
		return errorReport(url + ' error:' + ret['errorMsg'])
	return ret

def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2
    lon1, lat1, lon2, lat2 = map(float, [lon1, lat1, lon2, lat2])
    # 将十进制数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # 地球平均半径，单位为公里
    return c * r #公里

def test():
	n = 0
	retry = 0
	e = 0
	while n < 10000000:
		lon = random.uniform(1, 105)
		lat = random.uniform(1, 50)
		distance = distanceRange(lon,lat,lon,lat)
		if distance is False:
			e = e+1
			print('eee')
		n = n+1
		print(n)
		# print(json.dumps(distance))
	print('e:',e)

def distanceRange(lon1, lat1, lon2, lat2,maxdistance = 450,limitdistance = 10,chrr = '9'):
	distance = _distanceRange(lon1, lat1, lon2, lat2,maxdistance,limitdistance,chrr)
	return distance if distance is not False else _distanceRange(lon1, lat1, lon2, lat2,maxdistance,limitdistance,chrr = '0')

def _distanceRange(lon1, lat1, lon2, lat2,maxdistance = 450,limitdistance = 10,chrr = '9',i = 0):
	lon1, lat1, lon2, lat2 = map(str,[lon1, lat1, lon2, lat2])
	while True:
		i = i + 1
		lat2 = buildLon(lat2,i,chrr)
		if lat2 is not False:
		 	distance = {"distance":float('%.4f' % haversine(lon1, lat1, lon2, lat2)),"lon1":lon1, "lat1":lat1, "lon2":lon2, "lat2":lat2}
		else:
			return False
		if distance['distance']*1000 <= maxdistance and distance['distance']*1000 > limitdistance:
			return distance

def buildLon(lon2,i,chrr = '9'):
	for x in xrange(len(lon2)):
		if x == len(lon2)-i and x > 3:
			return lon2[:x-1] + str(chrr) + lon2[x:]
	return False

def create_sn():
    nowobj = datetime.datetime.now();
    return nowobj.strftime('%Y%m%d%H%M%S') + str(nowobj.microsecond)


def wx_Report(message, link='', flag='error'):
    """error report with wechat template message"""
    token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+appid+'&secret='+ app_secret
    token = request(url = token_url,method = 'get')

    touser = 'oJFSKw3iXFn3o7OZWQeunx5SZ7ms'
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token='+token['access_token']
    headers = {'Content-Type': 'application/json'}

    if flag == 'error':
        data = {
            "touser":touser,
            "template_id":template_id,
            "url":link,
            "data":{"first":{"value":"系统错误报告","color":"red"},
                "keyword1":{"value":"aux bot"},
                "keyword2":{"value":message,"color":"red"},
                "remark":{"value":"请通知技术同学及时处理"}}
        }
    elif flag == 'captcha':
        data = {
            "touser":touser,
            "template_id":template_id,
            "url":link,
            "data":{"first":{"value":"请输入验证码","color":"green"},
                "keyword1":{"value":"aux bot"},
                "keyword2":{"value":message,"color":"greeen"},
                "remark":{"value":"请速度输入，3q--！"}}
        }
        ret = request(url=url,method = 'post', data = json.dumps(data),headers = headers)
	return False


def current_time():
	stamps = time.time()
	cur_time = time.strftime("%Y-%m-%d", time.localtime(stamps))
	start_time = time.strftime("%Y-%m-%d", time.localtime(stamps-24*60*60*7))
	return cur_time, start_time

def HasAttrVar(obj,attr,value = None):
	try:
		if obj[attr] is value:
			return True
	except Exception as e:
		return False

def orderTracking(ord_id,operator_id,operator_name,title,desc,add_time):
	'''
	ord_id,operator_id,operator_name,title,desc,add_time
	'''
	from db_model.OrderTracking import OrderTracking
	from db_model import db
	track = OrderTracking()
	track.ord_id = ord_id
	track.operator_id = operator_id
	track.operator_name = operator_name
	track.title = title
	track.desc = desc
	track.add_time = add_time
	# print(track.desc)
	db.session.add(track)
	db.session.commit()
	db.session.close()
	return True

def base64Img(filename):
	file=open(filename,'rb')  
	imgdata=base64.b64encode(file.read())
	file.close()
	return imgdata

def baidumap(address = '成都市郫都区郫筒镇犀浦镇银河西街99号合能橙中心 淘淘橙一期2栋2单元4楼6号'):
	'''
	'''
	url = 'http://api.map.baidu.com/geocoder/v2/?address='+address+'&output=json&ak=DHzYAzfC8cPdcBEVgksK5Nn4E5sc47D2'
	r = request(url = url,method = 'get')
	print(json.dumps(r))
	if r['status'] != 0:
		return errorReport('百度地址解析失败:' + address)
	return r['result']['location']

def baidumapdecode(location = {'lat': 30.607999999994, 'lng': 104.13092079604}):
	url = 'http://api.map.baidu.com/geocoder/v2/?location='+str(location['lat'])+','+str(location['lng'])+'&output=json&pois=1&ak=DHzYAzfC8cPdcBEVgksK5Nn4E5sc47D2'
	r = request(url = url,method = 'get')
	if r.get("status") is False:
		errorReport("经纬度反解析失败:baidumapdecode"+json.dumps(location))
	return r

#'2017-12-27 00:23:23'
def strtime_to_time(strdatetime):
	t = datetime.datetime.strptime(strdatetime,'%Y-%m-%d %H:%M:%S')
	return int(time.mktime(t.timetuple()))