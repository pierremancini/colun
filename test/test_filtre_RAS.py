#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import filter_def
import re
import csv
import sys


""" Script to test RAS filter on list of file. """

def extract_anapath(filename):
    """ Get anapath from filename. """

    try:
        m = re.search(r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*", filename)
        anapath = m.group(1)
    except AttributeError:
        anapath = None

    return anapath



# Aucune mutation RAS ne doit être détectée dans ces fichiers.
JH665_files = ['data/files_excluded/*****_*****_IonXpress_091.annotation.1011.tsv',
    'data/files_excluded/*****-*****_IonXpress_028.annotation.1003.tsv',
    'data/files_excluded/***** *****_IonXpress_049.annotation.1095.tsv']


# Ligne 5 de BELLOCQ-JH665_IonXpress_028.annotation.1003.tsv
test_JH665_line = {'1000G_AFR_AF': 'NA',
    '1000G_ASN_AF': 'NA',
    'Amplicon': '',
    '1000G_ALL_PROBS_AA:AB:BB': 'NA:NA:NA',
    '1000G_AMR_PROBS_AA:AB:BB': 'NA:NA:NA',
    'Chr': 'chr1',
    'Start_Position': '115258745',
    '1000G_ASN_PROBS_AA:AB:BB': 'NA:NA:NA',
    'Var.freq.': '5',
    'Type': 'missense',
    'POLYPHEN2_HDIV_INTERPRETATION': 'Benign',
    'POLYPHEN2_HDIV_SCORE': '0.26',
    'Gene': 'NRAS', 'Comm.Bio': '',
    'SIFT_INTERPRETATION': 'Damaging',
    'COSMIC': 'ID=COSM571;OCCURENCE=5(haematopoietic_and_lymphoid_tissue),1(skin)',
    '1000G_AFR_PROBS_AA:AB:BB': 'NA:NA:NA',
    'Var.Cov.': '42',
    'CLINVAR': 'NA',
    'c.': 'c.37G>A',
    'Region': 'exonic',
    '1000G_EUR_AF': 'NA',
    'Ref.NM': 'NM_002524',
    'SIFT_SCORE': '0.01',
    '1000G_EUR_PROBS_AA:AB:BB': 'NA:NA:NA',
    'ESPFreq': '',
    'Pos.Cov.': '931',
    'Var.seq': 'T',
    '1000G_AMR_AF': 'NA',
    'Ref.seq': 'C',
    'POLYPHEN2_HVAR_INTERPRETATION': 'Possibly_damaging',
    'POLYPHEN2_HVAR_SCORE': '0.52',
    '1000G_ALL_AF': 'NA',
    'exon': '2',
    'dbSNP': 'rs121434595',
    'p.': 'p.G13S'}


def test_line(test_line):


    # pas de ligne avec uniquement des \t
    if ''.join(test_line.values()):
        if filter_def.RAS_1(test_line):
            pass


def test_files(tested_files):

    list_RAS = []
    list_non_RAS =[]

    for filepath in tested_files:
        line_nb = 1
        try:
            with open(filepath, 'r') as csvfile:
                dict_reader = csv.DictReader(csvfile, delimiter='\t')
                header = dict_reader.fieldnames
                for line in dict_reader:
                    line_nb += 1
                    # pas de ligne avec uniquement des \t
                    if ''.join(line.values()):
                        if filter_def.RAS_1(line):
                            list_RAS.append({'filename': os.path.split(filepath)[1], 'line': line_nb})
                            print(line)

        except KeyError as e:
            print('{} n\'a pas de fichier tsv'.format(filepath))
            pass

    print('list_RAS')
    print(list_RAS)


test_files(JH665_files)