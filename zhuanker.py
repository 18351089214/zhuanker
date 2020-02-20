import time
import platform
from lxml import etree
import os
import sys

import requests
from config import *
from db import *
from selenium import webdriver
from gtaasmysql import MySQL
from gtaaslogger import Log

requests.packages.urllib3.disable_warnings()


class Zhuanker(object):
    def __init__(self, website='zhuanker'):
        name = os.path.split(__file__)[-1].split(".")[0]
        if platform.platform().startswith('Windows'):
            self.log = Log(name=name, path=r'..\..\log' + '\\' + name + r".log", level='ERROR')
        else:
            self.log = Log(name=name, path=r'../../log' + '/' + name + r".log", level='ERROR')
        self.logger = self.log.Logger
        self.logger.debug('Enter func:【{}】'.format(sys._getframe().f_code.co_name))
        self.obj_mysql = MySQL(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DATABASE)
        self.obj_mysql.create(SQL_CREATE_ZHUANKER_FORUM_TABLE)

        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.chrome_options = webdriver.ChromeOptions()
        if platform.platform().startswith('Windows'):
            self.browser = webdriver.Chrome(chrome_options=self.chrome_options,
                                            executable_path=r'C:\ProgramData\Anaconda3\chromedriver.exe')
        else:
            self.browser = webdriver.Chrome(chrome_options=self.chrome_options,
                                            executable_path='/usr/bin/chromedriver')
        self.browser.get(
            'https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id=101544888&redirect_uri=http%3A%2F%2Fbbs.zhuanker.com%2Fsource%2Fplugin%2Fdzlab_qqoauth%2Fconnect.php&state=1')
        time.sleep(10)
        self.logger.debug('Leave func:【{}】'.format(sys._getframe().f_code.co_name))

    def main(self):
        self.logger.debug('Enter func:【{}】'.format(sys._getframe().f_code.co_name))
        while True:
            try:
                self.logger.debug('Crawling: http://bbs.zhuanker.com/forum-37-1.html')
                self.browser.get('http://bbs.zhuanker.com/forum-37-1.html')
                html = etree.HTML(self.browser.page_source)
                items = html.xpath("//table[@id='threadlisttableid']/tbody[contains(@id, 'normalthread_')]")
                for item in items:
                    data = {}
                    data['id'] = (item.xpath('./@id')[0]).split('_')[1]
                    data['title'] = ''.join(item.xpath('./tr/th/a[2]/text()'))
                    data['url'] = 'http://bbs.zhuanker.com/' + item.xpath('./tr/th/a[2]/@href')[0]
                    data['dt'] = ''.join(item.xpath("./tr/td[@class='by'][1]/em/span/text()"))
                    self.obj_mysql.insert(data, MYSQL_TABLE_ZHUANKER_FORUM)
                self.logger.debug('Succeeded to crawl: http://bbs.zhuanker.com/forum-37-1.html')
                time.sleep(60 * 10)
            except Exception as e:
                self.logger.error('Failed to crawl: http://bbs.zhuanker.com/forum-37-1.html')
        self.logger.debug('Leaev func:【{}】'.format(sys._getframe().f_code.co_name))

    def __del__(self):
        self.browser.close()


if __name__ == '__main__':
    zk = Zhuanker()
    zk.main()
