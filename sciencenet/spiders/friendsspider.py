# -*- coding: utf-8 -*-
import re
from scrapy.spider import Spider
# from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
import pandas as pd
from sciencenet.items import FriendItem
from sciencenet.common import urlpatterns

class FriendSpider(Spider):
    name = 'friend'
    allowed_domains = ['blog.sciencenet.cn']
    start_urls = []

    def __init__(self, *args, **kvargs):
        self.start_urls = [x.strip() for x in open('authorurls.txt')]

    def _check_blog_created(self, sel):
        return len(sel.css(u'body:contains(没有开通)')) > 0

    def parse(self, response):
        sel = Selector(response)

        if self._check_blog_created(sel):
            return

        url = sel.css(u'a:contains(博客首页)::attr(href)').extract()[0]
        uid = re.search(urlpatterns['home'], url).group(1)

        friendurltmp = 'http://blog.sciencenet.cn/home.php?mod=space&uid=%s&do=friend&from=space&page=%d'
        startfriendurl = friendurltmp % (uid, 1)
        yield Request(url=startfriendurl,
                      callback=self.follow_friend_list,
                      meta={'uid': uid})

    def follow_friend_list(self, response):
        uid = response.meta['uid']

        sel = Selector(response)
        friendids = sel.css('.xld .bbda > dd.avt a::attr(href)').re('\d+$')

        for friendid in friendids:
            item = FriendItem()
            item['userid'] = uid
            item['friendid'] = friendid
            yield item

        pages = sel.css('.pgs.cl .pg strong + a::attr(href)').extract()
        if len(pages) > 0:
            nextpage = pages[0]
            yield Request(url=nextpage,
                          callback=self.follow_friend_list,
                          meta={'uid': uid})
