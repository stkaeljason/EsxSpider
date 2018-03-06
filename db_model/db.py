# coding: utf8

import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy import inspect
from appBot import utils

conf = configparser.ConfigParser()
# ./config.stage.conf
if utils.is_product() is True:
	conf.read('./config.conf')
else:
	conf.read('./config.stage.conf')

mysql_host = conf['MYSQL']['mysql_host']
mysql_user = conf['MYSQL']['mysql_user']
mysql_pwd = conf['MYSQL']['mysql_pwd']
mysql_db = conf['MYSQL']['mysql_db']
mysql_port = conf['MYSQL']['mysql_port']

engine = create_engine('mysql+mysqlconnector://'+mysql_user+':'+mysql_pwd+'@'+mysql_host+':'+mysql_port+'/'+mysql_db+'',echo=False)
# DBSession = sessionmaker(bind=engine)
DBSession = sessionmaker(autoflush=True,autocommit=False,bind=engine)
# session = DBSession()
# session = scoped_session(sessionmaker(autoflush=True,autocommit=False,bind=engine))
session = scoped_session(DBSession)
# self.db_engine = create_engine(DATABASE_CONNECTION_INFO, echo=False)


def find(model,params):
	inst = inspect(model)
	attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
	data = session.query(model).filter(params).all()
	result = {}
	if data:
		for attr in attr_names:
			result[attr] = eval('data[0].' + attr)
	session.commit()
	session.close()
	return result

def select(model,params = None):
	if params is None:
		data = session.query(model).all()
	else:
		data = session.query(model).filter(params).all()
	inst = inspect(model)
	attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
	result = []
	if data:
		for item in data:
			temp = {}
			for attr in attr_names:
				temp[attr] = eval('item.' + attr)
			result.append(temp)
	session.commit()
	session.close()
	return result

