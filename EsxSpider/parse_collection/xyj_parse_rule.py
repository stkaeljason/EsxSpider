#coding:utf-8

import json
import sys
import datetime
import random
# sys.path.append('/home/jason/esx_work/ershixiong_auto/EsxSpider')  # 正式环境需要修改路径
from collections import OrderedDict


# from EsxSpider.items import MeidiDetailItem
from EsxSpider.tools import create_sn, get_latlng, get_every_addr, intercept_qu, current_timestamp, aptime_format, \
    time_to_timestamp2, time_to_timestamp3


def xyj_detail_parse(od_dict):
    '''美的订单详情数据组装'''
    item = OrderedDict()

    # dm_clean_order 表所需数据
    # 接件单号
    item['cord_user_name']= od_dict['SERVICE_CUSTOMER_NAME']
    item['cord_user_tel']= od_dict['CUSTOMER_TEL1']
    # 来源，喜悦家是1
    item['cord_source_id'] = 1
    addr_dict = get_every_addr(od_dict['SERVICE_CUSTOMER_ADDRESS']) # 计算地址dict
    item['cord_user_address']= addr_dict['addr_detail']
    item['cord_user_province']= addr_dict['province']
    item['cord_user_city']= addr_dict['city']
    item['cord_user_area']= addr_dict['strict']
    # 备注，对应于美的的服务请求描述
    item['cord_remark'] = od_dict['SERVICE_DESC']
    # 订单号，待确认
    item['cord_num']= 'Q'+ datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randrange(1000,9999))
    item['cord_is_pay'] = 0
    item['cord_create_time'] = current_timestamp()
    # 关联微信信息
    item['cord_open_id'] = 0
    # 订单关联渠道，默认0
    item['cord_merc_id'] = 0  #
    # 购买渠道id
    # item['ord_purchase_unit_id'] =    # 和渠道表的是同一个值，在查到渠道id后更新
    item['cord_status'] = 0              # 待发布
    # 业务类型
    item['cord_type'] = 0
    # 预约安装时间
    try:
        item['cord_ins_time'] = time_to_timestamp2(aptime_format(od_dict['APPOINT_TIME']))
    except:
        pass
    # 用户支付金额
    item['cord_user_cost'] = 0.0
    # 师傅所得金额
    # item['cord_mast_cost'] = '0.00'


    # clean_goods所需数据
    item['og_num'] = od_dict['PROD_NUM']
    return item



