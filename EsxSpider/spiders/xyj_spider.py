#coding:utf-8

# python
# scrapy
import json

import scrapy
import time
from scrapy.http import Request


# 自定义
from EsxSpider.db.clean_db import CleanDb
from EsxSpider.parse_collection.xyj_parse_rule import xyj_detail_parse
from EsxSpider.tools import time_to_timestamp, current_timestamp, current_timestr
from appBot.meidi_api import get_orders
from appBot.meidi_api import receive_order
from appBot.meidi_api import login
from EsxSpider.parse_collection.meidi_parse_rule import md_detail_parse
from EsxSpider.db.md_db import MdDb
from appBot.utils import saveApiLogs, errorReport, orderTracking
from db_model.MdDb import save_account, save_md_factory, query_md_factory, save_md_factory_tm, query_md_merchant
from appBot.meidi_api import get_engineers_data


class MeiDi_spider(scrapy.Spider):

    name = 'xyj_spider'
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

    def order_detail_parse_xyj(self):
        """针对洗悦家清洁业务"""
        account_info = query_md_merchant(2)[0]  # 1是midea账号表中宏旺的id
        usename = account_info.account
        pwd = account_info.password
        cookies = login(usename, pwd)
        # 测试用17
        res_json = get_orders(cookies=cookies)  # 默认抓取已派工订单
        # print 'daijie_orders:%s'%res_json
        order_list = res_json['content']['rows']
        if order_list:
            for od in order_list:
                try:
                    if od['ORDER_ORIGIN'] != u'网点自建':  # 只有订单来源是非网点自建的才做同步
                        # 从dm_midea_factory_order查询工单号,如果查不到进行同步
                        rs = query_md_factory(od['SERVICE_ORDER_NO'])
                        if not rs:
                            print od['SERVICE_ORDER_NO']
                            # 解析原始订单数据
                            detail_item = xyj_detail_parse(od)
                            clear_db = CleanDb(od_detail=detail_item)
                            # 保存详情数据
                            order_id = clear_db.save_order_detail()  # 保存订单详情
                            print ('order_id:%s' % order_id)
                            # errorReport('success save order_detail:'+str(order_id))
                            # 保存原始工单和对应的二师兄平台的订单对应id
                            save_md_factory(od, int(order_id),usename)
                            # errorReport('xyj success save md_factory:'+od['SERVICE_ORDER_NO']+' '+time.asctime(time.localtime(time.time())))
                            # 保存日志
                            api_logs = {'client': 'media_save_orderdetail',
                                        'order_source_data': od,
                                        'order_parse_data': detail_item,
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
                    # import traceback
                    # traceback.print_exc()
                    errorReport('xyj crawl exception->' + od['SERVICE_ORDER_NO'] + ':' + str(e) + str(e.args) + time.asctime(time.localtime(time.time())))
        # 保存美的师傅的数据
        shifu_data = get_engineers_data(cookies=cookies)
        if shifu_data:
            for shifu_data in shifu_data['content']['rows']:
                save_account(shifu_data, usename)  # 保存师傅数据
        self.log('finish save shifu_data')

    def crawl_order(self,response):
        # self.order_detail_parse()
        self.order_detail_parse_xyj()

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




