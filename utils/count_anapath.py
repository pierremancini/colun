#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, re, shutil

if __name__ == '__main__':


    in_dir = sys.argv[1]

    liste_file_name = os.listdir(in_dir)

    # Structure: {anapth1: nb, anapath2: nb, ...}
    dict_count = {}

    for file_name in liste_file_name:

        iter_anapath = re.finditer(r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*", file_name)
        for match_anapath in iter_anapath:
            if match_anapath is not None:
                dict_count.setdefault(match_anapath.group(1), []).append(match_anapath.group(1))

    print(dict_count)
    print(len(dict_count))