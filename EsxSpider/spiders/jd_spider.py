# -*- coding: utf-8 -*-

# python
import json
import time

# 第三方
import scrapy
from scrapy.http import Request

# 自定义
import appBot.jd_api as jp
from EsxSpider.db.jd_db import JdDb
from EsxSpider.parse_collection.jd_parse_rule import detail_parse, parse_static_data
# from EsxSpider.test import test_jd_datas
from EsxSpider.tools import time_to_timestamp, current_timestamp, current_timestr
from appBot.utils import saveApiLogs, errorReport, orderTracking
from db_model.JdDb import save_factory, save_account, query_factory, query_jd_ordid, query_jd_merchant



# from EsxSpider.test import test_jd_datas

class Jd_spider(scrapy.Spider):

    name = 'jd_spider'
    order_source = u'京东'
    login_page_url = 'https://passport.jd.com/uc/login?ReturnUrl=http%3A%2F%2Fjdfw.jd.com%2F'  # 登陆页url
    spider_db = JdDb()

    def start_requests(self):

        # return [Request(self.login_page_url, meta={'cookiejar': 1}, callback=self.order_detail_parse)]
        return [Request(self.login_page_url, meta={'cookiejar': 1}, callback=self.get_accout)]

    def get_accout(self,response):
        merchant_info = query_jd_merchant()
        # account_list = [{'username': merchant.account, 'password': merchant.password, 'platform_id': merchant.platform_id} for merchant in merchant_info]
        merchant_list = [merchant for merchant in merchant_info]

        for merchant in merchant_list:
            print('merchant.account:',merchant.account)
            self.order_detail_parse(merchant)
    # 新版
    def order_detail_parse(self,merchant):
        """在订单详情页提取订单详情数据"""
        jd_login = jp.JdLogin(merchant)
        cookies = jd_login.login()
        res_json = jp.quest_orders(cookies=cookies,merchant=merchant)  # 默认抓取已预约订单
        order_list = res_json['rows']
        # print('order_list',order_list)
        if order_list:
            for od in order_list:
                print '*' * 20 + str(od['orderno'])+'_start_' + '*' * 20
                try:
                    # 解析原始订单数据
                    static_data = parse_static_data(od['ordernoSecret'], cookies)
                    print 'orderno:%s' % od['orderno']
                    # 非送装一体的工单才同步
                    if not static_data['is_ins_join_send']:
                        # 查询factory表，查询为空才同步
                        is_exist_factory = query_factory(od['orderno'])
                        if not is_exist_factory:
                            is_exist_jd_ordid = query_jd_ordid(od['orderId'])
                            detail_item = detail_parse(od, static_data,merchant)

                            # 保存详情数据
                            spider_db = JdDb(od_detail=detail_item)
                            if not is_exist_jd_ordid:
                                # 同步订单，dm_order和apl表插入数据
                                order_id = spider_db.new_save_order_detail()  # 保存订单详情
                                # errorReport('success save order_detail:'+str(order_id))
                                # 保存原始工单和对应的二师兄平台的订单对应id
                                track_time = current_timestamp()
                                track_desc = u"系统在{}从{}同步了订单".format(current_timestr(), self.order_source)
                                orderTracking(order_id, 1, 'system', u'同步', track_desc, track_time)
                                print 'finish add order:%s'%order_id
                            if is_exist_jd_ordid:
                                # 更新订单，更新dm_order和apl
                                order_id = is_exist_jd_ordid[0]
                                spider_db.update_order_detail(order_id)
                                track_time = current_timestamp()
                                track_desc = u"系统在{}修改了订单".format(current_timestr())
                                orderTracking(order_id, 1, 'system', u'改单', track_desc, track_time)
                                print 'finish update order:%s'%order_id

                            # 保存factory信息
                            print('order_id:%s' % order_id)
                            save_factory(od, int(order_id), static_data)
                            # report_message = '%s->success save:' % self.name + str(
                            #     od['orderno']) + ' ' + od['orderId']+' '+time.asctime(time.localtime(time.time()))
                            # errorReport(report_message)
                            # 保存日志

                            print '*' * 20 + str(od['orderno'])+'_success_' + '*' * 20
                            api_logs = {'client': self.name,
                                        'order_source_data': od,
                                        'order_parse_data': detail_item,
                                        'order_id': order_id,
                                        'time': time.time()
                                        }
                            saveApiLogs(api_logs)

                            # print('finish order crawl:%s' % order_id)
                            # 增加跟单记录


                except Exception as e:
                    # import traceback
                    # traceback.print_exc()
                    errorReport('%s exception->' % self.name + str(od['orderno']) + ':' + str(e) + str(
                        e.args) + time.asctime(time.localtime(time.time())))

        # 保存师傅的数据
        shifu_datas = jp.get_engineers(cookies=cookies,merchant=merchant)
        if shifu_datas:
            for shifu_data in shifu_datas['rows']:
                save_account(shifu_data)  # 保存师傅数据
        print ('finish save shifu_data')