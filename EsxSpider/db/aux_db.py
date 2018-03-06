# -*- coding: utf-8 -*-


import MySQLdb
import traceback
# from EsxSpider.settings import MYSQL_CONFIG
import MySQLdb.cursors
from collections import OrderedDict
from db_model.db import mysql_host,mysql_user,mysql_pwd,mysql_port,mysql_db


class AuxDb():

    def __init__(self):
        self.orderType = {"1":u'安装',"3":u'移机',"5":u'维修'}

    def handle_select(self, sql):
        conn = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pwd,db=mysql_db,charset="utf8",cursorclass = MySQLdb.cursors.DictCursor)
        cursor = conn.cursor()
        try:
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

    def save_work_order(self, work_order):
        """保存工单"""
        sql = "INSERT INTO dm_auxfactory_order (factorynumber) values('%s')" % (work_order)
        self.handle_sql(sql)

    def save_order(self, order, work_order):
        """保存订单"""
        sql = "UPDATE dm_auxfactory_order SET aux_orderno = '%s' where factorynumber = '%s'" % (order, work_order)
        self.handle_sql(sql)

    def save_auxfactory(self, factorynumber, ord_id,created_time,order_type,aux_merc):
        sql = "INSERT INTO dm_auxfactory_order (factorynumber, platform_id, created_at, order_type,aux_merc) values('%s', '%s','%s','%s','%s')"%(factorynumber,ord_id,created_time,self.orderType.get(str(order_type)),aux_merc)
        self.handle_sql(sql)


    def save_order_detail(self, order_detail):
        """保存订单详情"""
        # print(order_detail)
        sql = "INSERT INTO dm_order (ord_cust_name, ord_cust_tel, ord_cust_addr, ord_province, ord_city,ord_district, ord_street, ord_remark,"
        sql += "ord_num, ord_pay_num, ord_grab_addr, ord_cust_fault, ord_accept_no,ord_ask_time, ord_create_time, ord_buy_time,"
        sql += "ord_cust_lng,ord_cust_lat,ord_weixin_num,ord_merc_id,ord_purchase_unit,ord_purchase_unit_id,ord_status,"
        sql += "ord_need_build,ord_type,ord_sale_unit,ord_accept_time) "
        sql += "values('%s','%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % tuple(order_detail.values()[:27])
        ord_id = self.handle_sql(sql)
        # print 'jajsjj:%s',ord_id

        # 测试用，把同步的订单先隐藏，正式上线时去除
        # hide_sql = "update dm_order set ord_is_hide = 2 where ord_id = %d"%ord_id
        # self.handle_sql(hide_sql)

        # 根据渠道名称和商家id获得渠道id
        # print('qudao:%s'%order_detail['qudao'],type(order_detail['qudao']))
        purchase_sql = "SELECT msu_id FROM dm_merchant_purchase_unit WHERE msu_sale_unit = '%s' and msu_merc_id = %d LIMIT 1" % (order_detail['qudao'].encode('utf-8'), order_detail['ord_merc_id'])
        msuinfo = self.handle_select(purchase_sql)
        # print('msuinfo:', msuinfo)

        # 如果渠道id没查到默认用厂家系统再查一次
        if not msuinfo:
            purchase_sql = "SELECT msu_id FROM dm_merchant_purchase_unit WHERE msu_sale_unit = '%s' and msu_merc_id = %d LIMIT 1" % (u'厂家系统'.encode('utf-8'), order_detail['ord_merc_id'])
            msuinfo = self.handle_select(purchase_sql)
        # print('purchase_sql:%s'%purchase_sql)
        print('msuinfo:', msuinfo)

        #　查找商家的城市id
        mercsql = "SELECT merc_city_id,merc_id FROM dm_merchant WHERE merc_id = %d LIMIT 1"%(order_detail['ord_merc_id'])
        mercInfo = self.handle_select(mercsql)
        # print('mercInfo:',mercInfo)


        # 根据渠道id，品牌，商家ｉｄ,apl_is_disable=0查找电器ｉｄ
        if msuinfo:
            # 更新dm_order的ord_purchase_unit_id，也就是渠道
            # ord_purchase_unit_sql = "update dm_order set ord_purchase_unit_id = %d, ord_purchase_unit = '%s' where ord_id = %d" % (msuinfo[0]['msu_id'],order_detail['qudao'],ord_id)
            ord_purchase_unit_sql = "update dm_order set ord_purchase_unit_id = %d where ord_id = %d" % (msuinfo[0]['msu_id'], ord_id)
            # print('ord_purchase_unit_sql:',ord_purchase_unit_sql)
            self.handle_sql(ord_purchase_unit_sql)

            dm_appliances_sql = "SELECT apl_id FROM `dm_appliances` WHERE "
            dm_appliances_sql += "apl_purchase_unit_id = %d and apl_brand = '%s' and apl_merc_id = %d and apl_is_disable = 0 LIMIT 1" % (
            msuinfo[0]['msu_id'], order_detail['brand'].encode('utf-8'), order_detail['ord_merc_id'])
            aplinfo = self.handle_select(dm_appliances_sql)
            # print('aplinfo:',aplinfo)



        # 根据电器ｉｄ和匹数获取电器型号
        amsql = "SELECT * FROM dm_appliances_model WHERE  apl_id = %d and is_disable = 0 and apl_model = '%s'  LIMIT 1"%(aplinfo[0]['apl_id'], str(order_detail['pi_num']))
        # print amsql
        amInfo = self.handle_select(amsql)
        # print 'amInfo:',amInfo

        # arsql = 'SELECT * FROM `dm_appliances_rate` WHERE ( rate_apl_model_id = '+str(amInfo[0]['id'])
        # arsql += ' and rate_city_id = '+str(mercInfo[0]['merc_city_id'])+') LIMIT 1'
        #　根据电器型号获取费用数据
        arsql = "SELECT * FROM `dm_appliances_rate` WHERE rate_apl_model_id = %d and rate_is_disable = 0 LIMIT 1" % (amInfo[0]['id'])
        arInfo = self.handle_select(arsql)
        # print 'arInfo:', arInfo

        # 组装电器订单表所需数据
        oaData = OrderedDict()
        oaData['oa_ord_id'] = ord_id
        # // $oaData['订单ID
        # // $oaData['电器ID，用来关联电器品牌和商标
        oaData['oa_apl_id'] = aplinfo[0]['apl_id']
        # // 具体型号
        if order_detail['machine_model']:
            oaData['oa_model'] = order_detail['machine_model']
        else:
            oaData['oa_model'] = '000'
        # // $oaData['具体型号
        oaData['oa_num'] = order_detail['condition_num']
        oaData['oa_apl_model'] = order_detail['pi_num']
        # // $oaData['电器型号
        oaData['oa_apl_rate'] = order_detail['pi_num'].replace('P','')
        oaData['oa_rate_merc_cost'] = arInfo[0]['rate_merc_cost'] * int(order_detail['condition_num'])
        # // $oaData['商家结算费用'] = '';
        oaData['oa_rate_mast_cost'] = arInfo[0]['rate_mast_cost'] * int(order_detail['condition_num'])
        # // $oaData['师傅结算费用
        oaData['oa_rate_show_cost'] = arInfo[0]['rate_show_cost'] * int(order_detail['condition_num'])
        # // $oaData['APP端显示金额
        oaData['oa_rate_guarantee_money'] = arInfo[0]['rate_guarantee_money']
        # // $oaData['质保金
        oaData['oa_rate_evaluation_money'] = arInfo[0]['rate_evaluation_money']
        # // $oaData['满意度评价金额
        oaData['oa_rate_base_money'] = arInfo[0]['rate_base_money'] * int(order_detail['condition_num'])
        # // $oaData['结算基本费用
        oaData['oa_rate_move_user_cost'] = arInfo[0]['rate_move_user_cost']
        # // $oaData['用户花费(非金卡)
        oaData['oa_rate_move_mast_cost'] = arInfo[0]['rate_move_mast_cost']
        # // $oaData['移机师傅结算费用(非金卡)
        oaData['oa_rate_move_merc_cost'] = arInfo[0]['rate_move_merc_cost']
        # // $oaData['移机商家结算费用(非金卡)
        oaData['oa_rate_move_user_cost_vip'] = arInfo[0]['rate_move_user_cost_vip']
        # // $oaData['用户花费(金卡)
        oaData['oa_rate_move_mast_cost_vip'] = arInfo[0]['rate_move_mast_cost_vip']
        # // $oaData['移机师傅结算费用(金卡)
        oaData['oa_rate_move_merc_cost_vip'] = arInfo[0]['rate_move_merc_cost_vip']
         # $oaData['移机商家结算费用(金卡)
        oaData['oa_rate_teardown_user_cost'] = arInfo[0]['rate_teardown_user_cost']
        # // $oaData['拆机用户支付费用(非金卡)
        oaData['oa_rate_teardown_mast_cost'] = arInfo[0]['rate_teardown_mast_cost']
        # // $oaData['拆机师傅获得费用(非金卡)
        oaData['oa_rate_teardown_merc_cost'] = arInfo[0]['rate_teardown_merc_cost']
        # // $oaData['拆机商家分成费用(非金卡)
        oaData['oa_rate_teardown_user_cost_vip'] = arInfo[0]['rate_teardown_user_cost_vip']
        # // $oaData['拆机用户支付费用(金卡)
        oaData['oa_rate_teardown_mast_cost_vip'] = arInfo[0]['rate_teardown_mast_cost_vip']
        # // $oaData['拆机师傅获得费用(金卡)
        oaData['oa_rate_teardown_merc_cost_vip'] = arInfo[0]['rate_teardown_merc_cost_vip']
        # // $oaData['拆机商家分成费用(金卡)
        oaData['oa_rate_repair_merc_cost'] = arInfo[0]['rate_repair_merc_cost']
        # // $oaData['维修商家保外奖励费用
        oaData['oa_rate_repair_warr_plat_extract'] = arInfo[0]['rate_repair_warr_plat_extract']
        # // $oaData['维修保外平台提取
        oaData['oa_rate_repair_merc_plat_cost'] = arInfo[0]['rate_repair_merc_plat_cost']

        # oasql = "INSERT INTO dm_order_aplicances (oa_rate_teardown_user_cost,oa_model,oa_rate_mast_cost,oa_ord_id,"
        # oasql += "oa_rate_teardown_mast_cost_vip,oa_rate_teardown_mast_cost,oa_rate_show_cost,oa_rate_evaluation_money,"
        # oasql += "oa_rate_teardown_merc_cost_vip,oa_rate_repair_warr_plat_extract,oa_num,oa_rate_merc_cost,"
        # oasql += "oa_rate_repair_merc_plat_cost,oa_apl_rate,oa_rate_move_merc_cost,oa_rate_teardown_merc_cost,"
        # oasql += "oa_rate_move_mast_cost_vip,oa_rate_repair_merc_cost,oa_rate_move_user_cost_vip,oa_rate_move_mast_cost,"
        # oasql += "oa_rate_teardown_user_cost_vip,oa_rate_move_merc_cost_vip,oa_rate_move_user_cost,oa_rate_guarantee_money,"
        # oasql += "oa_apl_model,oa_rate_base_money) "
        # oasql += "values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s' )" % tuple(oaData.values()[:26])
        # oa_id = self.handle_sql(oasql)
        oasql = "INSERT INTO dm_order_aplicances (oa_ord_id,oa_apl_id,oa_model,oa_num,oa_apl_model,"
        oasql += "oa_apl_rate,oa_rate_merc_cost,oa_rate_mast_cost,oa_rate_show_cost,"
        oasql += "oa_rate_guarantee_money,oa_rate_evaluation_money,oa_rate_base_money,oa_rate_move_user_cost,"
        oasql += "oa_rate_move_mast_cost,oa_rate_move_merc_cost,oa_rate_move_user_cost_vip,oa_rate_move_mast_cost_vip,"
        oasql += "oa_rate_move_merc_cost_vip,oa_rate_teardown_user_cost,oa_rate_teardown_mast_cost,"
        oasql += "oa_rate_teardown_merc_cost,oa_rate_teardown_user_cost_vip,oa_rate_teardown_mast_cost_vip,oa_rate_teardown_merc_cost_vip,"
        oasql += "oa_rate_repair_merc_cost,oa_rate_repair_warr_plat_extract,oa_rate_repair_merc_plat_cost) "
        oasql += "values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s' )" % tuple(oaData.values()[:27])
        oa_id = self.handle_sql(oasql)
        print('oa_id:%s'%oa_id)

        if order_detail['ord_type']==1:
            dataCost = dict()
            dataCost['ord_merc_cost'] = oaData['oa_rate_merc_cost']
            dataCost['ord_amount'] = oaData['oa_rate_show_cost']
            dataCost['ord_mast_cost'] = oaData['oa_rate_mast_cost']
            dataCost['ord_show_cost'] = oaData['oa_rate_show_cost']
            costsql = 'UPDATE `dm_order` SET `ord_merc_cost` = '+str(dataCost['ord_merc_cost'])
            costsql += ', `ord_mast_cost` = '+str(dataCost['ord_mast_cost'])+', `ord_show_cost` = '
            costsql += str(dataCost['ord_show_cost'])+', `ord_amount` = '+str(dataCost['ord_amount'])
            costsql += ' WHERE `dm_order`.`ord_id` = ' + str(ord_id)
            dump_ord_id = self.handle_sql(costsql)
        return ord_id


    def update_shifu(self,shifu_data):
        update_sql = "UPDATE dm_aux_account SET aux_id_number = '%s' where aux_name = '%s' and aux_id_number IS NULL"%(shifu_data['user_id'],shifu_data['name'])
        self.handle_sql(update_sql)


    def save_shifu(self, shifu_data):
        get_shifu_sql = "SELECT aux_name FROM dm_aux_account"
        selcet_r = self.handle_select(get_shifu_sql)
        # print('select shifu result:%s',r)
        shifu_dict = {r['aux_name']:None for r in selcet_r}
        if shifu_data['name'] not in shifu_dict:
            insert_shifu_sql = "INSERT INTO dm_aux_account (aux_name, aux_serial_number, aux_phone, aux_archives_number, aux_id_number) values('%s','%s','%s','%s','%s')" % (shifu_data['name'], shifu_data['aux_num'], shifu_data['phone'], shifu_data['num'], shifu_data['user_id'])
            self.handle_sql(insert_shifu_sql)


    def save_master(self, shifu_data):
        get_shifu_sql = "SELECT aux_phone FROM dm_aux_account"
        selcet_r = self.handle_select(get_shifu_sql)
        # print('select shifu result:%s',r)
        shifu_dict = {r['aux_phone']: None for r in selcet_r}
        if shifu_data['is_use'] == 'circle-green':
            if shifu_data['aux_phone'] not in shifu_dict:
                insert_shifu_sql = "INSERT INTO dm_aux_account (aux_merc_account, password, aux_id_number, aux_name, aux_serial_number, aux_phone,aux_archives_number,token,aux_add_time) values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                shifu_data['aux_merc_account'], shifu_data['password'], shifu_data['aux_id_number'], shifu_data['aux_name'], shifu_data['aux_serial_number'],shifu_data['aux_phone'],shifu_data['aux_archives_number'],shifu_data['token'],shifu_data['aux_add_time'])
                self.handle_sql(insert_shifu_sql)
            else:
                update_shifu_sql = "UPDATE dm_aux_account SET aux_merc_account = '%s', password = '%s', aux_id_number = '%s', aux_serial_number = '%s', aux_phone = '%s', aux_archives_number = '%s' where aux_phone = '%s'"%(shifu_data['aux_merc_account'], shifu_data['password'], shifu_data['aux_id_number'], shifu_data['aux_serial_number'],shifu_data['aux_phone'],shifu_data['aux_archives_number'],shifu_data['aux_phone'])
                self.handle_sql(update_shifu_sql)