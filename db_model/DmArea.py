# coding: utf8
from db_model.db import DBSession
from sqlalchemy import Column, String , Integer, SmallInteger,TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DmArea(Base):
    # 表的名字:
    __tablename__ = 'dm_area'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    parent_id = Column(SmallInteger)
    child_ids = Column(TEXT,nullable=True)
    initial = Column(String(1),nullable=True)
    sort = Column(Integer,nullable=True)


def query_area(name):
    session = DBSession()
    rs = session.query(DmArea).filter(DmArea.name == name)
    return rs


