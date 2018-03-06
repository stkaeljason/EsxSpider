# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


# from items import MeidiDetailItem, DmOrderItem
# from items import MeidiEngineerItem
# from db_model.db import DBSession
# from db_model.MdOrder import MdOrder
# from db_model.Order import Order
# from db_model.mdAccount import MdAccount
#
#
# class EsxspiderPipeline(object):
#
#     def open_spider(self, spider):
#         self.session = DBSession()
#
#     def process_item(self, item, spider):
#         if isinstance(item, MeidiDetailItem):
#             md_order = MdOrder(
#             ord_unit_name  = item['UNIT_NAME'],
#             ord_finish_time_  = item['FINISH_TIME_'],
#             ord_dispatch_order_time  = item['DISPATCH_ORDER_TIME'],
#
#             ord_area_num  = item['AREA_NUM'],
#
#             ord_unit_code  = item['UNIT_CODE'],
#
#             ord_service_method_code  = item['SERVICE_METHOD_CODE'],
#
#             ord_contain_ejfws  = item['CONTAIN_EJFWS'],
#
#             ord_receive_order_time  = item['RECEIVE_ORDER_TIME'],
#
#             ord_customer_level_  = item['CUSTOMER_LEVEL_'],
#
#             ord_service_sub_type_code  = item['SERVICE_SUB_TYPE_CODE'],
#
#             ord_service_type_code_ = item['SERVICE_TYPE_CODE_'],
#
#             ord_purchasing_channels = item['PURCHASING_CHANNELS'],
#
#             ord_service_customer_tel1 = item['SERVICE_CUSTOMER_TEL1'],
#
#             ord_contain_ejfws_ = item['CONTAIN_EJFWS_'],
#
#             ord_service_order_id = item['SERVICE_ORDER_ID'],
#
#             ord_pub_create_person = item['PUB_CREATE_PERSON'],
#
#             ord_receive_order_time_ = item['RECEIVE_ORDER_TIME_'],
#
#             ord_change_appoint_time = item['CHANGE_APPOINT_TIME'],
#
#             ord_unit_level = item['UNIT_LEVEL'],
#
#             ord_service_customer_address = item['SERVICE_CUSTOMER_ADDRESS'],
#
#             ord_customer_name = item['CUSTOMER_NAME'],
#
#             ord_complaint_flag_ = item['COMPLAINT_FLAG_'],
#
#             ord_service_order_status_ = item['SERVICE_ORDER_STATUS_'],
#
#             ord_contact_order_ser_item2_name = item['CONTACT_ORDER_SER_ITEM2_NAME'],
#
#             ord_purchasing_channels_ = item['PURCHASING_CHANNELS_'],
#
#             ord_branch_code = item['BRANCH_CODE'],
#
#             ord_service_type_code = item['SERVICE_TYPE_CODE'],
#
#             ord_account_statement_time = item['ACCOUNT_STATEMENT_TIME'],
#
#             ord_purchase_date = item['PURCHASE_DATE'],
#
#             ord_complaint_level_ = item['COMPLAINT_LEVEL_'],
#
#             ord_order_origin = item['ORDER_ORIGIN'],
#
#             ord_information_follow_ = item['INFORMATION_FOLLOW_'],
#
#             ord_service_sub_type_name = item['SERVICE_SUB_TYPE_NAME'],
#
#             ord_receive_order_person = item['RECEIVE_ORDER_PERSON'],
#
#             ord_information_follow = item['INFORMATION_FOLLOW'],
#
#             ord_prod_code = item['PROD_CODE'],
#
#             ord_tmp_row_no = item['TMP_ROW_NO'],
#
#             ord_service_desc = item['SERVICE_DESC'],
#
#             ord_implement_sub_type_code_ = item['IMPLEMENT_SUB_TYPE_CODE_'],
#
#             ord_prod_name = item['PROD_NAME'],
#
#             ord_pub_create_date = item['PUB_CREATE_DATE'],
#
#             ord_contact_time = item['CONTACT_TIME'],
#
#             ord_service_order_no = item['SERVICE_ORDER_NO'],
#
#             ord_order_origin_ = item['ORDER_ORIGIN_'],
#
#             ord_feedback_time_ = item['FEEDBACK_TIME_'],
#
#             ord_customer_level = item['CUSTOMER_LEVEL'],
#
#             ord_contact_time_ = item['CONTACT_TIME_'],
#
#             ord_service_customer_demand_id = item['SERVICE_CUSTOMER_DEMAND_ID'],
#
#             ord_change_appoint_time_ = item['CHANGE_APPOINT_TIME_'],
#
#             ord_implement_sub_type_code = item['IMPLEMENT_SUB_TYPE_CODE'],
#
#             ord_product_use_ = item['PRODUCT_USE_'],
#
#             ord_appoint_time = item['APPOINT_TIME'],
#
#             ord_product_use = item['PRODUCT_USE'],
#
#             ord_e_feedback_time = item['E_FEEDBACK_TIME'],
#
#             ord_finish_time = item['FINISH_TIME'],
#
#             ord_is_input_archives = item['IS_INPUT_ARCHIVES'],
#
#             ord_service_area_code = item['SERVICE_AREA_CODE'],
#
#             ord_prod_num = item['PROD_NUM'],
#
#             ord_contact_order_serv_type_name = item['CONTACT_ORDER_SERV_TYPE_NAME'],
#
#             ord_feedback_time = item['FEEDBACK_TIME'],
#
#             ord_customer_tel1 = item['CUSTOMER_TEL1'],
#
#             ord_branch_name = item['BRANCH_NAME'],
#
#             ord_implement_sub_type_name = item['IMPLEMENT_SUB_TYPE_NAME'],
#
#             ord_complaint_level = item['COMPLAINT_LEVEL'],
#
#             ord_account_statement_time_ = item['ACCOUNT_STATEMENT_TIME_'],
#
#             ord_brand_name = item['BRAND_NAME'],
#
#             ord_service_area_name = item['SERVICE_AREA_NAME'],
#
#             ord_urgent_level = item['URGENT_LEVEL'],
#
#             ord_complaint_flag = item['COMPLAINT_FLAG'],
#
#             ord_service_method_name = item['SERVICE_METHOD_NAME'],
#
#             ord_e_feedback_time_ = item['E_FEEDBACK_TIME_'],
#
#             ord_intf_order_code = item['INTF_ORDER_CODE'],
#
#             ord_dispatch_order_time_ = item['DISPATCH_ORDER_TIME_'],
#
#             ord_purchase_date_ = item['PURCHASE_DATE_'],
#
#             ord_customer_area_code = item['CUSTOMER_AREA_CODE'],
#
#             ord_service_customer_name = item['SERVICE_CUSTOMER_NAME'],
#
#             ord_service_order_status = item['SERVICE_ORDER_STATUS'],
#
#             ord_urgent_level_ = item['URGENT_LEVEL_'])
#             self.session.add(md_order)
#             self.session.commit()
#             return item
#         if isinstance(item, MeidiEngineerItem):
#             md_account = MdAccount(
#             aux_id = item['aux_id'],
#             serviceOrderNo = item['serviceOrderNo'],
#             serviceUserDemandIds = item['serviceUserDemandIds'],
#             engineerId = item['engineerId'],
#             engineerCode = item['engineerCode'],
#             engineerLevel = item['engineerLevel'],
#             engineerTel = item['engineerTel'],
#             engineerName = item['engineerName'],
#             workNo = item['workNo'],
#             unitCode = item['unitCode'],
#             # reassignmentReason = item['reassignmentReason'],
#             # operator = item['operator'],
#             # operateTime = item['operateTime'],
#             # page = item['page'],
#             # pageIndex = item['pageIndex'],
#             # pageSize = item['pageSize'],
#             # rows = item['rows'],
#             # count = item['count'],
#             # mapInfo = item['mapInfo'],
#                     )
#             self.session.add(md_account)
#             self.session.commit()
#             return item
#         # if isinstance(DmOrderItem):
#         #     order = Order(
#         #         ord_install_id = item['ord_install_id'],
#         #         ord_merc_cost = item['ord_merc_cost'],
#         #         ord_status = item['ord_status'],
#         #         ord_is_back = item['ord_is_back'],
#         #         ord_merc_id = item['ord_merc_id'],
#         #         ord_mast_id = item['ord_mast_id'],
#         #         ord_cust_name = item['ord_cust_name'],
#         #         ord_cust_sex = item['ord_cust_sex'],
#         #         ord_cust_tel = item['ord_cust_tel'],
#         #         ord_cust_addr = item['ord_cust_addr'],
#         #         ord_province = item['ord_province'],
#         #         ord_city = item['ord_city'],
#         #         ord_district = item['ord_district'],
#         #         ord_remark = item['ord_remark'],
#         #         ord_num = item['ord_num'],
#         #         ord_weixin_num = item['ord_weixin_num'],
#         #         ord_cust_told = item['ord_cust_told'],
#         #         ord_mast_cost = item['ord_mast_cost'],
#         #         ord_cust_lat = item['ord_cust_lat'],
#         #         ord_cust_lng = item['ord_cust_lng'],
#         #         ord_purchase_unit = item['ord_purchase_unit'],
#         #         ord_purchase_unit_id = item['ord_purchase_unit_id'],
#         #         ord_type = item['ord_type'],
#         #         ord_partner_id = item['ord_partner_id'],
#         #         ord_is_hide = item['ord_is_hide'],
#         #     )
#         #     self.session.add(order)
#         #     self.session.commit()
#
#     def close_spider(self,spider):
#         self.session.close()
