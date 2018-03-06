# -*- coding: utf-8 -*-

import re
from collections import OrderedDict

from appBot.utils import errorReport

try:
  from lxml import etree
except ImportError:
  import xml.etree.cElementTree as etree

from EsxSpider.tools import create_sn, get_latlng, get_every_addr, intercept_qu, current_timestamp, aptime_format, \
    time_to_timestamp2, time_to_timestamp3
from appBot.jd_api import request_od_page, request_od_detail


def detail_parse(od_dict, static_data,merchant):
    '''订单详情数据组装'''
    item = OrderedDict()

    # dm_order 表所需数据
    # 接件单号
    item['ord_cust_name']= od_dict['customerName']
    item['ord_cust_tel']= static_data['ord_cust_tel']
    addr_dict = parse_addr_jd(od_dict['serviceStreet']) # 计算地址dict
    item['ord_cust_addr']= addr_dict['addr_detail']
    item['ord_province']= addr_dict['province']
    item['ord_city']= addr_dict['city']
    item['ord_district']= addr_dict['strict']
    item['ord_street'] = addr_dict['street']
    # 备注，对应于美的的服务请求描述
    item['ord_remark'] = ''
    # 用户报修故障
    item['ord_cust_fault'] = ''
    item['ord_num']= create_sn()
    item['ord_pay_num'] = create_sn()
    item['ord_grab_addr'] = ''
    # 接件单号
    item['ord_accept_no'] = od_dict['orderId']
    # item['ord_ask_time'] =
    item['ord_create_time'] = current_timestamp()
    item['ord_buy_time'] = item['ord_create_time']
    lng_lat = get_latlng(addr_dict['city'],addr_dict['strict']+addr_dict['street']+addr_dict['addr_detail'])
    item['ord_cust_lng'] = lng_lat[0]
    item['ord_cust_lat'] = lng_lat[1]
    item['ord_weixin_num'] = ''
    # 商家id
    item['ord_merc_id'] = 1  # 兴科域
    # 购买单位，在后台表示信息来源
    item['ord_purchase_unit'] = u'京东'
    item['ord_status'] = 0              # 待发布
    item['ord_need_build'] = 2   # 不用建单
    # 业务类型
    if u'维修' in od_dict['serviceTypeName']:   # 根据实施业务类型字段判断业务类型
        item['ord_type'] = 5
    else:
        item['ord_type'] = 1
    ## 预约安装时间
    item['ord_ins_time'] = static_data['appoint_time'] # 和售后确认
    # 接件时间,接入时间
    item['ord_accept_time'] = time_to_timestamp3(static_data['ord_accept_time'])
    # 销售单位,购买渠道
    item['ord_sale_unit'] = u'京东'
    # 是否0元装
    if od_dict['freeinstall'] == 1:
        item['ord_free_ins'] = 1               # 免费
    elif od_dict['freeinstall'] == 2:
        item['ord_free_ins'] = 0               # 不免费
    # 购买渠道id
    item['ord_purchase_unit_id'] = 0   # 和渠道表的是同一个值，在查到渠道id后更新,和ord_purchase_unit对应


    # dm_order之外所需数据
    product_name = od_dict['productName']
    p_num_regex = r"）??.*?(?P<pi_num>[1-9](.[1-9])?)匹".decode('utf-8')
    model_regex = r"\((.*?)\)"
    # 商家名称
    item['shangjia'] = od_dict['outletsName']

    # 商家id
    item['merchant_id'] = merchant.platform_id
    # 购买渠道
    item['qudao'] = item['ord_sale_unit']

    # 匹数
    pi_result = re.search(p_num_regex, product_name)
    if pi_result:
        # item['pi_num'] = pi_result.group('pi_num') + 'P'   # 从产品名称中正则匹配匹数
        pass
    else:
        errorReport('regex pi_num fail', system_name='jd_parse_order')
    item['pi_num'] = pi_result.group('pi_num') + 'P'  # 从产品名称中正则匹配匹数

    # 产品型号
    model_result = re.search(model_regex, product_name)
    item['pro_model'] = model_result.group(1)  # 从产品名称中正则匹配型号

    ## 需要的数量
    item['pro_num'] = 1

    # 品牌名称
    point_index = od_dict['productBrandName'].index(u'（')
    item['brand'] = od_dict['productBrandName'][:point_index]

    # 默认电器id
    item['default_apl_id'] = 91            # 京东后台目前只有奥克斯的，渠道就是京东，商家兴科域

    return item


def parse_static_data(orderno_secret, cookies):
    sd_dict = dict()
    od_mid_page = request_od_page(orderno_secret, cookies)
    od_mid_page = etree.HTML(od_mid_page)
    detail_lis = od_mid_page.xpath('//ul[@class="clearfix titH2"]/li')
    detail_urls = [li.xpath('.//a/@href')[0] for li in detail_lis]
    # print('detail_urls:%s' % detail_urls)

    cus_data = prase_cus_info(detail_urls[0], orderno_secret, cookies)
    # info_deal_data = prase_cus_info(detail_urls[2], orderno_secret, cookies)
    handle_record_data = prase_handel_record(detail_urls[5], orderno_secret, cookies)

    sd_dict['ord_cust_tel'] = cus_data['ord_cust_tel']
    print('ord_cust_tel:%s' % sd_dict['ord_cust_tel'])
    sd_dict['ord_accept_time'] = handle_record_data['ord_accept_time']
    print('ord_accept_time:%s' % sd_dict['ord_accept_time'])
    sd_dict['is_ins_join_send'] = handle_record_data['is_ins_join_send']
    print('is_ins_join_send:%s' % sd_dict['is_ins_join_send'])
    sd_dict['appoint_time'] = handle_record_data['appoint_time']
    print('appoint_time:%s' % sd_dict['appoint_time'])

    return sd_dict


def prase_cus_info(tab_url, orderno_secret, cookies):
    data_dict = dict()
    data_page = request_od_detail(tab_url,orderno_secret, cookies)

    data_page = etree.HTML(data_page)
    # print(etree.tostring(data_page))
    cus_phone = data_page.xpath('//table[@class="table-0"][1]/tbody/tr[1]/td[6]/input[@name="customerPhone"]/@value')
    if cus_phone:
        customer_phone = cus_phone[0]
    else:
        customer_phone = ''
    # cus_tel = data_page.xpath('//table[@class="table-0"][1]/tbody/tr[1]/td[4]/input[@name="customerTel"]/@value')
    data_dict['ord_cust_tel'] = customer_phone
    return data_dict


def prase_deal_info(tab_url, orderno_secret, cookies):
    data_dict = dict()
    data_page = request_od_detail(tab_url, orderno_secret, cookies)
    return data_dict


def prase_handel_record(tab_url, orderno_secret, cookies):
    data_dict = dict()
    data_page = request_od_detail(tab_url, orderno_secret, cookies)
    data_page = etree.HTML(data_page)
    # print(etree.tostring(data_page))
    handle_actions = data_page.xpath('//tbody/tr[2]/td[1]/text()')
    in_sys_time = handle_actions[0]
    data_dict['ord_accept_time'] = in_sys_time
    is_ins_join_send = data_page.xpath('//tbody/tr[2]/td[2]/text()')[0]   # 第二条操作纪录的内容
    if u'送装一体' in is_ins_join_send:
        data_dict['is_ins_join_send'] = True
        data_dict['appoint_time'] = ''
    else:
        data_dict['is_ins_join_send'] = False
        appoint_time = data_page.xpath('//tbody/tr[4]/td[2]/text()')[0]
        try:
            data_dict['appoint_time'] = time_to_timestamp2(aptime_format(appoint_time[appoint_time.index(u'：') + 1:]))
        except:
            data_dict['appoint_time'] = ''

    return data_dict


def parse_addr_jd(addr_str):
    """京东解析地址"""
    city_index = addr_str.index(u'市')
    strict_index = addr_str.index(u'区')
    province = u'四川省'
    city = addr_str[:city_index + 1]
    strict = addr_str[city_index + 1:strict_index + 1]
    addr_detail = addr_str[strict_index + 1:]
    addr_dict = dict()
    addr_dict['province'] = province
    addr_dict['city'] = city.replace(u'四川','')
    addr_dict['strict'] = strict
    addr_dict['street'] = ''
    addr_dict['addr_detail'] = addr_detail
    return addr_dict