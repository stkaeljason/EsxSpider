# -*- coding: utf-8 -*-

import time
import uuid
import datetime
import requests
import urllib

from db_model.DmArea import query_area


def time_to_timestamp(time_str):
    if time_str:
        st = time.strptime(time_str, '%Y-%m-%d')
        source_timestamp = str(time.mktime(st))
        point_index = source_timestamp.index('.')
        return source_timestamp[:point_index]
    else:
        return ''


def time_to_timestamp2(time_str):
    if time_str:
        st = time.strptime(time_str, '%Y-%m-%d %H')
        source_timestamp = str(time.mktime(st))
        point_index = source_timestamp.index('.')
        return source_timestamp[:point_index]
    else:
        return ''


def time_to_timestamp3(time_str):
    if time_str:
        st = time.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        source_timestamp = str(time.mktime(st))
        point_index = source_timestamp.index('.')
        return source_timestamp[:point_index]
    else:
        return ''


def aptime_format(aptime):
    if u'点' in aptime:
        index = aptime.index(u'点')
    elif ':' in aptime:
        index = aptime.index(':')
    return aptime[:index]


def current_timestamp():
    source_timestamp = str(time.time())
    point_index = source_timestamp.index('.')
    return source_timestamp[:point_index]


def current_timestr():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


def get_latlng(city, addr):
    '''获取地址经纬度'''
    api_url = 'http://restapi.amap.com/v3/geocode/geo'
    data = {
        'key':'e06375c81f3c371c5e0c4a31cb684f7d',
        'address':addr,
        'city':city
    }
    # data = urllib.urlencode(data)
    # api_url = api_url+data
    # print(api_url)
    res = requests.get(api_url, params=data)
    x=res.json()
    # print(city, addr)
    # print 'x:%s'%x
    jing_wei = x['geocodes'][0]['location']
    return jing_wei.split(',')


def intercept_qu(addr):
    if u'区' in addr:
        qu_point = addr.index(u"区")
        return addr[qu_point+1:]
    else:
        return addr


def create_sn():
    nowobj = datetime.datetime.now();
    return nowobj.strftime('%Y%m%d%H%M%S') + str(nowobj.microsecond)


# def get_every_addr(addr_str):
#     addr_dict = dict()
#     try:
#         province_index = addr_str.index(u'省')
#         province = addr_str[:province_index + 1]
#
#         city_index = addr_str.index(u'市')
#         city = addr_str[province_index + 1:city_index + 1]
#
#         strict_index = addr_str.index(u'区')
#         strict = addr_str[city_index+1:strict_index+1]
#
#         addr_detail = addr_str[strict_index+1:]
#
#         addr_dict['province'] = province
#         addr_dict['city'] = city
#         addr_dict['strict'] = strict
#         addr_dict['addr_detail'] = addr_detail
#     except:
#         addr_dict['province'] = ''
#         addr_dict['city'] = ''
#         addr_dict['strict'] = ''
#         addr_dict['addr_detail'] = addr_str
#     # print addr_dict
#     return addr_dict


def get_every_addr(addr_str):
    '''midea'''
    addr_dict = dict()
    # zxs_list = [u'重庆市',u'北京市','天津市','上海市']
    try:
        if u'省' in addr_str:
            province_index = addr_str.index(u'省')
            province = addr_str[:province_index + 1]

            city_index = addr_str.index(u'市')
            city = addr_str[province_index + 1:city_index + 1]

            strict_index = addr_str.index(u'区')
            strict = addr_str[city_index + 1:strict_index + 1]

            addr_detail = addr_str[strict_index + 1:]

            # addr_dict['province'] = province
            # addr_dict['city'] = city
            # addr_dict['strict'] = strict
            # addr_dict['addr_detail'] = addr_detail
        elif u'四川' in addr_str:
            province_index = addr_str.index(u'川')
            province = u'四川省'

            city_index = addr_str.index(u'市')
            city = addr_str[province_index + 1:city_index + 1]

            strict_index = addr_str.index(u'区')
            strict = addr_str[city_index + 1:strict_index + 1]

            addr_detail = addr_str[strict_index + 1:]
        elif u'重庆' in addr_str:
            addr_str = addr_str.replace(u'重庆市辖区', '')
            city_index = addr_str.index(u'市')
            strict_index = addr_str.index(u'区')

            province = u'重庆'
            city = u'重庆市'
            strict = strict = addr_str[city_index + 1:strict_index + 1]
            addr_detail = addr_str[strict_index + 1:]

        addr_dict['province'] = province
        addr_dict['city'] = city
        addr_dict['strict'] = strict
        # 对详细地址做二次检查
        if addr_dict['strict'] not in addr_detail:
            addr_dict['addr_detail'] = addr_detail
        else:
            addr_dict['addr_detail'] = addr_detail.replace(addr_dict['strict'], '')
        check_street_result = get_street(addr_dict['city'],addr_dict['strict'], addr_dict['addr_detail'])
        addr_dict['street'] = check_street_result[0]
        addr_dict['addr_detail'] = check_street_result[1]

    except:
        addr_dict['province'] = u'四川省'
        addr_dict['city'] = u'成都市'
        addr_dict['strict'] = ''
        addr_dict['street'] = ''
        addr_dict['addr_detail'] = addr_str
    # print addr_dict
    return addr_dict


def get_street(city,strict,addres_detail):
    """根据省市区获取街道,目前针对midea"""
    street = ''
    if u'镇' not in addres_detail and u'乡' not in addres_detail and u'街' not in addres_detail:
        street = ''
        addres_detail = addres_detail
        print 1
    else:
        print 2
        # 根据街道关键字获取原始街道
        for key in [u'镇', u'乡', u'街道办', u'街道', u'街']:
            if key in addres_detail:
                length = len(key) - 1
                index = addres_detail.index(key) + length
                break
        street = addres_detail[:index+1]

        # 查询街道的所有父节点id
        street_info = query_area(street)
        strct_list = [s.parent_id for s in street_info]
        # print strct_list

        # 查询区的id
        city_id = query_area(city)[0].id
        # print city_id
        strct_infos = query_area(strict)
        for str_info in strct_infos:
            if str_info.parent_id == city_id:
                strict_id = str_info.id
                break
        else:
            # 如果循环结束都没有匹配到区的id则默认设置
            strict_id = None
            print 3

        # 区id和街道父节点匹配
        if strct_list:
            if strict_id in strct_list:
                street = street
                addres_detail =addres_detail.replace(street,'')
                print 4
            else:
                street = ''
                print 5
        else:
            street = ''
            print 6

    return street, addres_detail


# if __name__ == "__main__":
#     print intercept_qu(u'成都市高新区高新区天赋三级')

