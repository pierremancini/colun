#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import subprocess
import sys
import yaml
import re
import shutil
import logging


""" Rappatrie les données depuis sharefolder correspondants aux études colon et lung. """

def copy_remote_file(file_path, dest_path):

    if not os.path.exists(os.path.split(dest_path)[0]):
        os.mkdir(os.path.split(dest_path)[0])
    shutil.copyfile(file_path, dest_path)


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


logger = set_logger('get_files_logger', 'data_shared_folder.log', logging.DEBUG)

selected_anapath = ['*****', '*****']

shared_folder = '/path/to/colun_lung_plus_routine/'

# Dossier de destination des données
dest_folder = 'data/files_1er_2em_partie'

# On écrase l'ancien dossier
try:
    shutil.rmtree(dest_folder)
except FileNotFoundError:
    print('Creation du dossier {}'.format(dest_folder))
else:
    print('Ecrasement du dossier {}'.format(dest_folder))
finally:
    os.mkdir(dest_folder)

# {dossierpgm: sousdossierretenu }
to_copy = {}

# Rentre dans chaque dossiers de colun_lung_plus_routine
files = os.listdir(shared_folder)

pgm_folders = (element for element in files if os.path.isdir(os.path.join(shared_folder, element)))

all_shared = []

for pgm_folder in pgm_folders:

    subfolders = os.listdir(os.path.join(shared_folder, pgm_folder))

    for subfolder in subfolders:
        if os.path.isdir(os.path.join(shared_folder, pgm_folder, subfolder)):
            match = re.search(r'[^A-Za-z]([A-Za-z]{1,2}[0-9]{1,3})', subfolder)
            try:
                anapath = match.group(1)
            except AttributeError:
                logger.info('AttributeError: {}'.format(subfolder))
                pass
            else:
                # On compare l'anapath aux listes colon et lung
                all_shared.append(anapath)
                if anapath in selected_anapath:
                    # Copie tout les .tsv .vcf .xls
                    files = os.listdir(os.path.join(shared_folder, pgm_folder, subfolder))
                    for file in files:
                        extension = file.split('.')[-1]
                        if extension in ['vcf', 'tsv', 'xls']:
                            dest_path = os.path.join(dest_folder, file)
                            copy_remote_file(os.path.join(shared_folder, pgm_folder,
                                subfolder, file), dest_path)


selected_anapath = set(selected_anapath)
all_shared = set(all_shared)

not_found = selected_anapath - all_shared

logger.info('Nb de fichiers de la liste EK non trouvé sur cifs/pgm: {}'.format(len(not_found)))
logger.info(not_found)