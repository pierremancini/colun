#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, shutil, re, sys


def list_vcf_files(dir):
    """ list vcf file name and output them in a text."""

    # Seul ne nom de fichier doit être donner 

    # On ne prend que les .vcf
    list = os.listdir(dir)
    file_list = [x for x in list if re.search(r'\.vcf$', x)]

    with open(dir + '_list.txt', 'w') as f:
        for file_name in file_list:
            f.write('{}\n'.format(file_name))


list_folder = ['doublons', 'new_vcf', 'non-trio', 'non-EK']
for folder in list_folder:
    list_vcf_files(os.path.join('filter_vcf_out', folder))
