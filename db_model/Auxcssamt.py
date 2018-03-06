# coding: utf8

from sqlalchemy import Column, String , Integer,DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Auxcssamt(Base):
    # 表的名字:
    __tablename__ = 'dm_auxcssamt'

    # 表的结构:
    id = Column(Integer, primary_key=True,autoincrement = True)
    ord_id = Column(Integer,unique = True)
    sssd_source_bill_type_name = Column(String(60),nullable=True)
    sssd_serv_total_amt = Column(DECIMAL(10,2),nullable=True)
    sssd_other_total2_amt = Column(DECIMAL(10,2),nullable=True)
    incode = Column(String,nullable=True)
    outcode = Column(String,nullable=True)
    sssd_rowid = Column(String(20),nullable=True)
    css_account = Column(String(20),nullable=True)
    sssd_source_bill_no = Column(String(40),nullable=True)
    aa_serv_settle_no = Column(String(60),nullable=True)
    sssd_dv_audit_status_name = Column(String(40),nullable=True)
    sssd_ss_audit_status = Column(String(8),nullable=True)
    cscp_product_model = Column(String(100),nullable=True)
    sssd_serv_date = Column(String(100),nullable=True)
    svbl_submit_date = Column(String(100),nullable=True)
    cscm_mobile_phone1 = Column(String(100),nullable=True)
    sssd_created_date = Column(String(100),nullable=True)
    sssd_last_upd_date = Column(String(60),nullable=True)
    created_at = Column(Integer,nullable=True)