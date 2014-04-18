# -*- coding: utf-8 -*-
import re
from scrapy.spider import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy import log
from sciencenet.items import BlogerItem
from sciencenet.common import urlpatterns, create_level2_user

class UserSpider(Spider):
    name = 'user'
    allowed_domains = ['blog.sciencenet.cn']
    start_urls = ['http://blog.sciencenet.cn/home.php?mod=space&uid=213646']

    def __init__(self, *args, **kvargs):
        uids = create_level2_user('friend.csv')
        self.start_urls = ['http://blog.sciencenet.cn/home.php?mod=space&uid=%s' % uid
                      for uid in uids]

    def _check_blog_created(self, sel):
        return len(sel.css(u'body:contains(没有开通)')) > 0

    def _check_private(self, sel):
        return len(sel.css(u'body:contains(的隐私设置，你不能访问当前内容)'))

    def _parse_home_page(self, response, item=None):
        sel = Selector(response)

        if self._check_blog_created(sel):
            return

        if not item:
            item = BlogerItem()

        if self._check_private(sel):
            item['url'] = sel.css('div.avt > a::attr(href)').extract()[0]
            item['uid'] = re.search(urlpatterns['home'], item['url']).group(1)
            item['forbidden'] = True
            item['liveness'] = \
                sel.css(u'ul.bbda li:contains(活跃度)::text').re('\d+')[0]
            item['reputation'] = \
                sel.css(u'ul.bbda li:contains(威望)::text').re('\d+')[0]
        else:
            item['url'] = sel.css('#nv > ul > li:first-child a::attr(href)').extract()[0]
            item['uid'] = re.search(urlpatterns['home'], item['url']).group(1)

            ul = sel.css('#statistic_content ul li')
            if len(ul) > 0:
                item['reputation'] = ul.css(u'li:contains(威望) a::text').extract()
                if len(item['reputation']):
                    item['reputation'] = item['reputation'][0]

                item['liveness'] = ul.css(u'li:contains(活跃度) a::text').extract()
                if len(item['liveness']):
                    item['liveness'] = item['liveness'][0]
        return item

    # 在 home page 获取活跃度和威望
    def parse(self, response):
        item = self._parse_home_page(response)
        if not item: return

        profile_url = \
            'http://blog.sciencenet.cn/home.php?mod=space&uid=%s&do=profile' % item['uid']

        # 在个人资料页面请求其他数据
        yield Request(url=profile_url,
                      callback=self.parse_profile_page,
                      meta={'item': item})

    def parse_profile_page(self, response, returnval=False):
        sel = Selector(response)

        item = response.meta['item']

        item['name'] = sel.css('#pcd h2.xs2 a::text').extract()[0]
        item['nickname'] = sel.css('h2.mbn::text')[0].extract().strip()
        item['uid'] = sel.css('h2.mbn span::text')[0].re('\d+')[0]
        item['url'] = sel.css('#pcd h2.xs2 a::attr(href)').extract()[0]
        item['urlasrefer'] = sel.css('#domainurl::text').extract()[0]
        item['start_time'] = sel.css(u'#pbbs li:contains(注册)::text').extract()[0]

        item['view_count'] = sel.css(u'li:contains(博客访问量) strong::text').extract()[0]
        item['friend_count'] = sel.css(u'*:contains(好友数)::text').re('\d+')[0]
        item['blog_count'] = sel.css(u'a:contains(博文数)::text').re('\d+')[0]

        return item
