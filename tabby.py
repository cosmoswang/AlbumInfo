#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from plexapi.server import PlexServer
from datetime import datetime


def main():
    server = PlexServer()
    shows = server.library.section('电视节目')
    for show in shows.all():
        print(show.title)

if __name__ == '__main__':
    main()
