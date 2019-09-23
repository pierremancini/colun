#!/usr/bin/env python3
# -*- coding: utf-8 -*-


""" Traitement des multiples du 1er et du 2em set de trio de fichiers. """


import os
import sys
import re
import shutil
import csv
import xlsxwriter

from pprint import pprint


# 1er set
colon_anapath_1er = []
lung_anapath_1er = []

with open('data/NGS COLONS_colon-lung échantillons anapath_cleaned_nodups_sorted.txt', 'r') as f:
    for line in f:
        anapath = line.replace("\n", '')
        match_iter = re.finditer(r"-F$", anapath)
        for match in match_iter:
            if match is not None:
                anapath = anapath.replace("-F", "")
        colon_anapath_1er.append(anapath)

with open('data/NGS POUMONS_colon-lung échantillons anapath_cleaned_nodups_sorted.txt', 'r') as f:
    for line in f:
        anapath = line.replace("\n", '')
        match_iter = re.finditer(r"-F$", anapath)
        for match in match_iter:
            if match is not None:
                anapath = anapath.replace("-F", "")
        lung_anapath_1er.append(anapath)

# 2em set
colon_anapath_2em = []
lung_anapath_2em = []

with open('data/NGS échantillons COLON 2e partie.txt', 'r') as f:
    for line in f:
        anapath = line.replace("\n", '')
        match_iter = re.finditer(r"-F$", anapath)
        for match in match_iter:
            if match is not None:
                anapath = anapath.replace("-F", "")
        colon_anapath_2em.append(anapath)

with open('data/NGS échantillons POUMON 2e partie.txt', 'r') as f:
    for line in f:
        anapath = line.replace("\n", '')
        match_iter = re.finditer(r"-F$", anapath)
        for match in match_iter:
            if match is not None:
                anapath = anapath.replace("-F", "")
        lung_anapath_2em.append(anapath)

set1_patientid = {'colon': [], 'lung': []}

with open('data/NIP 1er set/NIP colons 1er set.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        set1_patientid['colon'].append(row[0])
    set1_patientid['colon'] = set1_patientid['colon'][1:]

with open('data/NIP 1er set/NIP poumons 1er set.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        set1_patientid['lung'].append(row[0])
    set1_patientid['lung'] = set1_patientid['lung'][1:]

# Récupération des n° anapath du 1er et 2em set

