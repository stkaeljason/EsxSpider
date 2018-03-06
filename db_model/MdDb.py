#coding:utf-8

import json

from db_model.db import DBSession
from db_model.mdAccount import MdAccount
from db_model.mdFactory import MdFactory
from db_model.MdMerchant import MdMerchant
from EsxSpider.tools import current_timestamp


# 测试用
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# eng = create_engine('mysql+mysqlconnector://'+'root'+':'+'root'+'@'+'127.0.0.1'+':'+'3306'+'/'+'ershixiong_anzhuang'+'')


def save_account(item,account):
    '''保存师傅账号信息'''
    session = DBSession()
    md_account = MdAccount(
                    )
    md_account.engineer_id = item['engineer_id']
    md_account.engineer_code = item['engineer_code']
    md_account.work_year = item['work_year']
    md_account.sex = item['sex']
    if item['address']:
        md_account.address = item['address']
    if item['unit_name']:
        md_account.unit_name = item['unit_name']
    if item['mobile']:
        md_account.engineer_tel = item['mobile']
    if item['engineer_name']:
        md_account.engineer_name = item['engineer_name']
    if item['work_no']:
        md_account.workNo = item['work_no']
    if item['unit_code']:
        md_account.unitCode = item['unit_code']
    md_account.account_source = account
    try:
        # 通过异常处理来避免插入时师傅重复
        session.add(md_account)           # 更好的方式是批量插入，add_all
        session.commit()
    except Exception as e:
        pass
        # print('shifu_add fail:'+str(e))


def save_md_factory(item, esx_orderno,accout):
    '''保存美的的工单号和对应的二师兄平台对应的订单号'''
    session = DBSession()
    md_factory = MdFactory(
        factorynumber=item['SERVICE_ORDER_NO'],      # 工单号
        service_order_id=item['SERVICE_ORDER_ID'],   # 和工单对应
        service_user_demandids=item['SERVICE_CUSTOMER_DEMAND_ID'],   # 和工单对应
        appoint_time=item['APPOINT_TIME'],           # 预约时间
        enginer_name=item['ENGINEER_NAME'],          # 派工师傅
        enginer_code=item['ENGINEER_CODE'],
        factory_data=json.dumps(item,encoding='utf-8',ensure_ascii=False),               # 所有数据
        platform_id= esx_orderno,                    # 二师兄平台订单插入id
        accout_source = accout,
        order_type= item['IMPLEMENT_SUB_TYPE_NAME'],
        created_at=current_timestamp()
    )
    session.add(md_factory)
    session.commit()

def save_md_factory_tm(item, esx_orderno):
    '''保存美的的工单号和对应的二师兄平台对应的订单号'''
    session = DBSession()
    md_factory = MdFactory(
        factorynumber=item['SERVICE_ORDER_NO'],      # 工单号
        service_order_id=item['SERVICE_ORDER_ID'],   # 和工单对应
        service_user_demandids=item['SERVICE_CUSTOMER_DEMAND_ID'],   # 和工单对应
        # appoint_time=item['APPOINT_TIME'],           # 预约时间
        # enginer_name=item['ENGINEER_NAME'],          # 派工师傅
        factory_data=json.dumps(item,encoding='utf-8',ensure_ascii=False),               # 所有数据
        platform_id= esx_orderno,                    # 二师兄平台订单插入id
        created_at=current_timestamp()
    )
    session.add(md_factory)
    session.commit()



def query_md_factory(factory_no):
    session = DBSession()
    rs = session.query(MdFactory).filter(MdFactory.factorynumber == factory_no)
    new_rs = [r for r in rs]
    return new_rs


def query_md_merchant(id):
    session = DBSession()
    rs = session.query(MdMerchant).filter(MdMerchant.id == id)
    # new_rs = [r for r in rs]
    return rs

def query_md_merchant_active():
    session = DBSession()
    rs = session.query(MdMerchant).filter(MdMerchant.is_active == 0)  # 0代表有效商家账号
    return rs
