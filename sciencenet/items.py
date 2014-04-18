# -*- coding: utf-8 -*-
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class FriendItem(Item):
    userid = Field()
    friendid = Field()

class BlogerItem(Item):
    name = Field()
    nickname = Field()
    uid = Field()
    url = Field()         # /home.php?...
    urlasrefer = Field()  # /u/:username
    start_time = Field()
    reputation = Field()
    liveness = Field()
    view_count = Field()
    friend_count = Field()
    blog_count = Field()
    forbidden = Field()

class ArticleItem(Item):
    author = Field()
    title = Field()
    url = Field()
    view_count = Field()
    pub_datetime = Field()
    own_category = Field()
    sys_category = Field()
    keywords = Field()
    rcmd_count = Field()
    rcmds = Field()
    comment_count = Field()

class FriendLink(Item):
    userurl = Field()
    linkto = Field()
