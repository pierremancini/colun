#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil, re, sys, csv, itertools

""" Tri des fichiers .tsv en fonction   """


def float_csv(string):
    """ Surcouche du cast float() pour accpeter les valeurs NA commme valeur False. """

    if string == 'NA':
        return 0
    else:
        return float(string)


def get_clinsig(clinvar):
    """ Extrait les différentes valeurs CLINSIG de la chaine de caractères CLINVAR. """

    list_clinsig = []

    # On prend la chaine entre CLINSIG= et le 1er ;
    match = re.match(r'CLINSIG=([^;]+)', clinvar)
    if match is not None:
        clinsig = match.group(1)
    else:
        clinsig = ''

    list_clinsig = clinsig.split('|')

    return list_clinsig


def compare_clinsig_voc(list_clinsig, voc):
    """ Compare clinsig worlds list with controlled vocabulary.

        Return False if there is no match
        Else return True
    """

    s = set(list_clinsig) & set(voc)

    if len(s) == 0:
        return False
    else:
        return True


def apply_filter(line):
    """ Apply filter on csv row given in first argument. """

    valid = True

    list_clinsig = get_clinsig(line['CLINVAR'])

    # Conditions communes
    if (int(line['Pos.Cov.']) < 200) | (float_csv(line['1000G_ALL_AF']) > 0.01):
        valid = False

    # 1er cas
    if int(line['Var.freq.']) < 2:
        valid = False

    clinvar_ok = compare_clinsig_voc(list_clinsig, ['pathogenic', 'drug-response', 'likely-pathogenic'])

    if not clinvar_ok:
        valid = clinvar_ok

    # 2em cas

    if not valid:

        if int(line['Var.freq.']) < 5:
            valid = False

        clinvar_ok = compare_clinsig_voc(list_clinsig, ['uncertain-significance',
            'conflicting-interpretations-of-pathogenicity', 'unknown', 'NA', ''])

        if not clinvar_ok:
            valid = clinvar_ok

    return valid


if __name__ == '__main__':

    # Dossier à traiter, donné en 1er argument du script
    in_dir = sys.argv[1]
    out_dir = 'filter_tsv_out'

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    liste_file_name = os.listdir(in_dir)

    for file_name in liste_file_name:
        iter = re.finditer(r"annotation.*\.tsv$", file_name)
        for match in iter:
            if match is not None:
                csv_dict = []
                with open(os.path.join(in_dir, file_name), 'rb') as csvfile:
                    dict_reader = csv.DictReader(csvfile, delimiter='\t')
                    header = dict_reader.fieldnames
                    for line in dict_reader:
                        # pas de ligne avec uniquement des \t
                        if ''.join(line.values()):
                            if apply_filter(line):
                                csv_dict.append(line)
                with open(os.path.join(out_dir, file_name), 'wb') as f:
                    w = csv.DictWriter(f, delimiter='\t', fieldnames=header)
                    w.writeheader()
                    for line in csv_dict:
                        w.writerow(line)
