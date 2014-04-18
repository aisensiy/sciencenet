# -*- coding: utf-8 -*-
import pandas as pd

urlpatterns = {
    'home': '/home.php\?mod=space\&uid=(\d+)',
    'blog': 'blog.sciencenet.cn/u/([^\/\&]+)'
}

def create_userlist(filename):
    sheets = [u'图书馆学', u'情报学', u'文献学', u'档案学', u'图书情报文献学其他']
    urls = []
    # filename = u'/Users/xushanchuan/Downloads/图情领域学者统计完整版.xlsx'
    for sheet in sheets:
        df = pd.read_excel(filename, sheet=sheet)
        urls += df[u'科学网地址'].tolist()
    return urls

# 从获取的好友列表中获取所有人的资料
def create_level2_user(filename):
    df = pd.read_csv(filename)
    return list(set(df['userid'].tolist()) | set(df['friendid'].tolist()))


if __name__ == '__main__':
    filename = u'/Users/xushanchuan/Downloads/图情领域学者统计完整版.xlsx'
    urls = create_userlist(filename)
    with open('authorurls.txt', 'w') as ofile:
        ofile.write('\n'.join(urls))
