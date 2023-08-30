#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, tempfile, requests, json, time, difflib

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
            print('处理文件: {}'.format(fullpath))
            metadata = readMetadata(fullpath)

            if 'lyrics' in metadata:
                lyrics = metadata['lyrics']
                lrcFile = os.path.splitext(fullpath)[0] + '.lrc'
                with open(lrcFile, 'w') as f:
                    f.write(lyrics)
                print('\t写入歌词文件: {}'.format(lrcFile))
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
                    print('\t下载歌词文件: {}'.format(lrcFile))
                else:
                    nolrcFile = os.path.splitext(fullpath)[0] + '.nolrc'
                    # 创建空文件
                    open(nolrcFile, 'w').close()

                    print('\t未找到歌词: {} - {}'.format(artist, title))

            

def downloadLyrics(artist, title, album):
    keyword = title is not None and title
    keyword += artist is not None and ' ' + artist
    keyword += album is not None and ' 《' + album + '》'

    print('\t搜索歌词: {}'.format(keyword))
    searchUrl = 'http://192.168.1.29:51100/search?keywords={}'.format(keyword)
    # 发送请求
    r = requests.get(searchUrl)

    if r.status_code != 200:
        print('\t请求失败: {}'.format(r.status_code))
        return
    
    # 解析返回的json
    result = json.loads(r.text)

    if 'result' not in result or 'songs' not in result['result'] or len(result['result']['songs']) == 0:
        print('\t未找到歌曲: {}'.format(r.text))
        return

    # id = result['result']['songs'][0]['id']
    id = -1
    for song in result['result']['songs']:
        song_name = song['name']
        # 根据相似度判断是否是同一首歌
        similarity = difflib.SequenceMatcher(None, song_name, title).quick_ratio()
        if similarity > 0.8:
            id = song['id']
            break

    if id == -1:
        id = result['result']['songs'][0]['id']

    lyricUrl = 'http://192.168.1.29:51100/lyric?id={}'.format(id)

    r = requests.get(lyricUrl)

    if r.status_code != 200:
        print('\t请求失败: {}'.format(r.status_code))
        return
    
    # 解析返回的json
    result = json.loads(r.text)

    if 'lrc' not in result or 'lyric' not in result['lrc']:
        print('\t未找到歌词: {}'.format(r.text))
        return

    lyric = result['lrc']['lyric']

    # 休眠300ms，防止请求过快
    time.sleep(0.3)
    # time.sleep(1)

    return lyric

def hasLyricsFile(file):
    lrcFile = os.path.splitext(file)[0] + '.lrc'
    noLrcFile = os.path.splitext(file)[0] + '.nolrc'
    return os.path.exists(lrcFile) or os.path.exists(noLrcFile)

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
            dict = line.split('=')
            if len(dict) < 2:
                continue
            key, value = dict[0], dict[1] 
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
