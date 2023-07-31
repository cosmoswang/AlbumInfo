#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from plexapi.server import PlexServer
from pypinyin import lazy_pinyin, Style
from datetime import datetime

def main():
    plex = PlexServer()

    movies = plex.library.section('电影')
    timefrom = readTime()
    log('timefrom: {}'.format(timefrom))
    for movie in movies.search(filters={'updatedAt>>': timefrom}):
        log('处理movie: {} at {}'.format(movie.title, movie.updatedAt))
        if movie.guid.startswith('local://'):
            log('跳过movie: {} ({})'.format(movie.title, movie.guid))
            pass
        elif movie.guid.startswith('plex://'):
            title = movie.title
            title = title.upper()
            sortedTitle = ''
            for c in title:
                pinyin = lazy_pinyin(c, style=Style.TONE3, errors='ignore')
                if len(pinyin) == 0:
                    sortedTitle += c
                else:
                    sortedTitle += '{:#<7}'.format(pinyin[0])[:7]

            sortedTitle = sortedTitle[:50]

            movie.edit(**{'titleSort.value': sortedTitle})
            movie.edit(**{'titleSort.locked': 1})
            log('处理movie: {} ({})'.format(movie.title, sortedTitle))
                        
        else:
            # log.warning('Unknown guid: {} - ({})'.format(movie.guid, movie.title))
            log('Unknown guid: {} - ({})'.format(movie.guid, movie.title))
            continue

def readTime():
    try:
        with open('time.txt', 'r') as f:
            str = f.read()
            return datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    except FileNotFoundError:
        return datetime(year=1990, month=1, day=1, hour=0, minute=0, second=0)
    
def writeTime(time):
    with open('time.txt', 'w') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S'))
        
def log(msg):
    print('[{}]:{}'.format(datetime.now(), msg))

if __name__ == '__main__':
    main()