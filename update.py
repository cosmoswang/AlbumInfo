#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from plexapi.server import PlexServer
import requests
import logging as log

def main():
    plex = PlexServer()
    music = plex.library.section('音乐')

    for album in music.albums():
        # if album.summary == None or album.summary == '':
        #     continue
        # print('{} - {}'.format(album.title, album.artist().title, album.summary))

        print('updating album info: {} - {}'.format(album.title, album.artist().title), end=' | ')
        album_name, album_company, summay = fetchAlbumInfo(album)
        if album_name == None:
            print('no info found')
            log.warning('no info found: {} - {}'.format(album.title, album.artist().title))
            continue

        print('info fetched', end=' | ')

        album.edit(**{'summary.value': summay})
        album.edit(**{'summary.locked': 1})

        print('summary updated', end=' | ')

        if album_company != None and album_company != '':
            album.edit(**{'studio.value': album_company})
            album.edit(**{'studio.locked': 1})
            print('company updated', end=' | ')
        else:
            print('no company', end=' | ')

        print('done')
        log.info('album info updated: {} - {}'.format(album.title, album.artist().title))

def fetchAlbumInfo(album):
    search_str = None
    if type(album) == ''.__class__:
        search_str = album
    else:
        search_str = '{} {}'.format(album.title, album.artist().title)

    # search album
    # url = 'https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={}&type=10&offset=0&total=true&limit=20'.format(album)
    url = 'http://192.168.1.29:51100/search?keywords={}&type=10'.format(search_str)
    r = requests.get(url)
    log.debug('search result:')
    log.debug(r.text)
    
    info = None
    all_info = r.json()['result']['albums']

    if len(all_info) == 0:
        return (None, None, None)

    if type(album) == ''.__class__:
        info = all_info[0]['id']
    else:
        for data in all_info:
            if data['name'] == album.title and data['artist']['name'] == album.artist().title:
                info = data['id']
                break

        if info == None:
            info = all_info[0]['id']

    # fetch album info
    # url = 'https://music.163.com/api/album/{}?ext=true&id={}&offset=0&total=true&limit=20'.format(info, info)
    url = 'http://192.168.1.29:51100/album?id={}'.format(info)
    r = requests.get(url)
    log.debug('album info:')
    log.debug(r.text)
    album_name = r.json()['album']['name']
    album_company = r.json()['album']['company']
    summay = r.json()['album']['description']

    return (album_name, album_company, summay)


if __name__ == '__main__':
    log.basicConfig(level=log.WARN)
    main()
    # fetchAlbumInfo('天空 王菲')