#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import shutil
import os
import csv

# il faut extraire le numéro anapth du fichiers data_samples.txt de la study
# On en fait une liste

anapath_filter_trio = set()
# On liste les no-EK et new_vcf
list_files = os.listdir(os.path.join('data', 'filter_vcf_out_100', 'non-EK'))
for file_name  in list_files:
    iter_anapath = re.finditer(r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*", file_name)
    for match_anapath in iter_anapath:
        if match_anapath is not None:
            sample_id = match_anapath.group(1)
            anapath_filter_trio.add(sample_id)
list_files = os.listdir(os.path.join('data', 'filter_vcf_out_100', 'new_vcf'))
for file_name  in list_files:
    iter_anapath = re.finditer(r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*", file_name)
    for match_anapath in iter_anapath:
        if match_anapath is not None:
            sample_id = match_anapath.group(1)
            anapath_filter_trio.add(sample_id)


anapath_non_trio = []
list_files = os.listdir(os.path.join('data', 'filter_vcf_out_100', 'non-trio'))
for file_name  in list_files:
    iter_anapath = re.finditer(r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*", file_name)
    for match_anapath in iter_anapath:
        if match_anapath is not None:
            sample_id = match_anapath.group(1)
            anapath_non_trio.append(sample_id)

anapath_doublons = []
list_files = os.listdir(os.path.join('data', 'filter_vcf_out_100', 'doublons'))
for file_name  in list_files:
    iter_anapath = re.finditer(r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*", file_name)
    for match_anapath in iter_anapath:
        if match_anapath is not None:
            sample_id = match_anapath.group(1)
            anapath_doublons.append(sample_id)


anapath_EK_colon = []
anapath_EK_lung = []
# On lit les anapath listé par Emmanuel K
with open('data', 'NGS colon-lung échantillons COLONS_anapath.txt', 'r') as f:
    for line in f:
        anapath = line.replace("\n", '')
        match_iter = re.finditer(r"-F$", anapath)
        for match in match_iter:
            if match is not None:
                anapath = anapath.replace("-F", "")
        anapath_EK_colon.append(anapath)

with open('data', 'NGS colon-lung échantillons POUMONS_anapath.txt', 'r') as f:
    for line in f:
        anapath = line.replace("\n", '')
        match_iter = re.finditer(r"-F$", anapath)
        for match in match_iter:
            if match is not None:
                anapath = anapath.replace("-F", "")
        anapath_EK_lung.append(anapath)

cbio = []
with open('data', 'list_cbio', 'r') as f:
    for line in f:
        anapath = line.replace("\n", '')
        cbio.append(anapath)

# print('anapath_EK_colon')
# print(len(set(anapath_EK_colon)))
# # print(anapath_EK_colon)
# print('anapath_EK_lung')
# print(len(set(anapath_EK_lung)))
# print(anapath_EK_lung)


manquant = set(anapath_EK_colon + anapath_EK_lung) - set(cbio)

print('manquant & non_trio | doublons')
print(len(manquant & set(anapath_doublons + anapath_non_trio)))

# print('manquant & non_trio')
# print(len(manquant & set()))

# print('manquant & doublons')
# print(len(manquant & set()))
# On ne supprime les doublons des listes d'Emmanuel
#print(len(set(anapath_EK)))

# print('anapath_filter_trio - anapath_EK')
# print(len(set(anapath_filter_trio) - set(anapath_EK)))
# print(set(anapath_filter_trio) - set(anapath_EK))

# print('anapath_EK - anapath_filter_trio')
# print(len(set(anapath_EK) - set(anapath_filter_trio)))
# print(set(anapath_EK) - set(anapath_filter_trio))

# print('anapath_EK - anapath_filter_trio - anapath_non_trio - anapath_doublons')
# print(len(set(anapath_EK) - set(anapath_filter_trio) - set(anapath_non_trio) - set(anapath_doublons)))
# print(set(anapath_EK) - set(anapath_filter_trio) - set(anapath_non_trio) - set(anapath_doublons))
