# coding:utf-8

from sqlalchemy import Column, String, INTEGER, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from db import engine


Base = declarative_base()


class MdOrder(Base):
    # 表名
    __tablename__ = 'dm_midea_order'

    ord_id = Column(INTEGER, primary_key=True, autoincrement=True,unique=True)
    ord_unit_name = Column(String, nullable=True)
    ord_finish_time_ = Column(String, nullable=True)
    ord_dispatch_order_time = Column(String, nullable=True)
    ord_area_num = Column(String, nullable=True)
    ord_unit_code = Column(String, nullable=True)
    ord_service_method_code = Column(String, nullable=True)
    ord_contain_ejfws = Column(String, nullable=True)
    ord_receive_order_time = Column(String, nullable=True)
    ord_customer_level_ = Column(String, nullable=True)
    ord_service_sub_type_code = Column(String, nullable=True)
    ord_service_type_code_= Column(String, nullable=True)
    ord_purchasing_channels= Column(String, nullable=True)
    ord_service_customer_tel1= Column(String, nullable=True)
    ord_contain_ejfws_= Column(String, nullable=True)
    ord_service_order_id= Column(String, nullable=True)
    ord_pub_create_person= Column(String, nullable=True)
    ord_receive_order_time_= Column(String, nullable=True)
    ord_change_appoint_time= Column(String, nullable=True)
    ord_unit_level= Column(String, nullable=True)
    ord_service_customer_address= Column(String)        # 用户地址
    ord_customer_name= Column(String, nullable=True)
    ord_complaint_flag_= Column(String, nullable=True)
    ord_service_order_status_= Column(String, nullable=True)
    ord_contact_order_ser_item2_name= Column(String, nullable=True)
    ord_purchasing_channels_= Column(String, nullable=True)
    ord_branch_code= Column(String, nullable=True)
    ord_service_type_code= Column(String, nullable=True)
    ord_account_statement_time= Column(String, nullable=True)
    ord_purchase_date= Column(String, nullable=True)
    ord_complaint_level_= Column(String, nullable=True)
    ord_order_origin= Column(String, nullable=True)
    ord_information_follow_= Column(String, nullable=True)
    ord_service_sub_type_name= Column(String, nullable=True)
    ord_receive_order_person= Column(String, nullable=True)
    ord_information_follow= Column(String, nullable=True)
    ord_prod_code= Column(String, nullable=True)
    ord_tmp_row_no= Column(INTEGER, nullable=True)
    ord_service_desc= Column(String, nullable=True)
    ord_implement_sub_type_code_= Column(String, nullable=True)
    ord_prod_name= Column(String, nullable=True)
    ord_pub_create_date= Column(String, nullable=True)
    ord_contact_time= Column(String, nullable=True)
    ord_service_order_no= Column(String, unique=True)                # 订单号,唯一
    ord_order_origin_= Column(String, nullable=True)
    ord_feedback_time_= Column(String, nullable=True)
    ord_customer_level= Column(String, nullable=True)
    ord_contact_time_= Column(String, nullable=True)
    ord_service_customer_demand_id= Column(String, nullable=True)
    ord_change_appoint_time_= Column(String, nullable=True)
    ord_implement_sub_type_code= Column(String, nullable=True)
    ord_product_use_= Column(String, nullable=True)
    ord_appoint_time= Column(String, nullable=True)
    ord_product_use= Column(String, nullable=True)
    ord_e_feedback_time= Column(String, nullable=True)
    ord_finish_time= Column(String, nullable=True)
    ord_is_input_archives= Column(INTEGER, nullable=True)
    ord_service_area_code= Column(String, nullable=True)
    ord_prod_num= Column(INTEGER, nullable=True)
    ord_contact_order_serv_type_name= Column(String, nullable=True)
    ord_feedback_time= Column(String, nullable=True)
    ord_customer_tel1= Column(String)              # 用户电话
    ord_branch_name= Column(String, nullable=True)
    ord_implement_sub_type_name= Column(String, nullable=True)
    ord_complaint_level= Column(String, nullable=True)
    ord_account_statement_time_= Column(String, nullable=True)
    ord_brand_name= Column(String, nullable=True)
    ord_service_area_name= Column(String, nullable=True)
    ord_urgent_level= Column(String, nullable=True)
    ord_complaint_flag= Column(String, nullable=True)
    ord_service_method_name= Column(String, nullable=True)
    ord_e_feedback_time_= Column(String, nullable=True)
    ord_intf_order_code= Column(String, nullable=True)
    ord_dispatch_order_time_= Column(String, nullable=True)
    ord_purchase_date_= Column(String, nullable=True)
    ord_customer_area_code= Column(String, nullable=True)
    ord_service_customer_name= Column(String)        # 用户姓名
    ord_service_order_status= Column(String, nullable=True)
    ord_urgent_level_= Column(String, nullable=True)

Base.metadata.create_all(bind=engine)    # 每次会自动检查表是否存在，不存在就会自动创建