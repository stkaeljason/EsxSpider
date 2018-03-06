# coding: utf8
import sys,os
reload(sys)
sys.setdefaultencoding('utf8')
from appBot import utils
from appBot.auxcss_api import Auxcss

utils.errorReport(u"auxcss爬虫运行","auxcss Bot")
try:
	auxcss = Auxcss()
	auxcss.get_amt()
except Exception as e:
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	msg = str(exc_type) + ":" + str(e.message) + " in file '" + str(fname) + "' line " + str(exc_tb.tb_lineno)
	utils.errorReport(msg,"auxcss Bot")
	print(msg)