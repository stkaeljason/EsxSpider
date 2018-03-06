#coding:utf-8

import json
import scrapy
from collections import OrderedDict

import time
# from EsxSpider.items import AuxFactoryItem, ShiFuItem
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from EsxSpider.db.aux_db import AuxDb
from EsxSpider.settings import daijie_data
from EsxSpider.tools import time_to_timestamp, current_timestamp, get_latlng, create_sn, intercept_qu, \
    time_to_timestamp3, current_timestr
import appBot.utils as utils


class Aux_spider(scrapy.Spider):
    name = 'man_spider'
    start_urls = ['']
    aux_db = AuxDb()
    # 接口url
    login_url = 'http://aux.bangjia.me/index.php/Public/login.html'  # 登陆url
    website_jiedai = 'http://aux.bangjia.me/index.php/auxtest/gridIndex'  # 待接单url
    shifu_url = 'http://aux.bangjia.me/index.php/Auxtest/index.html'  # 师傅信息url
    jjshifu_url = 'http://aux.bangjia.me/index.php/Member/masterlist.html'
    accept_oder_url = 'http://aux.bangjia.me/index.php/Auxtest/providerReceiptOrder.html'  # 接单接口url
    dispatch_url = 'http://aux.bangjia.me/index.php/Auxtest/dispatchorder.html'  # 派单url

    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT5.1;zh-CN;rv:1.9.1.5)Gecko/20091102Firefox/3.5.5',
        'Host': 'aux.bangjia.me',
    }


    def start_requests(self):
        # 测试错误处理
        # err_url = "http://www.httpbin.org/status/404"
        # return [Request(err_url, meta={'cookiejar': 1}, callback=self.login, errback=self.report_errror)]
        # # 兴科御
        # account_list = [{'username':'aux028307','password':'ZC2017','platform_id':1}]
        # 聚杰
        # account_list = [{'username': 'aux028327', 'password': '123456', 'platform_id': 91}]

        # 威远
        account_list = [{'username': 'aux832155', 'password': '123456', 'platform_id': 92}]
        for account in account_list:
            yield Request(self.login_url, meta={'cookiejar': account['username'], 'account_info':account}, callback=self.login, errback=self.report_errror,dont_filter=True)

    def login(self, response):
        """登录处理函数"""
        # print(response.body)
        return [
                FormRequest.from_response(response,
                                          meta={'cookiejar': response.meta['cookiejar'], 'account_info':response.meta['account_info']},
                                          headers=self.headers,  # 注意此处的headers
                                          formdata={
                                              'username': response.meta['account_info']['username'],
                                              'password': response.meta['account_info']['password'],
                                              'event_submit_do_login': 'submit',
                                              'submit-btn': '登录'
                                          },
                                          callback=self.after_login,
                                          errback=self.report_errror,
                                          dont_filter=True
                                          )
                ]

    def after_login(self, response):
        """在登录成功后构建所需的任务，即构建数据的接口任务并配置对应的解析方法"""
        # 测试用详情提取，之后注释或者删除
        test_url = 'http://aux.bangjia.me/index.php/Auxtest/detail/orderno/2018011793286729938606'
        yield Request(test_url, meta={'cookiejar':response.meta['cookiejar'],'account_info': response.meta['account_info']},
                      callback=self.order_detail_parse,
                      dont_filter=True
                      )
        # 构造待接单请求
        # yield FormRequest(url=self.website_jiedai,
        #               meta={'cookiejar':response.meta['cookiejar'],
        #                     'account_info': response.meta['account_info']},
        #               formdata=daijie_data,
        #               callback=self.work_order_parse,
        #               errback=self.report_errror,
        #               dont_filter=True)
        # # 构造师傅数据请求
        # yield Request(self.jjshifu_url, meta={'cookiejar':response.meta['cookiejar'],'account_info': response.meta['account_info']}, callback=self.master_parse, dont_filter=True, errback=self.report_errror)

    def work_order_parse(self, response):
        """"工单详情数据提取入口函数"""
        # print(response.body)
        res_data = json.loads(response.body)
        work_orders = [row['factorynumber'] for row in res_data['rows']]  # 获得所有工单号
        print('work_orders:',work_orders)
        # print response.meta['cookiejar']
        for order in work_orders:
            if order[0] != '3':                     # 订单以3开头不做任何处理
                # self.aux_db.save_work_order(order)  # 保存工单号
                # utils.errorReport('aux success get work_order:%s'%order+time.asctime(time.localtime(time.time())))
                # 对每个工单进行接单post请求, 接单
                print('factorynumber:%s'%order)
                return FormRequest(self.accept_oder_url,
                                  meta={'cookiejar':response.meta['cookiejar'],'account_info': response.meta['account_info']},
                                  headers=self.headers,
                                  formdata={
                                                  'factorynumber': order
                                              },
                                  callback=self.order_detail_request,
                                  errback=self.report_errror)

    def order_detail_request(self, response):
        # print("jiedan_response:%s"%response.body)
        res_data = json.loads(response.body)
        # print("jiedan_res:%s"%res_data)
        if res_data['ret'] == 1:
            order_no = res_data['orderno']  # 根据接单的post响应数据获得订单号
            order_detail_url = 'http://aux.bangjia.me/index.php/Auxtest/detail/orderno/' + str(order_no)
            return Request(order_detail_url, meta={'cookiejar':response.meta['cookiejar'],
                                                  'order_no':order_no,'account_info': response.meta['account_info']},
                          callback=self.order_detail_parse,
                          errback=self.report_errror)

    def order_detail_parse(self, response):
        """在订单详情页提取订单详情数据"""
        order_detail = OrderedDict()
        try:
            work_order_info = u"工单信息"
            cust_info = u"客户信息"
            service_post = u"服务请求"
            product_info = u"产品信息"

            selector = Selector(response)
            # 顾客姓名
            order_detail['ord_cust_name'] = self.new_selector(selector,'//input[@class="detail-data-form customerName"]/@value')
            # print('ord_cust_name:%s'%order_detail['ord_cust_name'])

            # 以下为dm_order所需数据
            # 拼接电话
            # print(self.new_selector(selector,'//div[@title="%s"]'%work_order_info))
            laidian_num = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[2]/input/@value'%work_order_info)
            print('laidian_numxxx:%s'%laidian_num)
            # laidian_num = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[2]/input/@value'%work_order_info)
            mobile_phone = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[6]/input/@value'%cust_info)
            print('mobile_phone:%s'%mobile_phone)
            order_detail['ord_cust_tel'] = laidian_num
            print('ord_cust_tel:%s'%order_detail['ord_cust_tel'])

            # 拼接具体用户地址
            town = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[4]/select[4]/option[@selected="selected"]/text()'%(cust_info))
            addr_detail = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[2]/input/@value'%(cust_info))
            distrct = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[4]/select[3]/option[@selected="selected"]/text()'%(cust_info))
            if distrct in addr_detail:
                ord_cust_addr = intercept_qu(addr_detail)
            elif town in addr_detail:
                ord_cust_addr = addr_detail.replace(town,'')
            else:
                ord_cust_addr = addr_detail
            order_detail['ord_cust_addr'] = ord_cust_addr
            # print('ord_cust_addr:%s'%order_detail['ord_cust_addr'])
            # 客户省市区
            order_detail['ord_province'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[4]/select[1]/option[@selected="selected"]/text()'%(cust_info))
            order_detail['ord_city'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[4]/select[2]/option[@selected="selected"]/text()'%(cust_info))
            order_detail['ord_district'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[4]/select[3]/option[@selected="selected"]/text()'%(cust_info))
            order_detail['ord_street'] = town
            # print order_detail['ord_street']

            # 服务描述
            order_detail['ord_remark'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[2]/textarea/text()'%service_post)
            # print('ord_remark:%s'%order_detail['ord_remark'])
            # 订单号
            order_detail['ord_num'] = create_sn()  # 利用东哥算法计算
            print("ord_num:%s"%order_detail['ord_num'])
            # 微信支付号
            order_detail['ord_pay_num'] = create_sn() # 利用东哥算法计算
            print("ord_pay_num:%s"%order_detail['ord_pay_num'])
            # 联合地址
            order_detail['ord_grab_addr'] = order_detail['ord_province'] + order_detail['ord_city'] + order_detail['ord_district'] + order_detail['ord_cust_addr']
            # print('ord_grab_addr:%s'%order_detail['ord_grab_addr'])
            # 服务描述
            order_detail['ord_cust_fault'] = order_detail['ord_remark']
            # 工单号
            order_detail['ord_accept_no'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[4]/input/@value'%work_order_info)
            print('ord_accept_no:%s'%order_detail['ord_accept_no'])
            # 要求服务时间
            ymd_time = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[2]/input[1]/@value'%service_post)

            # print(ymd_time)
            ymd_time_timestamps = time_to_timestamp(ymd_time)
            # ap_time = self.new_selector(selector,'//div[@title="请求"]/table/tbody/tr[3]/td[2]/input[2]/@value')
            order_detail['ord_ask_time'] = ymd_time_timestamps
            # print('ord_ask_time:%s'%order_detail['ord_ask_time'])
            # 当前时间戳
            order_detail['ord_create_time'] = current_timestamp()
            print('ord_create_time:%s'%order_detail['ord_create_time'])
            # 购买时间，存时间戳格式
            buy_time = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[2]/input/@value'%product_info)
            order_detail['ord_buy_time'] = time_to_timestamp(buy_time)
            print('ord_buy_time:%s'%order_detail['ord_buy_time'])
            # 经纬度
            # if u"区" in addr_detail:
            #     point_index = addr_detail.index(u'区')
            #     addr_detail = addr_detail[point_index+1:]
            order_detail['ord_cust_lng'], order_detail['ord_cust_lat'] = get_latlng(order_detail['ord_city'], order_detail['ord_cust_addr'])
            # print('ord_cust_lng:%s'%order_detail['ord_cust_lng'])

            order_detail['ord_weixin_num'] = '';
            order_detail['ord_merc_id'] = response.meta['account_info']['platform_id']  # 根据登录的账号商家决定
            print('ord_merc_id:%s'%order_detail['ord_merc_id'])
            order_detail['ord_purchase_unit'] = u'厂派'
            order_detail['ord_purchase_unit_id'] = 0
            order_detail['ord_status'] = 0
            order_detail['ord_need_build'] = 2#//不用建单
            order_detail['ord_type'] = 1
            # 销售单位，购买单位
            order_detail['ord_sale_unit'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[6]/input/@value'%(product_info))
            # 接件时间，受理日期
            order_detail['ord_accept_time'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[4]/input/@value'%service_post)
            order_detail['ord_accept_time'] = time_to_timestamp3(order_detail['ord_accept_time'])
            # order_detail['ord_show_cost'] = 0.0
            # 服务原因
            order_detail['service_reason'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[2]/select[1]/option[@selected="selected"]/text()'%work_order_info)

            if order_detail['service_reason'] == u'维修':
                if u'移机' in order_detail['ord_remark']:
                    order_detail['ord_type'] = 3
                else:
                    order_detail['ord_type'] = 5
            print 'ord_type:%s'%order_detail['ord_type']

            # 解析渠道,不会立即插入dm_order,这些渠道名称根据dm_merchant_purchase_unit获得
            if order_detail['ord_merc_id'] == 91:     # 聚杰因为没有厂家系统，京东其他渠道的配置，所以区别对待
                order_detail['qudao'] = u'天猫'
            elif u'京东' in order_detail['ord_sale_unit']:
                order_detail['qudao'] = u'京东'
            elif u'京.东' in order_detail['ord_sale_unit']:
                order_detail['qudao'] = u'京东'
            elif u'天猫' in order_detail['ord_sale_unit']:
                order_detail['qudao'] = u'天猫'
            elif u'国美' in order_detail['ord_sale_unit']:
                order_detail['qudao'] = u'国美'
            else:
                order_detail['qudao'] = u'厂家系统'



            # 下面为dm_order 暂时不需要数据
            # 以下工单信息
            # 进展查询码
            order_detail['ord_check_num'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[6]/input/@value'%work_order_info)
            # 工单途径
            order_detail['ord_way'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[8]/input/@value'%work_order_info)
            # # 服务原因
            # order_detail['service_reason'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[2]/select[1]/option[@selected="selected"]/text()'%work_order_info)
            # 投诉原因
            order_detail['complaint_reason'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[4]/select[1]/option[@selected="selected"]/text()'%work_order_info)
            # 处理类别
            order_detail['deal_category'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[6]/select[1]/option[@selected="selected"]/text()'%work_order_info)
            # 指令人
            order_detail['zhilin_ren'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[8]/input/@value'%work_order_info)
            # 工程单
            order_detail['eng_form'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[2]/span/text()'%work_order_info)
            # 处理级别
            order_detail['deal_level'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[4]/select[1]/option[@selected="selected"]/text()'%work_order_info)
            # 历史工单数
            order_detail['work_num_history'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[6]/select[1]/option[@selected="selected"]/text()'%work_order_info)
            # 重电次数
            order_detail['call_repeat_num'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[8]/input/@value'%work_order_info)
            # 工单类型
            order_detail['work_order_category'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[4]/td[2]/select[1]/option[@selected="selected"]/text()'%work_order_info)
            # 处理阶段
            order_detail['deal_stage'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[4]/td[4]/select[1]/option[@selected="selected"]/text()'%work_order_info)
            # 处理状态
            order_detail['deal_status'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[4]/td[6]/select[1]/option[@selected="selected"]/text()'%work_order_info)
            # 督办
            order_detail['duban'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[4]/td[8]/span/text()'%work_order_info)
            # 督办日期
            order_detail['duban_date'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[5]/td[2]/input/@value'%work_order_info)
            # 退单次数
            order_detail['return_num'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[5]/td[4]/input/@value'%work_order_info)
            # 服务时长
            order_detail['service_time_length'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[5]/td[6]/input/@value'%work_order_info)
            # 承诺时间
            order_detail['commit_time'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[5]/td[8]/input/@value'%work_order_info)
            # 做出承诺人
            order_detail['commit_person'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[6]/td[2]/input/@value'%work_order_info)
            # 做出承诺时间
            order_detail['do_commit_time'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[6]/td[4]/input/@value'%work_order_info)
            # 废单次数
            order_detail['discard_order_num'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[6]/td[6]/input/@value'%work_order_info)
            # 处理工程师
            order_detail['engineer'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[6]/td[8]/input/@value'%work_order_info)

            # 以下服务请求
            # 故障树方案
            order_detail['guzhang_'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[4]/textarea/text()'%service_post)
            # 空调台数
            order_detail['condition_num'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[2]/input/@value'%service_post)
            # 受理日期
            # order_detail['accepted_date'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[4]/input/@value'%service_post)
            # 服务项目
            order_detail['service_project'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[6]/input/@value'%service_post)
            # 上门预约日期
            ymr_yuyue = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[4]/input/@value'%service_post)
            # sfm_yuyue = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[4]/select[1]/option[@selected="selected"]/text()'%service_post)
            order_detail['yuyue_date'] = time_to_timestamp(ymr_yuyue)

            # 以下客户信息
            # 家庭电话
            order_detail['family_phone'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[2]/input/@value'%(cust_info))
            # 办公电话
            order_detail['office_phone'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[4]/input/@value'%(cust_info))
            # 移动电话
            order_detail['mobile_phone'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[6]/input/@value'%(cust_info))
            # 电话区号
            order_detail['quhao'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[4]/td[2]/input/@value'%(cust_info))
            # 微信账号
            order_detail['weixin_account'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[4]/td[4]/input/@value'%(cust_info))
            # 是否延保金用户
            order_detail['is_yanbao_account'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[5]/td[2]/span/text()'%(cust_info))
            # 延保卡号
            order_detail['yanbao_cardno'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[5]/td[4]/input/@value'%(cust_info))
            # 延保金卡地址
            order_detail['yanbao_card_addr'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[5]/td[6]/input/@value'%(cust_info))
            # 保养卡号
            order_detail['baoyang_cardno'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[5]/td[8]/input/@value'%(cust_info))

            # 以下产品信息
            # 品牌
            order_detail['brand'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[2]/select[1]/option[@selected="selected"]/text()'%(product_info))
            # 产品大类
            order_detail['product_category'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[4]/select[1]/option[@selected="selected"]/text()'%(product_info))
            # 整机型号
            order_detail['machine_model'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[6]/select[1]/option[@selected="selected"]/text()'%(product_info))
            # 整机型编号
            order_detail['machine_num'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[1]/td[8]/select[1]/option[@selected="selected"]/text()'%(product_info))
            # 是否延保
            order_detail['is_yanbao'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[4]/span/text()'%(product_info))
            # 延保年限
            order_detail['yanbao_year'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[6]/input/@value'%(product_info))
            # 匹数
            order_detail['pi_num'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[2]/td[8]/select[1]/option[@selected="selected"]/text()'%(product_info))
            # 内机编号
            order_detail['neiji_num'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[2]/input/@value'%(product_info))
            # 外机编号
            order_detail['waiji_num'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[4]/input/@value'%(product_info))
            # 购买单位
            # order_detail['buy_unit'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[6]/input/@value'%(product_info))
            # 安装单位
            order_detail['anzhuang_unit'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[3]/td[8]/input/@value'%(product_info))
            # 维修单位
            order_detail['weixiu_unit'] = self.new_selector(selector,'//div[@title="%s"]/table/tr[4]/td[2]/input/@value'%(product_info))

            # 保存订单详情数据
            # print(order_detail)
            if not order_detail['ord_accept_no']:
                utils.errorReport('aux_exption->parse order_detail fail' + ':' + time.asctime(time.localtime(time.time())))
            order_id = self.aux_db.save_order_detail(order_detail)
            print 'order_id:%s'%order_id
            # 保存工单和订单插入id的映射关系
            print 'ord_accept_no:%s' % order_detail['ord_accept_no']
            self.aux_db.save_auxfactory(order_detail['ord_accept_no'],order_id,current_timestamp(),order_detail['ord_type'],response.meta['account_info']['username'])
            # utils.errorReport('aux->success save order_detail:%s'%order_detail['ord_accept_no']+' '+response.meta['account_info']['username']+' '+time.asctime(time.localtime(time.time())))
            # 保存日志
            api_logs = {'client':'media_save_orderdetail',
                                        'order_source_data':response.body,
                                        'order_parse_data':order_detail,
                                        'order_id':order_id,
                                        'time':time.time()
                                        }
            utils.saveApiLogs(api_logs)
            track_time = current_timestamp()
            track_desc = u"系统在{}从奥克斯同步了订单".format(current_timestr())
            utils.orderTracking(order_id, 1, 'system', u'同步', track_desc, track_time)

        except Exception as e:
            import traceback
            traceback.print_exc()
            # print('aux_exption-->>'+str(e))
            # utils.errorReport('aux_exption->'+order_detail['ord_accept_no']+':'+str(e)+str(e.args)+time.asctime(time.localtime(time.time())))

    # def worker_acount_parse(self, response):
    #     """师傅账号数据提取函数"""
    #     item = {}
    #     selector = Selector(response)
    #     shifus = selector.xpath('//tbody[@id="record"]/tr')
    #     for master in shifus:
    #         item['user_id'] = master.xpath('.//td[1]/input/@value').extract()[0]
    #         # print 'user_id:%s'%item['user_id']
    #         item['name'] = master.xpath('.//td[2]/text()').extract()[0]
    #         # print(item['name'])
    #         item['aux_num'] = master.xpath('.//td[3]/text()').extract()[0]
    #         item['phone'] = master.xpath('.//td[4]/text()').extract()[0]
    #         item['num'] = master.xpath('.//td[5]/text()').extract()[0]
    #         self.aux_db.save_shifu(item)   # 保存师傅数据
    #         # self.save_spider_log(response, repr(item))

    def master_parse(self, response):
        item = {}
        selector = Selector(response)
        shifus = selector.xpath('//table[@class="table table-hover"]/tbody/tr')
        for master in shifus:
            item['aux_merc_account'] = response.meta['account_info']['username']
            item['password'] = response.meta['account_info']['password']
            item['aux_id_number'] = master.xpath('.//td[12]/a[1]/@data').extract()[0]
            item['aux_name'] = master.xpath('.//td[2]/text()').extract()[0]
            item['aux_serial_number'] = master.xpath('.//td[1]/text()').extract()[0]
            item['aux_phone'] = master.xpath('.//td[3]/text()').extract()[0]
            item['aux_archives_number'] = item['aux_serial_number'].replace('aux','')
            item['is_use'] = master.xpath('.//td[9]/div/@class').extract()[0]
            item['aux_add_time'] = current_timestamp()
            item['token'] = ''
            print item
            self.aux_db.save_master(item)





    def new_selector(self, sel, xpath_str):
        '''封装selcetor,xpath为空情况进行统一处理'''
        r = sel.xpath(xpath_str).extract()
        if r:
            return r[0]
        else:
            return ''

    def report_errror(self, failure):
        utils.errorReport('aux_crawl:'+repr(failure.value)+':'+repr(failure.value.response))
        # print("failure:%s"%repr(failure))
        # print("failure:%s"%(repr(failure.value)+':'+repr(failure.value.response)))

    # def save_spider_log(self,response,spider_data):
    #     api_logs = {'client':'aux_spider',
		# 		'method':response.request.method,
		# 		'url':response.url,
		# 		'status_code':response.status,
		# 		'request_headers':response.headers,
		# 		'request_data':response.request.body,  # 暂时设置为取body
		# 		'response_headers':response.headers,
		# 		'response_data':spider_data,
		# 		'user_id':'system',#system
		# 		'date':time.time()}
    #     # print('api_logs:',api_logs)
    #     utils.saveApiLogs(api_logs)

