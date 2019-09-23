#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Faire une liste des mutés RAS uniquement à partir des anapath des colons. """

import os
import filter_def
import re
import csv
import sys


def extract_anapath(filename):
    """ Get anapath from filename. """

    try:
        m = re.search(r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*", filename)
        anapath = m.group(1)
    except AttributeError:
        anapath = None

    return anapath


def has_values(line):
    """ Return True is there is only tab in the line."""

    return ''.join(line.values())


# L'input de build_study_data.py : in_build_study
# Dans in_build_study/vcf:
# On extrait le n° anapath de chaque fichier
for file_name in os.listdir('data/in_build_study/vcf'):
    # On extrait le n° anapath de chaque fichier
    iter_anapath = re.finditer(r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*", file_name)
    for match_anapath in iter_anapath:
        if match_anapath is not None:
            sample_id = match_anapath.group(1)


list_colon = []
study_file = 'data/NGS colon-lung échantillons COLONS_anapath.txt'
# Création la liste des échantillons à sélectionner
with open(study_file, 'r') as f:
    for line in f:
        anapath = line.replace("\n", '')
        match_iter = re.finditer(r"-F$", anapath)
        for match in match_iter:
            if match is not None:
                anapath = anapath.replace("-F", "")
        list_colon.append(anapath)


in_dir = os.path.join('data', 'files_excluded')

# On ne liste que les fichiers, pas les dossiers
list = (file for file in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, file)))

dict_trio = {}
for file_name in list:
    match = re.search(r"(.*(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*)(?:(?:\.annotation\.)|(?:\.variantcaller\.))[0-9]{3,4}\.(.*)$", file_name)
    if match is not None:

        name_head = match.group(1)
        extension = match.group(3)

        dict_trio.setdefault(name_head, {})
        dict_trio[name_head][extension] = file_name

list_RAS = []

for name in dict_trio:
    header = None
    # List contenant les infos lignes par lignes du .tsv
    csv_dict = []
    try:
        with open(os.path.join(in_dir, dict_trio[name]['tsv']), 'r') as csvfile:
            dict_reader = csv.DictReader(csvfile, delimiter='\t')
            header = dict_reader.fieldnames
            for line in dict_reader:
                # pas de ligne avec uniquement des \t
                if ''.join(line.values()):
                    if filter_def.RAS_1(line):
                        list_RAS.append(extract_anapath(name))
    except KeyError as e:
        print('{} n\'a pas de fichier tsv'.format(name))
        pass

colon_RAS = set(list_RAS) & set(list_colon)
colon_RAS = [i for i in colon_RAS]

print(len(colon_RAS))
print(colon_RAS)

if os.path.exists('data/RAS.tsv'):
    os.remove('data/RAS.tsv')

with open('data/RAS.tsv', 'w') as file:
    header = ['muté RAS = {}'.format(len(colon_RAS))]
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(header)
    for row in colon_RAS:
        writer.writerow([row])
