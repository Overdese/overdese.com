title: Архив
keywords: 
description: 
---


<div class="row">
     <div class="col-md-12 col-xs-12">
         <h1>Полный архив постов</h1>
     </div>
</div>

<!--% 
import datetime

posts = [p for p in pages if "blog" in p]
year = 0000
posts.sort(key=lambda p: p.datetime, reverse=True)

for post in posts:
    post_dt = time.strptime("%s" % post.datetime, "%Y-%m-%d %H:%M")    
    if year != post_dt.tm_year:
        year = post_dt.tm_year
        print("""<div class="row">
                     <div class="col-md-12 col-xs-12">
                         <h2>%d</h2>
                     </div>
                </div>""" % year)
               
    print("""<div class="row">
                 <div class="col-md-12 col-xs-12">
                     <p>%d-%02d-%02d <strong><a href="%s">%s</a></strong></p>
                 </div>             
             </div>""" % (post_dt.tm_year, post_dt.tm_mon, post_dt.tm_mday, fix_url(post["url"]), post["title"]))
%-->