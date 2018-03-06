# # -*- coding: utf-8 -*-
#
# import copy
# import json
#
# from utils import request
#
# class JdAppApi:
#
#     def __init__(self):
#         self.base_url = ''
#         self.wskey = 'AAFaHSg5AEC6volLlXhwF8Z0e1K41x-43A8gQWayG6IGJWBrajcKJynf9tTXcIwGYo6pi-mIf3vD4YQC3bsnUTPH_Dh6DnMv'
#         self.tgt = 'AAFaHSg5AEC6volLlXhwF8Z0e1K41x-43A8gQWayG6IGJWBrajcKJynf9tTXcIwGYo6pi-mIf3vD4YQC3bsnUTPH_Dh6DnMv'
#         self.base_headers = {
#             'Host': 'coomrd.jd.com',
#             'tgt': self.tgt,
#             'Content-Type': 'application/x-www-form-urlencoded',
#             'Accept-Encoding': 'br, gzip, deflate',
#             'wsKey': self.wskey,
#             'Accept': '*/*',
#             'Accept-Language': 'zh-Hans-CN;q=1',
#             'User-Agent': 'MRDLogistics/1.9.8 (iPhone; iOS 11.0.3; Scale/2.00)',
#             'pin': 'jd_635657561ffcc',           #jason
#
#         }
#
#     def login(self):
#         # api_url = ''
#         # headers = copy.copy(self.base_headers)
#         # form_data = {}
#         #
#         # # form_data = json.dumps(form_data)
#         # r = request(api_url, method='post', data=form_data, headers=headers)
#         # token = ''
#         # return token
#         pass
#
#     def check_appont(self):
#         api_url = ''
#         headers = copy.copy(self.base_headers)
#         form_data = {
#             'alias':'pcsjsf',
#             'appId': '8167',
#             'appName': 'JDApp',
#             'method': 'getAppointmentAndFeedbackList',
#             'param': '"1","1","377326A5-AB9A-4EC1-B952-3AA88ECF5187","13548106934"',
#             'service': 'com.jd.las.im.appserver.service.jdBigInstall.IAppointmentAndFeedbackService',
#         }
#         form_data = json.dumps(form_data)
#         r = request(api_url,method='post',data=form_data,headers=headers)
