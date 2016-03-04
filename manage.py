# coding: utf-8
import argparse
import os
from shutil import copy2
from pytils import translit
from datetime import datetime


def new_post(title, thumb=None):
    tmpl_list = ['extension', 'blank', 'post.md']
    if title is not None:
        if os.path.exists(os.path.join(*tmpl_list)):
            dt = datetime.now()
            path_list = ['input', 'blog', '%d' % dt.year, '%02d' % dt.month,
                         '%02d-%s' % (dt.day, translit.slugify(title)), 'index.md']
            try:
                os.makedirs(os.path.join(*path_list[:-1]))
            except OSError:
                print('Exist file. Choose another title.')
                return None

            with open(os.path.join(*tmpl_list), 'r', encoding='utf-8') as file_in:
                buff = file_in.read()
                with open(os.path.join(*path_list), 'w', encoding='utf-8') as file_out:
                    file_out.write(buff.format(title=title, datetime=dt.strftime('%Y-%m-%d %H:%M')))
            if thumb is not None:
                if thumb in show_thumbs(with_print=False):
                    src = list()
                    src.extend(tmpl_list[:-1])
                    src.append('thumb_%s.png' % thumb)
                    dst = list()
                    dst.extend(path_list[:-1])
                    dst.append('thumb_%s.png' % thumb)
                    copy2(os.path.join(*src), os.path.join(*dst))
        else:
            print('Template file missing')
    else:
        print('Need a title')


def show_thumbs(with_print=True):
    path_list = ['extension', 'blank']
    if os.path.exists(os.path.join(*path_list)):
        result = ['\tThumb name\t\tThumb filename']
        thumb_lst = list()
        for thumb in [e for e in os.listdir(os.path.join(*path_list))
                      if e.lower().endswith('.png') and e.lower().startswith('thumb_')]:
            result.append('\t%s\t\t%s' % (thumb.lower().replace('thumb_', '').replace('.png', ''), thumb.lower()))
            thumb_lst.append(thumb.lower().replace('thumb_', '').replace('.png', ''))
        if with_print:
            print('\n'.join(result))
        else:
            return thumb_lst


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--post', action='store_true', help='add new post')
    parser.add_argument('--title', action='store', help='title for post')
    parser.add_argument('--thumb', action='store', help='thumb for post')
    parser.add_argument('--show-thumb', action='store_true', dest='show_thumb', help='show all thumbnails')
    args = parser.parse_args()

    if args.post:
        new_post(args.title, args.thumb)
    elif args.show_thumb:
        show_thumbs()
    

if __name__ == '__main__':
    main()



