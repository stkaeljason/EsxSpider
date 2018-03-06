# -*- coding: utf-8 -*-

import os
import requests,json
from hashlib import md5

from EsxSpider.special_methods.encrypt_methods import midea_encrypt

try:
    import cookielib
except:
    import http.cookiejar as cookielib
import time

from utils import request
from utils import current_time
from utils import errorReport
from EsxSpider.tools import current_timestamp
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
#_cookie_attrs()

# try:
#     session.cookies.load(ignore_discard=True)
# except:
#     print('Cookie 未能加载')


headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
        'X-Requested-With':'XMLHttpRequest'
    }


def is_login(filename):
    url = 'https://cs.midea.com/c-css/views/css/desktop/index.jsp'
    headers_1 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
        'X-Requested-With':'XMLHttpRequest',
        # 'Upgrade-Insecure-Requests':'1',
        # 'Referer':'https://cs.midea.com/c-css/login'

    }
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            cook_content = f.readlines()
            cookies = cook_content[0].strip('\n')
            update_time = cook_content[1].strip('\n')
        headers_1['Cookie'] = cookies
        page = requests.get(url, headers=headers_1, allow_redirects=False, timeout=60)
        # r = get_daijie_orders(cookies)
        if "window.top.location.href = '/c-css/login'" in page.text:    # 表示重定向了
            return False
        else:
            return cookies
    else:
        return False


def do_login(form_data):
    login_url = 'https://cs.midea.com/c-css/signin'
    login_page = session.post(login_url, data=form_data, headers=headers)
    # print('login_page:%s'%login_page.text)
    # errorReport(str(login_page.text)+time.asctime(time.localtime(time.time())))
    # print(session.cookies)
    if login_page.json()['status'] == True:
        token_cookie = cookielib.Cookie(name='loginToken',
                                        value=login_page.json()['content']['loginToken'],
                                        expires=None,
                                        secure=False,
                                        version=None,
                                        port=None,
                                        port_specified=False,
                                        domain='cs.midea.com',
                                        domain_specified=None,
                                        domain_initial_dot=None,
                                        path='/c-css/', path_specified=None,
                                        discard=None,
                                        comment=None,
                                        comment_url=None,
                                        rest=None)
        session.cookies.set_cookie(token_cookie)
        print('testtesttest')
        return session.cookies, login_page.text
    else:
        return False,login_page.text


class RClient(object):

    def __init__(self, username, password, soft_id, soft_key):
        self.username = username
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.soft_key = soft_key
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=60):
        '''
        im: 图片字节
        im_type: 题目类型
        '''
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
        return r.json()

    def rk_report_error(self, im_id):
        '''
        im_id:报错题目的ID
        '''
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://api.ruokuai.com/reporterror.json', data=params, headers=self.headers)
        return r.json()


def down_image(captcha_api='https://cs.midea.com/c-css/captcha?r='):
    '''根据验证码接口获得图片,保存图片到服务器，返回图片字节'''

    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
    }
    t = str(int(time.time() * 1000))
    capt_url = captcha_api+t
    r = session.get(capt_url, headers=headers)
    # print('captcha_session:%s'%session.cookies)

    return r.content, t


# def rk_get_captcha():
#     im, t = down_image()
#     rc = RClient('WongTH', '147258369', '89380', 'c2faa5c3ff5d4b459c703f53ef3ad17b')
#     # im = open('captcha.jpg', 'rb').read()
#     cap_r = rc.rk_create(im=im, im_type=3040)   # 3040表示数字字母混合
#     print('captcha:%s'%cap_r['Result'])
#     image_name = 'captcha.jpg'
#     with open(image_name, 'wb') as f:
#         f.write(im)
#         # f.close()
#     return cap_r['Result']


def rk_get_captcha():
    im, t = down_image()
    rc = RClient('WongTH', '147258369', '89380', 'c2faa5c3ff5d4b459c703f53ef3ad17b')
    cap_r = rc.rk_create(im=im, im_type=3040)   # 3040表示数字字母混合
    print('captcha:%s'%cap_r['Result'])
    image_name = './captcha_images/'+cap_r['Result']+'_'+current_timestamp()+'.jpg'
    if not os.path.exists('./captcha_images/'):
        os.mkdir('./captcha_images/')
    with open(image_name, 'wb') as f:
        f.write(im)
    return cap_r['Result']

def login(usename,pwd):
    '''登陆主函数,如果失败重试3次'''
    cookie_f_name = './cookies_file/'+'midea_'+usename+'_cookies.txt'  # cookies文件的文件名
    useful_cookies = is_login(cookie_f_name)
    # print('useful_cookies:%s'%useful_cookies)
    if not useful_cookies:
        # 从数据库获取账号信息
        pwd = midea_encrypt(pwd)  # 对密码进行加密,必须放在重试循环之外

        # 登录获取cookies，有错重试，最大3次
        for i in range(3):
            try:
                try:
                    captcha = rk_get_captcha()
                    # errorReport('midea->get captcha:%s %s'%(captcha,str(i))+time.asctime(time.localtime(time.time())))
                    # with open('num_captcha.txt','a+') as x:
                    #     x.write('1'+'\n')
                except KeyError as e:
                    if str(e) == "'Result'":
                        print(str(e)+':'+'the ruokuai api run out')
                        errorReport('the ruokuai api run out')  # 表示若快的接口次数用完了,跳出循环
                        import sys
                        sys.exit('the ruokuai api run out')  # 结束进程
                        # break
                form_data ={
                    'userAccount':usename,
                    'userPassword':pwd,
                    'captcha':captcha
                }
                cookies_object, login_res = do_login(form_data)
                # 判断是否登陆成功，如果不是，跳出本次循环
                if not cookies_object:
                    errorReport('midea->%s->%s'%(usename+'_login_again_need',time.asctime(time.localtime(time.time()))))
                    continue
                else:
                    errorReport('midea->%s->%s' % (usename+'_login_success', time.asctime(time.localtime(time.time()))))

                print('cook_object:%s'%cookies_object)
                cook_list = []
                # 保存登陆成功获得的cookies
                for cookie in cookies_object:
                    cook_list.append(cookie.value)
                cookies_str = 'JSESSIONID={}; loginToken={}'.format(cook_list[0],cook_list[1])
                print('cookies_str:%s'%cookies_str)
                with open(cookie_f_name, 'w') as f:
                    f.write(cookies_str+'\n')
                    f.write(str(time.time()))
                # errorReport('testtest->success write cookies:%s->%s'%(str(i),time.asctime( time.localtime(time.time()) )))
                print('writewrite')
                return cookies_str
            except Exception as e:
                errorReport("testtest->%s"%str(e)+str(e.args))
                print("meidi login again:%s" % (str(e)))
    else:
        print('the cookies is still useful:%s'%useful_cookies)
        # errorReport('testtest->the cookies is still useful->%s'%time.asctime( time.localtime(time.time()) ))
        return useful_cookies


def get_orders(cookies, order_status='16'):
    '''
    查询所需要的工单
    order_status:工单状态对应的id；待派单:10,待接收:11，,已派工：16，全部：'',已预约：１５
    '''
    api_url = 'https://cs.midea.com/c-css/wom/serviceorderunit/listdata'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
        'X-Requested-With':'XMLHttpRequest',
        'Referer':'https://cs.midea.com/c-css/wom/serviceorderunit/list',
        'Content-Type':'application/json',
        'Cookie':cookies
    }

    CONTACT_TIME_end, CONTACT_TIME = current_time()      # 查询截止时间，为当前时间

    form_data = {
                'page': '1',
                'rows': '50',
                'pageIndex': '0',
                'pageSize': '50',
                'formConditions': {
                    'CONTACT_TIME': CONTACT_TIME,      # 此处设置为当前日期前5天
                    'CONTACT_TIME_end': CONTACT_TIME_end,  # 时间设置为当前日期
                    'SERVICE_ORDER_NO': '',
                    'SERVICE_CUSTOMER_TEL1': '',
                    'SERVICE_ORDER_STATUS': order_status,   # 待派单:10,待接收:11，全部：''
                    'IMPLEMENT_SUB_TYPE_CODE': '',
                    'ORDER_ORIGIN': '',
                    'SERVICE_PROCESS_TIME_OUT': '',
                    'URGE_COMPLAINT_ADDITIONAL': '',
                    'CONTAIN_EJFWS': 'N',
                    'PROD_CODE': '',
                    'refreshRowFlag': 'false',
                    'data': ''
                }
            }
    form_data = json.dumps(form_data)
    r = request(api_url,method='post', data=form_data,headers=headers)
    # print(r)
    if r and r['content']['status'] == False:
        errorReport(api_url+':'+ 'get api data fail')

    return r


def commit_order(form_data,cookies):
    '''
    录入订单接口
    form_data：录入的数据字典，示例
    {"serviceOrderVO":{"serviceOrderNo":"FW170994405222","serviceMainTypeCode":"10","serviceMainTypeName":"安装","serviceSubTypeCode":"1010","serviceSubTypeName":"安装","requireServiceDate":" ","implementMainTypeCode":"10","implementMainTypeName":"安装","implementSubTypeCode":"1010","implementSubTypeName":"安装","branchCode":"F5101000002","branchName":"成都销司","unitCode":"W5101007150","unitName":"武侯区宏旺电器维修服务部"},"serviceCustomerInfoVO":{"serviceCustomerId":"","serviceCustomerName":"王太红","serviceCustomerTel1":"18057486780","serviceCustomerTel2":"","serviceCustomerTel3":"","serviceCustomerType":"10","serviceCustomerLevel":"10","serviceAreaNumFlag":"2","serviceAreaNum":"028","serviceCustomerStarLevel":"","serviceAreaCode":"1510112001","serviceAreaName":"四川省成都市龙泉驿区龙泉街道","serviceCustomerAddress":"四川省成都市龙泉驿区龙泉街道芦溪河社区溪源居小区"},"serviceUserDemandInfoVOList":[{"prodCode":"1000","orgCode":"CS006","prodName":"家用空调","brandCode":"MIDEA","brandName":"美的","contactOrderServTypeCode":"BZ","contactOrderServTypeName":"报装","contactOrderSerItem1Code":"BZ01","contactOrderSerItem1Name":"报装","contactOrderSerItem2Code":"BZ01001","contactOrderSerItem2Name":"需要安装","productModel":"","prodNum":"1","productUse":"10","purchasingChannels":"10","purchaseDate":"","salesUnitCode":"","salesUnitName":"","serviceDesc":"需要安装","pubRemark":""}]}"
          }
    '''
    api_url = 'https://cs.midea.com/c-css/wom/womserviceorderdocument/formcommit'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
        'X-Requested-With':'XMLHttpRequest',
        'Content-Type':'application/json',
        'Cookie':cookies
    }
    form_data = json.dumps(form_data)
    r = request(api_url,method='post', data=form_data,headers=headers)
    if r and r['content']['status'] == False:
        errorReport(api_url+':'+ 'get api data fail')
    return r


def receive_order(serviceOrderId, unitCode,cookies):
    '''
    接单接口
    serviceOrderId：订单号
    unitCode：服务网点编码
    '''
    api_url = 'https://cs.midea.com/c-css/wom/serviceorderunit/unitreceiveorder'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
        'X-Requested-With':'XMLHttpRequest',
        'Content-Type':'application/json',
        'Cookie':cookies
    }
    form_data = {
        'serviceOrderId':serviceOrderId,
        'unitCode':unitCode,
        'operator':'AW5101007150'
    }
    form_data = json.dumps(form_data)
    r = request(api_url,method='post', data=form_data,headers=headers)
    if r and r['content']['status'] == False:
        errorReport(api_url+':'+ 'get api data fail')
        return False
    return r


def appoint_order(form_data,cookies):
    '''
    预约工单
    接口需抓包或者js查找
    appint_data:预约数据
    示例：
    form_data = {'serviceOrderNo':'FW170994405222',  工单号
                 'serviceOrderId':'1042879214',
                 'serviceMethodCode':'10',
                 'serviceMethodName':'上门',
                 'appointDesc':'已预约',
                 'appointTime':'2017-09-27 8点-10点'  预约时间
          }
    '''
    api_url = 'https://cs.midea.com/c-css/wom/serviceorderunit/unitappoint'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
        'X-Requested-With':'XMLHttpRequest',
        'Content-Type':'application/json',
        'Cookie':cookies
    }
    form_data = json.dumps(form_data)
    r = request(api_url,method='post', data=form_data,headers=headers)
    if r and r['content']['status'] == False:
        errorReport(api_url+':'+ 'get api data fail')
    return r


def dispatch_order(form_data, cookies):
    '''
    派单
    form_data(示例):
    {'serviceOrderNo':'FW170994405222',   # 工单号
    'serviceOrderId':'1042879214',
    'serviceUserDemandIds':'1043261180',
    'engineerCode':'E0199658'}  # 师傅编号
    需要拿待派单的单子测试
    '''
    api_url = 'https://cs.midea.com/c-css/wom/serviceorderunit/dispatchorder'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
        'X-Requested-With':'XMLHttpRequest',
        'Content-Type':'application/json',
        'Cookie':cookies
    }

    form_data = json.dumps(form_data)
    r = request(api_url,method='post', data=form_data,headers=headers)
    if r and r['content']['status'] == False:
        errorReport(api_url+':'+ 'get api data fail')
    return r


def get_engineers_data(cookies):
    '''
    获取师傅数据接口
    :param cookies: 登陆cookies
    :return: 美的师傅列表数据
    '''
    api_url = 'https://cs.midea.com/c-css/css/autoGrid/autoGrid.do?query'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
        'X-Requested-With':'XMLHttpRequest',
        'Content-Type':'application/json',
        'Cookie':cookies
    }
    # condition = {"condColumns":["flow_status"],"condOperates":["="],"condValues":["14"],"condTypes":["1"]}
    # form_data={"page":1,
    #            "rows":50,
    #            "model_type":"sup",
    #            "gridId":"201",
    #            "conditions":condition
    #            }

    condition = {"condColumns": ["doc_status"], "condOperates": ["="], "condValues": ["11"], "condTypes": ["1"]}
    form_data = {"page": 1,
                 "rows": 50,
                 "model_type": "sup",
                 "gridId": "50",
                 "conditions": condition
                 }

    form_data = json.dumps(form_data)
    r = request(api_url,method='post', data=form_data,headers=headers)
    print 'success request midea shifu_api'
    if r and r['content']['status'] == False:
        errorReport(api_url+':'+ 'get api data fail')
    return r
