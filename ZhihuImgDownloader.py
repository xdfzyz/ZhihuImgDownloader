import time
from selenium import webdriver
import requests
import json
import jsonpath
import re
import os
from lxml import etree

Cookies = {}


def get_cookies():
    global Cookies
    username = input('账号:')
    password = input('密码:')
    driver = webdriver.Firefox()
    url = 'https://www.zhihu.com/'
    driver.get(url)
    driver.find_element_by_xpath('//div[@class="SignContainer-switch"]/span').click()
    driver.find_element_by_name("username").send_keys(username)
    driver.find_element_by_name("password").send_keys(password)
    print("请在浏览器端完成验证码输入。")
    time.sleep(2)
    input("输入任意键继续")
    try:
        driver.find_element_by_xpath('//button[@class="Button SignFlow-submitButton Button--primary Button--blue"]').click()
    finally:
        time.sleep(3)
        for cookies_dict in driver.get_cookies():
            Cookies[cookies_dict["name"]] = cookies_dict["value"]

        # print(Cookies)
        driver.quit()
        print("获取Cookies成功。")


def question_info():

    url = input('输入问题地址：')
    pattern = re.compile(r'\d+')
    q_id = pattern.search(url).group(0)
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"
    }
    response = s.get(url, headers=headers, cookies=Cookies, verify=False)

    html = response.content.decode('utf-8')

    content = etree.HTML(html)

    title = content.xpath('//h1[@class="QuestionHeader-title"]/text()')[0][:-1]
    nums = int(content.xpath('//h4[@class="List-headerText"]/span/text()')[0])

    try:
        count = int(input("问题:%s----下有%d个回答，输入提取个数：" % (title, nums)))
        if os.path.exists(title):
            print("该问题图片已下载过。")
            return
        else:
            os.mkdir(title)
            if nums >= count > 0:
                for i in range(count):
                    load_json(q_id, i, title)
        print("%s 下载完成" % title)
    except:
        print('请输入整数')
        return


def load_json(q_id, i, title):
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"
    }
    url = "https://www.zhihu.com/api/v4/questions/" + q_id + "/answers?sort_by=default&include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics&limit=10&offset=" + str(i)

    response = s.get(url, headers=headers, cookies=Cookies, verify=False)

    html = response.content.decode("ascii")
    jsonobj = json.loads(html)
    name = jsonpath.jsonpath(jsonobj, "$..author.name")[0]
    content = jsonpath.jsonpath(jsonobj, "$..content")[0]
    pattern = re.compile(r'img.+?src="http(.+?).jpg')
    img_list = set(pattern.findall(content))
    download_img(title, name, i, img_list)
    print("正在下载%s%d...." % (name, i))


def download_img(title, name, i, img_list):
    dir_path = title+"/"+str(i)+name
    os.mkdir(dir_path)
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"
    }
    for url in img_list:
        url = "http" + url + ".jpg"
        img_name = url[-12:]
        response = s.get(url, headers=headers, cookies=Cookies, verify=False)
        img = response.content
        f = open(dir_path + "/" + img_name, 'wb')
        f.write(img)
        f.close()


if __name__ == '__main__':
    get_cookies()
    question_info()
