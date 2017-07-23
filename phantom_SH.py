# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pymysql.cursors
import json
import time
import ast
from multiprocessing.pool import ThreadPool as Pool
pool_size = 5  # your "parallelness"
pool = Pool(pool_size)



# 分类统计所有的QFII以及该QFII所持有的公司数量以及公司code--Amount
# 分类统计所有的社保基金以及该社保基金所持有的公司数量以及公司code--Amount

url = 'https://xueqiu.com/hq#exchange=CN&plate=1_1_0&firstName=1&secondName=1_1&type=sha'

# url = 'https://xueqiu.com/hq#exchange=CN&plate=1_1_1&firstName=1&secondName=1_1&type=sza'

agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = agent
phantomJs = webdriver.PhantomJS(desired_capabilities=dcap)
phantomJs.set_window_size(1024, 768)

# phantomJs.save_screenshot('xueqiu.png')

# codedict = {}

# save all stock code and ZYGD url
codedict = {}

# get every page Code and assemble url
def get_code_dict(phantomjs, url):
    phantomJs = phantomjs
    phantomJs.get(url)
    trList = phantomJs.find_elements_by_xpath("//tbody/tr")

    for tr in trList:
        codelist = []
        code = tr.find_elements(By.TAG_NAME, 'td')[0].text.encode('utf-8')
        # print type(code)
        codelist.append("https://xueqiu.com/S/" + code + "/ZYGD")
        # current price
        codelist.append(str(tr.find_elements(By.TAG_NAME, 'td')[2].text))
        # print 'current price' + str(tr.find_elements(By.TAG_NAME, 'td')[2].text)
        # print codeUrl
        codedict[code] = codelist
        # print tr.get_attribute('code')
    # print codedict
    # print codedict.values()
    print codedict
    return codedict

def check_exist_element(phantomjs, url):
    phantomJs = phantomjs
    print url
    phantomJs.get(url)
    try:
        element_a = phantomJs.find_element_by_xpath("//li[contains(@class, 'next')]/a")
        print element_a.text
        # element_a.click()
        return True
    except NoSuchElementException as e:
        return False
        # print 'Error' + str(e)

# implement Multi-Thread
# pool = ThreadPool(10)
# pool.map(get_code_dict, [(phantomJs, url)])

# get_code_dict(phantomJs, url)

# ZYGD
focus_on_list = []
all_qfii = {}
all_sbjj = {}
all_jr = {}
all_ssgs = {}

def get_zygd(phantomJs, codedict):
    for code in codedict:
        phantomJs.get(codedict[code][0])
        zygdtrlist = phantomJs.find_elements_by_xpath(
                "//div[contains(@class,'tab-table-responsive dataTable-div')][1]//tr[position()>3]")
        for zygdtr in zygdtrlist:
            # print zygdtr.find_elements(By.TAG_NAME, 'td')[0].text

            # print 'stocknumbers is : ' + str(zygdtr.find_elements(By.TAG_NAME, 'td')[3].text)

            # 股东类型
            zygd_type = unicode(zygdtr.find_elements_by_tag_name("td")[1].text).encode('utf-8')
            # 股东名称
            zygd_name = unicode(zygdtr.find_elements(By.TAG_NAME, 'td')[0].text).encode('utf-8')
            # 该股东所持股票数量
            stock_numbers = str(zygdtr.find_elements(By.TAG_NAME, 'td')[3].text).replace(',', '')
            # 该股东所持股票总额
            stock_amount = str(float(codedict[code][1]) * float(stock_numbers))
            if zygd_type == 'QFII':
                if zygd_name in all_qfii:
                    all_qfii[zygd_name].append("{'" + code + "':" + stock_amount + "}")
                else:
                    all_qfii[zygd_name] = ["{'" + code + "':" + stock_amount + "}"]
            elif zygd_type == '全国社保基金':
                if zygd_name in all_sbjj:
                    all_sbjj[zygd_name].append("{'" + code + "':" + stock_amount + "}")
                else:
                    all_sbjj[zygd_name] = ["{'" + code + "':" + stock_amount + "}"]
            elif zygd_type == '金融':
                if zygd_name in all_jr:
                    all_jr[zygd_name].append("{'" + code + "':" + stock_amount + "}")
                else:
                    all_jr[zygd_name] = ["{'" + code + "':" + stock_amount + "}"]
            elif zygd_type == '上市公司':
                if zygd_name in all_ssgs:
                    all_ssgs[zygd_name].append("{'" + code + "':" + stock_amount + "}")
                else:
                    all_ssgs[zygd_name] = ["{'" + code + "':" + stock_amount + "}"]

        print "all_qfii",  json.dumps(all_qfii, encoding="UTF-8", ensure_ascii=False)
        print "all_sbjj",  json.dumps(all_sbjj, encoding="UTF-8", ensure_ascii=False)
        print "all_jr",  json.dumps(all_jr, encoding="UTF-8", ensure_ascii=False)
        print "all_ssgs",  json.dumps(all_ssgs, encoding="UTF-8", ensure_ascii=False)
        print "----------------------------------------------------------------------"


def main(url):

    # region Sorted Dict
    # a_list = [ "{'SH600262':4633.1911}", "{'SH600452':11308.616}", "{'SH600462':18.616}", "{'SH600472':308.616}"]
    # new_dict = {}
    # for single_dict in a_list:
    #     new_dict.update(ast.literal_eval(single_dict))
    # print sorted(new_dict, key=new_dict.get, reverse=True)
    # endregion

    # traverse all SH-stock list, get all code, assemble ZYGD url



    # get all stock code and ZYGD url

    # get_zygd(phantomJs, get_code_dict(phantomJs, url))
    get_code_dict(phantomJs, url)
    while check_exist_element(phantomJs, url):
        phantomJs.find_element_by_xpath("//li[contains(@class, 'next')]/a").click()
        # Loop condition
        url = phantomJs.current_url
        get_code_dict(phantomJs, url)
        # get_zygd(phantomJs, get_code_dict(phantomJs, phantomJs.current_url))
    print 'SH stock num is :', len(codedict)

    # traverse all ZYGD url
    get_zygd(phantomJs, codedict);





    # how to implement Multi-Thread
    # pool.apply_async(get_zygd, (phantomJs, get_code_dict(phantomJs, phantomJs.current_url)), )
    # pool.close()
    # pool.join()

    # print 'focus_on_list length : ' + str(len(focus_on_list))

    # print "all_qfii",  json.dumps(all_qfii, encoding="UTF-8", ensure_ascii=False)
    # print "all_sbjj",  json.dumps(all_sbjj, encoding="UTF-8", ensure_ascii=False)
    # print "all_jr",  json.dumps(all_jr, encoding="UTF-8", ensure_ascii=False)
    # print "all_ssgs",  json.dumps(all_ssgs, encoding="UTF-8", ensure_ascii=False)

    # Connect to the database
    connection = pymysql.connect(host='127.0.0.1',
                                 user='test',
                                 password='test',
                                 db='test',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    # at the beginning of the script
    start_time = time.time()
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `portfolio` (`portfolio_name`, `portfolio_stocks`, `portfolio_type`) VALUES (%s, %s, %s)"
            sql_list = []
            if all_sbjj:
                for sbjj_name in all_sbjj:
                    sql_list.append((sbjj_name, str(all_sbjj[sbjj_name]), 'SBJJ'))
                    # cursor.execute(sql, (sbjj_name, str(all_sbjj[sbjj_name]), 'SBJJ'))
            if all_qfii:
                for qfii_name in all_qfii:
                    sql_list.append((qfii_name, str(all_qfii[qfii_name]), 'QFII'))
                    # cursor.execute(sql, (qfii_name, str(all_qfii[qfii_name]), 'QFII'))
            if all_jr:
                for jr_name in all_jr:
                    sql_list.append((jr_name, str(all_jr[jr_name]), 'FINANCE'))
                    # cursor.execute(sql, (jr_name, str(all_jr[jr_name]), 'FINANCE'))
            if all_ssgs:
                for ssgs_name in all_ssgs:
                    sql_list.append((ssgs_name, str(all_ssgs[ssgs_name]), 'LISTED'))
                    # cursor.execute(sql, (ssgs_name, str(all_ssgs[ssgs_name]), 'LISTED'))
            cursor.executemany(sql, sql_list)

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
    finally:
        print("---insert DB spend  %s seconds ---" % (time.time() - start_time))
        connection.close()

print main(url)