#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, tempfile, requests, json, time

temp_metadata_file = os.path.join(tempfile.gettempdir(), 'plex_metadata.txt')

def main(path):
    # 遍历目录
    for root, dirs, files in os.walk(path):
        for file in files:
            if not isMusicFile(file):
                continue

            fullpath = os.path.join(root, file)

            if hasLyricsFile(fullpath):
                continue

            # 读取元数据
            metadata = readMetadata(fullpath)

            if 'lyrics' in metadata:
                lyrics = metadata['lyrics']
                lrcFile = os.path.splitext(fullpath)[0] + '.lrc'
                with open(lrcFile, 'w') as f:
                    f.write(lyrics)
                print('写入歌词文件: {}'.format(lrcFile))
            else:
                ## 从网上下载歌词
                artist = metadata['artist'] if 'artist' in metadata else None
                title = metadata['title'] if 'title' in metadata else None
                album = metadata['album'] if 'album' in metadata else None
                lyrics = downloadLyrics(artist, title, album)
                if lyrics is not None:
                    lrcFile = os.path.splitext(fullpath)[0] + '.lrc'
                    with open(lrcFile, 'w') as f:
                        f.write(lyrics)
                    print('下载歌词文件: {}'.format(lrcFile))
                else:
                    print('未找到歌词: {} - {}'.format(artist, title))

            

def downloadLyrics(artist, title, album):
    keyword = title is not None and title
    keyword += artist is not None and ' ' + artist
    keyword += album is not None and ' ' + album

    searchUrl = 'http://192.168.1.29:51100/search?keywords={}'.format(keyword)
    # 发送请求
    r = requests.get(searchUrl)

    if r.status_code != 200:
        print('请求失败: {}'.format(r.status_code))
        return
    
    # 解析返回的json
    result = json.loads(r.text)

    id = result['result']['songs'][0]['id']

    lyricUrl = 'http://192.168.1.29:51100/lyric?id={}'.format(id)

    r = requests.get(lyricUrl)

    if r.status_code != 200:
        print('请求失败: {}'.format(r.status_code))
        return
    
    # 解析返回的json
    result = json.loads(r.text)

    lyric = result['lrc']['lyric']

    # 休眠一秒钟
    time.sleep(1)

    return lyric

def hasLyricsFile(file):
    lrcFile = os.path.splitext(file)[0] + '.lrc'
    return os.path.exists(lrcFile)

def readMetadata(file):
    os.system('ffmpeg -i "{}" -f ffmetadata -y -loglevel error "{}"'.format(file, temp_metadata_file))
    with open(temp_metadata_file, 'r') as f:
        metadata_string = f.read()
        
    os.remove(temp_metadata_file)

    # 解析ffmpeg输出的元数据
    # ;FFMETADATA1
    # track=02
    # album=陌生人
    # album_artist=蔡健雅
    # title=无底洞
    # artist=蔡健雅
    # date=2003
    # encoder=Lavf60.3.100
    metadata = {}
    metadata_string = metadata_string.replace('\\\n', '#LINEBREAK#')
    for line in metadata_string.split('\n'):
        if '=' in line:
            key, value = line.split('=')
            metadata[key.lower()] = value.replace('#LINEBREAK#', '\n')

    return metadata



def isMusicFile(file):
    musicExt = ['.mp3', '.flac', '.ape', '.wav', '.m4a']
    return file.endswith(tuple(musicExt))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        # print('Usage: {} <path>'.format(sys.argv[0]))
        main('/Volumes/Music/Music/陈小春/绝对收藏/disc2')
