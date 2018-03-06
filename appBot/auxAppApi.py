# coding: utf8
import sys
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from db_model.auxAccount import auxAccount
from db_model.Order import Order
from db_model.AuxOrder import AuxOrder
from db_model.OrderImg import OrderImg
from db_model.OrderCode import OrderCode
from db_model.db import DBSession
import db_model.db as db
import time
import oss2
import utils
import configparser
import requests
import mysql.connector
import json
from aux_api import AuxApi
from Utils import image_mark
from datetime import datetime

class auxAppApi:
	"""aux app api"""
	# config.stage.conf
	def __init__(self, conf_file = './config.conf'):
		#config
		conf = configparser.ConfigParser()
		conf.read(conf_file)

		self.aux_base_url = conf['AUX']['aux_base_url']

		self.mysql_host = conf['MYSQL']['mysql_host']
		self.mysql_user = conf['MYSQL']['mysql_user']
		self.mysql_pwd = conf['MYSQL']['mysql_pwd']
		self.mysql_db = conf['MYSQL']['mysql_db']
		self.mysql_port = conf['MYSQL']['mysql_port']
		
		self.aux_accessKeyId = conf['OSS']['aux_accessKeyId']
		self.aux_accessKeySecret = conf['OSS']['aux_accessKeySecret']
		self.aux_ossbase_url = conf['OSS']['aux_ossbase_url']
		self.aux_endpoint = conf['OSS']['aux_endpoint']
		self.aux_object_base = conf['OSS']['aux_object_base']
		self.aux_bucket = conf['OSS']['aux_bucket']
		self.aux_user_agent = conf['OSS']['aux_user_agent']

		self.headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'Connection': 'Keep-Alive',
			'Accept-Encoding': 'gzip',
			'User-Agent': 'okhttp/3.8.1'
		}

		self.system_name = 'Aux bot'

	# 登录授权操作
	def auth(self,userid = '33580'):
		print(userid)
		userid = str(userid)
		session = DBSession()
		ret = session.query(auxAccount).filter(auxAccount.aux_id_number==userid).all()
		if ret:
			self.account = ret[0]
		else:
			return utils.errorReport('查无用户,aux_userid:' + userid + "ord_id:" + self.ord_id,system_name = self.system_name)
		print(self.account.aux_serial_number)
		element = self.login2("123456",self.account.aux_serial_number,'')
		print(element['username'])
		print(element['channelid'])
		if element == False:
			return element
		self.account.token = element['token']
		self.token = element['token']
		self.userid = userid
		self.adminid = element['adminid']
		self.account.channelid = element['channelid']
		self.account.aux_adminid = element['adminid']
		session.add(self.account)
		session.commit()
		session.close()
		kickoff_element = self.kickoff(element)
		print(json.dumps(kickoff_element))
		if kickoff_element == False:
			return kickoff_element
		return self.addchannel(kickoff_element)
	
	# 登录
	def login2(self,password='123456',mobile = 'aux0283070198', imei=''):
		#md5 password
		password = utils.getMd5(password)
		url = self.aux_base_url + 'login2/'

		requestData = {'password':password,'mobile':mobile,'imei':''}
		res_obj = utils.request(url = url,method = 'get',data = requestData)

		if res_obj['ret']!='13':
			return utils.errorReport(res_obj['msg']+ ",account:" + mobile + ' ord_id:'+self.ord_id+" "+sys._getframe().f_code.co_name,system_name = self.system_name)
		return res_obj['element']

	def kickoff(self,element):
		url = self.aux_base_url + 'kickoff/'
		requestData = {
			'password':element['password'],
			'mobile': element['mobile'],
			'imei':'',
			'channelid':element['channelid']
		}
		r = utils.request(url = url,method = 'get',data = requestData,timeout = 30)

		if str(r.get('ret')) is not '0':
			return utils.errorReport(r['msg']+' '+sys._getframe().f_code.co_name,system_name = self.system_name)
		return r['element']

	def addchannel(self,element):
		""" add channel 类似Jpush的jid"""
		url = self.aux_base_url + 'addchannel/'
		requestData = {'userid':element['userid'],'channelid':element['channelid'],'token':element['token']}
		r = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		print('addchannel',r.get('ret'))
		if r.get('ret') != u'0':
			return utils.errorReport(r['msg']+' '+sys._getframe().f_code.co_name,system_name = self.system_name)
		return r

	def mastergetfinish(self,userid,token,pagesize = 20,page = 1):
		"""get finish order"""
		url = self.aux_base_url + 'mastergetfinish/'
		requestData = {'pagesize':pagesize,'page':page,'type':'3','userid':userid,'token':token}
		# response = requests.post(url,data = requestData,headers = headers)
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)

		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+' '+sys._getframe().f_code.co_name,system_name = self.system_name)
		# do something
		if len(obj['element'] == pagesize):
			page += 1
			mastergetfinish(self,userid,token,pagesize = 20,page=page)
		else:
			return obj['element']

	def mastergetwait(self, userid, token, pagesize = 20, page = 1):
		userid,token,pagesize,page = map(str,[userid,token,pagesize,page])
		print(userid,token,pagesize,page)
		print('/Api/Index/mastergetwait/')
		url = self.aux_base_url + 'mastergetwait/'
		print(url)
		requestData = {'pagesize':pagesize,'page':page,'userid':userid,'token':token}
		
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		print('mastergetwait:',json.dumps(obj))
		print(json.dumps(obj))
		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+" "+sys._getframe().f_code.co_name,system_name = self.system_name)
		# do something
		if len(obj['element']) == pagesize:
			page = int(page)+1
			self.mastergetwait(self, userid, token, pagesize = 20, page = page)
		else:
			if len(obj['element']) > 0:
				self._after_mastergetwait(obj['element'])
			return obj['element']

	def _after_mastergetwait(self,obj):
		session = DBSession()
		for item in obj:
			isexists = session.query(AuxOrder).filter(AuxOrder.aux_orderno == item['orderno']).all()
			if isexists:
				aux = isexists[0]
				aux.json_detail = json.dumps(item)
				session.add(aux)
		session.commit()
		session.close()

	# 处理中的订单
	def mastergetservice2(self,userid,token,pagesize = 20,page = 1):
		userid,token,pagesize,page = map(str,[userid,token,pagesize,page])
		url = self.aux_base_url + 'mastergetservice2/'
		requestData = {'pagesize':pagesize,'page':page,'userid':userid,'token':token}
		# response = requests.post(url,data = requestData,headers = headers)
		print('data:',json.dumps(requestData))
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		print('headers:',json.dumps(self.headers))
		print('mastergetservice2:',json.dumps(obj))
		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+" "+sys._getframe().f_code.co_name,system_name = self.system_name)
		# do something
		if len(obj['element'][0]['detail']) == pagesize or len(obj['element'][1]['detail']) == pagesize or len(obj['element'][2]['detail']) == pagesize:
			page = int(page)+1
			mastergetservice2(self, userid, token, pagesize = 20, page = page)
		else:
			self._after_mastergetservice2(obj['element'])
			return obj['element']

	def _after_mastergetservice2(self,lists):
		session = DBSession()
		for item in lists:
			if len(item['detail']) == 0:
				continue
			for order in item['detail']:
				isexists = session.query(AuxOrder).filter(AuxOrder.aux_orderno == order['orderno']).all()
				if isexists:
					aux = isexists[0]
					aux.json_detail = json.dumps(order)
					session.add(aux)
		session.commit()
		session.close()
	# 在线报告
	def ismonline(self,userid,token):
		url = self.aux_base_url + 'ismonline/'
		requestData = {'userid':userid,'token':token}
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+ " "+sys._getframe().f_code.co_name,system_name = self.system_name)
		else:
			return obj

	# acceptorder 接单
	def acceptorder(self,acceptlat,orderno,acceptlng,userid,token,operator = None):
		acceptlat,orderno,acceptlng,userid,token = map(str,[acceptlat,orderno,acceptlng,userid,token])
		url = self.aux_base_url + 'acceptorder/'
		requestData = {'acceptlat':acceptlat,'orderno':orderno,'acceptlng':acceptlng,"userid":userid,'token':token}
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+' ord_id:'+self.ord_id+" "+sys._getframe().f_code.co_name,system_name = self.system_name)
		self._after_accept(operator = operator,userid = userid)
		return obj

	def _after_accept(self,operator,userid):
		utils.orderTracking(ord_id = operator['ord_id'],
                            operator_id = operator['operator_id'],
                            operator_name = operator['operator_name'],
                            title = '师傅帮家系统接单',
                            desc = operator['operator_name'] + '操作/帮家接单成功['+userid+']',
                            add_time = time.time())

	# get machinelist for order
	def machinelist(self,orderno,userid,token):
		url = self.aux_base_url + 'machinelist/'
		requestData = {'orderno':orderno,'userid':userid,'token':token}
		# response = requests.post(url,data = requestData,headers = headers)
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+" "+sys._getframe().f_code.co_name,system_name = self.system_name)
		return obj

	# 内机stype=N/外机W,验证内外机条码
	def getmachinedetail(self,sn,userid,token,sntype='N'):
		url = self.aux_base_url + 'getmachinedetail/'
		requestData = {'sntype':sntype,'sn':sn,'userid':userid,'token':token}
		return utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)

	# add install machine
	def addinstallmachine(self,requestData,retry = 1,operator = None):
		print(operator)
		print(operator['ord_id'])
		url = self.aux_base_url + 'addinstallmachine/'
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		if obj['ret'] !='0' and retry == 1:
			retry = retry + 1
			self.acceptorder(requestData['lat'],requestData['orderno'],requestData['lng'],requestData['userid'],requestData['token'],operator = operator)
			obj = self.addinstallmachine(requestData,retry,operator = operator)
		if obj['ret'] !='0' and retry > 1:
			return utils.errorReport(obj['msg']+' ord_id:'+ self.ord_id + " " + sys._getframe().f_code.co_name,system_name = self.system_name)
		self._after_addinstall(requestData = requestData,operator = operator)
		return obj

	def _after_addinstall(self,requestData,operator):
		utils.orderTracking(ord_id = operator['ord_id'],
                            operator_id = operator['operator_id'],
                            operator_name = operator['operator_name'],
                            title = '帮家系统添加机器',
                            desc = operator['operator_name'] + '在帮家系统添加了一条机器.auxorderno:' + requestData['orderno'],
                            add_time = time.time())

	# finish order
	def finishorder2(self,data = [],operator = None):
		url = self.aux_base_url + 'finishorder2/'
		requestData = {
			'note':'',
			'orderno':data['orderno'],
			'lng':data['lng'],
			'userid':data['userid'],
			'machinemadedate':'',
			'yanbao':{},
			'isbatch':0,
			'token':data['token'],
			'tuoji':{},
			'price':0,
			'outprice':'',
			'accessory':{},
			'lat':data['lat']
		}

		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)

		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+' ord_id:' + self.ord_id + " " +sys._getframe().f_code.co_name,system_name = self.system_name)
		self._after_finish(data,operator)
		return obj
	
	def _after_finish(self,data,operator):
		session = DBSession()
		_auxorder = session.query(AuxOrder).filter(AuxOrder.aux_orderno == data['orderno']).all()
		auxorder = _auxorder[0]
		auxorder.is_pending = 0
		auxorder.is_finish = 1
		session.add(auxorder)
		session.commit()
		session.close()

		utils.orderTracking(ord_id = operator['ord_id'],
                            operator_id = operator['operator_id'],
                            operator_name = operator['operator_name'],
                            title = '师傅帮家系统完成订单',
                            desc = operator['operator_name'] + '在帮家系统完成了订单auxordno' + data['orderno'],
                            add_time = time.time())

	# add repair machine
	def addrepairmachine(self,data):
		url = self.aux_base_url + 'addrepairmachine/'
		requestData = {
			'orderno':data['orderno'],
			'repairinfo':data['repairinfo'],
			'piclist':data['piclist'],
			'lng':data['lng'],
			'guarantee':data['guarantee'],
			'userid':data['userid'],
			'mac':data['mac'],
			'machinetype':'空调',
			'token':data['token'],
			'buydate':data['buydate'],
			'traftype':data['traftype'],
			'servdesc':data['servdesc'],
			'kilometer2':data['kilometer2'],
			'appid':0,
			'sn':data['sn'],
			'brand':'奥克斯',
			'lat':data['lat'],
			'servmethod':data['servmethod']
		}

		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)

		if obj['ret'] !='0':
			return utils.errorReport(obj['msg']+' ord_id:'+ self.ord_id + " " +sys._getframe().f_code.co_name,system_name = self.system_name)
		return obj

	# 维修　故障现象配置获取
	def getfaultphenomenon(self,userid,token):
		userid,token = map(str,[userid,token])
		url = self.aux_base_url + 'getfaultphenomenon/'
		requestData = {'userid':userid,'token':token}
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+' '+sys._getframe().f_code.co_name,system_name = self.system_name)
		return obj['element']

	# 故障原因 配置获取
	def getfaultmaintain(self):
		url = self.aux_base_url + 'getfaultmaintain/'
		requestData = {'row_id':row_id,'userid':userid,'token':token}
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		
		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+' '+sys._getframe().f_code.co_name,system_name = self.system_name)
		return obj['element']

	# 故障代码　配置获取
	def getmaintainitem(self,row_id,userid,token):
		url = self.aux_base_url + 'getmaintainitem/'
		requestData = {'row_id':row_id,'userid':userid,'token':token}
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+' '+sys._getframe().f_code.co_name,system_name = self.system_name)
		return obj['element']

	# 换下件 配置
	def searchServDtlMateria(self,causeId,maintainItemId,flag,phenomenonId,materialTypeId,userid,token):
		url = self.aux_base_url + 'searchServDtlMateria/'
		requestData = {
			'causeId':causeId,
			'maintainItemId':maintainItemId,
			'flag':flag,
			'phenomenonId':phenomenonId,
			'materialTypeId':materialTypeId,
			'userid':userid,
			'token':token
		}
		obj = utils.request(url = url,method = 'post',data = requestData ,headers = self.headers)
		if obj['ret']!='0':
			return utils.errorReport(obj['msg']+' ' +sys._getframe().f_code.co_name,system_name = self.system_name)
		return obj['element']

	# def orderpic(self,file_path,orderno,userid):
	def orderpic(self,file_stream,orderno,userid):
		userid = str(userid)
		orderno = str(orderno)
		print('orderno,userid',orderno,userid)
		auth = oss2.Auth(self.aux_accessKeyId, self.aux_accessKeySecret)
		bucket = oss2.Bucket(auth, self.aux_endpoint, self.aux_bucket)
		print('file_stream type:',type(file_stream))
		print('aux_object_base:',self.aux_object_base)
		obj = self.aux_object_base + orderno + '-' + userid + '0_' + utils.getRandomStr(6) + '.jpg'
		print('obj:',obj)
		print('aux_ossbase_url:',self.aux_ossbase_url)
		picurl = self.aux_ossbase_url + obj
		print('picurl',picurl)
		response = bucket.put_object(obj, file_stream)
		print('upload response:',response)
		if format(response.status)!='200':
			return utils.errorReport('upload picture field,ord_id:' + self.ord_id + ",userid:" + userid,system_name = self.system_name)
		print('picurl',picurl)
		return picurl

	#业务处理
	def accept(self,data):
		orderinfo = db.find(Order,Order.ord_id == data['platform_orderid'])
		if len(orderinfo) < 1:
			return utils.errorReport('师傅接单错误,无订单:'+data['platform_orderid'],system_name = self.system_name)
		self.auth(userid = data['aux_userid'])
		print(orderinfo)
		return self.acceptorder(orderinfo['ord_cust_lat'],data['aux_orderno'],orderinfo['ord_cust_lng'],data['aux_userid'],self.token)
	
	def _before_addorder(self,data):
		pass
	
	def addinstall_orderpic_finish(self,data):
		'''
		add and finsh:data['addinstall'] , data['finish']
		'''
		print("addinstall_orderpic_finish")
		self.ord_id = data['operator']['ord_id']
		if data.get('add'):
			self.auxapi = AuxApi(data['add']['info']['account'],data['add']['info']['password'])
			add_dis = self.auxapi.add_dispatch(data['add'],operator = data['operator'])
			print('add_dis',add_dis)
			if add_dis is not True:
				print('建单派单失败')
				return False
			print("al add")
			ord_id = data['add']['info']['platform_orderid']
			auxorder = db.find(AuxOrder,AuxOrder.platform_orderid == str(ord_id))
			data['finish']['orderno'] = auxorder['aux_orderno']
			data['finish']['userid'] = auxorder['aux_userid']
		if data['finish']['userid'] is None:
			data['finish']['userid'] = '77181'
		print('before auth')
		self.auth(data['finish']['userid'])
		print('after auth')
		self.mastergetservice2(self.userid,token = self.token,pagesize = 20,page = 1)
		print('after mastergetservice2')
		self.mastergetwait(self.userid, self.token, pagesize = 20, page = 1)
		print('after mastergetwait')

		session = DBSession()
		_aux= session.query(AuxOrder).filter(AuxOrder.platform_orderid==data['operator']['ord_id']).all()
		aux = _aux[0]
		aux.is_pending = 1
		session.add(aux)
		json_detail = aux.json_detail
		aux_userid = aux.aux_userid
		session.commit()
		session.close()

		aux_account = db.find(auxAccount,auxAccount.aux_id_number==aux_userid)
		print('json_detail:',json_detail)
		if json.loads(json_detail)['lng'] is None:
			return utils.errorReport('The value of latitude and longitude is not allowed to be None.ord_id:'+data['operator']['ord_id'])
		distance = utils.distanceRange(lon1 = json.loads(json_detail)['lng'],
										lat1 = json.loads(json_detail)['lat'],
										lon2 = json.loads(json_detail)['lng'],
										lat2 = json.loads(json_detail)['lat'],
										maxdistance = 490)
		if distance is False:
			return utils.errorReport('经纬度距离超过450米,提交阻止.ord_id:' + data['operator']['ord_id'])
		
		data['finish']['lng'] = distance['lon2']
		data['finish']['lat'] = distance['lat2']
		print(distance)
		regeo = utils.baidumapdecode({'lat': distance['lat2'], 'lng': distance['lon2']})
		print(regeo)
		if regeo.get("result").get("addressComponent") is None:
			print('regeo field')
			return False
		
		for m in data['addinstall']:
			print('for addinstall 1')
			if vars().has_key('auxorder') is True:
				m['orderno'] = auxorder['aux_orderno']
				m['userid'] = auxorder['aux_userid']
			print('for addinstall 2')
			
			for pic in m['piclist']:
				print('for piclist 1')
				pic['finishlng'] = distance['lon2']
				pic['finishlat'] = distance['lat2']
				text1 = aux_account['aux_name'] + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				street_number = str(regeo["result"]["addressComponent"]["street_number"])
				if street_number != "" and u"号" not in street_number:
					street_number + "号"
				text2 = "在"+regeo["result"]["addressComponent"]["street"] + street_number + "附近"
				print(text2)
				IM = image_mark.ImageMark()
				# file_stream = IM.aux_mark(ttf_file = "./library/fonts/msyh.ttf",link = pic['picurl'],text1 = text1,text2 = text2)
				try:
					#有照片资源路劲无法访问的情况
					file_stream = IM.aux_mark(ttf_file = "./library/fonts/msyh.ttf",link = pic['picurl'],text1 = text1,text2 = text2)
				except Exception as e:
					return utils.errorReport(str(e) + '.ord_id:' + self.ord_id + '.url:' + pic['picurl'],system_name = self.system_name)
				picret = self.orderpic(file_stream,m['orderno'],m['userid'])
				print('for piclist 2')
				
				if picret is False:
					return utils.errorReport('aliyun oss upload picture field.ord_id:' + self.ord_id,system_name = self.system_name)
				pic['picurl'] = picret
			
			m['piclist'] = json.dumps(m['piclist'],encoding="UTF-8", ensure_ascii=False)
			m['token'] = self.token
			m['userid'] = self.userid
			m['lng'] = data['finish']['lng']
			m['lat'] = data['finish']['lat']
			print('add 1')
			
			addret = self.addinstallmachine(requestData = m,operator = data['operator'])
			print('add 2')
			if addret is False:
				return addret
		
		data['finish']['token'] = self.token
		data['finish']['userid'] = self.userid
		print('finish 1')
		
		finshret = self.finishorder2(data['finish'],operator = data['operator'])
		print('finish 2')
		if finshret is False:
			return finshret
		print('done')

	def allauth(self):
		account = db.select(auxAccount)
		for a in account:
			try:
				self.auth(a['aux_id_number'])
			except Exception as e:
				print(str(e))