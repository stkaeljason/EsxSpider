# -*- coding: utf-8 -*-

# Scrapy settings for EsxSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'EsxSpider'

SPIDER_MODULES = ['EsxSpider.spiders']
NEWSPIDER_MODULE = 'EsxSpider.spiders'

# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5'
# FEED_URI = 'file:///home/jason/Desktop/%(name)s/%(time)s.csv'  # 定义爬取的数据保存路径
# FEED_FORMAT = 'csv'  # 定义爬取的数据保存格式
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'EsxSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True
# MYSQL_CONFIG = {
#     'host': '127.0.0.1',
#     'port': 3306,
#     'user': 'root',
#     'passwd': 'root',
#     'db': 'ershixiong_anzhuang',
#     'charset': 'utf8'
# }

DOWNLOAD_HANDLERS = {'s3': None}

# ITEM_PIPELINES = {
#     'EsxSpider.pipelines.EsxspiderPipeline': 300
# }



# 工单详情信息数据定义
order_detail = {
    'ord_cust_name': 'bitch',   # 用户名
    'ord_cust_tel': '22',    # 来电电话 + ',' + 移动电话(如果移动电话不为空)
    'ord_cust_addr': '2',   # 用户地址(镇+详细地址)
    'ord_province': '2',    #
    'ord_city': '2',                #
    'ord_district': '8',                #
    'ord_remark': 'f',                # 服务描述
    'ord_num': '6',                # 需要自己生成一个订单号
    'ord_pay_num': '6',                # 需要自己生成一个微信支付号
    'ord_grab_addr': '6',                # province + city + district + town + address
    'ord_cust_fault': '6',                # 服务描述
    'ord_accept_no': '6',                # factorynumber
    'ord_ask_time': '66',                # 要求服务时间，时间戳存数据库
    'ord_create_time': '66',                # 当前时间戳
    'ord_buy_time': 'dfdf',            # 购买时间，存时间戳格式
}

# 访问待接单的form_data
daijie_data = {
    'status'        :'110',       # 110:待接单，1：师傅接单，2：待完单
    # 'overtime'      :'',
    # 'day'           :'',
    # 'ordername'     :'',
    # 'originname'    :'',
    # 'machinetype'   :'',
    # 'brand'         :'',
    # 'orderlevel'    :'',
    # 'masterid'     :'',
    # 'datetype'      :'',
    # 'startdate'     :'',
    # 'enddate'       :'',
    # 'keywordoption' :'',
    # 'keyword'       :'',
    # 'page'          :'1',
    # 'rows'          :'100'
}






# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'EsxSpider.middlewares.EsxspiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'EsxSpider.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'EsxSpider.pipelines.EsxspiderPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
