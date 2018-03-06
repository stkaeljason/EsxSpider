# -*- coding: utf-8 -*-
import requests,json,random
import appBot.utils as utils
import appBot.auxAppApi
import time
import os.path
from db_model.auxAccount import auxAccount
from db_model.AuxFactoryOrder import AuxFactoryOrder
from db_model.AuxOrder import AuxOrder
from db_model.AuxMerchant import AuxMerchant
from db_model.db import DBSession

class AuxApi():
    """ aux web api """
    def __init__(self,account,password):
        print(account,password)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Host': 'aux.bangjia.me',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            "Accept-Encoding":"gzip, deflate",
            "Accept-Language":"zh-CN,zh;q=0.8"
        }
        self.index_url = "http://aux.bangjia.me/index.php/Ucenter/index.html"
        self.account = account
        self.password = password
        self.system_name = "Aux web"
        self.s = requests.Session()
        self.s.get(self.index_url)
        r = self.login()
        if "用户名或密码错误" in r:
            utils.errorReport("用户名或密码错误:"+self.account,system_name = self.system_name)
            print("用户名或密码错误")
            return None
    
    def login(self,event_submit_do_login = "submit",submit_btn=u'登录'):
        data = "username="+self.account+"&password="+self.password+"&event_submit_do_login=submit&submit-btn=登录"
        headers = self.headers
        headers['Referer'] = "http://aux.bangjia.me/index.php/Public/login.html"
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        login_url = 'http://aux.bangjia.me/index.php/Public/login.html'
        r = self.s.post(url = login_url,data = data,headers = self.headers)
        return r.text

    def add_order(self,data,operator = None):
        '''添加订单接口
        data:字典'''
        add_order_url = 'http://aux.bangjia.me/index.php/Auxtest/auxaddOrder.html'
        r = self.s.post(url = add_order_url,data = data,headers = self.headers,timeout = 30.0)
        ret = r.text
        print(r.text)
        try:
            if u'添加成功' in ret or '添加成功' in ret:
                self._after_add(data,operator)
                return True
        except Exception as e:
            pass
        
        try:
            if str(ret['status']) == '1':
                self._after_add(data,operator)
                return True
        except Exception as e:
            pass
        return utils.errorReport('帮家建单失败:'+json.dumps(ret)+'info:' + json.dumps(ret),system_name = self.system_name)

    def _after_add(self,data,operator):
        utils.orderTracking(ord_id = operator['ord_id'],
                                operator_id = operator['operator_id'],
                                operator_name = operator['operator_name'],
                                title = '帮家建单',
                                desc = operator['operator_name'] + '帮家建单成功',
                                add_time = time.time())
    
    def dispatch_order(self,orderno, userid,operator = None):
        '''派单接口
        orderno:订单号，字符串
        userid：订单的内容数据，字典
        '''
        dispatch_url = 'http://aux.bangjia.me/index.php/Auxtest/dispatchorder.html'
        from_data = {
            'orderno': orderno,
            'userid[]': userid
        }
        r = self.s.post(url = dispatch_url,data = from_data,headers = self.headers)
        print("dispatch:")
        ret = r.text
        print(r.text)
        try:
            if '派单成功' in ret or u'派单成功' in ret:
                print('dispatch ok')
                self._after_dispatch(orderno = orderno,userid = userid,operator = operator)
                print('dispatch ok after')
                return True
        except Exception as e:
            pass
    
        try:
            if str(ret['status']) == '1':
                print('dispatch field')
                self._after_dispatch(orderno,userid,operator,ret)
                return False
        except Exception as e:
            pass
        return utils.errorReport('帮家派单失败,' + ',orderno:' + orderno,system_name = self.system_name)

    def _after_dispatch(self,orderno,userid,operator):
        print(orderno,userid,operator)
        utils.orderTracking(ord_id = operator['ord_id'],
                                operator_id = operator['operator_id'],
                                operator_name = operator['operator_name'],
                                title = '帮家派单',
                                desc = operator['operator_name'] + '帮家派单成功' +str(userid),
                                add_time = time.time())

    def gridIndex(self,test = None):
        '''wait accept order'''
        url = 'http://aux.bangjia.me/index.php/auxtest/gridIndex'
        data = {'status':110,'page':1,'rows':100}
        r = self.s.post(url = url,data = data,headers = self.headers)
        return json.loads(r.text)

    def providerReceiptOrder(self,factorynumber,operator = None):
        url = 'http://aux.bangjia.me/index.php/Auxtest/providerReceiptOrder.html'
        data = {'factorynumber':factorynumber}
        r = self.s.post(url = url,headers = self.headers,data = data)
        print('接单返回:')
        print(r.text)
        ret = json.loads(r.text)
        print("ret",ret)
        print(ret['ret'])
        if str(ret['ret']) == '1':
            self._after_Receipt(factorynumber,operator,ret)        
            return ret
        return utils.errorReport('[帮家]商家接单失败:factorynumber' + factorynumber + 'info:' + ret['msg'],system_name = self.system_name)

    def _after_Receipt(self,factorynumber,operator,ret):
        print("_after_Receipt:",factorynumber)
        utils.orderTracking(ord_id = operator['ord_id'],
                                operator_id = operator['operator_id'],
                                operator_name = operator['operator_name'],
                                title = '商家接单成功[帮家]',
                                desc = operator['operator_name'] + '操作在在帮家后台接单成功',
                                add_time = time.time())

    def get_finished_order(self,order):
        api_url = 'http://aux.bangjia.me/index.php/Auxtest/getfinishinfo/orderno/{}/type/install.html'.format(order)
        r = self.s.get(url = api_url,headers = self.headers)
        return r.text

    def get_installcard(self,id):
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
            'Host': 'aux.bangjia.me',
            'X-Requested-With': 'XMLHttpRequest'
        }
        api_url = 'http://aux.bangjia.me/index.php/Auxtest/getinstallcardinfo.html'
        form_data = {
            'id':id,
        }
        r = self.s.post(url = api_url,data = form_data,headers = headers)
        return r.text


    def search_sn(self,sntype,key_word):
        '''搜索内机号
        key_word:str类型
        for test
        '''
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
            'Host': 'aux.bangjia.me',
            'X-Requested-With': 'XMLHttpRequest'
        }
        api_url = 'http://aux.bangjia.me/index.php/Auxtest/countorder.html'
        data = {
            'day':'',
            'originname':'',
            'brand':'',
            'ordername':'',
            'machinetype':'',
            'orderlevel':'',
            'masterid':'',
            'datetype':2,
            'startdate':'',
            'enddate':'',
            'keywordoption':sntype,
            'keyword':key_word,
            'overtime':''
        }
        r = self.s.get(url = api_url,data = data,headers = headers)
        return r.text

    #业务代码
    def add_dispatch(self,data,operator = None):
        '''
        建单，接单，派单业务处理
        '''
        print('add_dispatch')
        print(self.account)
        add_ret = self.add_order(data['adddata'],operator = operator)
        if add_ret is False:
           return add_ret
        grid = self.gridIndex(None)
        if grid.get('total') != '0':
            for item in grid['rows']:
                if item['mobile']==data['adddata']['callNo']:
                    receipt = self.providerReceiptOrder(item['factorynumber'],operator = operator)
                    print("receiptJon:",receipt)
                    if receipt is False:
                        return receipt
                    account = self.getAccountByName(data['info']['user'])
                    print("account:",account)
                    aux = AuxOrder()
                    session = DBSession()
                    aux.aux_orderno = receipt['orderno']
                    aux.platform_orderid = data['info']['platform_orderid']
                    aux.aux_userid = account['aux_id_number']
                    session.add(aux)
                    fac = AuxFactoryOrder()
                    fac.factorynumber = item['factorynumber']
                    fac.platform_id = data['info']['platform_orderid']
                    fac.aux_orderno = receipt['orderno']
                    fac.order_type = data['adddata']['servDesc']
                    fac.created_at = str(time.time())[:str(time.time()).index('.')]
                    fac.order_type = self.get_order_type(data['adddata']['servDesc'])
                    session.add(fac)
                    session.commit()
                    session.close()
                    return self.dispatch_order(orderno = receipt['orderno'],userid = account['aux_id_number'],operator = operator)
        print('no wait accept order.')
        utils.errorReport('notice:no wait accept order',system_name = self.system_name)
        return False

    def get_order_type(self,ordertype):
        types = {"1":'安装',"2":'拆机',"3":'移机',"4":'带货安装',"5":'维修'}
        return types.get(str(ordertype)) if  types.get(str(ordertype)) is not None else "unknown"

    def dispatch_appaccept(self,data):
        '''
        派单和app接单
        '''
        account = self.getAccountByName(data['aux_name'])
        dispatch = self.dispatch_order(data['aux_orderno'], account['aux_id_number'])
        appapi = auxAppApi.auxAppApi()
        data['platform_orderid'] = data['platform_id']
        data['aux_userid'] = account['aux_id_number']
        return appapi.accept(data)

    def getAccountByName(self,name = ''):
        session = DBSession()
        account = session.query(auxAccount).filter((auxAccount.aux_name==name) & (auxAccount.channelid!='-1') & (auxAccount.channelid!=None) & (auxAccount.aux_merc_account==self.account)).all()
        if account:
            data = account[0]
            r = {"aux_id_number":data.aux_id_number}
            session.commit()
            session.close()
            return r
        else:
            # session = DBSession()
            aux_node = session.query(AuxMerchant).filter(AuxMerchant.account==self.account).all()
            r = {"aux_id_number":aux_node[0].default_master}
            session.commit()
            session.close()
            return r
