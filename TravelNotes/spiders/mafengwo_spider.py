import scrapy
import re
import requests
from scrapy.http import Request
import json
from scrapy.selector import Selector
from TravelNotes.items import TravelNotesItem

def my_strip(string):
    return ' '.join(string.split())

def list_to_string(word_list):
    string = ""
    for word in word_list:
        string += word
    return string

def my_bytes(string):
    return bytes(string, encoding="utf-8")

def getText(response):
    text = []
    # 初始加载的text
    split_text_list = response.xpath('//div[@class="_j_content_box"]//p/text()').extract()
    text.append(my_strip(list_to_string(split_text_list)))

    # Query String Parameters
    # qsp除seq参数外保持不变
    qsp = {}

    qsp['act'] = 'getNoteDetailContentChunk'
    qsp['id'] = response.xpath('//meta[@name="author"]/@content').extract()[0].split(",")[0]

    new_iid_string = response.xpath('//script[@type="text/javascript"]/text()').extract_first()
    new_iid_pattern = r'new_iid":"\d+'
    new_iid = re.search(new_iid_pattern, new_iid_string).group().split('"')[2]

    qsp['new_iid'] = new_iid

    seq = response.xpath('//div[@class="_j_content_box"]//@data-seq').extract()[-1]
    qsp['seq'] = seq

    qsp['back'] = '0'

    r = requests.get("http://www.mafengwo.cn/note/ajax.php", params=qsp)
    json_dict = json.loads(r.text)
    # 当加载出内容不为空
    while (json_dict['data']['html'] != ""):
        # 存入ajax加载出的内容
        html = json_dict['data']['html']
        split_text_list = Selector(text=html).xpath('//p//text()').extract()
        text.append(my_strip(list_to_string(split_text_list)))
        # 如果还有内容没加载完则获取下一个seq
        if (json_dict['data']['has_more'] == True):
            next_seq = re.findall(r'data-seq=\\"\d+', r.text)[-1].split('"')[1]
            qsp['seq'] = next_seq
            r = requests.get("http://www.mafengwo.cn/note/ajax.php", params=qsp)
            json_dict = json.loads(r.text)
        # 如果内容已经加载完毕就终止循环
        else:
            break
    # 合并text
    text = list_to_string(text)
    return text

def build_vct_url(iid):
    url = 'http://pagelet.mafengwo.cn/note/pagelet/headOperateApi?callback=jQuery18107804142991945704_1536312586718' \
          '&params={"iid":"%s"}&_=1536312586853'
    vct_url = url % iid
    return vct_url


def parse_item(response):
    titlestring = response.xpath('//title/text()').extract_first()
    title = titlestring.split(',北京旅游攻略 - 马蜂窝')[0]
    author = response.xpath('//meta[@name="author"]/@content').extract()[0].split(",")[1]
    #游记编号
    iid = response.url.split('/')[-1].split('.')[0]
    #头部信息请求js,全部采用正则表达式从r.text中提取
    vc_time_request = build_vct_url(iid)
    r = requests.get(vc_time_request)
    #游记分享时间
    share_time = re.search(r'\d{4}-\d{1,2}-\d{1,2}\s\d+:\d+:\d+', r.text).group()
    view_and_comment = re.search(r'ico_view\\\"><\\/i>\d+\.*\d+w*\\/\d+',r.text).group()
    #浏览数
    viewCount = view_and_comment.split('>')[-1].split('\/')[0]
    #评论数
    commentCount = view_and_comment.split('>')[-1].split('\/')[1]
    #收藏分享span
    fav_and_share = re.findall(r'i><span>\d+', r.text)
    #收藏次数
    favCount = fav_and_share[1].split('>')[-1]
    #被分享次数
    shareCount = fav_and_share[0].split('>')[-1]
    #travel_dir_list详情
    #开始时间，持续时间，花费，人物类型
    startTime = None
    duration = None
    averageCost = None
    personType = None
    travel_dir_list = response.xpath('//div[@class="tarvel_dir_list clearfix"]')
    try:
        if(travel_dir_list != None):
            li_time = travel_dir_list.xpath('//li[@class="time"]//text()')
            li_day = travel_dir_list.xpath('//li[@class="day"]//text()')
            li_people = travel_dir_list.xpath('//li[@class="people"]//text()')
            li_cost = travel_dir_list.xpath('//li[@class="cost"]//text()')
            if(li_time != None):
                startTime = li_time.extract()[-1]
            if(li_day != None):
                duration = li_day.extract()[-1]
            if(li_cost != None):
                averageCost = li_cost.extract()[-1]
            if(li_people != None):
                personType = li_people.extract()[-1]
    except :
        print("TRAVEL_DIR_LIST出现异常！")
    #游记内容
    text = getText(response)

    item = TravelNotesItem()
    item['iid'] = iid
    item['title'] = title
    item['author'] = author
    item['shareTime'] = share_time
    item['viewCount'] = viewCount
    item['commentCount'] = commentCount
    item['favCount'] = favCount
    item['shareCount'] = shareCount
    item['startTime'] = startTime
    item['duration'] = duration
    item['personType'] = personType
    item['averageCost'] = averageCost
    item['content'] = text

    return item

class MafengwoSpider(scrapy.Spider):
    name = "mafengwo"
    #从第一页开始
    start_urls = ["http://www.mafengwo.cn/yj/10065/"]

    def parse(self, response):
        url = response.url
        #游记详情页
        if(re.match(r'http://www.mafengwo.cn/i/', url)):
            yield(parse_item(response))
        #游记列表页
        elif(re.match(r'http://www.mafengwo.cn/yj/', url)):
            url_list = response.xpath('//div[@class="post-cover"]//a/@href').extract()
            for url in url_list:
                url = "http://www.mafengwo.cn" + url
                yield Request(url, callback=self.parse)

            next_page_url = response.xpath('//a[@class="ti next"]/@href').extract_first()
            next_page_url = "http://www.mafengwo.cn" + next_page_url
            if(next_page_url != None):
                yield Request(next_page_url, callback=self.parse)


