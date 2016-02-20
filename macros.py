# coding: utf-8
import re
import os
import email.utils
import time
from datetime import datetime
import markdown
import bleach
import json
import shutil
import codecs


SITE_NAME = '/home/overdese'
SITE_URL = 'http://overdese.com'
SITE_DESCRIPTION = 'NameError: name overdese is not defined'

# POSTS_PER_PAGE = 6
# MAX_POSTS_PAGES = 10


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

# fix posts urls
def hook_preconvert_fix_posts_url():
    for post in pages:
        if not post.url.startswith('/'):
            post.url = '/%s' % post.url

# label features

def get_post_labels(post):
    lst = list()
    for label in [x.strip() for x in post.labels.split(',') if x != '']:
        for post in [post for post in pages if 'label' in post if label == post.title]:
            lst.append(post)
    return lst



def make_labels():

    labels = list()           
    label_dict = dict()

    posts = [p for p in pages if "blog" in p]
    labels = list()

    for post in posts:        
        try:
            lst = [x.strip() for x in post['labels'].split(',') if x.strip() != '']
            labels.extend(lst)
            post.label_list = lst
        except KeyError:
            pass     

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


def hook_preconvert_labels():
    make_labels()

    # add game to menu
    for label in [l for l in pages if 'label' in l if l.title == 'how-to']:
        print('OK')
        label.keywords = "FUCK!!"
        print(dir(label.source))
        label.menu_position = 0
        # setattr(label, 'menu_position', 0)

# comments

def disqus_comments():
    return '''
    <div id="disqus_thread"></div>
    <script type="text/javascript">
        /* * * CONFIGURATION VARIABLES * * */
        var disqus_shortname = 'overdese-com';
        
        /* * * DON'T EDIT BELOW THIS LINE * * */
        (function() {
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();
    </script>
    <noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript" rel="nofollow">comments powered by Disqus.</a></noscript>
    '''

#  preview posts

# def hook_preconvert_post_preview():
#     for post in [p for p in pages if "blog" in p]:        
#         prev_lst = post.source.split('\n<!-- more -->\n')
#         prev = bleach.clean(markdown.markdown(prev_lst[0], extensions=['extra']), tags=[], strip=True)
#         if len(prev_lst) > 1:
#             post.preview = ''.join([prev, ' ...'])
#         else:
#             post.preview = truncate_str(prev, 250)

def get_preview_img(post):    
    pattern = re.compile(r'thumb.(jpg|jpeg|png|gif)')    
    for fn in os.listdir('/'.join(post.fname.split('\\')[:-1])):
        if pattern.match(fn) is not None:
            post_url = post.url.split('/')[:-1]
            post_url.append('.'.join(['thumb', pattern.match(fn).group(1)]))
            return '/'.join(post_url)
    return '/static/custom/img/no_previw.jpg'

# analytics

# google

def google_analytics():
    return '''
            <script>
                (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
                (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
                m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
                })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

                ga('create', 'UA-40751112-3', 'auto');
                ga('send', 'pageview');
            </script>
            '''

# posts json files generate

def make_js_posts(posts, posts_per_file, max_files, label=None):
    json_id = 0
    json_dict = dict(posts=list())
    post_id = 0    

    for post in posts:
        if json_id >= max_files:
            json_dict['posts'][:] = []
            break

        json_file = 'posts_%d.js' % json_id if label is None else '%s_posts_%d.js' % (label, json_id)

        json_dict['posts'].append({
            'title': post.title,
            'url': post.url,
            'datetime': post.datetime,
            'image': get_preview_img(post)
            })
        post_id += 1
        
        if not(post_id < posts_per_file):            
            with codecs.open(os.path.join('output', 'ajax', json_file), 'w', encoding='UTF-8') as tmp_f:
                json.dump(json_dict, tmp_f, ensure_ascii=False)
            json_dict['posts'][:] = []
            post_id = 0
            json_id += 1
    if json_dict['posts']:
        with codecs.open(os.path.join('output', 'ajax', json_file), 'w', encoding='UTF-8') as tmp_f:
            json.dump(json_dict, tmp_f, ensure_ascii=False)


def hook_postconvert_ajax_js():
    try:
        shutil.rmtree(os.path.join(output, 'ajax'))
    except OSError:
        pass
    os.makedirs(os.path.join(output, 'ajax'))
    
    posts = [p for p in pages if "blog" in p]
    posts.sort(key=lambda p: p.datetime, reverse=True)
    make_js_posts(posts[:60], 1, 10)

    for label in [l for l in pages if 'label' in l]:        
        posts = [p for p in pages if 'blog' in p if label.title in p.label_list]
        posts.sort(key=lambda p: p.datetime, reverse=True)
        make_js_posts(posts[:60], 1, 10, label.title)

# RSS
# def hook_postconvert_rss():
#     _RSS = u"""<?xml version="1.0" encoding="UTF-8" ?>
# <rss version="2.0">
# <channel>
#     <title>%s</title>
#     <link>%s</link>
#     <description>%s</description>
#     <language>ru-ru</language>
#     <pubDate>%s</pubDate>
#     %s
# </channel>
# </rss>
# """

#     _RSS_ITEM = u"""
# <item>
#     <title>%s</title>
#     <link>%s</link>
#     <description>%s</description>
#     <pubDate>%s</pubDate>
#     <guid>%s</guid>
# </item>
# """

#     items = []
#     posts = [p for p in pages if "blog" in p] # get all blog post pages
#     posts.sort(key=lambda p: p.datetime, reverse=True)
#     for p in posts:
#         title = p.title.encode('utf-8').decode('cp1251')
#         link = "%s/%s" % (SITE_URL.rstrip("/"), p.url)
#         desc = p.get("description", "")
#         date = time.mktime(time.strptime("%s +0300" % p.datetime, "%Y-%m-%d %H:%M %z"))  # 2015-07-01 16:03
#         date = email.utils.formatdate(date)
#         items.append(_RSS_ITEM % (title, link, desc, date, link))

#     items = "".join(items)

#     title = SITE_NAME
#     link = ''.join([SITE_URL.rstrip('/'), '/blog/'])
#     desc = SITE_DESCRIPTION
#     date = email.utils.formatdate()

#     rss = _RSS % (title, link, desc, date, items)

#     fp = open(os.path.join(output, "rss.xml"), 'w')
#     fp.write(rss)
#     fp.close()


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