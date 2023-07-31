#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from plexapi.server import PlexServer

def main():
    plex = PlexServer()

    movies = plex.library.section('电影')

    for movie in movies.all():
        print(movie)

if __name__ == '__main__':
    main()