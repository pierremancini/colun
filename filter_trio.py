#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil, re, sys, csv
import vcf
import argparse
import logging
import json
import filter_def
import itertools

from pprint import pprint

""" Tri des fichiers .tsv"""


def set_logger(logger_name, file_name, level):
    """ Set un logger en fonction du nom de fichier de log donné.

        :param level: exemple logging.DEBUG

    """

    # Création d'un formateur qui va ajouter le n°process, le temps et le niveau
    # à chaque message de log
    formatter = logging.Formatter('%(process)d :: %(asctime)s :: %(levelname)s :: %(message)s')

    # Création du logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # FileHandler
    handler = logging.FileHandler(file_name)
    handler.setLevel(level)
    handler.setFormatter(formatter)

    # StreamHandler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(stream_handler)

    return logger


def set_count_log():
    """ Mise en place du systeme de log dédié au décompte des fichiers vcf."""

    vcf_logger = set_logger('vcf_logger', 'count_vcf.log', logging.DEBUG)

    return vcf_logger


def extract_anapath(filename):
    """ Get anapath from filename. """

    try:
        m = re.search(r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*", filename)
        anapath = m.group(1)
    except AttributeError:
        anapath = None

    return anapath


def get_extension(filename):
    """ Get extension of filename. """

    extension = filename.split('.')[-1]

    return extension


def remove_useless(in_dir, out_dir="data/files_filtered"):
    """ Remove useless files from given directory.

    - Enlève tout les fichiers considéré comme inutile, c'est à dire les fichiers qui on dans leur nom un des éléments de la liste useless.
    - Créé un dossier "files_filtered" qui contiendra les fichiers utiles.
    - Retourne le nom du dossier créé
    """

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    useless = ['pcr', 'temoin', "test", "acrometrix", "acometrix", "control", "t+", ".cov.", "all_amplicon",
             "_robot_", "_manuel_", "_contamination_", "eeq", "blanc_"]
    for f in os.listdir(in_dir):
        if f:
            cp = True
            for u in useless:
                if u in f.lower():
                    cp = False
            if cp:
                shutil.copy(os.path.join(in_dir, f), os.path.join(out_dir, f))

    return out_dir


def select_from_doublons(list_doublons, path_PGM):
    """ Retourne une liste des filename à ne pas mettre à part et
        une liste de filename à mettre à part.

        :param path_PGM: Path to PGM folder containing three PGM files.
    """

    retenus = []
    non_retenus = []

    doublon_logger = set_logger('doublon_logger', 'doublon_selection.log', logging.DEBUG)
    # doublon_logger.info('developpement')

    def build_dict_anapath_pgm(list_pgm_files, PGM_path):
        """ Build dictionary : {anapath: pgm} """

        def get_pgm_anapath(line):
            """ Extract pgm's n° and filename."""

            line = line.split('/')

            # Extraction du pgm
            pgm = line[1]
            try:
                m = re.search(r"PGM-?([0-9]{3})-?", pgm)
                pgm_num = m.group(1)
            except AttributeError:
                pgm_split = pgm.split('PGM-')
                try:
                    pgm_num = pgm_split[1]
                except IndexError:
                    # print('IndexError pgm_split: ')
                    # print(pgm_split)
                    pgm_num = None

            file_name = line[-1].strip('\n')

            anapath = extract_anapath(file_name)

            return (anapath, pgm_num, file_name)

        # Structure:
        # {filename: pgm_num}
        dict_PGM = {}

        for pgm_file in list_pgm_files:
            with open(os.path.join(PGM_path, pgm_file), 'r') as f:
                dict_PGM_temp = {}
                for line in f:
                    anapath, pgm_num, file_name = get_pgm_anapath(line)
                    if anapath and pgm_num:
                        dict_PGM_temp.setdefault(file_name, pgm_num)
                    else:
                        # print(pgm_num)
                        pass

            dict_PGM.update(dict_PGM_temp)

        return dict_PGM

    PGM_path = os.path.join('data', 'PGM', '1er_2em')
    list_pgm_files = os.listdir(PGM_path)
    dict_PGM = build_dict_anapath_pgm(list_pgm_files, PGM_path)

    doublon_anapath_files = {}
    for filename in list_doublons:
        anapath = extract_anapath(filename)
        doublon_anapath_files.setdefault(anapath, []).append(filename)

    # sorted_doublon: <- doublon
    # { anapath: {pgm : [filenames]}
    sorted_doublon = {}

    for anapath in doublon_anapath_files:
        for filename in doublon_anapath_files[anapath]:
            pgm = dict_PGM[filename]

            sorted_doublon.setdefault(anapath, {}).setdefault(pgm, []).append(filename)

    def choose_file(anapath_dict):
        """
            :param anapath_dict: filename ayant le même numéro anapath

            Régles de tri:
            Si plus de un trio -> le trio avec le pgm le plus élevé est choisi
            Et
            Si le pgm le plus élevé correspond à un non trio -> log du nom des fichiers associés
            avec num anapath, tout ça tout ça
        """

        extensions = ['tsv', 'vcf', 'xls']
        retenus = []
        non_retenus = []

        # structure
        # {pgm: [file1, file2 ...], pgm: [file1, file2 ...]}
        for pgm in anapath_dict:
            nb_extensions = {'tsv': 0, 'vcf': 0, 'xls': 0}
            for filename in anapath_dict[pgm]:
                if get_extension(filename) in extensions:
                    nb_extensions[get_extension(filename)] += 1

        pgm_max = 0
        for pgm in anapath_dict:
            if pgm > pgm_max:
                pgm_max = pgm

        # le plus grand pgm correspond-il à un trio ?
        if len(anapath_dict[pgm_max]) < 3:
            # Message dans le log
            doublon_logger.info('----------')
            doublon_logger.info('Le plus grand PGM n\'est pas un trio:')
            doublon_logger.info(json.dumps(anapath_dict))
            doublon_logger.info('----------')

            # Tout les file du lot sont non_retenu
            non_retenus += [anapath_dict[pgm] for pgm in anapath_dict]

        else:
            retenus += anapath_dict[pgm_max]
            non_retenus += [sublist for pgm in anapath_dict for sublist in anapath_dict[pgm] if pgm != pgm_max]
            doublon_logger.info('----------')
            doublon_logger.info('Le plus grand PGM est choisi:')
            doublon_logger.info(json.dumps(anapath_dict[pgm_max]))
            doublon_logger.info('Les autres fichiers sont mis de coté:')
            doublon_logger.info(json.dumps(non_retenus))
            doublon_logger.info('----------')

        return (retenus, non_retenus)

    same_pgm = {}
    # Doublon avec le même PGM:
    doublon_logger.info('----------')
    doublon_logger.info('Doublons avec le même PGM:')
    for anapath in sorted_doublon:
        for pgm in sorted_doublon[anapath]:
            if len(sorted_doublon[anapath][pgm]) > 3:
                doublon_logger.info('PGM ' + pgm + ' :')
                for filename in sorted_doublon[anapath][pgm]:
                    same_pgm.setdefault(anapath, {}).setdefault(pgm, []).append(filename)

                    # Mettre les same_pgm dans non_retenus
                    # -> sous le format filename simple, ou {anapath: [filename]} ?
                    non_retenus.append(filename)
                    doublon_logger.info(filename)

    doublon_logger.info('----------')

    # sorted_doublon - same_pgm
    # pgm_diff = {}
    for anapath in sorted_doublon:
        if anapath not in same_pgm:
            item_retenus, item_non_retenus = choose_file(sorted_doublon[anapath])
            # Pour le debug/info pour Emmanuel, on peut utilise pgm_diff
            # pgm_diff = sorted_doublon[anapath]
            retenus += item_retenus
            non_retenus += item_non_retenus

    return (retenus, non_retenus)


def clean_trio(dir):
    """ Déplace les non-trio et doublons dans des dossiers apparts. """

    # Creation des dossiers pour les doublons et les non-trio
    if not os.path.exists(os.path.join(out_dir, 'doublons-non-retenus')):
        os.mkdir(os.path.join(out_dir, 'doublons-non-retenus'))
    if not os.path.exists(os.path.join(out_dir, 'non-trio')):
        os.mkdir(os.path.join(out_dir, 'non-trio'))

    list_doublons = []
    list_non_trio = []

    # Structure: {'name':{'tsv':tsv_filename, 'vcf': 'vcfc_filename', 'xls': 'xls_filename'}}
    dict_trio = {}

    liste_file_name = os.listdir(dir)

    # Tri des fichiers par extension
    for file_name in liste_file_name:

        # r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*"
        # old regex iter = re.finditer(r"([^\.]*)((?:\.annotation\.)|(?:\.variantcaller\.))[0-9]{3,4}\.(.*)$", file_name)
        match = re.search(r"(.*(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*)(?:(?:\.annotation\.)|(?:\.variantcaller\.))[0-9]{3,4}\.(.*)$", file_name)
        if match is not None:

            name_head = match.group(1)
            extension = match.group(3)

            dict_trio.setdefault(name_head, {}).setdefault(extension, []).append(file_name)

    for name in dict_trio:
        if set(dict_trio[name].keys()) != set(['tsv', 'xls', 'vcf']):

            # On stock les autres fichiers du même name
            # Mais il ne faut les stocker qu'une seule fois
            lists = [sublist for extension_temp in dict_trio[name] for sublist in dict_trio[name][extension_temp]]
            list_non_trio += lists

        else:
            for extension_temp in dict_trio[name]:
                if len(dict_trio[name][extension]) > 1:
                    lists = dict_trio[name][extension_temp]
                    list_doublons += lists

    # On a besoin des non_retenus et pas des retenus
    # car on ne déplacera que les non_retenu
    retenus, non_retenus = select_from_doublons(list_doublons, os.path.join(dir, 'PGM'))

    # Déplacement de tout les fichier dict_trio[name] dans le dossier 'doublon'
    # si ils n'ont pas déjà été déplacés
    for file_name in non_retenus:
        shutil.move(os.path.join(dir, file_name), os.path.join(dir, 'doublons-non-retenus', file_name))

    # Déplacement de tout les fichiers dict_trio[name] dans le dossier 'non-trio'
    # si ils n'ont pas déjà été déplacés
    for file_name in list_non_trio:
        shutil.move(os.path.join(dir, file_name), os.path.join(dir, 'non-trio', file_name))


def count_vcf(path_dir):
    """ Retourne le nombre de fichiers .vcf présent dans un dossier."""

    list = os.listdir(path_dir)
    nb_vcf = len([x for x in list if re.search(r'\.vcf$', x)])

    return nb_vcf


def filter_tsv_lines(dir):
    """ Utilisation des filtres d'Emmanuel Khalifa.

        Les fichiers .tsv sont réécrit en fonction du filtre
    """

    # Création du dossier non-EK
    if not os.path.exists(os.path.join(out_dir, 'non-EK')):
        os.mkdir(os.path.join(out_dir, 'non-EK'))

    # On ne liste que les fichiers, pas les dossiers
    list = (file for file in os.listdir(dir) if os.path.isfile(os.path.join(dir, file)))


    # On créé un dict_trio mis à jour utilisé uniquement dans le contexte de la fonction
    dict_trio = {}
    for file_name in list:

        match = re.search(r"(.*(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*)(?:(?:\.annotation\.)|(?:\.variantcaller\.))[0-9]{3,4}\.(.*)$", file_name)
        if match is not None:

            name_head = match.group(1)
            extension = match.group(3)

            dict_trio.setdefault(name_head, {})
            dict_trio[name_head][extension] = file_name

    list_RAS = []
    list_no_RAS = []

    for name in dict_trio:
        header = None
        # List contenant les infos lignes par lignes du .tsv
        csv_dict = []

        with open(os.path.join(dir, dict_trio[name]['tsv']), 'rb') as csvfile:
            dict_reader = csv.DictReader(csvfile, delimiter='\t')
            header = dict_reader.fieldnames
            for line in dict_reader:
                # pas de ligne avec uniquement des \t
                if ''.join(line.values()):
                    if filter_def.general_tsv_2(line):
                        csv_dict.append(line)

        # Si le tsv ne passe pas le filtre EK, le trio de fichier est déplacé
        if len(csv_dict) == 0:
            for extension in dict_trio[name]:
                shutil.move(os.path.join(dir, dict_trio[name][extension]), os.path.join(dir, 'non-EK', dict_trio[name][extension]))
        else:
            with open(os.path.join(dir, dict_trio[name]['tsv']), 'wb') as f:
                w = csv.DictWriter(f, delimiter='\t', fieldnames=header)
                w.writeheader()
                for line in csv_dict:
                    w.writerow(line)


def rewrite_pos_vcf(dir):
    """ Réécriture des fichiers vcf du dossier dir.

    Récrit le .vcf en fonction des lignes restantes dans .tsv et de la
     correspondance position dans .vcf <-> position dans .tsv dans .xls """

    # creation du dossier pour mettre les .vcf réécrit à part des anciens .vcf
    if not os.path.exists(os.path.join(dir, 'new_vcf')):
        os.mkdir(os.path.join(dir, 'new_vcf'))

    # On ne liste que les fichiers, pas les dossiers
    list = (file for file in os.listdir(dir) if os.path.isfile(os.path.join(dir, file)))

    # On créé un dict_trio mis à jour utilisé uniquement dans le contexte de la fonction
    dict_trio = {}
    for file_name in list:
        match = re.search(r"(.*(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*)(?:(?:\.annotation\.)|(?:\.variantcaller\.))[0-9]{3,4}\.(.*)$", file_name)
        if match is not None:

            name_head = match.group(1)
            extension = match.group(3)

            dict_trio.setdefault(name_head, {})
            dict_trio[name_head][extension] = file_name

    for name in dict_trio:

        list_pos_tsv = []
        lines_new_vcf = []
        # caller = VCF Position : Position
        caller = {}

        with open(os.path.join(dir, dict_trio[name]['xls']), 'rb') as f:
            xls_reader = csv.DictReader(f, delimiter='\t')
            for line_xls in xls_reader:
                caller.setdefault(line_xls['VCF Position'], line_xls['Position'])

        with open(os.path.join(dir, dict_trio[name]['tsv']), 'rb') as f:
            tsv_reader = csv.DictReader(f, delimiter='\t')
            for line_tsv in tsv_reader:
                list_pos_tsv.append(line_tsv['Start_Position'])

        with open(os.path.join(dir, dict_trio[name]['vcf']), 'rb') as f:
            vcf_reader = vcf.Reader(f)
            for record in vcf_reader:
                # On enregistre le record si n° correspondant est dans le .tsv
                if caller[str(record.POS)] in list_pos_tsv:
                    # Remplacement du n° pos
                    record.POS = caller[str(record.POS)]
                    lines_new_vcf.append(record)

        with open(os.path.join(dir, 'new_vcf', dict_trio[name]['vcf']), 'wb') as new_f:
            vcf_writer = vcf.Writer(new_f, vcf_reader)
            for new_record in lines_new_vcf:
                vcf_writer.write_record(new_record)


def main(in_dir='data/files_trio', out_dir='data/filter_vcf_out', config_file=None):
    """ Enrobe tout le script dans une fonction pour faire communiquer le script avec d'autres script par des imports """

    if os.path.exists(out_dir):
        print('Le dossier {} existe déjà.'.format(out_dir))
        repeat = True
        while repeat:
            remove_dir = raw_input('Voulez-vous supprimer le dossier et son contenu ? (y/n) ')
            if remove_dir == 'y':
                repeat = False
                shutil.rmtree(out_dir)
            elif remove_dir == 'n':
                repeat = False
                sys.exit('Arret du script')
            else:
                # On repose la question
                pass

    # On compte le nombre de .vcf dans le dossier brut
    nb_vcf = count_vcf(in_dir)
    vcf_logger.info('Nb brut de .vcf, avant remove_useless: {}'.format(nb_vcf))

    remove_useless(in_dir, out_dir)

    # On compte le nombre de .vcf après remove_useless
    nb_vcf = count_vcf(out_dir)
    vcf_logger.info('Nb .vcf après remove_useless: {}'.format(nb_vcf))

    # Déplace les fichiers doublons-non-retenus et non-trio dans des dossiers à part
    clean_trio(out_dir)

    # On compte les .vcf du dossier doublons-non-retenus
    nb_vcf = count_vcf(os.path.join(out_dir, 'doublons-non-retenus'))
    vcf_logger.info('Nombre de .vcf dans le dossier doublons-non-retenus: {}'.format(nb_vcf))
    # On compte les .vcf du dossier non-trio
    nb_vcf = count_vcf(os.path.join(out_dir, 'non-trio'))
    vcf_logger.info('Nombre de .vcf dans le dossier non-trio: {}'.format(nb_vcf))

    # La fonction doit créer un dossier appelé non-EK
    filter_tsv_lines(out_dir)

    # On compte les .vcf du dossier non-trio
    nb_vcf = count_vcf(os.path.join(out_dir, 'non-EK'))
    vcf_logger.info('Nombre de .vcf dans le dossier non-EK: {}'.format(nb_vcf))

    rewrite_pos_vcf(out_dir)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('in_dir')
    args = parser.parse_args()

    in_dir = args.in_dir  # Ex: data/files_1er_2em_partie
    out_dir = '1er_2em_correction_filtered'

    # Mise en place du système de log
    vcf_logger = set_count_log()
    vcf_logger.info('Utilisation du vcf_logger')

    main(in_dir, out_dir)
