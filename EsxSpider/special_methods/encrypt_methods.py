#coding:utf-8

import execjs


def get_js(js_path):
    # f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
    f = open(js_path, 'r')
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    return htmlstr


def midea_encrypt(pwd):
    js_str = get_js('./EsxSpider/special_methods/midea_encrypt.js')
    ctx = execjs.compile(js_str)
    secret_pwd = ctx.call('encry_pwd',pwd)
    return secret_pwd