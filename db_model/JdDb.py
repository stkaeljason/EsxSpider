#coding:utf-8

import json

from db_model.db import DBSession
from db_model.jd_model import JdAccount
from db_model.jd_model import JdFactory
from db_model.jd_model import JdMerchant
from EsxSpider.tools import current_timestamp


# 测试用
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# eng = create_engine('mysql+mysqlconnector://'+'root'+':'+'root'+'@'+'127.0.0.1'+':'+'3306'+'/'+'ershixiong_anzhuang'+'')

def save_order_detail(item):
    """保存订单详情"""
    pass


def save_account(item):
    '''保存师傅账号信息'''
    session = DBSession()
    md_account = JdAccount(
                    )
    md_account.engineer_id = item['engineerNoSec']
    md_account.engineer_code = item['engineerNo']
    # md_account.work_year = item['work_year']
    # md_account.sex = item['sex']
    if item['address']:
        md_account.address = item['address']
    if item['websiteName']:
        md_account.unit_name = item['websiteName']
    if item['mobile']:
        md_account.engineer_tel = item['mobile']
    if item['engineerName']:
        md_account.engineer_name = item['engineerName']
    # if item['work_no']:
    #     md_account.workNo = item['work_no']
    if item['websiteNo']:
        md_account.unitCode = item['websiteNo']
    try:
        # 通过异常处理来避免插入时师傅姓名重复
        session.add(md_account)           # 更好的方式是批量插入，add_all
        session.commit()
    except Exception as e:
        pass
        # print('shifu_add fail:'+str(e))


def save_factory(item, esx_orderno, static_data):
    '''保存美的的工单号和对应的二师兄平台对应的订单号'''
    session = DBSession()
    md_factory = JdFactory(
        factorynumber=item['orderno'],      # 工单号
        service_order_id=item['orderId'],   # 和工单对应
        # service_user_demandids=item['SERVICE_CUSTOMER_DEMAND_ID'],   # 和工单对应
        appoint_time=static_data['appoint_time'],         # 预约时间
        enginer_name=item['engineerName'],          # 派工师傅
        factory_data=json.dumps(item,encoding='utf-8',ensure_ascii=False),               # 所有数据
        esx_order_id=esx_orderno,                    # 二师兄平台订单插入id
        created_at=current_timestamp()
    )
    session.add(md_factory)
    session.commit()


def query_factory(factory_no):
    session = DBSession()
    rs = session.query(JdFactory).filter(JdFactory.factorynumber == factory_no)
    new_rs = [r for r in rs]
    return new_rs


def query_jd_ordid(order_id):
    session = DBSession()
    rs = session.query(JdFactory.esx_order_id).filter(JdFactory.service_order_id == order_id)
    new_rs = [r.esx_order_id for r in rs]
    return new_rs


def query_jd_merchant():
    session = DBSession()
    rs = session.query(JdMerchant).filter(JdMerchant.is_active == 0) # 只获取激活的商家账号0,未激活是１
    return rs