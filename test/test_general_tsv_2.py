#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import filter_def
import os
import csv
import re

""" Test du filtre filter_def.general_tsv_2 """
csv_dict = []

line_nb = 0


filenames = os.listdir('data/files_1er_2em_partie')


for filename in filenames:

    ext = filename.split('.')[-1:][0]

    if ext == 'tsv':

        print(filename)
        with open(os.path.join('data', 'files_1er_2em_partie', filename), 'rb') as csvfile:
            dict_reader = csv.DictReader(csvfile, delimiter='\t')
            header = dict_reader.fieldnames
            for line in dict_reader:
                line_nb += 1
                # pas de ligne avec uniquement des \t
                if ''.join(line.values()):
                    if filter_def.general_tsv_2(line):  # TODO: ce nouveau filtre est à tester
                        print('Ligne n° {} retenue'.format(line_nb))
                        csv_dict.append(line)
                    else:
                        print('Ligne n° {} non retenue'.format(line_nb))

            