# coding: utf8

from sqlalchemy import Column, String , Integer,DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Order(Base):
    # 表的名字:
    __tablename__ = 'dm_order'

    # 表的结构:
    ord_id = Column(Integer, primary_key=True)
    ord_install_id = Column(Integer)
    ord_merc_cost = Column(DECIMAL(10,2),nullable=True)
    ord_status = Column(Integer,nullable=True)
    ord_is_back = Column(Integer,nullable=True)
    ord_merc_id = Column(Integer,nullable=True)
    ord_mast_id = Column(Integer,nullable=True)
    ord_finish_time = Column(Integer,nullable=True)
    ord_cust_name = Column(String,nullable=True)
    ord_cust_sex = Column(Integer,nullable=True)
    ord_cust_tel = Column(String,nullable=True)
    ord_cust_addr = Column(String,nullable=True)
    ord_province = Column(String,nullable=True)
    ord_city = Column(String,nullable=True)
    ord_district = Column(String,nullable=True)
    ord_remark = Column(String,nullable=True)
    ord_num = Column(String,nullable=True)
    ord_weixin_num = Column(String,nullable=True)
    ord_cust_told = Column(String,nullable=True)
    # ord_mast_cost = Column(String,nullable=True)
    ord_mast_cost = Column(DECIMAL(10,2),nullable=True)
    ord_cust_lat = Column(String,nullable=True)
    ord_cust_lng = Column(String,nullable=True)
    ord_purchase_unit = Column(String,nullable=True)
    ord_purchase_unit_id = Column(String,nullable=True)
    ord_type = Column(String,nullable=True)
    ord_partner_id = Column(String,nullable=True)
    ord_is_hide = Column(String,nullable=True)