#coding:utf-8

# python
# scrapy
import json

import scrapy
import time
from scrapy.http import Request


# 自定义
from EsxSpider.tools import time_to_timestamp, current_timestamp, current_timestr
from appBot.meidi_api import get_orders
# from appBot.meidi_api import receive_order
from appBot.meidi_api import login
from EsxSpider.parse_collection.meidi_parse_rule import md_detail_parse
from EsxSpider.db.md_db import MdDb
from appBot.utils import saveApiLogs, errorReport, orderTracking
from db_model.MdDb import save_account, save_md_factory, query_md_factory, save_md_factory_tm, query_md_merchant,query_md_merchant_active
from appBot.meidi_api import get_engineers_data


class MeiDi_spider(scrapy.Spider):

    name = 'midea_spider'
    factory_name = 'Midea'
    # 接口url
    login_page_url = 'https://cs.midea.com/c-css/login'  # 登陆页url
    login_url = 'https://cs.midea.com/c-css/signin'      # 登陆api
    captcha_url = 'https://cs.midea.com/c-css/captcha'
    order_daijie_url = 'https://cs.midea.com/c-css/wom/serviceorderunit/listdata'  # 待接单url
    order_detail_url = ''
    shifu_url = ''  # 师傅信息url
    accept_oder_url = ''  # 接单接口url
    md_db = MdDb()

    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'cs.midea.com',
        'X-Requested-With':'XMLHttpRequest'
    }

    def start_requests(self):

        return [Request(self.login_page_url, meta={'cookiejar': 1}, callback=self.crawl_order, errback=self.report_errror)]

    def order_detail_parse_fortianmao(self,cookies):
        res_json = get_orders(cookies=cookies, order_status='14')  #   已接单以后开始
        # print 'daijie_orders:%s'%res_json
        order_list = res_json['content']['rows']
        if order_list:
            for od in order_list[:1]:
                print 'tianmao :%s'%od['SERVICE_ORDER_NO']
                try:
                    if od['ORDER_ORIGIN'] == u'天猫接入':  # 只有订单来源是非网点自建的才做同步
                        rs = query_md_factory(od['SERVICE_ORDER_NO'])
                        if not rs:
                            # 解析原始订单数据
                            meidi_detail_item = md_detail_parse(od)
                            # 保存详情数据
                            order_id = self.md_db.save_order_detail(meidi_detail_item)  # 保存订单详情
                            self.log('order_id:%s' % order_id)
                            # 保存原始工单和对应的二师兄平台的订单对应id
                            save_md_factory_tm(od, int(order_id))
                            # errorReport('success save md_factory:' + od['SERVICE_ORDER_NO'] + ' ' + time.asctime(
                            #     time.localtime(time.time())))
                            # 保存日志
                            api_logs = {'client': 'media_save_orderdetail',
                                        'order_source_data': od,
                                        'order_parse_data': meidi_detail_item,
                                        'order_id': order_id,
                                        'time': time.time()
                                        }
                            saveApiLogs(api_logs)

                            self.log('finish order crawl:%s' % order_id)
                            # 增加跟单记录
                            track_time = current_timestamp()
                            track_desc = u"系统在{}从美的同步了订单".format(current_timestr())
                            orderTracking(order_id, 1, 'system', u'同步', track_desc, track_time)

                except Exception as e:
                    errorReport(
                        'media tianmao crawl exception->' + od['SERVICE_ORDER_NO'] + ':' + str(e) + str(e.args) + time.asctime(
                            time.localtime(time.time())))


    def order_detail_parse(self,merchant):
        """在订单详情页提取订单详情数据"""
        # 从数据库获取账号信息
        # account_info = query_md_merchant(1)[0]       # 1是midea账号表中宏旺的id
        #
        # usename = account_info.account
        # pwd = account_info.password
        usename = merchant.account
        pwd = merchant.password
        # 登录获取订单
        cookies = login(usename,pwd)
        self.order_detail_parse_fortianmao(cookies)
        res_json = get_orders(cookies=cookies)      # 默认抓取已派工订单
        # print 'daijie_orders:%s'%res_json
        order_list =res_json['content']['rows']
        if order_list:
            for od in order_list:
                try:
                    if od['ORDER_ORIGIN'] != u'网点自建':  # 只有订单来源是非网点自建的才做同步
                        print '*'*20+od['SERVICE_ORDER_NO']+'*'*20

                        # r = receive_order(od['SERVICE_ORDER_ID'], od['UNIT_CODE'], cookies=cookies)  # 对待接单订单进行接单
                        # # r=True
                        # if r:
                        # 从dm_midea_factory_order查询工单号,如果查不到进行同步
                        rs = query_md_factory(od['SERVICE_ORDER_NO'])
                        print 'success query rs:%s'%od['SERVICE_ORDER_NO']
                        if not rs:
                            # 解析原始订单数据
                            meidi_detail_item = md_detail_parse(od,merchant)
                            print 'success parse order:%s'%od['SERVICE_ORDER_NO']
                            # 保存详情数据
                            order_id = self.md_db.save_order_detail(meidi_detail_item)  # 保存订单详情
                            print('success save order_id:%s'%order_id)
                            # errorReport('success save order_detail:'+str(order_id))
                            # 保存原始工单和对应的二师兄平台的订单对应id
                            save_md_factory(od, int(order_id),usename)
                            print('success save md_factory:%s'%od['SERVICE_ORDER_NO'])
                            # errorReport('success save md_factory:'+od['SERVICE_ORDER_NO']+' '+time.asctime(time.localtime(time.time())))
                            print('*' * 20+ od['SERVICE_ORDER_NO'] + '*' * 20)
                            # 保存日志
                            api_logs = {'client':'media_save_orderdetail',
                                        'order_source_data':od,
                                        'order_parse_data':meidi_detail_item,
                                        'order_id':order_id,
                                        'time':time.time()
                                        }
                            saveApiLogs(api_logs)
                            # print('success save apilogs:%s'%od['SERVICE_ORDER_NO'])
                            # 增加跟单记录
                            track_time = current_timestamp()
                            track_desc = u"系统在{}从美的同步了订单".format(current_timestr())
                            orderTracking(order_id, 1, 'system',u'同步',track_desc,track_time)

                except Exception as e:
                    # import traceback
                    # traceback.print_exc()
                    errorReport('media crawl exception->'+od['SERVICE_ORDER_NO']+':'+str(e)+str(e.args)+time.asctime(time.localtime(time.time())))

        # 保存美的师傅的数据
        shifu_data = get_engineers_data(cookies=cookies)
        if shifu_data:
            for shifu_data in shifu_data['content']['rows']:
                save_account(shifu_data, usename)  # 保存师傅数据
        self.log('finish save shifu_data')

    def crawl_order(self,response):
        merchant_info = query_md_merchant_active()
        merchant_list = [merchant for merchant in merchant_info]
        # print(merchant_list)
        for merchant in merchant_list:
            self.order_detail_parse(merchant)
        # self.order_detail_parse()

    def new_selector(self, sel, xpath_str):
        '''封装selcetor,xpath为空情况进行统一处理'''
        r = sel.xpath(xpath_str).extract()
        if r:
            return r[0]
        else:
            return ''

    def report_errror(self):
        pass

    def save_spider_log(self,response,spider_data):
        api_logs = {'client':'md_spider',
				'method':response.request.method,
				'url':response.url,
				'status_code':response.status,
				'request_headers':response.headers,
				'request_data':response.request.body,  # 暂时设置为取body
				'response_headers':response.headers,
				'response_data':spider_data,
				'user_id':'system',#system
				'date':time.time()}
        # print('api_logs:',api_logs)
        saveApiLogs(api_logs)




