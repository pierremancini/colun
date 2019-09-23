#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import re
import shutil
import csv
import xlsxwriter

import filter_def

from pprint import pprint


""" Traitement de la deuxième partie fichiers trio. """


def contain_RAS(tsv_file):
    """
        :param tsv_file: Path to tsv file.

    """

    # List contenant les infos lignes par lignes du .tsv
    csv_dict = []
    with open(tsv_file, 'r') as csvfile:
        dict_reader = csv.DictReader(csvfile, delimiter='\t')
        header = dict_reader.fieldnames
        for line in dict_reader:
            # pas de ligne avec uniquement des \t
            if ''.join(line.values()):
                if filter_def.RAS_1(line):
                    return True


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


def write_tabular(filepath, selection):
    """
        :param selection: Dictionnary of selected patient_id and corresponding n° anapath.
    """

    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet()

    row = 0
    for patient_id in selection:

        column = 0
        worksheet.write(row, column, patient_id)
        print('worksheet.write({}, {}, {})'.format(row, column, patient_id))
        for anapath in selection[patient_id]:
            column += 1
            worksheet.write(row, column, anapath)
            print('worksheet.write({}, {}, {})'.format(row, column, patient_id))
        row += 1

    workbook.close()


def write_files():

    write_list_xlsx(os.path.join(listes_folder, 'liste initiale.xlsx'), liste_initiale_trio)
    write_list_xlsx(os.path.join(listes_folder, 'liste initiale - non trio.xlsx'), liste_initiale_trio)

    # colon
    write_list_xlsx(os.path.join(listes_folder, 'colon', 'liste initiale colon - non trio.xlsx'), colon_liste_initiale_trio)
    write_list_xlsx(os.path.join(listes_folder, 'colon', 'colon after_KW250.xlsx'), colon_after_KW250)

    write_list_xlsx(os.path.join(listes_folder, 'colon', 'colon liste initiale - non trio - after_KW250.xlsx'), colon_liste_initiale_trio_before_KW250)

    write_list_xlsx(os.path.join(listes_folder, 'colon', 'colon RAS muté before_KW250.xlsx'), colon_RAS_mute_before_KW250)

    write_list_xlsx(os.path.join(listes_folder, 'colon', 'colon liste initiale - non trio - after_KW250 - RAS muté.xlsx'), colon_liste_initiale_trio_before_KW250_no_RAS_mute)

    # write_list_xlsx(os.path.join(listes_folder, 'colon', 'colon_echantillon_multiple_2em_set.xlsx'), echantillon_mult_colon)
    
    write_tabular(os.path.join(listes_folder, 'colon', 
        'tableau_colon_echantillon_multiple_2em_set.xlsx'), echantillon_mult_colon)

    write_list_xlsx(os.path.join(listes_folder, 'colon', 'colon_analyse_multiple.xlsx'), analyses_multiples_colon)

    # lung
    write_list_xlsx(os.path.join(listes_folder, 'lung', 'lung liste initiale - non trio.xlsx'), lung_liste_initiale_trio)

    # write_list_xlsx(os.path.join(listes_folder, 'lung', 'lung_echantillon_multiple_2em_set.xlsx'), echantillon_mult_lung)
    write_tabular(os.path.join(listes_folder, 'lung', 
        'tableau_lung_echantillon_multiple_2em_set.xlsx'), echantillon_mult_lung)

    write_list_xlsx(os.path.join(listes_folder, 'lung', 'lung_analyse_multiple.xlsx'), analyses_multiples_lung)


def get_dict_trio(base_dir):
    """ Create dictonnnary of files that should form trios.

        /!\ Fonction spécifique au type d'arborescence du dossier
        files_2em_partie. Ne peut pas être utilisée sur le 1er set.

        :return dict_trio: Dictionnaire des fichiers comme dans filter_trio.py

        Structure: {anapath: {folder_name:
            {'tsv':[tsv_filename],
            'vcf': ['vcf_filename'],
            'xls': ['xls_filename']}}

    """

    dict_trio = {}

    folders = os.listdir(base_dir)

    # Le n° anapath est déjà déterminé par le nom des dossiers
    for folder in folders:
        match = re.search(r'[^A-Za-z]([A-Za-z]{1,2}[0-9]{1,3})', folder)
        try:
            anapath = match.group(1)
        except AttributeError as e:
            raise e

        dict_trio.setdefault(anapath, {})

        files = os.listdir(os.path.join(base_dir, folder))

        dict_trio[anapath].setdefault(folder, {})

        for file in files:
            extension = file.split('.')[-1]
            dict_trio[anapath][folder].setdefault(extension, []).append(file)

    return dict_trio


def get_anapath_list(file_path):

    anapath_list = []

    with open(file_path, 'r') as f:
        for line in f:
            anapath = line.replace("\n", '')
            match_iter = re.finditer(r"-F$", anapath)
            for match in match_iter:
                if match is not None:
                    anapath = anapath.replace("-F", "")
            anapath_list.append(anapath)

    return anapath_list


if __name__ == '__main__':


    base_dir = 'data/files_2em_partie'

    # output folder
    output_folder = 'data/chosen_2em_partie'
    listes_folder = 'data/listes_2em_partie'

    # On écrase l'ancien dossier output_folder
    try:
        shutil.rmtree(output_folder)
    except FileNotFoundError:
        print('Creation du dossier {}'.format(output_folder))
    else:
        print('Ecrasement du dossier {}'.format(output_folder))
    finally:
        os.mkdir(output_folder)
        os.mkdir(os.path.join(output_folder, 'colon'))
        os.mkdir(os.path.join(output_folder, 'lung'))
        os.mkdir(os.path.join(output_folder, 'colon', 'RAS'))
        os.mkdir(os.path.join(output_folder, 'colon', 'KW250'))
        os.mkdir(os.path.join(output_folder, 'colon', 'multiples'))
        os.mkdir(os.path.join(output_folder, 'lung', 'multiples'))


    # On écrase l'ancien dossier listes_folder
    try:
        shutil.rmtree(listes_folder)
    except FileNotFoundError:
        print('Creation du dossier {}'.format(listes_folder))
    else:
        print('Ecrasement du dossier {}'.format(listes_folder))
    finally:
        os.mkdir(listes_folder)
        os.mkdir(os.path.join(listes_folder, 'colon'))
        os.mkdir(os.path.join(listes_folder, 'lung'))


    dict_trio = get_dict_trio(base_dir)

    colon_file = os.path.join('data', 'NGS échantillons COLON 2e partie.txt')
    lung_file = os.path.join('data', 'NGS échantillons POUMON 2e partie.txt')

    colon_anapath = get_anapath_list(colon_file)
    lung_anapath = get_anapath_list(lung_file)


    # A partir d'ici le script fait deux choses:
    # Trouve les échantillons et analyses multiples après filtrage
    # Créé les listes de n° anapath en fonction du résultat du filtrage

    # liste_initiale = [] # == à liste_initiale_trio
    # non_trio = [] # Vide

    # liste initiale - non trio
    liste_initiale_trio = []

    colon_liste_initiale_trio = []
    lung_liste_initiale_trio = []

    colon_after_KW250 = []

    # liste initiale - non trio - after_KW250
    colon_liste_initiale_trio_before_KW250 = []

    # RAS muté before KW250
    colon_RAS_mute_before_KW250 = []

    # liste initiale - non trio - after KW250 - RAS muté
    colon_liste_initiale_trio_before_KW250_no_RAS_mute = []

    # Copie de la structure de dict_trio
    # pour visualiser les multiples restant après filtrage RAS
    # Structure: {anapath: {folder_name:
    #    {'tsv':[tsv_filename], 'vcf': ['vcf_filename'], 'xls': ['xls_filename']}}
    filtered_dict_trio = {'colon': {}, 'lung': {}}

    for anapath in dict_trio:

        liste_initiale_trio.append(anapath)

        for folder in dict_trio[anapath]:

            for tsv_file in dict_trio[anapath][folder]['tsv']:
                # Colon
                if anapath in colon_anapath:

                    # Données cliniques plus vieilles -> on garde
                    if anapath < 'KW250':
                        colon_liste_initiale_trio_before_KW250.append(anapath)

                        if contain_RAS(os.path.join(base_dir, folder, tsv_file)):
                            # Il faut enregistrer par fichier et pas par anapath
                            # pour permettre une detection des multiples

                            colon_RAS_mute_before_KW250.append(tsv_file)
                        else:
                            colon_liste_initiale_trio_before_KW250_no_RAS_mute.append(anapath)
                            filtered_dict_trio['colon'].setdefault(anapath, {}).setdefault(folder, {})
                            files = os.listdir(os.path.join(base_dir, folder))
                            for file in files:
                                extension = file.split('.')[-1]
                                filtered_dict_trio['colon'][anapath][folder].setdefault(extension, []).append(file)

                    # Trop récent on ne garde pas
                    else:
                        colon_after_KW250.append(anapath)

                # Lung
                else:
                    if anapath not in lung_anapath:
                        print('Erreur ni colon ni lung')
                        sys.exit()
                    else:
                        lung_liste_initiale_trio.append(anapath)
                        filtered_dict_trio['lung'].setdefault(anapath, {}).setdefault(folder, {})
                        files = os.listdir(os.path.join(base_dir, folder))
                        for file in files:
                            extension = file.split('.')[-1]
                            filtered_dict_trio['lung'][anapath][folder].setdefault(extension, []).append(file)

    analyses_multiples_colon = []
    analyses_multiples_lung = []

    for anapath in filtered_dict_trio['colon']:
        # Plusieurs dossiers
        # Echantillon multiples -> analyses multiples aussi
        if len(filtered_dict_trio['colon'][anapath]) > 1:
            analyses_multiples_colon.append(anapath)

        # Un dossier
        else:
            # Analyses multiples des échantillons non multiples
            for folder in filtered_dict_trio['colon'][anapath]:
                nb_tsv = len(set(filtered_dict_trio['colon'][anapath][folder]['tsv']))
                nb_vcf = len(set(filtered_dict_trio['colon'][anapath][folder]['vcf']))
                nb_xls = len(set(filtered_dict_trio['colon'][anapath][folder]['xls']))
                if nb_tsv > 1 or nb_vcf > 1:
                    analyses_multiples_colon.append(anapath)

    for anapath in filtered_dict_trio['lung']:
        # Plusieurs dossiers
        # Echantillon multiples -> analyses multiples aussi
        if len(filtered_dict_trio['lung'][anapath]) > 1:
            analyses_multiples_lung.append(anapath)

        # Un dossier
        else:
            # Analyses multiples des échantillons non multiples
            for folder in filtered_dict_trio['lung'][anapath]:
                nb_tsv = len(set(filtered_dict_trio['lung'][anapath][folder]['tsv']))
                nb_vcf = len(set(filtered_dict_trio['lung'][anapath][folder]['vcf']))
                nb_xls = len(set(filtered_dict_trio['lung'][anapath][folder]['xls']))
                if nb_tsv > 1 or nb_vcf > 1:
                    analyses_multiples_lung.append(anapath)

    # {patient_id: [anapath, ...]}
    patient_id_anapath = {}

    # {anapath: patient_id}
    anapath_patient_id = {}

    # {patient_id: [anapath, ...]}
    echantillon_mult_colon = {}
    echantillon_mult_lung = {}

    with open('data/corresp_patientid_anapath09-11-17.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            anapath = row[0]
            patient_id = row[1]
            patient_id_anapath.setdefault(patient_id, []).append(anapath)
            anapath_patient_id[anapath] = patient_id

    # Nom de variable plus court pour la lisibilité
    colon_selected = colon_liste_initiale_trio_before_KW250_no_RAS_mute

    # Comme patient_id_anapath sauf que les n° anapath sont tous des colon de la liste de selection
    colon_patient_id_anapath = {}
    # Comme patient_id_anapath sauf que les n° anapath sont tous des lung de la liste de selection
    lung_patient_id_anapath = {}

    for patient_id in patient_id_anapath:
        for anapath in patient_id_anapath[patient_id]:
            if anapath in colon_selected:
                colon_patient_id_anapath.setdefault(patient_id, []).append(anapath)
            elif anapath in lung_liste_initiale_trio:
                lung_patient_id_anapath.setdefault(patient_id, []).append(anapath)

    # Création de echantillon_mult_colon et echantillon_mult_lung
    for patient_id in colon_patient_id_anapath:
        if len(set(colon_patient_id_anapath[patient_id])) > 1:
            echantillon_mult_colon[patient_id] = list(set(colon_patient_id_anapath[patient_id]))

    for patient_id in lung_patient_id_anapath:
        if len(set(lung_patient_id_anapath[patient_id])) > 1:
            echantillon_mult_lung[patient_id] = list(set(lung_patient_id_anapath[patient_id]))

    write_files()

    # Détermine les échantillons multiple 1er/2em set en comparant les patient_id communs
    # entre les deux sets
    set1_patientid = {'colon': [], 'lung': []}

    # Fichiers fournis par Emmanuel K:
    # Liste des NIP/patient_id du 1er set
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

    list_patient_id_set2_colon = [patient_id for patient_id in colon_patient_id_anapath]
    list_patient_id_set2_colon = set(list_patient_id_set2_colon)

    list_patient_id_set2_lung = [patient_id for patient_id in lung_patient_id_anapath]
    list_patient_id_set2_lung = set(list_patient_id_set2_lung)

    print('list_patient_id_set2_colon')
    print(list_patient_id_set2_colon)
    print('list_patient_id_set2_lung')
    print(list_patient_id_set2_lung)
    print()

    print('set(set1_patientid[\'colon\'])')
    print(set(set1_patientid['colon']))

    print('set(set1_patientid[\'lung\'])')
    print(set(set1_patientid['lung']))

    print('list_patient_id_set2_colon & set(set1_patientid[\'colon\'])')
    print(list_patient_id_set2_colon & set(set1_patientid['colon']))
    print('list_patient_id_set2_lung & set(set1_patientid[\'lung\'])')
    print(list_patient_id_set2_lung & set(set1_patientid['lung']))
