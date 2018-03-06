# coding: utf8
import requests
import json
import demjson
import utils
import time
import datetime
import Queue
import threading
import sys
import os
import pickle
from sqlalchemy.sql import text
from db_model.AuxFactoryOrder import AuxFactoryOrder
from db_model.OrderRepair import OrderRepair
from db_model.AuxMerchant import AuxMerchant
from db_model.OrderTracking import OrderTracking
from sqlalchemy.orm import aliased
from db_model.Order import Order
from db_model.OrderCode import OrderCode
from db_model.Auxcssamt import Auxcssamt
from db_model import db


class Auxcss:
    """Auxcss systerm api by Jon"""

    def __init__(self):
        self.system_name = "Auxcss Bot"
        self.index_url = u'http://www.auxcss.com/auxcss/index.jsp'
        self.login_url = u'http://www.auxcss.com/auxcss/platform/style/skyblue/jsp/loginHandle.jsp'
        self.logout_url = u'http://www.auxcss.com/auxcss/platform/style/skyblue/jsp/logoutHandle.jsp'
        self.doSearchQuery_url = u'http://www.auxcss.com/auxcss/st/servsettle/stssd/StssdRia.do?method=doSearchByConditionAll'
        self.headers = {
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Language': 'zh-cn',
            'UA-CPU': 'AMD64',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)',
            'Host': 'www.auxcss.com',
            'Connection': 'Keep-Alive',
            'Cache-Control': 'no-cache'
        }

        self.in_queue = Queue.Queue()
        for i in range(1):
            t = threading.Thread(target = self.use_queue,args = (self.in_queue,))
            t.setDaemon(True)
            t.start()
        
        self.in_queue.join()

    def auth(self, userID, passwd):
        s = requests.Session()
        data = {"userID":userID,"passwd":passwd}
        r = s.post(url=self.login_url, headers=self.headers, data=data)
        print(r.request.body)
        r_json = json.loads(r.text)
        if r_json.get('rstCode') != '1':
            print(r_json.get('rstDesc'))
            # utils.errorReport(r_json.get('rstDesc') + r.request.body, system_name=self.system_name)
        # res = {"status": True, "msg": r_json['rstDesc'], "do": 'auth', "r": r_json}
        # res['status'] = True if r_json.get('rstCode') is not '1' else False
        return s

    def logout(self):
        return self.s.post(url = self.logout_url,headers = self.headers)

    def doSearchQuery(self,sssd_COMPANY_ID,cscp_PRIM_PROD_SN,session = None):
        headers = self.headers
        headers['ajaxrequest'] = 'true'
        headers['Pragma'] = 'no-cache'
        headers['Content-Type'] = 'multipart/form-data'
        headers['Referer'] = 'http://www.auxcss.com/auxcss/jsp/css/sv/svgl/fwlrquery/FwlrQueryList.jsp?clear=true&programId=300204'
        # 繁琐的参数....不要随意更改
        data = {
            "body": {
                    "dataStores": {
                        "queryDataStore": {
                            "rowSet": {
                                "filter": [],
                                "primary": [
                                    {
                                        "svbl_SUBMIT_DATE_E": None,
                                        "sssd_ORG_TYPE": "SS",
                                        "svbl_SUBMIT_DATE_B": None,
                                        "_t": "1",
                                        "sssd_DV_AUDIT_STATUS": "Y",
                                        "_o": {
                                            "sssd_ORG_TYPE": None,
                                            "sssd_COMPANY_ID": None,
                                            "sssd_DV_AUDIT_STATUS": None,
                                            "cscp_PRIM_PROD_SN": None
                                        },
                                        "cscp_PRIM_PROD_SN": cscp_PRIM_PROD_SN,
                                        "sssd_COMPANY_ID": sssd_COMPANY_ID
                                    }
                                ],
                                "delete": []
                            },
                            "name": "queryDataStore",
                            "pageSize": 20,
                            "rowSetName": "com.neusoft.ermsuite.css.st.servsettle.stssd.vo.StssdSearchVO",
                            "recordCount": 1,
                            "pageNumber": 1
                        }
                    },
                    "parameters": {}
                },
                "header": {
                    "message": {
                        "detail": "",
                        "title": ""
                    },
                    "code": -100
                }
            }
        r = session.get(url=self.doSearchQuery_url)
        rq = session.post(url=self.doSearchQuery_url, data=json.dumps(data), headers=headers,timeout=60)
        try:
            rqobj = demjson.decode(rq.text)
        except Exception as e:
            return None
        # print(json.dumps(rqobj))
        if len(rqobj['body']['dataStores']['listDataStore']['rowSet']['primary']) is 0:
            return None
        return rqobj['body']['dataStores']['listDataStore']['rowSet']['primary']

    def _after_doSearchQuery(self, data):
        pass

    def get_amt(self):
        # self.auth(userID=u"028327", passwd=u"028327jj")
        # self.auth(userID=u'028307', passwd=u"XKY20171111")
        fac_alias = aliased(AuxFactoryOrder, name='fac_alias')
        dbsession = db.DBSession()
        s = text('SELECT c.oc_within_code,c.oc_abroad_code,mer.css_account,mer.css_password,mer.css_companyid,mer.css_name,a.apl_brand,o.ord_id,o.ord_finish_time FROM dm_order_code as c LEFT JOIN dm_order as o on o.ord_id=c.oc_ord_id LEFT JOIN dm_auxmerchant as mer on mer.platform_id=o.ord_merc_id left JOIN dm_order_aplicances as oa on oa.oa_ord_id=c.oc_ord_id LEFT JOIN dm_appliances as a on a.apl_id=oa.oa_apl_id WHERE c.oc_is_amt = "0" AND o.ord_cust_name NOT LIKE "%测试%" AND oa.oa_apl_model = c.oc_apl_model AND a.apl_brand = "奥克斯" AND mer.css_account is NOT NULL AND o.ord_type!="1" AND CHAR_LENGTH(c.oc_within_code) > 10 ORDER BY mer.css_account,o.ord_id DESC')
        r = dbsession.execute(s).fetchall()
        accounts_s = text('SELECT dm_auxmerchant.css_account,dm_auxmerchant.css_password FROM dm_auxmerchant')
        account_list = dbsession.execute(accounts_s).fetchall()
        session_list = {}
        for x in account_list:
            s = self.auth(x[0],x[1])
            session_list[x[0]] = pickle.dumps(s)
        dbsession.commit()
        dbsession.close()
        print(str(len(r)) + '条数据')

        for x in xrange(len(r)):
            tp = list(r[x])
            tp.append(session_list[tp[2]])
            incode,outcode,css_account,css_passwd,cid,cssname,brand,ord_id,ord_finish_time,session_pick = tp
            r_session = pickle.loads(session_pick)
            self.query_and_save(r_session,incode,outcode,css_account,css_passwd,cid,cssname,ord_id,ord_finish_time)
            # self.in_queue.put(json.dumps(tp))

    def use_queue(self,in_queue):
        while True:
            p = self.in_queue.get()
            p = json.loads(p)
            try:
                incode,outcode,css_account,css_passwd,cid,cssname,brand,ord_id,ord_finish_time,session_pick = p
                r_session = pickle.loads(session_pick)
                self.query_and_save(r_session,incode,outcode,css_account,css_passwd,cid,cssname,ord_id,ord_finish_time)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                msg = str(exc_type) + ":" + e.message + " in file '" + fname + "' line " + str(exc_tb.tb_lineno)
                utils.errorReport(msg,self.system_name)
            self.in_queue.task_done()

    def query_and_save(self,session,incode,outcode,css_account,css_passwd,cid,cssname,ord_id,ord_finish_time):
        r = self.doSearchQuery(cid,incode,session = session)
        # r = self.doSearchQuery(cid,"111808101306190060",session = session)
        if r is None:
            print(incode + "查询无结果")
            return True
        dbsession = db.DBSession()
        for item in r:
            if item['sssd_SERV_DATE'] is datetime.datetime.fromtimestamp(ord_finish_time).strftime('%Y-%m-%d'):
                c = dbsession.query(OrderCode).filter((OrderCode.oc_ord_id==ord_id) & (OrderCode.oc_within_code==incode)).all()
                c[0].oc_is_amt = 1
                dbsession.add(c[0])
                print("匹配:ord_id:",ord_id)

            # css = dbsession.query(Auxcssamt).filter((Auxcssamt.sssd_serv_date==item['sssd_SERV_DATE']) & (Auxcssamt.incode==incode)).all()
            css = dbsession.query(Auxcssamt).filter(Auxcssamt.sssd_source_bill_no==item['sssd_SOURCE_BILL_NO']).all()
            if css:
                print(incode+"已经存在!")
                return True
            
            cssamt = Auxcssamt()
            cssamt.ord_id = ord_id
            cssamt.sssd_source_bill_type_name = item['sssd_SOURCE_BILL_TYPE_NAME']
            cssamt.sssd_serv_total_amt = item['sssd_SERV_TOTAL_AMT']
            cssamt.sssd_other_total2_amt = item['sssd_OTHER_TOTAL2_AMT']
            cssamt.sssd_rowid = item['sssd_ROW_ID']
            cssamt.sssd_source_bill_no = item['sssd_SOURCE_BILL_NO']
            cssamt.aa_serv_settle_no = item['aa_serv_settle_no']
            cssamt.sssd_dv_audit_status_name = item['sssd_DV_AUDIT_STATUS_NAME']
            cssamt.sssd_ss_audit_status = item['sssd_SS_AUDIT_STATUS']
            cssamt.cscp_product_model = item['cscp_PRODUCT_MODEL']
            cssamt.sssd_serv_date = item['sssd_SERV_DATE']
            cssamt.svbl_submit_date = item['svbl_SUBMIT_DATE']
            cssamt.sssd_created_date = item['sssd_CREATED_DATE']
            cssamt.cscm_mobile_phone1 = item['cscm_MOBILE_PHONE1']
            # cssamt.sssd_last_upd_date = utils.strtime_to_time(item['sssd_LAST_UPD_DATE'] + " 00:00:00")
            cssamt.sssd_last_upd_date = item['sssd_LAST_UPD_DATE']
            cssamt.created_at = int(time.time())
            cssamt.incode = incode
            cssamt.css_account = css_account
            cssamt.outcode = outcode
            dbsession.add(cssamt)

            # 写入跟单记录
            track = OrderTracking()
            track.ord_id = ord_id
            track.operator_id = 1
            track.operator_name = u'auxcss爬虫'
            track.title = u'auxcss爬虫同步厂家结算费用'
            track.desc = u"内机:" + incode + u'厂家结算费用:' + str(item['sssd_OTHER_TOTAL2_AMT']) + u"元.结算类型:"+ item['sssd_SOURCE_BILL_TYPE_NAME'] + u'.服务时间:' + item['sssd_SERV_DATE']
            track.add_time = time.time()
            dbsession.add(track)
            
        dbsession.commit()
        dbsession.close()
        print(incode,"done!")
