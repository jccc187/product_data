from selenium import webdriver
import pandas as pd
import xlwt
import time
import threading


firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0;) Gecko/20100101 Firefox/68.0"') # 更换头部
firefox_options.add_argument('--headless') # 使selenium不用触发页面


def selenium_comment(url, path): # url为详细页面的地址，path为评论数据的本地存放位置
    browser_comment = webdriver.Firefox(firefox_options=firefox_options)
    browser_comment.get(url)
    time.sleep(5) # 等待页面加载
    res_comment = []
    cnt = 0 # 记录已读取的页数
    wbk = xlwt.Workbook()
    sheet1 = wbk.add_sheet("sheet1")
    sheet1.write(0, 0, browser_comment.find_element_by_xpath('//div[@class="sku-name"]').text)
    sheet1.write(1, 0, "价格:" + browser_comment.find_element_by_xpath('//div[@class="summary summary-first"]//span[@class="p-price"]').text)
    sheet1.write(2, 0, "评论数:" + browser_comment.find_element_by_xpath('//div[@id="comment-count"]/a').text)
    try:
        if browser_comment.find_element_by_xpath(
                '//div[@id="detail"]/div[@class="tab-main large"]/ul/li[5]/s').text == "(0)":  # 如果页面评论数为0，直接返回
            return
        while cnt < 50: # 50指爬取50页的评论数据，可以修改
            while len(browser_comment.find_elements_by_xpath('//div[@id="comment"]//div[@class="tab-con"]//div[@class="comment-column J-comment-column"]/p[@class="comment-con"]'))==0:
                browser_comment.refresh()
                browser_comment.find_element_by_xpath('//div[@id="detail"]/div[@class="tab-main large"]/ul/li[5]').click()
                time.sleep(5) # 评论页面未刷新出来，重复加载页面直至页面加载
            time.sleep(10)
            comment = browser_comment.find_elements_by_xpath('//div[@id="comment"]//div[@class="tab-con"]//div[@class="comment-column J-comment-column"]/p[@class="comment-con"]')
            order_info = browser_comment.find_elements_by_xpath('//div[@id="comment"]//div[@class="tab-con"]//div[@class="order-info"]') # 评论内容以及评论时间及手机型号
            for i in range(len(comment)):
                sheet1.write(cnt*len(comment)+i+3, 0, order_info[i].text) # 手机型号以及评论时间
                sheet1.write(cnt*len(comment)+i+3, 1, comment[i].text.replace('\n', ''))  # 评论内容
            cnt += 1
            if len(browser_comment.find_elements_by_xpath('//div[@id="comment"]//a[@class="ui-pager-next"]'))>0:  #判断是否有下一页
                browser_comment.find_element_by_xpath('//div[@id="comment"]//a[@class="ui-pager-next"]').click() # 评论换页
                continue
            else:
                break
    except:
        pass
    wbk.save(path)
    browser_comment.close()
    return res_comment


def selenium_page_simple(browser): # 从列表页爬取每件商品的销售量、价格、评价数量，并分别对每一商品的评论进行爬取
    try:
        # for i in range(141): # 列表页总页数
        time.sleep(5)
        name_list = browser.find_elements_by_xpath('//div[@id="plist"]/ul/li[@class="gl-item"]/div/div[4]/a/em') # 商品名称
        href_list = browser.find_elements_by_xpath('//div[@id="plist"]/ul/li[@class="gl-item"]//div[@class="p-img"]/a') # 商品详细页面的地址
        # price_list = browser.find_elements_by_xpath('//div[@id="plist"]//div[@class="p-price"]') # 价格
        # comment_list = browser.find_elements_by_xpath('//div[@id="plist"]//div[@class="p-commit"]//a') # 评论数量
        for each in range(len(name_list)):
            name_list[each].text.replace('/','') # 替换一些可能会影响路径的字符
            selenium_comment(href_list[each].get_attribute("href"), "C://users/94880/desktop/comment3/"+name_list[each].text.replace('\n', '')+".xls")  # 调用selenium_comment函数爬去每个商品的具体评论
        # browser.find_element_by_xpath('//a[@class="pn-next"]').click() # 换页
    except:
        pass
    browser.close()


if __name__ == "__main__":
    for j in range(0, 141, 3):
        for i in range(j, j + 3):
            browser = webdriver.Firefox(firefox_options=firefox_options)
            browser.delete_all_cookies()  # 删除cookie
            try:
                browser.get("https://list.jd.com/list.html?cat=9987,653,655&page="+str(i)+"&sort=sort_rank_asc&trans=1&JL=6_0_0&ms=10#J_main")
                thread = threading.Thread(target=selenium_page_simple, args=(browser,))
                thread.start() # 同时开启三个线程
            except:
                pass
