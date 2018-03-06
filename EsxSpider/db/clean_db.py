# -*- coding: utf-8 -*-

import MySQLdb
import traceback
import MySQLdb.cursors

from collections import OrderedDict
from db_model.db import mysql_host,mysql_user,mysql_pwd,mysql_port,mysql_db


class CleanDb():

    def __init__(self, od_detail=None):
        self.order_detail = od_detail

    def handle_select(self, sql):
        conn = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pwd,db=mysql_db,charset="utf8",cursorclass = MySQLdb.cursors.DictCursor)
        cursor = conn.cursor()
        try:
            # sql = sql.encode('utf-8')

            cursor.execute(sql)
            return cursor.fetchall()

        except:
            traceback.print_exc()
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def handle_sql(self, sql):
        conn = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pwd,db=mysql_db,charset="utf8")
        cursor = conn.cursor()
        try:
            # cursor.execute(sql)
            # conn.commit()
            cursor.execute(sql)
            result_id = int(conn.insert_id())
            conn.commit()
            return result_id

        except:
            traceback.print_exc()
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def insert_clean_order(self):
        """订单基本信息插入"""
        # dm_order数据插入
        sql = "INSERT INTO dm_clean_order (cord_user_name, cord_user_tel, cord_source_id, cord_user_address, cord_user_province,cord_user_city, cord_user_area, "
        sql += "cord_remark,cord_num, cord_is_pay, cord_create_time, cord_open_id,cord_merc_id,cord_status,"
        sql += "cord_type,cord_ins_time)"
        sql += "values('%s','%s','%s','%s','%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s')" % tuple(self.order_detail.values()[:16])
        ord_id = self.handle_sql(sql)
        print ord_id
        return ord_id

    def update_clean_order(self, ord_id):
        award_sql = "SELECT award_ratio FROM dm_topup_award_ratio WHERE award_id = 3"
        award = self.handle_select(award_sql)
        award = float(award[0]['award_ratio']/100)
        print 'award:%s'%award,type(award)
        print self.order_detail['cord_user_cost']*award
        update_cost_sql = "UPDATE dm_clean_order SET cord_settlement = %s where cord_id = %d "%(award,ord_id)
        self.handle_sql(update_cost_sql)
    # def insert_clean_goods(self, oaData):
    #     oasql = "INSERT INTO dm_clean_goods (oa_ord_id,oa_apl_id,oa_model,oa_num,oa_apl_model)"
    #     oasql += "values('%s','%s','%s','%s')" % tuple(oaData.values()[:27])
    #     oa_id = self.handle_sql(oasql)
    #     print('oa_id:%s' % oa_id)
    #     return oa_id

    def save_order_detail(self):
        ord_id = self.insert_clean_order()
        self.update_clean_order(ord_id)
        return ord_id