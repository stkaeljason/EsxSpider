# coding:utf-8
import json
import time
import redis
import datetime
import utils
import uuid
from multiprocessing.dummy import Pool as ThreadPool
import requests
import Queue
import threading
from db_model.mdAccount import MdAccount
from db_model.MideaMmpstore import MideaMmpstore
from db_model.Mdmmppictureconfig import Mdmmppictureconfig
from db_model.MdMmpregions import MdMmpregions
from db_model.MdSubmitcard import MdSubmitcard
from db_model.mdFactory import MdFactory
from db_model.MdMmprepairfault import MdMmprepairfault
from db_model.MdMmpFaultreson import MdMmpFaultreson
from db_model.MdMmpfaultmaint import MdMmpfaultmaint
from db_model.MdMmpmaterialinfos import MdMmpmaterialinfos
from db_model.MdMmpmaterialreplace import MdMmpmaterialreplace
from db_model.db import DBSession
from db_model import db

class MdAppApi():
    """美的通App api Author by Jon"""
    def __init__(self):
        # headers:
        self.UserAgent = 'Mozilla/5.0 (Linux; Android 5.1.1; NX511J_V3 Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/50.0.2661.86 Mobile Safari/537.36/mideaConnect'
        # self.UserAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60/mideaConnect/mideaConnect (396210176)'
        #url:
        self.base_url = 'http://map.midea.com/'
        self.maps_base_url = 'https://mapnew.midea.com/'
        self.postSale_url = self.maps_base_url + 'mas-api/restful/cssProIpmsUrl/api/mmp/'
        # self.postSale_url = self.maps_base_url + 'mas-api/restful/cssProIpmsUrl/api/mmp/repairarchives/'
        self.repair_url = self.maps_base_url + 'mas-api/restful/cssProIpmsUrl/api/mmp/repairarchives/'
        # c-css-ipms/api/mmp/
        self.map_base_url = 'http://map.midea.com/'
        self.cs_midea_url = 'https://cs.midea.com/'
        self.amap_base_url = 'https://restapi.amap.com/v3/'

        self.system_name = 'mdApp bot'

        self.sanshengxiang = {'lng':104.142168,'lat':30.588996}


    def login(self, user='18140038880', pw="BA8\/gHm93BA="):
        if user is None:
            return utils.errorReport("参数错误,账号不能为空",system_name = self.system_name)
        url = self.base_url + 'mapservice/user/login'
        headers = {
            'User-Agent':self.UserAgent,
            'Host':'map.midea.com',
            'content-Type':'application/json;charset=UTF-8'
        }
        data = {
                "appKey" : "27dce012d6b93e9cd9b60880f5ac1eb7",
                "username" : user,
                "password" : pw,
                "encrypt" : True
                }
        ret = utils.request(url, method='post', data=json.dumps(data), headers=headers)
        if utils.HasAttrVar(ret,'result',True):
            self.after_login(user,ret)
            return ret
        else:
            return utils.errorReport("登录错误:账号:" + user,system_name = self.system_name)

    def after_login(self,engineer_tel,ret):
        updateToken = self.updateToken(ret['content']['sessionKey'],username = engineer_tel,password = "BA8\/gHm93BA=")
        if updateToken:
            ret['content']['ssoToken'] = updateToken['content']['ssoToken']
        self.checkins(tel = engineer_tel)
        session = DBSession()
        accounts = session.query(MdAccount).filter(MdAccount.engineer_tel == engineer_tel).all()
        if accounts:
            account = accounts[0]
            account.login_ret = json.dumps(ret)
            account.last_login = time.time()
        else:
            mdAccount = MdAccount()
            mdAccount.engineer_tel = engineer_tel
            mdAccount.login_ret = json.dumps(ret)
            mdAccount.last_login = time.time()
            session.add(mdAccount)
        session.commit()
        session.close()
        self.h5add(ret['content']['sessionKey'],username = engineer_tel)
    
    def queue_init(self):
        self.in_queue = Queue.Queue()
        for i in range(2):
            t = threading.Thread(target = self.use_queue,args = (self.in_queue,))
            t.setDaemon(True)
            t.start()
        
        self.in_queue.join()

        self.in_queue_pre = Queue.Queue()
        for i in range(2):
            t = threading.Thread(target = self.use_queue_pre,args = (self.in_queue_pre,))
            t.setDaemon(True)
            t.start()
        
        self.in_queue_pre.join()

    def updateToken(self,sessionKey,username = '18140038880',password = "BA8\/gHm93BA="):
        url = self.base_url + 'mapservice/user/updateToken?sessionKey=' + sessionKey
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8',
            'locale': 'cn',
            'User-Agent': self.UserAgent,
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        data = {
            "appKey": "27dce012d6b93e9cd9b60880f5ac1eb7","password": password,"username": username
        }
        ret = utils.request(url,method = 'get',data = json.dumps(data),headers = headers)
        if utils.HasAttrVar(ret,'result',False):
            return utils.errorReport('updateToken field.info:' + json.dumps(ret),system_name = self.system_name)
        return ret

    def checkins(self,tel = '18140038880'):
        url = self.base_url + 'mapservice/push/checkins/tags'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8',
            'locale': 'cn',
            'User-Agent': self.UserAgent,
            'Host': 'map.midea.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        data = {
            "alias": tel,
            "appId": "27dce012d6b93e9cd9b60880f5ac1eb7",
            "appVersion": "1.1.7",
            "channelId": "openfire",
            "deviceId": "ffffffff-828b-bf7b-7cf7-aff6717d0f70",
            "deviceName": "NX511J_V3",
            "gis": "",
            "osName": "Android",
            "osVersion": "5.1.1",
            "pushToken": "A00000379AFE73",
            "tags": [{
                "key": "platform",
                "value": "Android"
            }, {
                "key": "role",
                "value": "CSS_SHGCS,com.midea.connect.out"
            }]
        }
        ret = utils.request(url = url,method = 'post',data = json.dumps(data),headers = headers)
        # {"result":true,"msgCode":"MSG_PUSH_TAG","erorrCode":null,"content":null}
        if utils.HasAttrVar(ret,'result',False):
            return utils.errorReport('checkins error:' + ret['erorrCode'],system_name = self.system_name)
        return ret

    def saveengineerposition(self,engineerCode1 = 'E0199658',engineerTel1 = '18140038880',lng = '104.152536,',lat = '30.589629'):
        '''
        '''
        url = self.cs_midea_url + 'c-css-ipms/api/mmp/saveengineerposition'
        data = {
            'orgCode':'',
            'engineerCode1':engineerCode1,
            'engineerTel1':engineerTel1,
            'longitude':lng,
            'latitude':lat,
            'status':''
        }
        headers = {
            'Accept': 'application/json',
            'locale': 'cn',
            'Host': 'cs.midea.com',
            'Connection': 'Keep-Alive'
        }
        r = utils.request(url = url,method = 'get',data = data,headers = headers)
        if utils.HasAttrVar(r,'status',False):
            utils.errorReport('saveengineerposition error:' + r['errorMsg'],system_name = self.system_name)
        return {"status":r['status'],"msg":r['errorMsg'],"type":'appsearchfromsn',"r":r}

    def orderprocesslist(self,engineerCode = 'E0199658',dateFlag = '',dispatchOrderStatus = '11;12;13;14;18',is_submit = '0',statusCondition=""):
        '''
        10是待接单'11;12;13;14;18'是待处理
        待处理:dateFlag:2=明天,0=今天,3=最近7天
        待接单:dateFlag:1
        /mas-api/proxy?alias=srm.postSale.orderprocesslist&engineerCode=E0199658&dispatchOrderStatus=10&resultNum=99&statusCondition=readytodo HTTP/1.1
        '''
        url = self.postSale_url + 'orderprocesslist'
        data = {
            'engineerCode':engineerCode,
            'dateFlag':dateFlag,#today
            'statusCondition':'readytodo',
            'dispatchOrderStatus':dispatchOrderStatus,
            'resultNum':'99',
            'statusCondition':statusCondition
        }
        headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out',
        }
        ret = utils.request(url = url,method = 'get',headers = headers,data = data,timeout = 10.0)
        if ret.get('status') is not True:
            utils.errorReport('获取今天待处理订单失败.info:' + ret['errorMsg'],system_name = self.system_name)
            return {"status":ret['status'],"msg":ret['errorMsg'],"type":'orderprocesslist',"r":ret}
        if len(ret['list']) > 0:
            # self._after_process(ret['list'])
            # if is_submit == '1':
            self._after_process_card(ret['list'],engineerCode=engineerCode)
        return {"status":ret['status'],"msg":ret['errorMsg'],"type":'orderprocesslist',"r":ret}
    
    # def getWaitacceptOrder(self):
        '''GET /mas-api/restful/cssProIpmsUrl/api/mmp/orderprocesslist?engineerCode=E0199658&dispatchOrderStatus=10&resultNum=99&statusCondition=readytodo'''
        # url = self.postSale_url + 'orderprocesslistorderprocesslist?engineerCode=E0199658&dispatchOrderStatus=10&resultNum=99&statusCondition=readytodo'
    
    def _after_process(self,lists):
        session = DBSession()
        for item in lists:
            try:
                model = session.query(MdFactory).filter(MdFactory.factorynumber == item['serviceOrderNo']).one()
                model.process = json.dumps(item)
                session.add(model)
            except Exception as e:
                mdFactory = MdFactory()
                mdFactory.service_order_id = item['serviceOrderId']
                mdFactory.factorynumber = item['serviceOrderNo']
                mdFactory.process = json.dumps(item)
                mdFactory.created_at = time.time()
                session.add(mdFactory)
        session.commit()
        session.close()
        print('save done')

    def _after_process_card(self,lists,engineerCode):
        session = DBSession()
        for item in lists:
            platform_id = None
            fac_model = session.query(MdFactory).filter(MdFactory.factorynumber == item['serviceOrderNo']).all()
            if fac_model:
                platform_id = fac_model[0].platform_id
            try:
                model = session.query(MdSubmitcard).filter(MdSubmitcard.service_orderno == item['serviceOrderNo']).one()
                model.detail_text = json.dumps(item)
                model.platform_id = platform_id
                model.install_desc = item['implementSubTypeName']
                model.engineer_code1 = engineerCode
                session.add(model)
            except Exception as e:
                submitcard = MdSubmitcard()
                submitcard.service_orderid = item['serviceOrderId']
                submitcard.service_orderno = item['serviceOrderNo']
                submitcard.install_desc = item['implementSubTypeName']
                submitcard.engineer_code1 = engineerCode
                submitcard.platform_id = platform_id
                submitcard.detail_text = json.dumps(item)
                submitcard.created_at = time.time()
                session.add(submitcard)
        session.commit()
        session.close()
        print('save done')

    def serviceorderlocklist(self,engineerCode = 'E0199658',orgCode = ''):
        url = self.postSale_url + 'serviceorderlocklist'
        data = {
            'engineerCode':engineerCode,
            'orgCode':orgCode,
            'resultNum':'99'
        }
        headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out',
        }
        ret = utils.request(url = url,method = 'get',headers = headers,data = data)
        if utils.HasAttrVar(ret,'status',False):
            return utils.errorReport('获取今天待处理订单失败.info:' + ret['errorMsg'],system_name = self.system_name)
        return ret
    
    def graborderlist(self,engineerCode = 'E0199658'):
        '''获取抢单列表'''
        url = self.postSale_url + 'graborderlist'
        data = {
            'engineerCode':engineerCode,'orgCode':'','resultNum':99
        }
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        ret = utils.request(url = url,method = 'get',data = data,headers = headers)
        if utils.HasAttrVar(ret,'status',False):
            return utils.errorReport('graborderlist error:' + ret['errorMsg'],system_name = self.system_name)
        return ret
    
    def httpGetEngineer(self,mobile = '18140038880'):
        '''
        获取工程师信息
        '''
        url = self.cs_midea_url + 'c-css-ipms/api/mmp/httpGetEngineer'
        headers = {
            'Accept': 'application/json',
            'locale': 'cn',
            'Host': 'cs.midea.com',
            'Connection': 'Keep-Alive'
        }
        data = {'mobile':mobile}
        ret = utils.request(url,method = 'get',data = json.dumps(data),headers = headers)
        if utils.HasAttrVar(ret,'resultCode','0'):
            return utils.errorReport('httpGetEngineer field.info:' + ret['resultMsg'],system_name = self.system_name)
        return ret

    def getmmpstorelist(self,saleUnitName = '守卫者科技',regionCode = '1510107000',page = 1,resultNum = '20'):
        '''
        动态购买单位:serviceAreaCode is regionCode
        all:resultNum:131860
        '''
        url = self.postSale_url + 'getmmpstorelist?json={"regionCode":"'
        url +=regionCode+'","resultNum":'+resultNum+',"orderColumn":"1","page":"'
        url +=str(page)+'","saleUnitName":"'+saleUnitName+'"}'
        headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        ret = utils.request(url,method = 'get',headers = headers,timeout=300.0)
        print('status:',ret['status'])
        print('errorCode:',ret['errorCode'])
        print('errorMsg:',ret['errorMsg'])
        print('pageIndex:',ret['pageIndex'])
        print('pageSize:',ret['pageSize'])
        print('pageCount:',ret['pageCount'])
        print('total:',ret['total'])
        print(len(ret['list']))
        if utils.HasAttrVar(ret,'status',False):
            return utils.errorReport('获取失败,info:' + ret['errorMsg'],system_name = self.system_name)
        if len(ret['list']) > 0:
            rc = redis.Redis(host='127.0.0.1')
            rc.set('mmd',json.dumps(ret))
            self.after_mmpstore(ret,regionCode)#需要谨慎
            if len(ret['list']) == int(resultNum):
                print(len(ret['list']))
                print('done!')
                # self.getmmpstorelist(saleUnitName = saleUnitName,regionCode = regionCode,page = page,resultNum = resultNum)
        return ret
    
    def after_mmpstore(self,ret,regionCode):
        i = 0
        print(len(ret['list']))
        session = DBSession()
        for item in ret['list']:
            #分片
            i = i+1
            if '名成' in item['saleUnitName']:
                print(item['saleUnitName'])
            try:
                store = session.query(MideaMmpstore).filter(MideaMmpstore.sale_unit_code == item['saleUnitCode']).one()
                store.sale_unit_name = item['saleUnitName']
                store.updated_at = time.time()
                session.add(store)
            except Exception as e:
                mmpstore = MideaMmpstore()
                mmpstore.sale_unit_code = item['saleUnitCode']
                mmpstore.sale_unit_name = item['saleUnitName']
                mmpstore.region_code = regionCode
                mmpstore.created_at = time.time()
                session.add(mmpstore)
            # if i==10000:
                # session.commit()
                # session.close()
                # i = 0
        session.commit()
        session.close()
    
    def getmmpunitengineer(self,orgCode = 'CS006',unitCode = 'W5101007150',engineerName = '唐'):
        '''
        动态获取工程师,搜索
        '''
        url = self.postSale_url + 'getmmpunitengineer&json={"orgCode":"'+orgCode+'","unitCode":"'+unitCode+'","engineerName":"'+engineerName+'"}'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        ret = utils.request(url,method = 'get',headers = headers,timeout=3.0)
        if utils.HasAttrVar(ret,'status',False):
            return utils.errorReport('获取工程师失败,info:' + ret['errorMsg'],system_name = self.system_name)
        return ret

    def dosaveinstallarchives(self,sceneCustomerName = '吴成华',
                            sceneCustomerTel1 = '13608010964',
                            sceneCustomerTel2 = None,
                            sceneCustomerTel3 = None,
                            sceneAreaNum = "028",
                            sceneCustomerAreaCode = "1510107064",
                            sceneCustomerAreaName = "四川省成都市武侯区桂溪街道",
                            sceneCustomerAddress = "四川省成都市武侯区桂溪街道老成仁路8号育才竹岛1-2504",
                            insideBarcode = "2112201164378080542041",
                            outsideBarcode = "21122010898781505A0516",
                            installCode = "W100001098",
                            installDesc = "安装",
                            installUnitCode = "W5101007150",
                            installUnitName = "武侯区宏旺电器维修服务部",
                            purchaseDate = "2017-10-05",#购买时间
                            productionDate = "2017-08-15",#生产日期
                            areaCode = "1510107013",
                            areaName = "四川省成都市武侯区桂溪街道",
                            machineAddress = "四川省成都市武侯区桂溪街道老成仁路8号育才竹岛1-2504",
                            brandCode = "MIDEA",
                            brandName = "美的",
                            prodCode = "1000",
                            prodName = "家用空调",
                            productModel = "KFR-23W-A01",
                            saleUnitCode = "K00016532",
                            saleUnitName = "四川名成机电安装工程有限公司",
                            engineerName1 = "刘原志",
                            engineerCode1 = "E0199658",
                            engineerName2 = "陈章列",
                            engineerCode2 = "E0271970",
                            unitCode = "W5101007150",
                            unitName = "武侯区宏旺电器维修服务部",
                            productCode = "31022010004009",
                            checkCode = "AA",
                            unactivedReson = None,
                            serviceOrderNo = "FW171103319067",
                            dispatchOrderNo = "PG171103319551",
                            engineerMachineApproval = "S蜀申1604990",
                            cardNo = "",
                            pubRemark = "",
                            lbcsFlag = "Y",
                            intelligenceFlag = "N",
                            orgCode = "CS006",
                            bootStrapCode = "",
                            aumaterialRows = [],
                            createType = 10,
                            archivesNo = None,
                            machineId = "",
                            installArchivesId = "",
                            longitude = 104.074389,
                            latitude = 30.533986,
                            engineerTel1 = None):
        '''
        保存安装档案
        '''
        url = self.postSale_url + 'dosaveinstallarchives'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Origin': 'file://',
            'User-Agent': self.UserAgent,
            'content-type': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        localtion = utils.distanceRange(longitude, latitude, longitude, latitude,maxdistance = 450,limitdistance = 10,chrr = '9')
        print(localtion)
        position = self.saveengineerposition(engineerCode1 = engineerCode1,engineerTel1 = engineerTel1,lng = localtion['lon2'],lat = localtion['lat2'])
        data = {
            "jsonstr":{
                "sceneCustomerName": sceneCustomerName,
                "sceneCustomerTel1": sceneCustomerTel1,
                "sceneCustomerTel2": sceneCustomerTel2,
                "sceneCustomerTel3": sceneCustomerTel3,
                "sceneAreaNum": sceneAreaNum,
                "sceneCustomerAreaCode": sceneCustomerAreaCode,
                "sceneCustomerAreaName": sceneCustomerAreaName,
                "sceneCustomerAddress": sceneCustomerAddress,
                "insideBarcode": insideBarcode,
                "outsideBarcode": outsideBarcode,
                "installCode": installCode,
                "installDesc": installDesc,
                "installUnitCode": installUnitCode,
                "installUnitName": installUnitName,
                "purchaseDate": purchaseDate,
                "productionDate": productionDate,
                "areaCode": areaCode,
                "areaName": areaName,
                "machineAddress": machineAddress,
                "brandCode": brandCode,
                "brandName": brandName,
                "prodCode": prodCode,
                "prodName": prodName,
                "productModel": productModel,
                "saleUnitCode": saleUnitCode,
                "saleUnitName": saleUnitName,
                "engineerName1": engineerName1,
                "engineerCode1": engineerCode1,
                "engineerName2": engineerName2,
                "engineerCode2": engineerCode2,
                "unitCode": unitCode,
                "unitName": unitName,
                "productCode": productCode,
                "checkCode": checkCode,
                "unactivedReson": unactivedReson,
                "serviceOrderNo": serviceOrderNo,
                "dispatchOrderNo": dispatchOrderNo,
                "engineerMachineApproval": engineerMachineApproval,
                "cardNo": cardNo,
                "pubRemark": pubRemark,
                "lbcsFlag": lbcsFlag,
                "intelligenceFlag": intelligenceFlag,
                "orgCode": orgCode,
                "bootStrapCode": bootStrapCode,
                "aumaterialRows": aumaterialRows,
                "createType": createType,
                "archivesNo": archivesNo,
                "machineId": machineId,
                "installArchivesId": installArchivesId,
                "longitude": localtion['lon2'],
                "latitude": localtion['lat2']
            }
        }
        print(json.dumps(data))

        r = utils.request(url,method = 'post',data = json.dumps(data),headers = headers)
        print(json.dumps(r))
        if r.get('status') is False:
            utils.errorReport('保存安装档案失败,info:' + json.dumps(data),system_name = self.system_name)
        return {"status":r['status'],"msg":r['errorMsg'],"type":'saveinstallcard',"r":r}

    def doupload(self,isGetlocation = True,
                fileIndex = 1,
                fileName = str(int(round(time.time() * 1000))) + ".jpeg",
                serviceOrderNo = "",
                account = "E0199658",
                archivesNo = '',
                pictureCreateTime = int(round(time.time() * 1000)),
                longitude = 104.074389,
                latitude = 30.533986,
                address = "四川省成都市武侯区桂溪街道老成仁路8号育才竹岛1-2504",
                contentStr = ""):
        '''
        '''
        localtion = utils.distanceRange(longitude, latitude, longitude, latitude,maxdistance = 450,limitdistance = 10,chrr = '9')
        url = self.postSale_url + 'doupload'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Origin': 'file://',
            'User-Agent': self.UserAgent,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        fileContent = {
            "fileIndex": fileIndex, 
            "fileName": fileName, 
            "serviceOrderNo": serviceOrderNo, 
            "account": account, 
            "archivesNo": archivesNo, 
            "pictureCreateTime": pictureCreateTime, 
            "longitude": localtion['lon2'],
            "latitude": localtion['lat2'], 
            "address": address,
            "contentStr": contentStr
        }
        data = {
            "isGetlocation":isGetlocation,
            "fileContent":json.dumps(fileContent)
        }
        r = utils.request(url,method = 'post',data = data,headers = headers)
        if r.get('status') is False:
            utils.errorReport('图片上传失败,info:' + json.dumps(data),system_name = self.system_name)
            return {"status":r['status'],"msg":r['errorMsg'],"type":'saveinstallcard',"r":r}
        return r

    def getmmppictureconfiglist(self,orgCode = 'CS006',serviceTypeCode = '1010',prodCode = '1000'):
        '''
        获取图片配置
        '''
        url = self.postSale_url + 'getmmppictureconfiglist&json={"orgCode":"'+orgCode+'","serviceTypeCode":'+serviceTypeCode+',"prodCode":"'+prodCode+'"}'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        ret = utils.request(url,method = 'get',headers = headers)
        if utils.HasAttrVar(ret,'status',False):
            return utils.errorReport('获取配置失败,info:' + ret['errorMsg'],system_name = self.system_name)
        self.after_getpicconfig(ret)
        return ret

    def after_getpicconfig(self,ret):
        mmpconfig = Mdmmppictureconfig()
        session = DBSession()
        for item in ret['list']:
            try:
                config = session.query(Mdmmppictureconfig).filter(Mdmmppictureconfig.configid == item['configId']).one()
                config.picture_type_name = item['pictureTypeName']
                config.picture_number = item['pictureNumber']
                config.configid = item['configId']
                config.updated_at = time.time()
                session.add(config)
            except Exception as e:
                mmpconfig.picture_type_name = item['pictureTypeName']
                mmpconfig.picture_number = item['pictureNumber']
                mmpconfig.configid = item['configId']
                mmpconfig.created_at = time.time()
                session.add(mmpconfig)
        session.commit()
        session.close()

    def getfeedbackitems(self,orgCode = 'CS006',serviceOrderNo = 'FW170771101389'):
        '''
        获取订单的反馈配置
        '''
        url = self.postSale_url + 'getfeedbackitems'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        data = {
            'orgCode':orgCode,
            'serviceOrderNo':serviceOrderNo
        }
        return utils.request(url,method = 'get',data = json.dumps(data),headers = headers)

    def appsearchfromsn(self,data,operator = None):
    # def appsearchfromsn(self,parseType = '10',productSn1 = '21122593051751502B0423',businessFlag = 'AZ'):
        '''
        内机条码校验
        '''
        url = self.postSale_url + 'appsearchfromsn'
        # data = {
        #     "parseType": parseType,
        #     "productSn1": productSn1,
        #     "businessFlag": businessFlag
        # }
        headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Origin': 'file://',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; NX511J_V3 Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/50.0.2661.86 Mobile Safari/537.36/mideaConnect',
            'content-type': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(url = url,method = 'post',data = json.dumps(data),headers = headers,timeout = 4.0)
        return {"status":r['status'],"msg":r['errorMsg'],"type":'appsearchfromsn',"r":r}

    def appsearchfromsn_wai(self,data,operator = None):
    # def appsearchfromsn_wai(self,parseType = '11',productSn1 = '21122593051751502B0423',productCode = '31022510000059',productSn2 = '21122593052751202Z0096',businessFlag = 'AZ'):
        '''
        检验外机条码
        '''
        url = self.postSale_url + 'appsearchfromsn'
        # data = {
        #     'parseType': parseType,
        #     'productSn1': productSn1,
        #     'productCode': productCode,
        #     'productSn2': productSn2,
        #     'businessFlag': businessFlag
        # }
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Origin': 'file://',
            'User-Agent': self.UserAgent,
            'content-type': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(url,data = json.dumps(data),method = 'post',headers = headers)
        return {"status":r['status'],"msg":r['errorMsg'],"type":'appsearchfromsn_wai',"r":r}

    # /mas-api/restful/cssProIpmsUrl/api/mmp/checkengineermachineapproval?json=%7B%22orgCode%22:%22CS006%22,%22engineerMachineNo%22:%22S%C3%A8%C2%9C%C2%80%C3%A7%C2%94%C2%B31604990%22%257
    def checkengineermachineapproval(self,data):
        #工程机批文
        url = self.postSale_url + 'checkengineermachineapproval?json='+json.dumps(data)
        headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(url = url,headers = headers,method = 'get')
        res = {"status":r['status'],"msg":r['errorMsg'],"type":'checkengineermachineapproval',"r":r}
        return res
    
    def checkcodevalidly(self,data):
        '''安装检验码 /mas-api/restful/cssProIpmsUrl/api/mmp/checkcodevalidly'''
        '''
        {
            "checkCode": "AA",
            "insideBarcode": "2112201164378080542041",
            "mobile": "18140038880",#工程师
            "unitCode": "W5101007150",#安装单位
            "orgCode": "CS006"
        }
        '''
        url = self.postSale_url + 'checkcodevalidly'
        headers = {
            "Connection": 'keep-alive',
            "Accept": '*/*',
            "Origin": 'file://',
            "User-Agent": self.UserAgent,
            "content-type": 'application/json',
            "Accept-Encoding": 'gzip, deflate',
            "Accept-Language": 'zh-CN,en-US;q=0.8',
            "X-Requested-With": 'com.midea.connect.out'
        }
        r = utils.request(url = url,headers = headers,method = 'post',data = json.dumps(data))
        return {"status":r['status'],"msg":r['errorMsg'],"type":'checkcodevalidly','r':r}
    
    def getmmpinstallarchive(self,orgCode = 'CS006',archivesNo = 'AZ171048675924'):
        '''
        获取档案信息
        '''
        url = self.postSale_url + 'getmmpinstallarchive&json={"orgCode":"'+orgCode+'","archivesNo":"'+archivesNo+'"}'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        ret = utils.request(url,method = 'get',headers = headers)
        if utils.HasAttrVar(ret,'status',False):
            return utils.errorReport('获取安装档案失败,info:' + json.dumps(ret),system_name = self.system_name)
        return ret

    def h5add(self,sessionKey = 'user81e22553-da91-4d8a-a425-dbd5ef86b25d',username = '18140038880'):
        '''
        登录之后，h5 add
        '''
        # url = self.map_base_url + 'mapservice/monitor/H5/add?sessionKey=' + sessionKey
        url = self.map_base_url + 'mapservice/monitor/H5/add?sessionKey='+sessionKey
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8',
            'locale': 'cn',
            'User-Agent': self.UserAgent,
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'Host': 'map.midea.com'
        }
        data = {
            "action": "login",            
            "appKey": "27dce012d6b93e9cd9b60880f5ac1eb7",
            "appVersion": "1.1.7",
            "identifier": "com.midea.postsale",
            "platform": "android",
            "username": username,
            "widgetVersion": "1.0.63"
        }
        ret = utils.request(url,method = 'post',data = json.dumps(data),headers = headers)
        if ret.get('result') is False:
            return utils.errorReport('h5 add　field.info:' + json.dumps(ret),system_name = self.system_name)
        return ret

    def basicdata(self):
        '''
        获取基础数据
        '''
        url = self.postSale_url + 'basicdata'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        data = {}
        ret = utils.request(url,method = 'get',data = data,headers = headers)
        if ret.get('status') is False:
            return utils.errorReport('获取基础数据错误,info:' + json.dumps(ret),system_name = self.system_name)
        return ret

    def getdispatchordernum(self,engineerCode = 'E0199658',dispatchOrderStatus = 1):
        '''
        获取任务数量:dispatchOrderStatus:1=待接收，2=待处理,３=已完成
        '''
        url = self.postSale_url + 'getdispatchordernum'
        data = {
            'engineerCode':engineerCode,
            'dispatchOrderStatus':dispatchOrderStatus
        }
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        ret = utils.request(url = url,data = json.dumps(data),method = 'get',headers = headers)
        if utils.HasAttrVar(ret,'status',False):
            return utils.errorReport('getdispatchordernum error:' + ret['errorMsg'],system_name = self.system_name)
        return ret

    def orderrecrej(self,engineerCode='E0293031',
                    orgCode='CS006',
                    serviceOrderNo='FW171214328190',
                    dispatchOrderNo='PG171214329449',
                    receiveResult='0',
                    engineerName='王健',
                    engineerCode1='E0293031',
                    engineerTel1='15208390257',
                    appointStartTime='2017-11-09+16:00:00',
                    appointEndTime='2017-11-09+18:00:00',
                    rejectType='',
                    rejectReason='',
                    longitude='104.152936',
                    latitude='30.589929'):
        '''
        接单
        https://mapnew.midea.com/mas-api/proxy?alias=srm.postSale.orderrecrej
        '''
        url = self.postSale_url + 'orderrecrej'
        data = {
            'engineerCode':engineerCode,
            'orgCode':orgCode,
            'serviceOrderNo':serviceOrderNo,
            'dispatchOrderNo':dispatchOrderNo,
            'receiveResult':receiveResult,
            'engineerName':engineerName,
            'engineerCode1':engineerCode1,
            'engineerTel1':engineerTel1,
            'appointStartTime':appointStartTime,
            'appointEndTime':appointEndTime,
            'rejectType':rejectType,
            'rejectReason':rejectReason,
            'longitude':longitude,
            'latitude':latitude
        }
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        ret = utils.request(url = url,data = data,method = 'get',headers = headers)
        print(json.dumps(ret))
        if str(ret.get('status')) is '0':
            utils.errorReport('orderrecrej error:' + ret['errorMsg'],system_name = self.system_name)
            return {"status":ret['status'],"msg":ret['errorMsg'],"type":'orderrecrej',"r":ret}
        self.after_orderrecrej(ret)
        return ret
    
    def after_orderrecrej(self,ret):
        pass
    
    def dispatchimpement_startoff(self,engineerCode = 'E0293031',
                        engineerTel = '15208390257',
                        serviceOrderNo = 'FW171214328190',
                        dispatchOrderNo = 'PG171214329449',
                        processType = '10',
                        lng = '104.070592',
                        lat = '30.549197'):
        '''
        出发:/mas-api/restful/cssProIpmsUrl/api/mmp/dispatchimpement
        ?engineerCode=E0199658&orgCode=&engineerTel=18140038880
        &serviceOrderNo=FW171103319067&dispatchOrderNo=PG171103319551
        &processType=10&longitude=104.075153&latitude=30.53841
        '''
        engineerCode,engineerTel,serviceOrderNo,dispatchOrderNo,processType,lng,lat = map(str,[engineerCode,engineerTel,serviceOrderNo,dispatchOrderNo,processType,lng,lat])
        url = self.postSale_url + 'dispatchimpement?engineerCode='+engineerCode
        url += '&orgCode=&engineerTel='+engineerTel+'&serviceOrderNo='+serviceOrderNo
        url +='&dispatchOrderNo='+dispatchOrderNo+'&processType='+processType
        url +='&longitude='+lng+'&latitude='+lat
        print('url',url);
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(url = url,method = 'get',headers = headers)
        print(json.dumps(r))
        if r.get('status') is False:
            utils.errorReport('出发失败,serviceOrderNo:' + serviceOrderNo + ',info:' + r['errorMsg'],system_name = self.system_name)
        return {"status":r['status'],"msg":r['errorMsg'],"type":'orderrecrej',"r":r}

    #改约
    def docustomerappoint(self,engineerCode="E0293031",
                        engineerName="王健",
                        dispatchOrderNo="PG171214329449",
                        serviceOrderNo="FW171214328190",
                        appointStartTime="2017-12-09+16:00:00",
                        appointEndTime="2017-12-09+18:00:0"):
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        data = {
            "engineerCode":engineerCode,
            "engineerName":engineerName,
            "dispatchOrderNo":dispatchOrderNo,
            "serviceOrderNo":serviceOrderNo,
            "appointStartTime":appointStartTime,
            "appointEndTime":appointEndTime
        }
        url = self.postSale_url + 'docustomerappoint'
        r = utils.request(method = "get",headers = headers,data = data)
        return {"status":r['status'],"msg":r['errorMsg'],"type":'docustomerappoint',"r":r}
    
    #到达
    def dispatchimpement_arrivals(self,engineerCode = 'E0293031',
                        engineerTel = '15208390257',
                        serviceOrderNo = 'FW171214328190',
                        dispatchOrderNo = 'PG171214329449',
                        processType = '11',
                        operateType = '0',
                        distance = '0.109,',#公里数
                        lng = '104.074389',
                        lat = '30.533986'):
        '''
        到达:
        GET /mas-api/proxy?alias=srm.postSale.dispatchimpement
        &engineerCode=E0199658&orgCode=&engineerTel=18140038880
        &serviceOrderNo=FW170995120527&dispatchOrderNo=PG170995121478
        &processType=11&operateType=0&distance=3.94&longitude=104.075115
        &latitude=30.538955
        '''
        localtion = utils.distanceRange(lng, lat, lng, lat,maxdistance = 450,limitdistance = 10,chrr = '9')
        print(json.dumps(localtion))
        r = self.saveengineerposition(engineerCode1 = engineerCode,engineerTel1 = engineerTel,lng = localtion['lon2'],lat = localtion['lat2'])
        print(json.dumps(r))
        if r.get('status') is False:
            return r
        url = self.postSale_url + 'dispatchimpement?engineerCode='+engineerCode
        url += '&orgCode=&engineerTel='+engineerTel+'&serviceOrderNo='+serviceOrderNo
        url +='&dispatchOrderNo='+dispatchOrderNo+'&processType='+processType
        url +='&operateType=0&distance='+str(localtion['distance'])+'&longitude='
        url +=localtion['lon2']+'&latitude='+localtion['lat2']
        print(url);

        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        ret = utils.request(url = url,method = 'get',headers = headers)
        print(json.dumps(ret))
        if ret.get('status') is False:
            utils.errorReport('到达失败,serviceOrderNo:' + serviceOrderNo + ',info:' + ret['errorMsg'],system_name = self.system_name)
        return {"status":ret['status'],"msg":ret['errorMsg'],"type":'orderrecrej',"r":ret}
    
    def test(self):
        img = {
            '1':'./pic/qd.png',
            '2':'./pic/z.png',
            '3':'./pic/23nj.png',
            '4':'./pic/z1.png',
        }
        print(img)
        for i in img:
            self.doupload(fileIndex = int(i),contentStr = utils.base64Img(img[i]),archivesNo = '1036763616')

    #提交反馈
    def processfeedback(self,orgCode='CS006',
                            engineerCode='E0293031',
                            engineerTel='15208390257',
                            serviceOrderNo='FW171214328190',
                            dispatchOrderNo='PG171214329449',
                            pubRemark='',
                            feedbackResultCode='11',
                            feedbackDesc='维修完成，调试运行正常，用户认可',
                            mmpArchivesRequestList='',
                            serviceCustomerId = "1041362971", 
                            serviceMainTypeCode = "10", 
                            serviceCustomerDemandId = "1052969483", 
                            insideBarCode = "D110001103915507330225",
                            outsideBarcode = "D110001104015527330015",
                            productCode = "",
                            prodCode = "1000",
                            prodName = "家用空调",
                            productModel = "", 
                            warrantyType = "",
                            expirationDate = "",
                            sceneCustomerMobile = "",
                            sceneCustomerAddress ="",
                            installUnitName = "", 
                            saleUnitCode = "", 
                            saleUnitName = "", 
                            brandCode = "MIDEA", 
                            brandName = "美的",
                            productUse = "", 
                            productionDateStr = "", 
                            machineId = "",
                            feedbackType=15,
                            feedbackMainItemCode='FW01',
                            feedbackMainItemName='处理好，用户满意',
                            feedbackSubItemCode='FW0101',
                            feedbackSubItemName='通过送货、安装、调整、维修、清洗、保养、退换机处理好',
                            contactSystem='网点自建',
                            contactTime='2017-12-07',
                            nuit_longitude=104.074359,
                            unit_latitude=30.533986,
                            distance=0.05,#公里数
                            operateType=0,
                            longitude=104.074389,
                            latitude=30.589629):
        localtion = utils.distanceRange(longitude, latitude, longitude, latitude,maxdistance = 450,limitdistance = 10,chrr = '9')
        print(localtion)
        longitude = localtion['lon2']
        latitude = localtion['lat2']
        distance = localtion['distance']
        '''
        GET /mas-api/restful/cssProIpmsUrl/api/mmp/processfeedback
        orgCode=CS006
        engineerCode=E0199658
        engineerTel=18140038880
        serviceOrderNo=FW171098058836
        dispatchOrderNo=PG171098061782
        pubRemark=
        feedbackResultCode=11
        feedbackDesc=安装完成，用户认可
        mmpArchivesRequestList=
        [
            {
                "orgCode": "CS006", 
                "serviceCustomerId": "MA260020160729664367", 
                "serviceMainTypeCode": "10", 
                "serviceOrderNo": "FW171098058836", 
                "serviceCustomerDemandId": "1045002162", 
                "insideBarCode": "", 
                "outsideBarcode": "", 
                "productCode": "", 
                "prodCode": "1000", 
                "prodName": "家用空调", 
                "productModel": "", 
                "warrantyType": "", 
                "expirationDate": "", 
                "sceneCustomerMobile": "", 
                "sceneCustomerAddress": "", 
                "pubRemark": "", 
                "installUnitName": "", 
                "saleUnitCode": "", 
                "saleUnitName": "", 
                "brandCode": "MIDEA", 
                "brandName": "美的", 
                "productUse": "", 
                "productionDateStr": "", 
                "machineId": ""
            }
        ]
        feedbackType=15
        feedbackMainItemCode=FW01
        feedbackMainItemName=处理好，用户满意
        feedbackSubItemCode=FW0101
        feedbackSubItemName=通过送货、安装、调整、维修、清洗、保养、退换机处理好
        contactSystem=网点自建
        contactTime=2017-10-12
        nuit_longitude=104.075124
        unit_latitude=30.538986
        distance=41.66
        operateType=0
        longitude=104.075123
        latitude=30.538987
        '''
        # mmpArchivesRequestList = {
        #         "orgCode": orgCode, 
        #         "serviceCustomerId": serviceCustomerId, 
        #         "serviceMainTypeCode": serviceMainTypeCode, 
        #         "serviceOrderNo": serviceOrderNo, 
        #         "serviceCustomerDemandId": serviceCustomerDemandId, 
        #         "insideBarCode": insideBarCode, 
        #         "outsideBarcode": outsideBarcode, 
        #         "productCode": productCode,
        #         "prodCode": prodCode,
        #         "prodName": prodName,
        #         "productModel": productModel,
        #         "warrantyType": warrantyType, 
        #         "expirationDate": expirationDate,
        #         "sceneCustomerMobile": sceneCustomerMobile,
        #         "sceneCustomerAddress": sceneCustomerAddress,
        #         "pubRemark": pubRemark,
        #         "installUnitName": installUnitName,
        #         "saleUnitCode": saleUnitCode,
        #         "saleUnitName": saleUnitName,
        #         "brandCode": brandCode,
        #         "brandName": brandName,
        #         "productUse": productUse,
        #         "productionDateStr": productionDateStr,
        #         "machineId": machineId
        #     }
        # data = {
        #     'orgCode':orgCode,
        #     'engineerCode':engineerCode,
        #     'engineerTel':engineerTel,
        #     'serviceOrderNo':serviceOrderNo,
        #     'dispatchOrderNo':dispatchOrderNo,
        #     'pubRemark':pubRemark,
        #     'feedbackResultCode':feedbackResultCode,
        #     'feedbackDesc':feedbackDesc,
        #     'feedbackType':feedbackType,
        #     'feedbackMainItemCode':feedbackMainItemCode,
        #     'feedbackMainItemName':feedbackMainItemName,
        #     'feedbackSubItemCode':feedbackSubItemCode,
        #     'feedbackSubItemName':feedbackSubItemName,
        #     'contactSystem':contactSystem,
        #     'contactTime':contactTime,
        #     'nuit_longitude':nuit_longitude,
        #     'unit_latitude':unit_latitude,
        #     'distance':distance,
        #     'operateType':operateType,
        #     'longitude':longitude,
        #     'latitude':latitude,
        #     'mmpArchivesRequestList':mmpArchivesRequestList
        # }
        params = self.postSale_url + 'processfeedback'
        params += '?orgCode='+orgCode+'&engineerCode='+engineerCode+'&engineerTel='+engineerTel
        params +='&serviceOrderNo='+serviceOrderNo+'&dispatchOrderNo='+dispatchOrderNo+'&pubRemark='
        params +=pubRemark+'&feedbackResultCode='+str(feedbackResultCode)
        params +=u'&feedbackDesc=安装完成，用户认可&mmpArchivesRequestList=[{"orgCode":"'+str(orgCode)
        params +='","serviceCustomerId":"'+serviceCustomerId
        params +='","serviceMainTypeCode":"'+serviceMainTypeCode+'","serviceOrderNo":"'
        params +=serviceOrderNo+'","serviceCustomerDemandId":"'+serviceCustomerDemandId
        params +='","insideBarCode":"'+insideBarCode+'","outsideBarcode":"'+outsideBarcode
        params +='","productCode":"'+productCode+'","prodCode":"'+prodCode
        params +='","prodName":"'+prodName+'","productModel":"'+productModel+'","warrantyType":"'
        params +=warrantyType+'","expirationDate":"'+expirationDate+'","sceneCustomerMobile":"'
        params +=sceneCustomerMobile+'","sceneCustomerAddress":"'+sceneCustomerAddress
        params +='","pubRemark":"'+pubRemark+'","installUnitName":"'+installUnitName
        params +='","saleUnitCode":"'+saleUnitCode+'","saleUnitName":"'+saleUnitName
        params +='","brandCode":"'+brandCode+'","brandName":"'+brandName+'","productUse":"'
        params +=productUse+'","productionDateStr":"'+productionDateStr+'","machineId":"'+machineId+'"}]'
        params +='&feedbackType='+str(feedbackType)+'&feedbackMainItemCode='+feedbackMainItemCode
        params +='&feedbackMainItemName='+feedbackMainItemName+'&feedbackSubItemCode='
        params +=feedbackSubItemCode+'&feedbackSubItemName='+feedbackSubItemName
        params +='&contactSystem='+contactSystem
        params +='&contactTime='+str(contactTime)+'&nuit_longitude='+str(nuit_longitude)
        params +='&unit_latitude='+str(unit_latitude)
        params +='&distance='+str(distance)+'&operateType='+str(operateType)+'&longitude'
        params +=str(longitude)+'=&latitude='+str(latitude)
        headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; NX511J_V3 Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/50.0.2661.86 Mobile Safari/537.36/mideaConnect',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        print(params)
        r = utils.request(url = params,method = 'get',headers = headers)
        print(json.dumps(r))
        if r.get('status') is False:
            utils.errorReport('提交反馈失败:' + serviceOrderNo,system_name = self.system_name)
        return {"status":r['status'],"msg":r['errorMsg'],"type":'dosavefeedback',"r":r}

    def _after_processfeedback(data,ret):
        pass

    #
    def machinewarranty(self):
        '''/mas-api/restful/cssProIpmsUrl/api/mmp/machinewarranty?engineerTel=18140038880&productSN1=21122593051751502B0423&businessType=1'''
        url = self.postSale_url + 'machinewarranty?engineerTel=18140038880&productSN1=21122593051751502B0423&productSN1=21122593052751202Z0096&businessType=1'
        r = utils.request(url = url,method = 'get')
        print(json.dumps(r))

    def getmmpinstallarchives(self,serviceOrderNo = 'FW171110164157',engineerCode = 'E0199658',is_submit = 0):
        # /mas-api/restful/cssProIpmsUrl/api/mmp/getmmpinstallarchives?json={"orgCode":"CS006","serviceOrderNo":"FW171103319067","engineerCode":"E0199658","resultNum":"99","time":1509703953278}
        url = self.postSale_url + 'getmmpinstallarchives?json={"orgCode":"CS006","serviceOrderNo":"'+serviceOrderNo+'","engineerCode":"'+engineerCode+'","resultNum":"99","time":"'+str(int(time.time())*1000)+'"}'
        print(url)
        headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; NX511J_V3 Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/50.0.2661.86 Mobile Safari/537.36/mideaConnect',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(url = url,headers = headers,method = 'get')
        res = {"status":r['status'],"msg":r['errorMsg'],"type":'getmmpinstallarchives',"r":r}
        if r.get('status') is False:
            utils.errorReport('获取档案失败:'+r['errorMsg']+"NO:"+str(serviceOrderNo))
            return res
        if is_submit == 1 and r.get('total') > 0:
            self.after_getmmpinstallarchives(serviceOrderNo,r.get('list'))
        return res
    
    def after_getmmpinstallarchives(self,serviceOrderNo,data):
        session = DBSession()
        ins = session.query(MdSubmitcard).filter(MdSubmitcard.service_orderno==serviceOrderNo).all()
        if ins:
            info = ins[0]
            info.archives = json.dumps(data)
            session.commit()
            session.close()
            return True
        session.commit()
        session.close()

    def getmmpregions(self,regionLevel = '1',parentRegId = '',orgCode = 'CS006',branchCode = 'F5101000002'):
        '''
        F5101000002:四川
        /mas-api/restful/cssProIpmsUrl/api/mmp/getmmpregions
        /mas-api/restful/cssProIpmsUrl/api/mmp/getmmpregions?json={"regionLevel":1,"parentRegId":"","orgCode":"CS006","branchCode":"F5101000002"}
        '''
        url = self.postSale_url + 'getmmpregions?json={"regionLevel":'+str(regionLevel)+',"parentRegId":"'+str(parentRegId)+'","orgCode":"'+orgCode+'","branchCode":"'+branchCode+'"}'
        r = utils.request(url = url,method = 'get')
        print(url)
        if r.get('status') is not True:
            return utils.errorReport('getmmpregions error:' + r['errorMsg'],system_name = self.system_name)
        self._after_getmmpregions(r['list'])
        for item in r['list']:
            if item['regionLevel']== 4:
                break
            self.getmmpregions(regionLevel = item['regionLevel'] + 1,parentRegId = item['regionCode'],orgCode = 'CS006',branchCode = 'F5101000002')

    def _after_getmmpregions(self,r):
        session = DBSession()
        for item in r:
            regions = session.query(MdMmpregions).filter(MdMmpregions.region_code ==item['regionCode']).all()
            if regions:
                reg = regions[0]
                reg.parent_reg_id = item['parentRegId']
                reg.region_level = item['regionLevel']
                reg.asst_code = item['asstCode']
                reg.region_desc = item['regionDesc']
                reg.zip_code = item['zipCode']
                reg.area_num = item['areaNum']
                reg.longitude = item['longitude']
                reg.latitude = item['latitude']
                session.add(reg)
            else:
                mmpregions = MdMmpregions()
                mmpregions.region_code = item['regionCode']
                mmpregions.parent_reg_id = item['parentRegId']
                mmpregions.region_level = item['regionLevel']
                mmpregions.asst_code = item['asstCode']
                mmpregions.region_desc = item['regionDesc']
                mmpregions.zip_code = item['zipCode']
                mmpregions.area_num = item['areaNum']
                mmpregions.longitude = item['longitude']
                mmpregions.latitude = item['latitude']
                session.add(mmpregions)
        session.commit()
        session.close()

    def orderlist_all_data_update(self,engineer = {}):
        default_engineer = {'E0293031','E0199658','E0206442'}
        engineerCodes = engineer if engineer else default_engineer
        for engineerCode in engineerCodes:
            rprocess = self.orderprocesslist(engineerCode = engineerCode,dateFlag = '0',dispatchOrderStatus = '11;12;13;14;18',is_submit = '1')
            if rprocess.get('status') is False:
                return rprocess
            rprocess2 = self.orderprocesslist(engineerCode = engineerCode,dateFlag = '',dispatchOrderStatus = '10',is_submit = '1',statusCondition = 'readytodo')
            if rprocess2.get('status') is False:
                return rprocess2
            rprocess3 = self.orderprocesslist(engineerCode = engineerCode,dateFlag = '1',dispatchOrderStatus = '15,16,17',is_submit = '1')
            print('333')
            print(rprocess3)
            if rprocess3.get('status') is False:
                return rprocess3
            r = {"status":rprocess3['status'],"msg":rprocess3['msg'],"type":'data_update'}
        print(r)
        return r
        
        '''
        10是待接单'11;12;13;14;18'是待处理
        待处理:dateFlag:2=明天,0=今天,3=最近7天
        待接单:dateFlag:1
        明天待处理:/mas-api/restful/cssProIpmsUrl/api/mmp/orderprocesslist?engineerCode=E0199658&dateFlag=2&statusCondition=readytodo&dispatchOrderStatus=11%3B12%3B13%3B14%3B18&resultNum=9
        '''
    def recrej_startoff_arrivals(self,data,detail,order_location):
        if str(detail['dispatchOrderStatus']) == '10':
            print("10")
            recrej = self.orderrecrej(engineerCode=data['engineerCode1'],
                    orgCode=data['orgCode'],
                    serviceOrderNo=data['serviceOrderNo'],
                    dispatchOrderNo=detail['dispatchOrderNo'],
                    receiveResult='0',
                    engineerName=data['engineerName1'],
                    engineerCode1=data['engineerCode1'],
                    engineerTel1=data['engineerTel1'],
                    appointStartTime=datetime.datetime.fromtimestamp(detail['appointStartTime']/1000).strftime('%Y-%m-%d+%H:%M:%S'),
                    appointEndTime=datetime.datetime.fromtimestamp(detail['appointEndTime']/1000).strftime('%Y-%m-%d+%H:%M:%S'),
                    rejectType='',
                    rejectReason='',
                    longitude=self.sanshengxiang['lng'],
                    latitude=self.sanshengxiang['lat'])
            if recrej.get('status') is False:
                return recrej
            print(json.dumps(recrej))

            startoff = self.dispatchimpement_startoff(engineerCode = data['engineerCode1'],
                        engineerTel = data['engineerTel1'],
                        serviceOrderNo = data['serviceOrderNo'],
                        dispatchOrderNo = detail['dispatchOrderNo'],
                        processType = '10',
                        lng = self.sanshengxiang['lng'],
                        lat = self.sanshengxiang['lat'])
            if startoff.get('status') is False:
                return startoff
            arrivals = self.dispatchimpement_arrivals(engineerCode = data['engineerCode1'],
                        engineerTel = data['engineerTel1'],
                        serviceOrderNo = data['serviceOrderNo'],
                        dispatchOrderNo = detail['dispatchOrderNo'],
                        processType = '11',
                        operateType = '0',
                        distance = '0.05',#公里数
                        lng = order_location['lng'],
                        lat = order_location['lat'])
            if arrivals.get('status') is False:
                return arrivals
        elif str(detail['dispatchOrderStatus']) == '11':
            print('11')
            startoff = self.dispatchimpement_startoff(engineerCode = data['engineerCode1'],
                        engineerTel = data['engineerTel1'],
                        serviceOrderNo = data['serviceOrderNo'],
                        dispatchOrderNo = detail['dispatchOrderNo'],
                        processType = '10',
                        lng = self.sanshengxiang['lng'],
                        lat = self.sanshengxiang['lat'])
            print(json.dumps(startoff))

            if startoff.get('status') is False:
                return startoff
            arrivals = self.dispatchimpement_arrivals(engineerCode = data['engineerCode1'],
                        engineerTel = data['engineerTel1'],
                        serviceOrderNo = data['serviceOrderNo'],
                        dispatchOrderNo = detail['dispatchOrderNo'],
                        processType = '11',
                        operateType = '0',
                        distance = '0.05',#公里数
                        lng = order_location['lng'],
                        lat = order_location['lat'])
            if arrivals.get('status') is False:
                return arrivals
        elif str(detail['dispatchOrderStatus']) == '13':
            print('13')
            arrivals = self.dispatchimpement_arrivals(engineerCode = data['engineerCode1'],
                        engineerTel = data['engineerTel1'],
                        serviceOrderNo = data['serviceOrderNo'],
                        dispatchOrderNo = detail['dispatchOrderNo'],
                        processType = '11',
                        operateType = '0',
                        distance = '0.05',#公里数
                        lng = order_location['lng'],
                        lat = order_location['lat'])
            print(json.dumps(arrivals))
            if arrivals.get('status') is False:
                return arrivals
        else:
            print("next do save")
        return {"status":True}

    def saveinstallcard(self,data):
        '''
        "10"=>"待接收",
        "11"=>"未出发",
        "13"=>"已出发",
        "14"=>"已到达",
        '''
        #先获取最新的订单信息
        self.orderlist_all_data_update()
        print('save')
        info = db.find(MdSubmitcard,MdSubmitcard.service_orderno==data['serviceOrderNo'])
        detail = json.loads(info['detail_text'])
        order_location = utils.lnglat(detail['serviceCustomerAddress'])
        print(json.dumps(self.sanshengxiang))
        print(json.dumps(order_location))
        if data.get('sceneCustomerAreaCode') is None:
            data['sceneCustomerAreaCode'] = detail['customerAreaCode']
        rsa = self.recrej_startoff_arrivals(data,detail,order_location)
        if rsa.get("status") is False:
            return rsa
        r = self.dosaveinstallarchives(
                            sceneCustomerName = data['sceneCustomerName'],
                            sceneCustomerTel1 = data['sceneCustomerTel1'],
                            sceneCustomerTel2 = None,
                            sceneCustomerTel3 = None,
                            sceneAreaNum = detail['serviceAreaNum'],
                            sceneCustomerAreaCode = data['sceneCustomerAreaCode'],
                            sceneCustomerAreaName = data['customerAreaName'],
                            sceneCustomerAddress = data['sceneCustomerAddress'],
                            insideBarcode = data['insideBarcode'],
                            outsideBarcode = data['outsideBarcode'],
                            installCode = data['installCode'],
                            installDesc = data['installDesc'],
                            installUnitCode = "W5101007150",
                            installUnitName = "武侯区宏旺电器维修服务部",
                            purchaseDate = data['purchaseDate'],#购买时间
                            productionDate = data['productionDate'],#生产日期
                            areaCode = data['sceneCustomerAreaCode'],
                            areaName = data['customerAreaName'],
                            machineAddress = data['customerAreaName'],
                            brandCode = data['brandCode'],
                            brandName = data['brandName'],
                            prodCode = data['prodCode'],
                            prodName = data['prodName'],
                            productModel = data['productModel'],
                            saleUnitCode = data['saleUnitCode'],
                            saleUnitName = data['saleUnitName'],
                            engineerName1 = data['engineerName1'],
                            engineerCode1 = data['engineerCode1'],
                            engineerName2 = data['engineerName2'],
                            engineerCode2 = data['engineerCode2'],
                            unitCode = "W5101007150",
                            unitName = "武侯区宏旺电器维修服务部",
                            productCode = data['productCode'],
                            checkCode = data['checkCode'],
                            unactivedReson = None,
                            serviceOrderNo = data['serviceOrderNo'],
                            dispatchOrderNo = detail['dispatchOrderNo'],
                            engineerMachineApproval = data['engineerMachineApproval'],
                            cardNo = "",
                            pubRemark = "",
                            lbcsFlag = data['lbcsFlag'],
                            intelligenceFlag = data['intelligenceFlag'],
                            orgCode = data['orgCode'],
                            bootStrapCode = data['bootStrapCode'],
                            aumaterialRows = [],
                            createType = 10,
                            archivesNo = None,
                            machineId = data['machineId'],
                            installArchivesId = "",
                            longitude = order_location['lng'],
                            latitude = order_location['lat'],
                            engineerTel1 = data['engineerTel1'])
        if r.get('status') is False:
            utils.errorReport('添加安装卡失败:',data['serviceOrderNo'])
            return r
        print(json.dumps(r))
        for x in xrange(1,7):
            index = ""
            index = "pic[" + str(x) + "]"
            if data.get(index) != "":
                print(index)
                upload = self.doupload(isGetlocation = True,
                    fileIndex = x,
                    fileName = str(int(round(time.time() * 1000))) + ".jpeg",
                    serviceOrderNo = data['serviceOrderNo'],
                    account = data['engineerCode1'],
                    archivesNo = r['r']['installArchivesId'],
                    pictureCreateTime = int(round(time.time() * 1000)),
                    longitude = float(order_location['lng']),
                    latitude = float(order_location['lat']),
                    address = data['sceneCustomerAddress'],
                    contentStr = data.get(index))
                print(json.dumps(upload))
                if upload.get('status') is not True:
                    utils.errorReport('doupload error.index:'+str(x),data['serviceOrderNo'],r['installArchivesId'])
                    return upload
        archives = self.getmmpinstallarchives(serviceOrderNo = data['serviceOrderNo'],engineerCode = data['engineerCode1'],is_submit = 1)
        print(json.dumps(archives))
        if archives.get('status') is False:
            return archives
        return {"status":True,"msg":'add installcard success.',"type":'saveinstallcard',"r":r}

    def savearchivescard(self,data):
        '''
        "10"=>"待接收",
        "11"=>"未出发",
        "13"=>"已出发",
        "14"=>"已到达",
        '''
        #先获取最新的订单信息
        self.orderlist_all_data_update()
        print('save')
        info = db.find(MdSubmitcard,MdSubmitcard.service_orderno==data['serviceOrderNo'])
        detail = json.loads(info['detail_text'])
        order_location = utils.lnglat(detail['serviceCustomerAddress'])
        print(json.dumps(self.sanshengxiang))
        print(json.dumps(order_location))
        if data.get('sceneCustomerAreaCode') is None:
            data['sceneCustomerAreaCode'] = detail['customerAreaCode']
        
        rsa = self.recrej_startoff_arrivals(data,detail,order_location)
        if rsa.get("status") is False:
            return rsa
        repairArchivesNo = "WX"+data['serviceOrderNo'][2:7] + str(int(time.time()))[-7:]
        configId = "7c42addd-f3f6-436a-a097-58964bfd"
        r = self.doSaveRepairArchives(curUserAccount = data['engineerTel1'],#师傅电话
                        insideBarcode=data['insideBarcode'],
                        outsideBarcode=data['outsideBarcode'],
                        brandCode=data['brandCode'],
                        brandName=data['brandName'],
                        machineAddress=data['customerAreaName'],
                        machineId=data['machineId'],
                        prodCode=data["prodCode"],
                        prodName=data["prodName"],
                        productCode=data["productCode"],
                        productionDateStr=data["productionDateStr"],
                        installDateStr=data["installDateStr"],
                        productDesc=data["productDesc"],
                        productModel=data["productModel"],
                        purchaseDateStr=data["purchaseDateStr"],
                        repairStartDateStr=data["repairStartDateStr"],
                        warrantyTypeCode=data["warrantyTypeCode"],
                        faultDesc=data["faultDesc"],
                        faultCode=data["faultCode"],
                        partsDesc=data["partsDesc"],
                        partsCode=data["partsCode"],
                        maintContent=data["maintContent"],
                        maintContentCode=data["maintContentCode"],
                        materialFlag="N",
                        warrantyType=data["warrantyType"],
                        orgCode=data["orgCode"],
                        useStatus=data["useStatus"],
                        warrantyType_11="11",
                        womActFlag="1",
                        cardNo=data["cardNo"],
                        contactTimeStr=data["contactTimeStr"],
                        dispatchOrderNo=data["dispatchOrderNo"],
                        engineerCode1=data["engineerCode1"],
                        engineerName1=data["engineerName1"],
                        partsCode_2="null",
                        partsDesc_2='null',
                        pubRemark="null",
                        oldMaterialName=data["oldMaterialName"],
                        oldMaterialCode=data["oldMaterialCode"],
                        oldMaterialModel=data["oldMaterialModel"],
                        newMaterialModel=data["newMaterialModel"],
                        newMaterialName=data["newMaterialName"],
                        newMaterialCode=data["newMaterialCode"],
                        oldMaterialNum=data["oldMaterialNum"],
                        newMaterialNum=data["newMaterialNum"],
                        renovateTimeStr="null",
                        repairArchivesNo=repairArchivesNo,
                        repairProcess=data["repairProcess"],
                        breakdownDesc=data["breakdownDesc"],
                        sceneAreaNum=data["sceneAreaNum"],
                        sceneCustomerAddress=data["sceneCustomerAddress"],
                        sceneCustomerAddressId=data["sceneCustomerAddressId"],
                        sceneCustomerAreaCode=data["sceneCustomerAreaCode"],
                        sceneCustomerAreaName=data["sceneCustomerAreaName"],
                        sceneCustomerCode=data["sceneCustomerCode"],
                        sceneCustomerId=data["sceneCustomerId"],
                        sceneCustomerName=data["sceneCustomerName"],
                        sceneCustomerTel1=data["sceneCustomerTel1"],
                        serviceCustomerDemandId=data["serviceCustomerDemandId"],
                        serviceMethodCode="10",
                        serviceOrderId=data["serviceOrderId"],
                        serviceOrderNo=data["serviceOrderNo"],
                        unitCode=data["unitCode"],
                        unitName=data["unitName"],
                        vipSettlementRatioStr="1.00",
                        workNo1=data['engineerCode1'])

        if r.get('status') is False:
            utils.errorReport('添加维修卡失败:'+ data['serviceOrderNo']+r['msg'],system_name = self.system_name)
            return r
        print(json.dumps(r))
        for x in xrange(1,7):
            _ttt = int(round(time.time() * 1000))
            index = ""
            index = "pic[" + str(x) + "]"
            if data.get(index) != "":
                print(index)
                upload = self.repair_doupload(
                    data.get(index),
                    str(x),
                    str(_ttt) + ".jpeg",
                    data['serviceOrderNo'],
                    str(configId),
                    repairArchivesNo,
                    _ttt)
                print(json.dumps(upload))
                if upload.get('status') is False:
                    print(upload["msg"])
                    return upload

        archives = self.getmmpinstallarchives(serviceOrderNo = data['serviceOrderNo'],engineerCode = data['engineerCode1'],is_submit = 1)
        print(json.dumps(archives))
        if archives.get('status') is False:
            return archives
        return {"status":True,"msg":'add installcard success.',"type":'savearchivescard',"r":r}

    def dosavefeedback(self,data):
        print(json.dumps(data))
        info = db.find(MdSubmitcard,MdSubmitcard.service_orderno==data['serviceOrderNo'])
        detail = json.loads(info['detail_text'])
        order_location = utils.lnglat(detail['serviceCustomerAddress'])
        archives = self.getmmpinstallarchives(serviceOrderNo = data['serviceOrderNo'],engineerCode = data['engineerCode'],is_submit = 1)
        if archives.get('status') is False:
            return archives
        if archives.get('r').get('total') == 0:
            return {"status":False,"msg":'未录入档案.请录入档案',"type":'dosavefeedback',"r":{}}
        print(archives.get('r').get('total')-1)
        lists = archives.get('r').get('list')
        barcode = lists[archives.get('r').get('total')-1]        
        feedback = self.processfeedback(
                            orgCode=detail['orgCode'],
                            engineerCode=data['engineerCode'],
                            engineerTel=data['engineerTel'],
                            serviceOrderNo=data['serviceOrderNo'],
                            dispatchOrderNo=detail['dispatchOrderNo'],
                            pubRemark='',
                            feedbackResultCode='11',
                            feedbackDesc=u'安装完成，用户认可',
                            mmpArchivesRequestList='',
                            serviceCustomerId = detail['serviceCustomerId'], 
                            serviceMainTypeCode = detail['serviceMainTypeCode'], 
                            serviceCustomerDemandId = detail['womServiceUserDemandVOs'][0]['serviceCustomerDemandId'],
                            insideBarCode = barcode['insideBarcode'],
                            outsideBarcode = barcode['outsideBarcode'],
                            productCode = "",
                            prodCode = detail['womServiceUserDemandVOs'][0]['prodCode'],
                            prodName = detail['womServiceUserDemandVOs'][0]['prodName'],
                            productModel = "", 
                            warrantyType = "",
                            expirationDate = "",
                            sceneCustomerMobile = "",
                            sceneCustomerAddress ="",
                            installUnitName = "", 
                            saleUnitCode = "", 
                            saleUnitName = "", 
                            brandCode = detail['womServiceUserDemandVOs'][0]['brandCode'], 
                            brandName = detail['womServiceUserDemandVOs'][0]['brandName'],
                            productUse = "", 
                            productionDateStr = "", 
                            machineId = "",
                            feedbackType='15',
                            feedbackMainItemCode=u'FW01',
                            feedbackMainItemName=u'处理好，用户满意',
                            feedbackSubItemCode=u'FW0101',
                            feedbackSubItemName=u'通过送货、安装、调整、维修、清洗、保养、退换机处理好',
                            contactSystem=detail['contactSystem'],
                            contactTime=datetime.datetime.fromtimestamp(detail['contactTime']/1000).strftime('%Y-%m-%d'),
                            nuit_longitude=order_location['lng'],
                            unit_latitude=order_location['lat'],
                            distance='0.05',#公里数
                            operateType='0',
                            longitude=order_location['lng'],
                            latitude=order_location['lat'])
        print(json.dumps(feedback))
        if feedback.get('status') is False:
            return feedback
        session = DBSession()
        order = session.query(MdSubmitcard).filter(MdSubmitcard.service_orderno==data['serviceOrderNo']).all()
        _order = order[0]
        _order.status = 1
        session.commit()
        session.close()
        return feedback

    def getFaultList(self, productCode = '31022010000101'):
        url = self.repair_url + 'getFaultList'
        data = 'json={"body":{"supDbFaultVO":{"classCode":"SHWX","orgCode":"CS006","prodCodeThird":"1000","productCode":'+productCode+'}}}'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Origin': 'file://',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(method = 'post',url = url,data = data,headers = headers)
        if r.get('status') is False:
            return {"msg":r.get('errorMsg'),"status":False}
        self.__after_getFaultList(r.get('returnObject').get('supDbFaultVOs'),productCode = productCode)
        return r

    def __after_getFaultList(self,data,productCode):
        for item in data:
            self.getFaultResonList(productCode = productCode,faultCode = item.get('faultCode'),orgCode=item.get('orgCode'))
            continue
            session = DBSession()
            mmp = MdMmprepairfault()
            mmp.fault_id = item.get('faultId')
            mmp.fault_code = item.get('faultCode')
            mmp.fault_desc = item.get('faultDesc')
            mmp.prod_code_third = item.get('prodCodeThird')
            mmp.org_code = item.get('orgCode')
            mmp.product_code = productCode
            mmp.sort = item.get('sort')
            mmp.content_text = json.dumps(item)
            session.add(mmp)
            session.commit()
            session.close()
            self.getFaultResonList(productCode = productCode,faultCode = item.get('faultCode'),orgCode=item.get('orgCode'))
        # session.commit()
        # session.close()

    def getFaultResonList(self, productCode,faultCode,orgCode,prodCode='1000',classCode = 'SHWX'):
        url = self.repair_url + 'getFaultResonList'
        data = 'json={"body":{"supDbFaultReasonVO":{"classCode":"'+classCode+'","orgCode":"'+orgCode+'","productCode":"'+productCode+'","prodCode":"'+prodCode+'","faultCode":"'+faultCode+'"}}}'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Origin': 'file://',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(method = 'post',url = url,data = data,headers = headers)
        if r is False:
            r = utils.request(method = 'post',url = url,data = data,headers = headers)
        if r is False:
            r = utils.request(method = 'post',url = url,data = data,headers = headers)
        if r is False:
            r = utils.request(method = 'post',url = url,data = data,headers = headers)
        if r is False:
            print("getFaultResonList 获取失败")
            return True
        if r.get('status') is False:
            return {"msg":r.get('errorMsg'),"status":False}
        self.__after_getFaultResonList(r.get('returnObject').get('supDbResonVOs'),productCode,faultCode)
        return r

    def __after_getFaultResonList(self,data,productCode,faultCode):
        for item in data:
            self.getMaintList(productCode,item.get('resonCode'),'SHWX',item.get('orgCode'),item.get('prodCodeThird'))
            continue
            session = DBSession()
            mmp = MdMmpFaultreson()
            mmp.reson_id = item.get('resonId')
            mmp.reson_code = item.get('resonCode')
            mmp.reson_desc = item.get('resonDesc')
            mmp.product_code = productCode
            mmp.fault_code = faultCode
            mmp.prod_code_third = item.get('prodCodeThird')
            mmp.org_code = item.get('orgCode')
            mmp.content_text = json.dumps(item)
            session.add(mmp)
            session.commit()
            session.close()
            # self.getMaintList(productCode,item.get('resonCode'),'SHWX',item.get('orgCode'),item.get('prodCodeThird'))
        # session.commit()
        # session.close()

    def getMaintList(self, productCode,resonCode,classCode,orgCode,prodCodeThird):
        url = self.repair_url + 'getMaintList'
        data = 'json={"body":{"supDbMaintVO":{"classCode":"'+classCode+'","orgCode":"'+orgCode+'","prodCodeThird":"'+prodCodeThird+'","resonCode":"'+resonCode+'","productCode":"'+productCode+'"}}}'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Origin': 'file://',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(method = 'post',url = url,data = data,headers = headers)
        if r is False:
            r = utils.request(method = 'post',url = url,data = data,headers = headers)
        if r is False:
            r = utils.request(method = 'post',url = url,data = data,headers = headers)
        if r is False:
            print('////////////////')
            return True
        if r.get('status') is False:
            return {"msg":r.get('errorMsg'),"status":False}
        self.__after_getMaintList(r.get('returnObject').get('rows'),productCode,classCode)
        return r

    def __after_getMaintList(self,data,productCode,classCode):
        # print(len(data))
        for item in data:
            self.getMaterialInfos(item.get('maintCode'),productCode,item.get('orgCode'),prodCode='1000',unitCode = 'W5101007150')
            continue
            session = DBSession()
            mmp = MdMmpfaultmaint()
            mmp.maint_id = item.get('maintId')
            mmp.maint_settlement_id = item.get('maintSettlementId')
            mmp.maint_settlement_code = item.get('maintSettlementCode')
            mmp.maint_settlement_desc = item.get('maintSettlementDesc')
            mmp.maint_code = item.get('maintCode')
            mmp.class_code = classCode
            mmp.reson_code = item.get('resonCode')
            mmp.reson_desc = item.get('resonDesc')
            mmp.maint_desc = item.get('maintDesc')
            mmp.product_code = productCode
            mmp.prod_code_third = item.get('prodCodeThird')
            mmp.org_code = item.get('orgCode')
            mmp.content_text = json.dumps(item)
            session.add(mmp)
            session.commit()
            session.close()
            # self.getMaterialInfos(item.get('maintCode'),productCode,item.get('orgCode'),prodCode='1000',unitCode = 'W5101007150')
        # db.session.commit()
        # db.session.close()

    def getMaterialInfos(self,maintCode,productCode,orgCode,prodCode,unitCode = 'W5101007150'):
        r = self.getMaterialInfosByParam(productCode=productCode,
                            maintCode=maintCode,
                            orgCode=orgCode,
                            unitCode = unitCode,
                            prodCode = prodCode,
                            page = 1,
                            rows = 20,
                            is_pre=True)
        if len(r.get('returnObject').get('rows')) == 0:
            print(r.get('returnObject').get('rows'))
            print(r.get('returnObject'))
            print("空.")
            return True
        total = r.get('returnObject').get('total')
        page = 0
        page_size = 200
        while page * page_size < total:
            page = page + 1
            p = {"productCode":productCode,"maintCode":maintCode,"orgCode":orgCode,"unitCode":unitCode,"prodCode":prodCode,"page":page,"rows":page_size}
            self.in_queue_pre.put(json.dumps(p))
            # self.getMaterialInfosByParam(productCode=productCode,
            #                 maintCode=maintCode,
            #                 orgCode=orgCode,
            #                 unitCode = unitCode,
            #                 prodCode = prodCode,
            #                 page = page,
            #                 rows = page_size)
    
    # def getMaterialInfosByParam(self, productCode='31022010000101',
    #                         maintCode='W100000716',
    #                         orgCode='CS006',
    #                         unitCode = 'W5101007150',
    #                         prodCode = '1000',
    #                         page = 1,
    #                         rows = 200,
    #                         is_pre = False):
    def getMaterialInfosByParam(self, requestData, is_pre = False):
        url = self.repair_url + 'getMaterialInfosByParam'
        # data = 'json={"body":{"productCode":"'+productCode
        # data +='","materialCode":"","materialName":"","maintCode":"'
        # data +=maintCode+'","orgCode":"'+orgCode+'","prodCode":"'+prodCode
        # data +='","unitCode":"'+unitCode+'","page":'+str(page)+',"rows":'+str(rows)+'}}'
        body = {"body":requestData}
        data = "json=" + json.dumps(body)
        # json={"body":{"productCode":"31022010000101","materialCode":"","materialName":"电控","maintCode":"W100000716","orgCode":"CS006","prodCode":"1000","unitCode":"W5101007150","page":1,"rows":20}}
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Origin': 'file://',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(method = 'post',url = url,data = data,headers = headers,timeout=200)
        # print(len(r.get('returnObject').get('rows')))
        if r is False:
            r = utils.request(method = 'post',url = url,data = data,headers = headers,timeout=200)
        if r is False:
            r = utils.request(method = 'post',url = url,data = data,headers = headers,timeout=200)
        # if is_pre is True and r.get('returnObject') is not None:
            # self.__after_getMaterialInfosByParam(r.get('returnObject').get('rows'),productCode,orgCode,prodCode,maintCode,unitCode)
        print(r)
        return {"msg":r.get('errorMsg'),"status":r.get('status'),"r":r,"type":"getMaterialInfosByParam"}

    def __after_getMaterialInfosByParam(self,data,productCode,orgCode,prodCode,maintCode,unitCode):
        print("MaterialInfos len",len(data))
        for item in data:
            session = DBSession()
            mmp = MdMmpmaterialinfos()
            mmp.material_type_main_code = item.get('materialTypeMainCode')
            mmp.material_type_main_name = item.get('materialTypeMainName')
            mmp.material_type_mid_code = item.get('materialTypeMidCode')
            mmp.material_type_mid_name = item.get('materialTypeMidName')
            mmp.material_code = item.get('materialCode')
            mmp.material_name = item.get('materialName')
            mmp.material_model = item.get('materialModel')
            mmp.material_desc = item.get('materialDesc')
            mmp.storage_qty = item.get('storageQty')
            mmp.product_code = productCode
            mmp.maint_code = maintCode
            mmp.org_code = orgCode
            mmp.prod_code = prodCode
            mmp.unit_code = unitCode
            mmp.content_text = json.dumps(item)
            session.add(mmp)
            print("infos")
            session.commit()
            session.close()
            params = {"materialCode":item.get('materialCode'),"maintCode":maintCode,"orgCode":orgCode}
            self.in_queue.put(json.dumps(params))
            # self.getMaterialReplace(item.get('materialCode'),maintCode,orgCode)
    
    def use_queue(self,in_queue):
        while True:
            p = self.in_queue.get()
            p = json.loads(p)
            self.getMaterialReplace(p.get('materialCode'),p.get("maintCode"),p.get("orgCode"))
            # ret = self.getMaterialReplace(self.in_queue,url = url)
            self.in_queue.task_done()#向任务已经完成的队列发送一个消息

    def use_queue_pre(self,in_queue_pre):
        while True:
            p = self.in_queue_pre.get()
            p = json.loads(p)
            self.getMaterialInfosByParam(p.get('productCode'),
                                p.get("maintCode"),
                                p.get("orgCode"),
                                p.get("unitCode"),
                                p.get("prodCode"),
                                p.get("page"),
                                p.get("rows"),True)
            # ret = self.getMaterialReplace(self.in_queue,url = url)
            self.in_queue_pre.task_done()#向任务已经完成的队列发送一个消息
    
    # def getMaterialReplace(self, materialCode,
    #                         maintCode,
    #                         orgCode='CS006'):
    def getMaterialReplace(self, requestData):
        url = self.repair_url + 'getMaterialReplace'
        # data = 'json={"body":{"supMaterialReplaceVO":{"beforMaterialCode":"'+materialCode
        # data +='","orgCode":"'+orgCode+'"}}}'
        body = {"body":{"supMaterialReplaceVO":requestData}}
        data = "json=" + json.dumps(body)
        # json={"body":{"supMaterialReplaceVO":{"beforMaterialCode":"17222000000074","orgCode":"CS006"}}}
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Origin': 'file://',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(method = 'post',url = url,data = data,headers = headers,timeout=20)
        if r is False:
            r = utils.request(method = 'post',url = url,data = data,headers = headers,timeout=20)
        if r is False:
            r = utils.request(method = 'post',url = url,data = data,headers = headers,timeout=20)
        if r is False:
            return {"msg":"网络请求无响应","status":False,"r":r,"type":"getMaterialReplace"}
        return {"msg":r.get('errorMsg'),"status":r.get('status'),"r":r,"type":"getMaterialReplace"}

    def __after_getMaterialReplace(self,data,materialCode,maintCode):
        session = DBSession()
        for item in data:
            mmp = MdMmpmaterialreplace()
            mmp.replace_id = item.get('replaceId')
            mmp.maint_code = maintCode
            mmp.replace_code = item.get('replaceCode')
            mmp.befor_material_code = item.get('beforMaterialCode')
            mmp.befor_material_name = item.get('beforMaterialName')
            mmp.material_code = materialCode
            mmp.befor_source_material_code = item.get('beforSourceMaterialCode')
            mmp.after_material_code = item.get('afterMaterialCode')
            mmp.after_material_name = item.get('afterMaterialName')
            mmp.replace_type = item.get('replaceType')
            mmp.pub_validly = item.get('pubValidly')
            mmp.org_code = item.get('orgCode')
            mmp.content_text = json.dumps(item)
            print("mmp replace")
            session.add(mmp)
        session.commit()
        session.close()

    '''
        {
            "body": {
                "brandCode": "MIDEA",
                "purchaseDate": "2013-01-28",
                "plantProtectTime": "2013-01-28",
                "insideBarcode": "D110001012913227310253",
                "outsideBarcode": "D110001013013107331171",
                "prodCode": "1000",
                "productCode": "31022010000101",
                "concatcTime": "2017-12-01",
                "repairTypeCode": [
                    "W100000716"
                ],
                "userMsg": {
                    "customerId": "1010698423"
                }
            }
        }
    '''
    def getTypeoftotalcare(self, requestData):
        url = self.repair_url + 'getTypeoftotalcare'
        data = "json=" + json.dumps(requestData)
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Origin': 'file://',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'com.midea.connect.out'
        }
        r = utils.request(method = 'post',url = url,data = data,headers = headers)
        return {"msg":r.get('errorMsg'),"status":r.get("status"),"r":r,"type":"getTypeoftotalcare"}

    def doSaveRepairArchives(self,curUserAccount = '15208390257',
                        insideBarcode='D110001103915507330225',
                        outsideBarcode='D110001104015527330015',
                        brandCode='MIDEA',
                        brandName="美的",
                        machineAddress="成都市成华区全区文德路宝泰家园5栋1单元2401号",
                        machineId="MA260020150607516103",
                        prodCode="1000",
                        prodName="家用空调",
                        productCode="31022010000584",
                        productionDateStr="2015-05-07 00:00:00",
                        installDateStr="2015-06-16 13:01:30",
                        productDesc="KFR-35GW/BP3DN1Y-KB(B1) 变频分体挂壁式空调器 水蜜红 美的",
                        productModel="KFR-35GW/BP3DN1Y-KB(B1) ",
                        purchaseDateStr="2015-06-14 00:00:00",
                        repairStartDateStr="2015-06-14 00:00:00",
                        warrantyTypeCode="10",
                        faultDesc="产品工作效果差",
                        faultCode="X1000002",
                        partsDesc="其它问题",
                        partsCode="Y10000033",
                        maintContent="空调缺氟未找到漏点，调试加氟",
                        maintContentCode="W100000161",
                        materialFlag="N",
                        warrantyType="10",
                        orgCode="CS006",
                        useStatus="11",
                        warrantyType_11="11",
                        womActFlag="1",
                        cardNo="",
                        contactTimeStr="2017-12-07",
                        dispatchOrderNo="PG171214329449",
                        engineerCode1="E0293031",
                        engineerName1="王健",
                        partsCode_2="null",
                        partsDesc_2='null',
                        pubRemark="null",
                        oldMaterialName="",
                        oldMaterialCode="",
                        oldMaterialModel="",
                        newMaterialModel="",
                        newMaterialName="",
                        newMaterialCode="",
                        oldMaterialNum="",
                        newMaterialNum="",
                        renovateTimeStr="null",
                        repairArchivesNo="WX171214425160",
                        repairProcess="空调缺氟，加氟后试机运行正常",
                        breakdownDesc="空调不制热，制热效果不好",
                        sceneAreaNum="028",
                        sceneCustomerAddress="四川省成都市武侯区桂溪街道老成仁路8号育才竹岛1栋2506",
                        sceneCustomerAddressId="1510107064",
                        sceneCustomerAreaCode="",
                        sceneCustomerAreaName="四川省成都市武侯区桂溪街道",
                        sceneCustomerCode="YH17120108368468",
                        sceneCustomerId="1041362971",
                        sceneCustomerName="王宁",
                        sceneCustomerTel1="18981989160",
                        serviceCustomerDemandId="1052969483",
                        serviceMethodCode="10",
                        serviceOrderId="1052443176",
                        serviceOrderNo="FW171214328190",
                        unitCode="W5101007150",
                        unitName="武侯区宏旺电器维修服务部",
                        vipSettlementRatioStr="1.00",
                        workNo1="E0293031"):
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Origin': 'file://',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'com.midea.connect.out'
        }
        url = self.repair_url + 'doSaveArchives'

        body = {
                "body": {
                    "curUserAccount": curUserAccount,
                    "machineArchivesVO": {
                        "insideBarcode": insideBarcode,
                        "outsideBarcode": outsideBarcode,
                        "brandCode": brandCode,
                        "brandName": brandName,
                        "machineAddress": machineAddress,
                        "machineId": machineId,
                        "orgCode": orgCode,
                        "prodCode": prodCode,
                        "prodName": prodName,
                        "productCode": productCode,
                        "productionDateStr": productionDateStr,
                        "installDateStr": installDateStr,
                        "productDesc": productDesc,
                        "productModel": productModel,
                        "purchaseDateStr": purchaseDateStr,
                        "repairStartDateStr": repairStartDateStr,
                        "warrantyTypeCode": warrantyTypeCode
                    },
                    "maintenanceProjectList": [
                        {
                            "faultDesc": faultDesc,
                            "faultCode": faultCode,
                            "partsDesc": partsDesc,
                            "partsCode": partsCode,
                            "maintContent": maintContent,
                            "maintContentCode": maintContentCode,
                            "materialFlag": materialFlag,
                            "orgCode": orgCode,
                            "warrantyType": warrantyType
                        }
                    ],
                    "materialList": [
                        # {
                        #     "maintContentCode": maintContentCode,
                        #     "oldMaterialName": oldMaterialName,
                        #     "oldMaterialCode": oldMaterialCode,
                        #     "oldMaterialModel": oldMaterialModel,
                        #     "newMaterialModel": newMaterialModel,
                        #     "newMaterialName": newMaterialName,
                        #     "newMaterialCode": newMaterialCode,
                        #     "oldMaterialNum": oldMaterialNum,
                        #     "newMaterialNum": newMaterialNum,
                        #     "orgCode": orgCode,
                        #     "useStatus": useStatus,
                        #     "warrantyType": warrantyType
                        # }
                    ],
                    "orgCode": orgCode,
                    "womActFlag": womActFlag,
                    "repairArchivesVO": {
                        "cardNo": cardNo,
                        "contactTimeStr": contactTimeStr,
                        "dispatchOrderNo": dispatchOrderNo,
                        "engineerCode1": engineerCode1,
                        "engineerName1": engineerName1,
                        "partsCode": partsCode,
                        "partsDesc": partsDesc,
                        "prodCode": prodCode,
                        "pubRemark": pubRemark,
                        "renovateTimeStr": renovateTimeStr,
                        "repairArchivesNo": repairArchivesNo,
                        "repairProcess": repairProcess,
                        "breakdownDesc": breakdownDesc,
                        "sceneAreaNum": sceneAreaNum,
                        "sceneCustomerAddress": sceneCustomerAddress,
                        "sceneCustomerAddressId": sceneCustomerAddressId,
                        "sceneCustomerAreaCode": sceneCustomerAreaCode,
                        "sceneCustomerAreaName": sceneCustomerAreaName,
                        "sceneCustomerCode": sceneCustomerCode,
                        "sceneCustomerId": sceneCustomerId,
                        "sceneCustomerName": sceneCustomerName,
                        "sceneCustomerTel1": sceneCustomerTel1,
                        "serviceCustomerDemandId": serviceCustomerDemandId,
                        "serviceMethodCode": serviceMethodCode,
                        "serviceOrderId": serviceOrderId,
                        "serviceOrderNo": serviceOrderNo,
                        "unitCode": unitCode,
                        "unitName": unitName,
                        "vipSettlementRatioStr": vipSettlementRatioStr,
                        "workNo1": workNo1
                    }
                }
            }
        if newMaterialName is not "":
            materialList = {
                "maintContentCode": maintContentCode,
                "oldMaterialName": oldMaterialName,
                "oldMaterialCode": oldMaterialCode,
                "oldMaterialModel": oldMaterialModel,
                "newMaterialModel": newMaterialModel,
                "newMaterialName": newMaterialName,
                "newMaterialCode": newMaterialCode,
                "oldMaterialNum": oldMaterialNum,
                "newMaterialNum": newMaterialNum,
                "orgCode": orgCode,
                "useStatus": "11",
                "warrantyType": "11"
            }
            body['body']["materialList"].append(materialList)
        data = "json=" + json.dumps(body)
        print(data)
        r = utils.request(method = 'post',url = url,data = data,headers = headers)
        print(json.dumps(r))
        return {"msg":r.get('errorMsg'),"status":r.get("status"),"r":r,"type":"doSaveRepairArchives"}

    #configId=str(uuid.uuid4()),
    def repair_doupload(self,contentStr,
                fileIndex="1",
                fileName = str(int(round(time.time() * 1000))) + ".jpeg",
                serviceOrderNo="FW171212739293",
                configId='7c42addd-f3f6-436a-a097-58964bfd',
                subId='WX171211931982',
                pictureCreateTime = int(round(time.time() * 1000))):
        url = self.postSale_url + 'doupload'
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Origin': 'file://',
            'User-Agent': self.UserAgent,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.midea.connect.out'
        }
        fileContent = {
            "contentStr":contentStr,
            "fileIndex":fileIndex,
            "fileName":fileName,
            "serviceOrderNo":serviceOrderNo,
            "configId":configId,
            "subId":subId,
            "pictureCreateTime":pictureCreateTime
        }
        data = {
            "fileContent":json.dumps(fileContent)
        }
        r = utils.request(url,method = 'post',data = data,headers = headers)
        print(json.dumps(r))
        if r.get('status') is False:
            utils.errorReport('图片上传失败,info:' + r['errorMsg'] + subId,system_name = self.system_name)
        return {"status":r['status'],"msg":r['errorMsg'],"type":'repair_doupload',"r":r}

    def searchFromSnMmp(self,requestData,
                    businessFlag="WX",
                    wholeMachineFlag="x"):
        url = self.repair_url + "searchFromSnMmp"
        headers = {
            'Host': 'mapnew.midea.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': self.UserAgent,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Origin': 'file://',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'com.midea.connect.out'
        }
        data = 'json={"body":{"orgCode":"'+requestData['orgCode']+'","insideBarcode":"'+requestData['insideBarcode']+'","businessFlag":"'+businessFlag+'","wholeMachineFlag":"'+wholeMachineFlag+'"}}'
        r = utils.request(headers = headers,data = data,method = 'post',url = url)
        return {"status":r['status'],"msg":r['errorMsg'],"type":'searchFromSnMmp',"r":r}

    def rtest(self):
        img = {
            '1':u'./pic/35-wx-加氟.jpg',
            '2':u'./pic/35-wx-加氟2.jpg',
            '3':u'./pic/35-wx-加氟3.jpg'
        }
        print(img)
        configId = configId=str(uuid.uuid4())
        configId = "7c42addd-f3f6-436a-a097-58964bfd"
        subId = "WX171214425160"
        _ttt = int(round(time.time() * 1000))
        for i in img:
            self.repair_doupload(utils.base64Img(img[i]),str(i),str(_ttt) + ".jpeg",'FW171214328190',str(configId),subId,_ttt)