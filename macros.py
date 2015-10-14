# coding: utf-8
import re
import os
import email.utils
import time
from datetime import datetime
import markdown
import bleach


SITE_NAME = '/home/overdese'
SITE_URL = 'http://www.overdese.com'
SITE_DESCRIPTION = 'NameError: name overdese is not defined'


def fix_url(path):
    """
    Remove index.html in end of url
    """
    return re.sub(r'/?index.html$', r'/', path)


def truncate_str(text_str, length):
	"""
	Truncate text string to length
	"""	
	if len(text_str) > length:
		return '%s...' % text_str[:int(length)]
	else:
		return text_str
	

# label features

def get_post_labels(post):
    lst = list()
    for label in [x.strip() for x in post.labels.split(',') if x != '']:
        for post in [post for post in pages if 'label' in post if label == post.title]:
            lst.append(post)
    return lst


def hook_preconvert_labels():
    posts = [p for p in pages if "blog" in p]
    labels = list()

    for post in posts:        
        try:
            labels.extend([x.strip() for x in post['labels'].split(',') if x.strip() != ''])
        except KeyError:
            pass            

    label_dict = dict()

    for label in labels:
        if label in label_dict:
            label_dict[label] += 1
        else:
            label_dict[label] = 1

    labels[:] = []

    for key in label_dict:
        labels.append({'name': key,
                       'count': label_dict[key]})

    for label in labels:
        os.makedirs(os.path.join(output, 'labels', label['name']))

        #print(open(os.path.join('extension', 'labels', 'label.md'), 'r', encoding='utf-8').readlines())

        page = Page(os.path.join('labels', label['name'], 'index.md'), title=label['name'], count=label['count'],
                    virtual=open(os.path.join('extension', 'labels', 'label.md'), 'r', encoding='utf-8').readlines())
        page.count = label['count']
        pages.append(page)
        #print(page.url)

    page = Page(os.path.join('labels', 'index.md'),
                virtual=open(os.path.join('extension', 'labels', 'index.md'), 'r', encoding='utf-8').readlines())
    pages.append(page)


# comments

def disqus_comments():
    return '''КОММЕНТЫ!'''

# preview posts

def hook_preconvert_post_preview():
    for post in [p for p in pages if "blog" in p]:        
        prev_lst = post.source.split('\n<!-- more -->\n')
        prev = bleach.clean(markdown.markdown(prev_lst[0], extensions=['extra']), tags=[], strip=True)
        if len(prev_lst) > 1:
            post.preview = ''.join([prev, ' ...'])
        else:
            post.preview = truncate_str(prev, 250)

def get_preview_img(post):    
    pattern = re.compile(r'main.(jpg|jpeg|png|gif)')    
    for fn in os.listdir('/'.join(post.fname.split('/')[:-1])):
        if pattern.match(fn) is not None:
            post_url = post.url.split('/')[:-1]
            post_url.append('.'.join(['main', pattern.match(fn).group(1)]))
            return '/'.join(post_url)
    return '/static/img/no_preview.jpg'


# RSS

def hook_postconvert_rss():
    _RSS = u"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>%s</title>
    <link>%s</link>
    <description>%s</description>
    <language>ru-ru</language>
    <pubDate>%s</pubDate>
    %s
</channel>
</rss>
"""

    _RSS_ITEM = u"""
<item>
    <title>%s</title>
    <link>%s</link>
    <description>%s</description>
    <pubDate>%s</pubDate>
    <guid>%s</guid>
</item>
"""

    items = []
    posts = [p for p in pages if "blog" in p] # get all blog post pages
    posts.sort(key=lambda p: p.datetime, reverse=True)
    for p in posts:
        title = p.title.encode('utf-8').decode('cp1251')
        link = "%s/%s" % (SITE_URL.rstrip("/"), p.url)
        desc = p.get("description", "")
        date = time.mktime(time.strptime("%s +0300" % p.datetime, "%Y-%m-%d %H:%M %z"))  # 2015-07-01 16:03
        date = email.utils.formatdate(date)
        items.append(_RSS_ITEM % (title, link, desc, date, link))

    items = "".join(items)

    title = SITE_NAME
    link = ''.join([SITE_URL.rstrip('/'), '/blog/'])
    desc = SITE_DESCRIPTION
    date = email.utils.formatdate()

    rss = _RSS % (title, link, desc, date, items)

    fp = open(os.path.join(output, "rss.xml"), 'w')
    fp.write(rss)
    fp.close()


# sitemap

def hook_preconvert_sitemap():
    _SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    %s
</urlset>
    """

    _SITEMAP_URL = """
<url>
    <loc>%s/%s</loc>
    <lastmod>%s</lastmod>
</url>
    """
    date = datetime.strftime(datetime.now(), "%Y-%m-%d")
    urls = []
    for p in pages:
        urls.append(_SITEMAP_URL % (SITE_URL.rstrip("/"), p.url, date))
    fname = os.path.join(options.project, "output", "sitemap.xml")
    fp = open(fname, 'w')
    fp.write(_SITEMAP % "".join(urls))
    fp.close()
