#coding:utf-8

import MySQLdb
import traceback
import MySQLdb.cursors

from collections import OrderedDict
from db_model.db import mysql_host,mysql_user,mysql_pwd,mysql_port,mysql_db
from appBot.utils import saveApiLogs, errorReport


class MdDb():

    def __init__(self):
        pass

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

    def save_order_detail(self, order_detail):

        # dm_order数据插入
        sql = "INSERT INTO dm_order (ord_cust_name, ord_cust_tel, ord_cust_addr, ord_province, ord_city,ord_district, ord_street, ord_remark, "
        sql += "ord_cust_fault,ord_num, ord_pay_num, ord_grab_addr, ord_accept_no,ord_create_time,ord_buy_time,"
        sql += "ord_cust_lng,ord_cust_lat,ord_weixin_num,ord_merc_id,ord_purchase_unit,ord_status,"
        sql += "ord_need_build,ord_type,ord_ins_time,ord_accept_time,ord_sale_unit,ord_purchase_unit_id) "
        sql += "values('%s','%s','%s','%s','%s','%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % tuple(order_detail.values()[:27])
        ord_id = self.handle_sql(sql)
        print('ord_id:%s'%ord_id, type(ord_id))
        # 测试用，把同步的订单先隐藏，正式上线时去除
        # hide_sql = "update dm_order set ord_is_hide = 2 where ord_id = %d"%ord_id
        # self.handle_sql(hide_sql)

        # 依据商家名称获取商家id
        # merc_id_sql = "SELECT platform_id FROM `dm_media_merchant` WHERE `merchant_name` = '%s' LIMIT 1"%(order_detail['shangjia'])
        # # print('merc_id_sql:%s'%merc_id_sql)
        # platform_info = self.handle_select(merc_id_sql)
        # # print('platform_info:%s'%platform_info)
        # print('platform_id:%s'%platform_info[0]['platform_id'])

        # 根据渠道名称和商家id获得渠道id
        # print('qudao:%s'%order_detail['qudao'])
        purchase_sql = "SELECT msu_id FROM dm_merchant_purchase_unit WHERE msu_sale_unit = '%s' and msu_merc_id = %d LIMIT 1"%(order_detail['qudao'].encode('utf-8'), order_detail['merchant_id'])
        msuinfo = self.handle_select(purchase_sql)

        # 如果渠道没查到，默认用厂家系统来查询
        if not msuinfo:
            purchase_sql = "SELECT msu_id FROM dm_merchant_purchase_unit WHERE msu_sale_unit = '%s' and msu_merc_id = %d LIMIT 1" % (u'厂家系统'.encode('utf-8'),order_detail['merchant_id'])
            msuinfo = self.handle_select(purchase_sql)
        # print('purchase_sql:%s'%purchase_sql)
        print('msuinfo:', msuinfo)

        # 获取城市id
        mercsql = "SELECT merc_city_id,merc_id FROM `dm_merchant` WHERE `merc_id` = %d LIMIT 1"%(order_detail['merchant_id'])
        mercInfo = self.handle_select(mercsql)
        # print('mercInfo:%s'%mercInfo)

        # 根据渠道id和城市id查找电器id,如果渠道id能查到就用查到的渠道id,apl_is_disable=0，查不到电器id默认为22
        if msuinfo:
            # 更新ord_purchase_unit_id
            ord_purchase_unit_sql = "update dm_order set ord_purchase_unit_id = %d where ord_id = %d" % (msuinfo[0]['msu_id'], ord_id)
            self.handle_sql(ord_purchase_unit_sql)

            dm_appliances_sql = "SELECT apl_id FROM `dm_appliances` WHERE "
            dm_appliances_sql += "apl_city_id = %d and apl_purchase_unit_id = %d and apl_brand = '%s' and apl_merc_id = %d and apl_is_disable = 0 LIMIT 1" % (mercInfo[0]['merc_city_id'], msuinfo[0]['msu_id'],'美的',order_detail['merchant_id'])
            # print dm_appliances_sql
            aplinfo = self.handle_select(dm_appliances_sql)
            print('aplinfo:%s' % aplinfo)

        else:
            # dm_appliances_sql = "SELECT apl_id FROM `dm_appliances` WHERE `apl_city_id` = %d and 'apl_purchase_unit_id' = %d LIMIT 1"%(mercInfo[0]['merc_city_id'], 22)
            aplinfo = ({'apl_id':22},)    # 暂时留着，目前没啥用，不会到这里
        # print('aplinfo:%s'%aplinfo)


        # 获取电器型号
        amsql = "SELECT * FROM `dm_appliances_model` WHERE ( apl_id = %d and is_disable = 0 and apl_model = '%s' and flag = 0 and is_disable = 0) LIMIT 1"%(aplinfo[0]['apl_id'], order_detail['pi_num'])
        amInfo = self.handle_select(amsql)
        # print('amInfo:',amInfo)

        # 根据电器型号和城市id获取费用数据
        arsql = "SELECT * FROM `dm_appliances_rate` WHERE rate_apl_model_id = %d and rate_city_id = %d and rate_is_disable = 0 LIMIT 1"%(amInfo[0]['id'], mercInfo[0]['merc_city_id'])
        # arsql = "SELECT * FROM `dm_appliances_rate` WHERE rate_apl_model_id = %d and rate_is_disable = 0 LIMIT 1"%(amInfo[0]['id'])
        arInfo = self.handle_select(arsql)
        # print('arInfo:%s'%arInfo)

        # 组装字典
        oaData = OrderedDict()
        oaData['oa_ord_id'] = ord_id
        # // $oaData['订单ID
        # // $oaData['电器ID，用来关联电器品牌和商标
        oaData['oa_apl_id'] = aplinfo[0]['apl_id']
        # // 具体型号
        oaData['oa_model'] = order_detail['pro_model']
        # // $oaData['具体型号
        oaData['oa_num'] = order_detail['pro_num']
        oaData['oa_apl_model'] = order_detail['pi_num']   # 美的订单里没有p数
        # // $oaData['电器型号
        oaData['oa_apl_rate'] = order_detail['pi_num'].replace('P','')   # 美的订单里没有p数
        oaData['oa_rate_merc_cost'] = arInfo[0]['rate_merc_cost'] * int(order_detail['pro_num'])
        # // $oaData['商家结算费用'] = '';
        oaData['oa_rate_mast_cost'] = arInfo[0]['rate_mast_cost'] * int(order_detail['pro_num'])
        # // $oaData['师傅结算费用
        oaData['oa_rate_show_cost'] = arInfo[0]['rate_show_cost'] * int(order_detail['pro_num'])
        # // $oaData['APP端显示金额
        oaData['oa_rate_guarantee_money'] = arInfo[0]['rate_guarantee_money']
        # // $oaData['质保金
        oaData['oa_rate_evaluation_money'] = arInfo[0]['rate_evaluation_money']
        # // $oaData['满意度评价金额
        oaData['oa_rate_base_money'] = arInfo[0]['rate_base_money'] * int(order_detail['pro_num'])
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

        # 只有是安装类型才会在dm_order中设置以下参数
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
        # if order_detail['ord_type'] == 5:
        #     errorReport('test>> md_fix_order: %s'%ord_id)
        return ord_id