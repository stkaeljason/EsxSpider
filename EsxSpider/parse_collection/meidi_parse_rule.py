#coding:utf-8

import json
import sys
sys.path.append('/home/jason/esx_work/ershixiong_auto/EsxSpider')  # 正式环境需要修改路径
from collections import OrderedDict

# from EsxSpider.items import MeidiDetailItem
from EsxSpider.tools import create_sn, get_latlng, get_every_addr, intercept_qu, current_timestamp, aptime_format, \
    time_to_timestamp2, time_to_timestamp3


def md_detail_parse(od_dict,merchant):
    '''美的订单详情数据组装'''
    item = OrderedDict()

    # dm_order 表所需数据，18个
    # 接件单号
    item['ord_cust_name']= od_dict['SERVICE_CUSTOMER_NAME']
    item['ord_cust_tel']= od_dict['CUSTOMER_TEL1']
    addr_dict = get_every_addr(od_dict['SERVICE_CUSTOMER_ADDRESS']) # 计算地址dict
    item['ord_cust_addr']= addr_dict['addr_detail']
    item['ord_province']= addr_dict['province']
    item['ord_city']= addr_dict['city']
    item['ord_district']= addr_dict['strict']
    item['ord_street'] = addr_dict['street']
    # 备注，对应于美的的服务请求描述
    item['ord_remark'] = od_dict['SERVICE_DESC']
    # 用户报修故障
    item['ord_cust_fault'] = od_dict['SERVICE_DESC']
    item['ord_num']= create_sn()
    item['ord_pay_num'] = create_sn()
    item['ord_grab_addr'] = ''
    item['ord_accept_no'] = od_dict['SERVICE_ORDER_NO']
    # item['ord_ask_time'] =
    item['ord_create_time'] = current_timestamp()
    item['ord_buy_time'] = item['ord_create_time']
    lng_lat = get_latlng(addr_dict['city'], addr_dict['strict']+addr_dict['street']+addr_dict['addr_detail'])
    # print lng_lat
    item['ord_cust_lng'] = lng_lat[0]
    item['ord_cust_lat'] = lng_lat[1]
    item['ord_weixin_num'] = ''
    item['ord_merc_id'] = 4  # 科域伟业
    # 购买单位
    item['ord_purchase_unit'] = u'厂派'
    item['ord_status'] = 0              # 待发布
    item['ord_need_build'] = 2   # 不用建单
    # 业务类型
    if u'维修' in od_dict['IMPLEMENT_SUB_TYPE_NAME']:   # 根据实施业务类型字段判断业务类型
        item['ord_type'] = 5
    else:
        item['ord_type'] = 1
    # 预约安装时间
    try:
        item['ord_ins_time'] = time_to_timestamp2(aptime_format(od_dict['APPOINT_TIME']))
    except:
        item['ord_ins_time'] = ''
    # 接件时间, midea接入时间
    item['ord_accept_time'] = time_to_timestamp3(od_dict['DISPATCH_ORDER_TIME'])
    # 销售单位,midea购买渠道
    item['ord_sale_unit'] = od_dict['PURCHASING_CHANNELS']
    # 购买渠道id
    item['ord_purchase_unit_id'] = 0  # 和渠道表的是同一个值，在查到渠道id后更新;和上面的ord_purchase_unit在渠道表中对应


    # dm_order表之外的表所需数据
    item['shangjia'] = od_dict['UNIT_NAME']
    # print('channel:%s'%od_dict['PURCHASING_CHANNELS'])
    # 商家ｉｄ
    item['merchant_id'] = merchant.platform_id

    if od_dict['PURCHASING_CHANNELS']:
        item['qudao'] = od_dict['PURCHASING_CHANNELS']
    else:
        item['qudao'] = ''
    item['pi_num'] = '1.5P'                  # md订单详情中没有此数据，由于1.5p以下包括1.5费用都是一样的默认为1.5
    item['pro_model'] = '000'    # md订单详情没有此数据，型号暂时默认为空
    item['pro_num'] = od_dict['PROD_NUM']
    return item
