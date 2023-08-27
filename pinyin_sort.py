#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from plexapi.server import PlexServer
from pypinyin import lazy_pinyin, Style
from datetime import datetime
import sys

def test(timefile='time1.txt'):
    time = readTime(timefile)
    print(time)
    writeTime(datetime.now(), timefile)

def main(timefile='time.txt'):
    plex = PlexServer()

    movies = plex.library.section('电影')
    timefrom = readTime(timefile)
    log('timefrom: {}, timefile: {}'.format(timefrom, timefile))
    for section in plex.library.sections():
        if not filterSection(section):
            continue
        
        if section.type == 'movie':
            log('处理section: {} - {}'.format(section.title, section.type))
            process_movie_section(section, timefrom)
            process_movie_collection(section, timefrom)
        elif section.type == 'show':
            log('处理section: {} - {}'.format(section.title, section.type))
            process_show_section(section, timefrom)

    writeTime(datetime.now(), timefile)
        

def filterSection(section):
    return section.title in ['电影', '电视节目']
    

def process_movie_section(movies, timefrom):
    for movie in movies.search(filters={'updatedAt>>': timefrom}):
        log('处理movie: {} at {}'.format(movie.title, movie.updatedAt))
        if movie.guid.startswith('local://'):
            log('跳过movie: {} ({})'.format(movie.title, movie.guid))
            pass
        elif movie.guid.startswith('plex://'):
            if isTitleSortLocked(movie):
                log('跳过movie: {} (titleSort.locked)'.format(movie.title))
                continue

            title = movie.title
            sortedTitle = generateSortTitle(title)

            movie.edit(**{'titleSort.value': sortedTitle})
            movie.edit(**{'titleSort.locked': 1})
            log('处理movie: {} ({})'.format(movie.title, sortedTitle))
                        
        else:
            # log.warning('Unknown guid: {} - ({})'.format(movie.guid, movie.title))
            log('Unknown guid: {} - ({})'.format(movie.guid, movie.title))
            continue

def process_movie_collection(movies, timefrom):
    for collection in movies.collections():
        if timefrom > collection.updatedAt:
            continue

        if isTitleSortLocked(collection):
            log('跳过collection: {} (titleSort.locked)'.format(collection.title))
            continue

        sortedTitle = generateSortTitle(collection.title)

        collection.editSortTitle(sortedTitle)
        log('处理collection: {} ({})'.format(collection.title, sortedTitle))
        
def process_show_section(shows, timefrom):
    for show in shows.search(filters={'updatedAt>>': timefrom}):
        log('处理show: {} at {}'.format(show.title, show.updatedAt))
        if show.guid.startswith('local://'):
            log('跳过show: {} ({})'.format(show.title, show.guid))
            pass
        elif show.guid.startswith('plex://') or show.guid.startswith('com.plexapp.agents.themoviedb://') or show.guid.startswith('com.plexapp.agents.none://') or show.guid.startswith('com.plexapp.agents.thetvdb://'):
            if isTitleSortLocked(show):
                log('跳过show: {} (titleSort.locked)'.format(show.title))
                continue

            title = show.title
            sortedTitle = generateSortTitle(title)

            show.edit(**{'titleSort.value': sortedTitle})
            show.edit(**{'titleSort.locked': 1})
            log('处理show: {} ({})'.format(show.title, sortedTitle))
                        
        else:
            # log.warning('Unknown guid: {} - ({})'.format(show.guid, show.title))
            log('Unknown guid: {} - ({})'.format(show.guid, show.title))
            continue

def generateSortTitle(title):
    title = title.lower()
    sortedTitle = ''
    for c in title:
        pinyin = lazy_pinyin(c, style=Style.TONE3, errors='ignore')
        if len(pinyin) == 0:
            sortedTitle += c
        else:
            sortedTitle += '{:#<7}'.format(pinyin[0])[:7].upper()

    return sortedTitle[:50]

def readTime(timefile):
    try:
        with open(timefile, 'r') as f:
            str = f.read()
            return datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    except FileNotFoundError:
        return datetime(year=1990, month=1, day=1, hour=0, minute=0, second=0)
    
def writeTime(time, timefile):
    with open(timefile, 'w') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S'))

def isTitleSortLocked(movie):
    for f in movie.fields:
        if f.name == 'titleSort':
            return f.locked
        
def log(msg):
    print('[{}]:{}'.format(datetime.now(), msg))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
