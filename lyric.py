#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, tempfile

temp_metadata_file = os.path.join(tempfile.gettempdir(), 'plex_metadata.txt')

def main(path):
    # 遍历目录
    for root, dirs, files in os.walk(path):
        for file in files:
            if not isMusicFile(file):
                continue

            fullpath = os.path.join(root, file)

            # 读取元数据
            metadata = readMetadata(fullpath)

            if not 'lyrics' in metadata:
                print('{} - {} - {}'.format(metadata['artist'], metadata['title'], metadata['album']), end=' ')
            
                print(' lyrics: {}'.format('lyrics' in metadata))

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
        main('/Volumes/Music/Music/湖南卫视/歌手 2016')
