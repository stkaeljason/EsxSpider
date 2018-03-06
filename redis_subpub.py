# coding: utf8
import sys
import redis
import json
import os
import time
import Queue
import threading
reload(sys)
sys.setdefaultencoding('utf8')
from appBot.auxAppApi import auxAppApi
from appBot.mdAppApi import MdAppApi
from appBot import utils
import appBot.aux_api as aux_api
from db_model.Phppy import Phppy
from db_model.db import DBSession

def save_cmd(data):
    phppy = Phppy()
    phppy.data = item['data']
    phppy.time = time.time()
    phppy.channel = item['channel']
    
    session = DBSession()
    session.add(phppy)
    session.commit()
    session.close()

def use_queue(in_queue):
    while True:
        p = in_queue.get()
        p = json.loads(p)
        try:
            eval(p['cmd'])(p['params'])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            msg = str(exc_type) + ":" + e.message + " in file '" + fname + "' line " + str(exc_tb.tb_lineno)
            utils.errorReport(msg,"redis subpub")
        in_queue.task_done()#向任务已经完成的队列发送一个消息


if __name__ == '__main__':
    mdappapi = MdAppApi()
    
    auxappapi = auxAppApi()
    
    in_queue = Queue.Queue()
    for i in range(1):
        t = threading.Thread(target = use_queue,args = (in_queue,))
        t.setDaemon(True)
        t.start()
    
    in_queue.join()
    
    rc = redis.Redis(host='r-wz9ba7101fdca794.redis.rds.aliyuncs.com', port=6379, password='Ershixiong2017')
    # rc = redis.Redis(host='127.0.0.1')
    ps = rc.pubsub()
    # 订阅列表
    ps.subscribe(['auxbot','mdcode'])
    print('Listen start.')
    
    for item in ps.listen():
        if item['type'] == 'message':
            try:
                print(item['data'])
                save_cmd(item)
                in_queue.put(item['data'])
            except Exception as e:
            	exc_type, exc_obj, exc_tb = sys.exc_info()
            	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            	msg = str(exc_type) + ":" + e.message + " in file '" + fname + "' line " + str(exc_tb.tb_lineno)
            	utils.errorReport(msg,"redis subpub")
    else:
        utils.errorReport("listen stop!(For loop quit.)")
    
    print('Listen stop.(Exception)')