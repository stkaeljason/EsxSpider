# -*- coding: utf-8 -*-

import os
import random

import requests
import json

from EsxSpider.spider_utils import RClient
from EsxSpider.tools import current_timestamp, current_timestr

try:
  from lxml import etree
except ImportError:
  import xml.etree.cElementTree as etree

try:
    import cookielib
except:
    import http.cookiejar as cookielib
import time

from utils import request
from utils import errorReport


class JdLogin:

    def __init__(self, merchant):
        """登陆所需公共参数"""
        self.login_page = 'https://passport.jd.com/uc/login?ReturnUrl=http%3A%2F%2Fjdfw.jd.com%2F'
        self.login_bs_url = 'https://passport.jd.com/uc/loginService?'
        self.return_url = 'http%3A%2F%2Fjdfw.jd.com%2F'
        self.auth_url = 'https://passport.jd.com/uc/showAuthCode?'
        self.is_login_url = 'http://jdfw.jd.com/'
        self.version = '2015'
        self.login_url_fromat = '{login_bs_url}uuid={uuid}&ReturnUrl={return_url}&r={r}&version={version}'
        self.auth_format = '{auth_url}r={r}&version={version}'
        self.headers = {
            'Accept':'text/plain, */*; q=0.01',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Host':'passport.jd.com',
            'Origin':'https://passport.jd.com',
            'Referer':'https://passport.jd.com/uc/login?ReturnUrl=http%3A%2F%2Fjdfw.jd.com%2F',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest'
        }

        #　构建账号数据
        self.loginname = merchant.account
        self.pwd = merchant.password
        # eid随客户端不同而变
        self.eid = merchant.eid
        #  fp随账号不同而变
        self.fp = merchant.fp

        # cookies文件名
        self.cookie_file_name = './cookies_file/'+'jd_'+merchant.account+'_cookies.txt'

        #创建session
        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename='jd_cookies')

    def compute_pwd(self):
        pass

    def get_image(self,uuid):
        image_headers = {
            'Accept':'text/plain, */*; q=0.01',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Host':'authcode.jd.com',
            'Referer':'https://passport.jd.com/uc/login?ReturnUrl=http%3A%2F%2Fjdfw.jd.com%2F',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
        }
        auth_code_url = 'https://authcode.jd.com/verify/image?a=1&acid={}&uid={}&yys={}'.format(uuid, uuid, str(int(time.time() * 1000)))
        im = self.session.get(auth_code_url, headers=image_headers)
        return im.content

    def get_authcode(self,uuid):
        im = self.get_image(uuid)
        rc = RClient('WongTH', '147258369', '89380', 'c2faa5c3ff5d4b459c703f53ef3ad17b')
        cap_r = rc.rk_create(im=im, im_type=3040)   # 3040表示数字字母混合
        try:
            print('captcha:%s'%cap_r['Result'])
        except KeyError as e:
            if str(e) == "'Result'":
                errorReport('ruokuai count run out')
                import sys
                sys.exit('ruokuai count run out')

        image_name = './captcha_images/'+cap_r['Result']+'_'+current_timestamp()+'.jpg'
        if not os.path.exists('./captcha_images/'):
            os.mkdir('./captcha_images/')
        with open(image_name, 'wb') as f:
            f.write(im)
        return cap_r['Result']

    def compute_form_param(self):
        para_dict = dict()
        page = self.session.get(self.login_page)
        page = etree.HTML(page.text)
        # print(etree.tostring(page))
        para_dict['uuid'] = page.xpath('//input[@name="uuid"]')[0].get('value')
        para_dict['pubkey'] = page.xpath('//input[@name="pubKey"]')[0].get('value')
        para_dict['sa_token'] = page.xpath('//input[@name="sa_token"]')[0].get('value')
        para_dict['eid'] = page.xpath('//input[@name="eid"]')[0].get('value')
        print('eid:%s')%para_dict['eid']
        para_dict['fp'] = page.xpath('//input[@name="fp"]')[0].get('value')
        print('fp:%s')%para_dict['fp']

        # 确认是否需要验证码，如果需要获得验证码
        auth_url = self.auth_format.format(auth_url=self.auth_url, r=random.random(), version=self.version)
        acRequired = self.session.post(auth_url, data={'loginName':self.loginname}, headers=self.headers).text
        if 'true' in acRequired:
            print('acRequired:true')
            para_dict['authcode'] = self.get_authcode(para_dict['uuid'])
        else:
            print('acRequired:flase')
            para_dict['authcode'] = ''
        return para_dict

    def save_cookies(self,cookies_object):
        cookies_str = ''
        # 保存登陆成功获得的cookies
        for cookie in cookies_object:
            cookies_str += '{}={}; '.format(cookie.name, cookie.value)
        print('cookies_str:%s'%cookies_str)
        with open(self.cookie_file_name, 'w') as f:
            f.write(cookies_str+'\n')
            f.write(str(current_timestr()))
        print('write success')
        return cookies_str

    def is_login(self):
        """判断cookies是否依然有效"""
        is_headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Host':'jdfw.jd.com',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36Name'
        }

        if os.path.exists(self.cookie_file_name):
            with open(self.cookie_file_name, 'r') as f:
                cook_content = f.readlines()
                cookies = cook_content[0].strip('\n')
                is_headers['Cookie'] = cookies
                page = requests.get(self.is_login_url, headers=is_headers, allow_redirects=False, timeout=60)
                # print(page.status_code)
                # print('page.text:%s'%page.text)
                if page.status_code != 302:
                    print(page.status_code)
                    return cookies
                else:
                    return False
        else:
            return False

    def do_login(self, login_url, form_data):
        """登陆执行函数"""
        print('login_url:%s'%login_url)
        login_result = self.session.post(login_url, data=form_data, headers=self.headers)
        print('login_result.request:%s'%login_result.request)
        print('login_result:%s'%login_result.text)
        if 'success' in login_result.text:
            # self.session.cookies.save()
            return self.session.cookies
        else:
            return False

    def login(self):
        """登陆逻辑主函数"""
        useful_cookies = self.is_login()
        if not useful_cookies:
            print('the cookies is not alive')
            for i in range(4):
                try:
                    para_dict = self.compute_form_param()
                    r = random.random()
                    # pwd = self.compute_pwd()
                    login_url = self.login_url_fromat.format(login_bs_url=self.login_bs_url, uuid=para_dict['uuid'], return_url=self.return_url, r=r, version=self.version)

                    form_data = {
                        'uuid': para_dict['uuid'],
                        'eid': self.eid,
                        'fp': self.fp,
                        '_t': '_t',
                        'loginType': 'f',
                        'loginname': self.loginname,
                        'nloginpwd': self.pwd,
                        'chkRememberMe': '',
                        'authcode': para_dict['authcode'],
                        'pubKey': para_dict['pubkey'],
                        'sa_token': para_dict['sa_token']
                    }
                    cookies_object = self.do_login(login_url, form_data)
                    # 判断是否登陆成功，如果不是，跳出本次循环
                    if not cookies_object:
                        errorReport('jd->%s->%s'%('jd_'+self.loginname+'_login_again_need',time.asctime(time.localtime(time.time()))))
                        continue
                    else:
                        errorReport('jd->%s->%s' % ('jd_'+self.loginname+'_login_success', time.asctime(time.localtime(time.time()))))

                    cookies_str = self.save_cookies(cookies_object)
                    # print('cook_object:%s'%cookies_object)
                    return cookies_str
                except Exception as e:
                    errorReport("jd login again->%s"%str(e)+str(e.args))
                    print("jd login again:%s" % (str(e)))
        else:
            print('the cookies is still useful')
            return useful_cookies


def jd_home(cookies):
    """访问首页，用来测试"""
    api_url = 'http://jdfw.jd.com/'
    headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Host':'jdfw.jd.com',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36Name',
            'Cookie':cookies
        }
    r = request(api_url, method='get', headers=headers)
    print('jd_home:%s'%r)


def quest_orders(cookies,status='7',merchant=None):
    """根据京东订单状态获取订单列表，默认获取待反馈也就是派工以后的单,6:待派工,7:待反馈"""
    api_url = 'http://jdfw.jd.com/receipt/query.json'
    headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Host':'jdfw.jd.com',
            # 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36Name',
            'Origin':'http://jdfw.jd.com',
            'Referer':'http://jdfw.jd.com/receipt/search?serviceType=0&esSwitch=1',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest',
            'Cookie':cookies
        }
    form_data = {'atHomeFinishDateBegin': '',
                 'atHomeFinishDateEnd': '',
                 'createOrderTimeBegin': '',
                 'createOrderTimeEnd': '',
                 'customerName': '',
                 'customerPhone': '',
                 'customerPin': '',
                 'customerTel': '',
                 'deliveryDateEnd': '',
                 'deliveryDateStart': '',
                 'deliveryModel': '',
                 'endStatus': '',
                 'esSwitch': '1',
                 'expectAtHomeDateBegin': '',
                 'expectAtHomeDateEnd': '',
                 'fastDealNum': status,
                 'fastDealNumByColor': '',
                 'feedbackStatus': '',
                 'freeinstall': '',
                 'grabStatus': '',
                 'grabType': '',
                 'homePageDistinguish': '',
                 'invoiceNumber': '',
                 'isFast': '',
                 'oneShopFlag': '',
                 'order': 'desc',
                 'orderDistributionDateBegin': '',
                 'orderDistributionDateEnd': '',
                 'orderId': '',
                 'orderOrderStatus': '',
                 'orderStatus': '',
                 'ordernoGroup': '',
                 'otherReservationNum': '',
                 'outletsId': merchant.website_id,
                 'page': '1',
                 'productBrand': '',
                 'productName': '',
                 'productType1': '',
                 'productType2': '',
                 'productType3': '',
                 'reportLessFlag': '',
                 'reservationDateBegin': '',
                 'reservationDateEnd': '',
                 'reviewStatus': '',
                 'rows': '50',
                 'serviceStreet': '',
                 'serviceType': '0',
                 'sort': 'returnTime',
                 'sortKind': '4',
                 'startStatus': '',
                 'subCompanyId': '4',
                 'timeout': '',
                 'todayOtherReservationConditionName': '',
                 'wareId': '',
                 'wareInfoId': 'lw_4_992%25%254_2'}
    # form_data = json.dumps(form_data)
    r = request(api_url, method='post', data=form_data, headers=headers)
    # print('quest_orders:%s'%r)
    return r


def receive_order(order_no, cookies):
    api_url = 'http://jdfw.jd.com/receipt/batch/batchAccept'
    headers = {
            'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Content-Type':'application/x-www-form-urlencoded',
            'Host':'jdfw.jd.com',
            'Referer': 'http://jdfw.jd.com/receipt/search?serviceType=0&esSwitch=1',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36Name',
            'X-Requested-With':'XMLHttpRequest',
            'Cookie':cookies
        }
    form_data = {'noList':[order_no],
                 'subCompanyId':'4',
                 'outletsId':'028861803',
                 'baseWebsiteNo':'028861803',
                 'outletName':'成华区智诚电器经营部',
                 'receivePersonName':'傅敏',
                 'engineerFirstName':'',
                 'engineerSecondName':'',
                 'outletsAssignerName':'',
                 'reservationPeriodName':'',
                 'reservationPersonName':'',
                 'feedbackInfoName':'',
                 'receivePerson':'傅敏'}

    form_data = json.dumps(form_data)
    r = request(api_url, method='post', data=form_data, headers=headers)
    print('receive_order:%s'%r)
    return r


def appoint_order(order_no, cookies):
    api_url = 'http://jdfw.jd.com/receipt/batch/batchReservation'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'jdfw.jd.com',
        'Referer': 'http://jdfw.jd.com/receipt/search?serviceType=0&esSwitch=1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36Name',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookies
    }
    form_data = {
        'noList': [order_no],
        'subCompanyId': '4',
        'outletsId': '028861803',
        'baseWebsiteNo': '028861803',
        'outletName': '成华区智诚电器经营部',
        'receivePersonName': '傅敏',
        'engineerFirstName': '',
        'engineerSecondName': '',
        'outletsAssignerName': '',
        'reservationPeriodName': '14:00-18:00',
        'reservationPersonName': '',
        'feedbackInfoName': '',
        'reservationDate': '2017-11-02',
        'reservationPeriod': '1',
        'reservationPerson': ''
    }
    form_data = json.dumps(form_data)
    r = request(api_url, method='post', data=form_data, headers=headers)
    print('appoint_order:%s'%r)
    return r


def dispatch_order(form_data, cookies):
    """
    派单
    form_data示例：
    {
    'noList': [21970074],              服务工单号，要填
    'subCompanyId': '4',
    'outletsId': '028861803',
    'baseWebsiteNo': '028861803',
    'outletName': '成华区智诚电器经营部',
    'receivePersonName': '傅敏',
    'engineerFirstName': '兰平平',        师傅名称，要填
    'engineerSecondName': '请选择',       第二个师傅名称，有的话要填
    'outletsAssignerName': '',
    'reservationPeriodName': '14:00-18:00',    预约时间，要填
    'reservationPersonName': '',
    'feedbackInfoName': '',
    'engineerFirst': 'JDAZ018929',         师傅在京东的编码，要填,对应于京东师傅账号表的engineer_code字段
    'engineerSecond': '',                  第二个师傅在京东的编码，有则填
    'assigner': ''
}
    """

    api_url = 'http://jdfw.jd.com/receipt/batch/batchAssignWork'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'jdfw.jd.com',
        'Referer': 'http://jdfw.jd.com/receipt/search?serviceType=0&esSwitch=1',
        'Origin':'http://jdfw.jd.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36Name',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookies
    }
    form_data = json.dumps(form_data)
    r = request(api_url, method='post', data=form_data, headers=headers)
    print('dispatch_order:%s'%r)
    return r


def check_engieers(cookies):
    api_url = 'http://jdfw.jd.com/receipt/batch/getEngineersUnderOutlets.json'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'Content-Type': 'application/json',
        'Host': 'jdfw.jd.com',
        'Referer': 'http://jdfw.jd.com/receipt/search?serviceType=0&esSwitch=1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36Name',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookies
    }
    form_data = {
        'text': '028861803;870'
    }
    # form_data = json.dumps(form_data)
    r = request(api_url, method='post', data=form_data, headers=headers)
    print('check_engieers:%s'%r)
    return r


def get_engineers(cookies,merchant):
    """获取京东的在职师傅"""
    api_url = 'http://jdfw.jd.com/engineer/queryEngineerBy.json'
    headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Host':'jdfw.jd.com',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36Name',
            'X-Requested-With':'XMLHttpRequest',
            'Referer':'http://jdfw.jd.com/engineer/engineerPage',
            'Cookie':cookies
        }
    form_data = {
        'belongsBranchId':'4',
        'belongLargewarehouseId':'lw_4_992%%4_2',
        'websiteNo':merchant.website_id,
        'websiteName':'成华区智诚电器经营部',
        'currentStatus':'1',
        'mobile':'',
        'engineerName':'',
        'personId':'',
        'jdAccount':'',
        'page':'1',
        'rows':'50',
    }
    # form_data = json.dumps(form_data)
    r = request(api_url, method='post', data=form_data, headers=headers)
    # print('get_engineers:%s'%r)
    return r


def request_od_page(secret_order, cookies):
    """获取订单详情的中间页面，包含所需订单详情的url"""
    api_url = 'http://jdfw.jd.com/receipt/manage?orderno=' + secret_order
    headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Host':'jdfw.jd.com',
            'Referer': 'http://jdfw.jd.com/receipt/search?serviceType=0&esSwitch=1',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36Name',
            'X-Requested-With':'XMLHttpRequest',
            'Cookie':cookies
        }
    r = request(api_url, method='get', headers=headers)
    # print('request_od_page:%s'%r, type(r))
    return r


def request_od_detail(detail_url, secret_order, cookies):
    """根据中间页的详情url获取对应详情数据"""
    api_url = 'http://jdfw.jd.com' + detail_url
    headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Host':'jdfw.jd.com',
            'Referer':'http://jdfw.jd.com/receipt/manage?orderno='+secret_order,
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36Name',
            'X-Requested-With':'XMLHttpRequest',
            'Cookie':cookies
        }
    r = request(api_url, method='get', headers=headers)
    # print('request_od_detail:%s'%r, type(r))
    return r
