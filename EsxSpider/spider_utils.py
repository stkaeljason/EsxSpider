# -*- coding: utf-8 -*-

import time

import redis
import requests
import json
from hashlib import md5

import appBot.utils as util
from db_model.Phppy import Phppy
from db_model import db
from tools import create_sn
# from PIL import Image,ImageEnhance
# from pytesseract import image_to_string


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
        """
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
        return r.json()

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://api.ruokuai.com/reporterror.json', data=params, headers=self.headers)
        return r.json()


def get_login_params(factory_name):
    '''根据厂家名称计算对应后台的登陆时携带参数'''
    pass


def get_captcha(captcha_api):
    '''尝试3次，防止输入验证码过慢以及网络问题失败'''
    for i in range(3):
        captcha = compute_captcha(captcha_api)
        if captcha:
            return captcha


def compute_captcha(captcha_api):
    '''根据图片识别验证码,暂定用微信手工输入的方式'''
    captcha = ''
    pic_url = down_image(captcha_api)   # 需要encode
    uuid = create_sn()
    service = 'http://www.210xiong.com.cn/index.php?s=/index/weixin/mdcode&picurl='+pic_url+'&uuid='+uuid           # 携带pic_url和service请求后台服务
    message = 'the spider need the Verification code'

    # redis 订阅
    util.wx_Report(message=message, link=service, flag='captcha')
    rc = redis.Redis(host='r-wz9ba7101fdca794.redis.rds.aliyuncs.com', port=6379, password='Ershixiong2017')
    print(rc)
    ps = rc.pubsub()
    print(ps)
    # 订阅列表
    ps.subscribe(['mdcode'])

    judge = 0
    print('judge:%d'%judge)
    while judge < 60:
        for item in ps.listen():
            print(item)
            if item['type'] == 'message':
                phppy = Phppy()
                phppy.data = item['data']
                phppy.time = time.time()
                phppy.channel = item['channel']
                db.session.add(phppy)
                db.session.commit()
                db.session.close()
                data = json.loads(item['data'])
                print(data)
                if data['uuid'] == uuid and data['mdcode']:
                    print(data['mdcode'])
                    captcha = data['mdcode']
                    break
        time.sleep(1)
        judge += 1
        print(judge)
    return captcha


def down_image(captcha_api):
    '''根据验证码接口获得图片,保存图片到服务器，返回图片字节'''
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
    }
    t = str(int(time.time() * 1000))
    # image_name = 'captcha_images/'+t+'.jpg'
    r = util.request(captcha_api, method='get', data={'r':t}, headers=headers)

    return r.content, t


def rk_get_captcha(captcha_api):
    im, t = down_image(captcha_api)
    rc = RClient('WongTH', '147258369', '89380', 'c2faa5c3ff5d4b459c703f53ef3ad17b')
    # im = open('captcha.jpg', 'rb').read()
    cap_r = rc.rk_create(im=im, im_type=3040)   # 3040表示数字字母混合
    print('captcha:%s'%cap_r['Result'])
    image_name = 'captcha_images/'+cap_r['Result']+'_'+t+'.jpg'
    with open(image_name, 'wb') as f:
        f.write(im)
        f.close()
    return cap_r['Result']


# if __name__ == "__main__":
#     print rk_get_captcha('https://cs.midea.com/c-css/captcha')

