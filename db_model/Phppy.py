# coding: utf8

from sqlalchemy import Column, String , Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Phppy(Base):
    # 表的名字:
    __tablename__ = 'dm_phppy'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    data = Column(String(2600))
    time = Column(String(10))
    channel = Column(String(40))