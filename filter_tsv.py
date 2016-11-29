#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil, re, sys, csv

""" Tri des fichiers .tsv en fonction   """


def int_csv(string):
    """ Surcouche du cast int() pour accpeter les valeurs NA commme valeur False. """

    if (string == 'NA') | (string == ''):
        return False
    else:
        return int(string)


def float_csv(string):
    """ Surcouche du cast float() pour accpeter les valeurs NA commme valeur False. """

    if (string == 'NA') | (string == ''):
        return False
    else:
        return float(string)


def apply_filter(csv_dict):
    """ Apply filter on csv row given in first argument.

    Conditions:
    1ere combinaison:
    Pos coverage >200
    ET
    Var freq >2 (%)
    ET
    1000G_ALL_AF <0.01
    ET
    Clinvar: Clinsig=Pathogenic OU Drug response OU Likely pathogenic

    2eme combinaison:
    Pos coverage >200
    ET
    Var freq >5 (%)
    ET
    1000G_ALL_AF <0.01
    ET
    Clinvar: Clinsig= Uncertain significance OU Conflicting interpretations of pathogenicity OU Unknown OU NA"""

    valid = Trues

    # Conditions communes
    if (int(csv_dict['Pos.Cov.']) < 200) | (float_csv(csv_dict['1000G_ALL_AF']) > 0.01):
        valid = False

    # 1er cas

    if int(csv_dict['Var.freq.']) < 2:
        valid = False

    clinvar_ok = False
    for w in ['Pathogenic', 'Drug response', 'Likely pathogenic']:
        if w in csv_dict['CLINVAR']:
            clinvar_ok = True
            break

    if not clinvar_ok:
        valid = clinvar_ok

    # 2em cas

    if not valid:

        if int(csv_dict['Var.freq.']) < 5:
            valid = False

        clinvar_ok = False
        for w in ['Uncertain significance', 'Conflicting interpretations of pathogenicity',
                'Unknown', 'NA', '']:
            if w in csv_dict['CLINVAR']:
                clinvar_ok = True
                break

        if not clinvar_ok:
            valid = clinvar_ok

    return valid


if __name__ == '__main__':

    # Dossier à traiter, donné en 1er argument du script
    in_dir = sys.argv[1]

    liste_file_name = os.listdir(in_dir)

    csv_dict = []

    for file_name in liste_file_name:
        iter = re.finditer(r"annotation.*\.tsv$", file_name)
        for match in iter:
            if match is not None:
                with open(os.path.join(in_dir, file_name), 'rb') as csvfile:
                    dict_reader = csv.DictReader(csvfile, delimiter='\t')
                    for line in dict_reader:
                        print("Line valide: {rep}".format(rep=csv_dict))
                        if apply_filter(line):
                            csv_dict.append(line)
            
                    
                    