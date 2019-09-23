#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import re
import csv

import xlsxwriter

from pprint import pprint


def write_list_xlsx(filepath, liste):

    # Pas de valeur dupliquées
    set_list = set(liste)
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet()
    row = 0
    for item in set_list:
        worksheet.write(row, 0, item)
        row += 1

    workbook.close()


path_1er_set = 'data/Grille de recueil poumon 1er set patient rectifiée par provenance.csv'
path_2em_set = 'data/4-lung 2e set - non trio - éch surnuméraires.csv'
path_EGFR = 'data/Liste des mutés EGFR à exclure des lung sur les 2 sets de patients.csv'

set_1er = []
set_2em = []
EGFR = []

# Dictonnaire pour construire le fichier join_tsv, pour utiliser
# l'outil http://ib101b/html/tools/join_tsv/join_tsv.html
# {EGFR: [sample_id], noEGFR:[sample_id]}
join_dict = {}

# Pour le 1er set
# [(old, corrected)]
sample_id_corresp = []

# 1er set
with open(path_1er_set, 'r', encoding='utf-8') as file:
    dict_reader = csv.DictReader(file, delimiter='\t')
    for row in dict_reader:
        match = re.search(r'([A-Za-z]{1,2}\s*[0-9]{1,3})-?.*$', row['SampleId'])

        sample_id = match.group(1).replace(' ', '')
        set_1er.append(sample_id)

        join_dict.setdefault(sample_id, {'old': []})
        join_dict[sample_id]['old'].append(row['SampleId'])

# 2em set
with open(path_2em_set, 'r') as file:
    simple_reader = csv.reader(file, delimiter='\t')
    for row in simple_reader:
        set_2em += row

# liste des EGFR à enlever des sets
with open(path_EGFR, 'r') as file:
    simple_reader = csv.reader(file, delimiter='\t')

    # On passe le titre qui est dans la 1er cellule
    next(simple_reader)
    for row in simple_reader:
        EGFR += row

set_1er = set(set_1er)
set_2em = set(set_2em)
EGFR = set(EGFR)

set_1er_no_EGFR = list(set_1er - EGFR)
set_2em_no_EGFR = list(set_2em - EGFR)
set_1er_EGFR = list(set_1er & EGFR)
set_2em_EGFR = list(set_2em & EGFR)

for sample_id in set_1er:
    if sample_id in set_1er_no_EGFR:
        join_dict[sample_id]['EGRFStatus'] = 'not EGFR'
    elif sample_id in set_1er_EGFR:
        join_dict[sample_id]['EGRFStatus'] = 'is EGFR'
    else:
        raise ValueError('Sample id neither EGFR or not EGFR.')


with open('data/join_tsv_noEGFR_1set.tsv', 'w') as file:
    fieldnames = ['SampleId', 'EGRFStatus']
    dictwriter = csv.DictWriter(file, delimiter='\t', fieldnames=fieldnames)
    for sample_id in join_dict:
        # On utilise les sample_id brut non coriger pour avoir la bonne correspondance dans
        # le fichier .xlsx orginal de EK
        # (Grille de recueil poumon 1er set patient rectifiée par provenance.xlsx)

        for sample_old in join_dict[sample_id]['old']:
            dictwriter.writerow({'SampleId': sample_old,
                'EGRFStatus': join_dict[sample_id]['EGRFStatus']})
        # print({'SampleId': join_dict[sample_id]['old'], 'EGRFStatus': join})

# print(set_1er_no_EGFR)
print('set_1er_no_EGFR')
print(set_1er_no_EGFR)
write_list_xlsx('data/1er_set_lung_no_EGFR.xlsx', set_1er_no_EGFR)

print('set_2em_no_EGFR')
print(set_2em_no_EGFR)
write_list_xlsx('data/set_2em_lung_no_EGFR.xlsx', set_2em_no_EGFR)

print('set_1er_EGFR')
print(set_1er_EGFR)
write_list_xlsx('data/set_1er_lung_EGFR.xlsx', set_1er_EGFR)

print('set_2em_EGFR')
print(set_2em_EGFR)
write_list_xlsx('data/set_2em_lung_EGFR.xlsx', set_2em_EGFR)
