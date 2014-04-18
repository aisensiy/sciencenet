# -*- coding: utf-8 -*-
import re
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spider import Spider
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy import log
from sciencenet.items import FriendLink
from sciencenet.common import urlpatterns, create_level2_user

class FriendLinkSpider(CrawlSpider):
    name = 'friendlink'
    allowed_domains = ['blog.sciencenet.cn']
    start_urls = ['http://blog.sciencenet.cn/home.php?mod=space&uid=213646']
    rules = [
        Rule(
            SgmlLinkExtractor(
                allow=('home\.php\?mod=space\&uid=\d+', '\/u\/[^\/\?]+'),
                deny=('do=\w+',),
                restrict_xpaths=(u'//div[contains(., "友情链接")]',)),
            callback='parse_page'
        )
    ]

    def __init__(self, *args, **kvargs):
        uids = create_level2_user('friend.csv')
        self.log('Total users: %d' % len(uids))
        self.start_urls = ['http://blog.sciencenet.cn/home.php?mod=space&uid=%s' % uid
                           for uid in uids]
        super(FriendLinkSpider, self).__init__()


    def parse_page(self, response):
        sel = Selector(response)

        links = sel.css(u'.block.move-span:contains(友情) .content a::attr(href)').extract()

        friendlinks = []
        nextlinks = []
        for link in links:
            if (re.search(urlpatterns['blog'], link) or
                re.search(urlpatterns['home'], link)):

                item = FriendLink()
                item['userurl'] = response.url
                item['linkto'] = link

                friendlinks.append(item)
                nextlinks.append(link)

        # for link in nextlinks:
        #     yield Request(url=link, callback=self.parse)

        return friendlinks
