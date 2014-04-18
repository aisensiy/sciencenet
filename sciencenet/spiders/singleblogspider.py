# -*- coding: utf-8 -*-
import re
from scrapy.spider import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from sciencenet.items import ArticleItem
import pandas as pd
from sciencenet.common import urlpatterns

class SingleBlogSpider(Spider):
    name = 'blogs'
    allowed_domains = ['blog.sciencenet.cn']
    start_urls = ['http://blog.sciencenet.cn/home.php?mod=space&uid=213646&do=blog&view=me&from=space']

    def __init__(self, *args, **kvargs):
        uids = [re.search(urlpatterns['home'], x).group(1)
                for x in open('authorurls.txt')]
        self.start_urls = ['http://blog.sciencenet.cn/home.php?mod=space&uid=%s&do=blog&from=space' % uid \
                           for uid in uids]

    def parse(self, response):
        sel = Selector(response)

        url = sel.css(u'a:contains(博客首页)::attr(href)').extract()[0]
        uid = re.search(urlpatterns['home'], url).group(1)

        blog_url_tmp = 'http://blog.sciencenet.cn/'
        bloglinks = sel.css('.xld .bbda > dt.xs2 a[target]::attr(href)').extract()
        for link in bloglinks:
            url = blog_url_tmp + link
            yield Request(url=url, callback=self.parse_blog_page, meta={'uid': uid})

        pages = sel.css('.pgs.cl .pg strong + a::attr(href)').extract()
        if len(pages) > 0:
            nextpage = pages[0]
            yield Request(url=nextpage, callback=self.parse)

    def parse_blog_page(self, response):
        uid = response.meta['uid']
        sel = Selector(response)

        item = ArticleItem()
        item['author'] = uid
        item['title'] = sel.css('h1.ph::text').extract()[0].strip()
        item['url'] = response.url

        xgs = sel.css('.xg2')
        item['view_count'] = xgs.css('.xg1:first-child::text').re('\d+')[0]
        item['pub_datetime'] = xgs.css('.xg1:nth-child(2)::text').extract()[0]
        own_category = xgs.css(u'.xg1:contains(个人) a::text').extract()
        if len(own_category):
            item['own_category'] = own_category[0]
        item['sys_category'] = xgs.css(u'.xg1:contains(系统) a::text').extract()[0]
        item['keywords'] = xgs.css(u'.xg1:contains(关键词)::text').re(u'关键词:(.*)')
        item['rcmd_count'] = sel.css('h4.bbs.pbn span font::text').extract()[0]
        item['rcmds'] = sel.css('h4.bbs.pbn span a::attr(href)').re('uid=(\d+)')
        item['comment_count'] = sel.css('#comment_replynum::text').extract()[0]

        return item
