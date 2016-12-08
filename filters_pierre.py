#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Remove useless files (blanks, test, ...) an duplicates."""

import os, shutil, re, sys, csv


def remove_useless(in_dir, out_dir="files_filtered"):
    """ Remove useless files from given directory.

    - Enlève tout les fichiers considéré comme inutile, c'est à dire les fichiers qui on dans leur nom un des éléments de la liste useless.
    - Créé un dossier "files_filtered" qui contiendra les fichiers utiles.
    - Retourne le nom du dossier créé
    """

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    useless = ['pcr', 'temoin', "test", "acrometrix", "acometrix", "control", "t+", ".cov.", "all_amplicon",
            ".variantcaller.", "_robot_", "_manuel_", "_contamination_", "eeq", "blanc_"]
    for f in os.listdir(in_dir):
        if f:
            cp = True
            for u in useless:
                if u in f.lower():
                    cp = False
            if cp:
                shutil.copy(os.path.join(in_dir, f), os.path.join(out_dir, f))

    return out_dir


def concatenate_names(match):
    """ Concatenate names. """

    # Concatenation des noms
    name = match.group(1)
    last_name_group = None
    for i in range(2, 5):
        if match.group(i):
            name = name + " " + match.group(i)
            last_name_group = match.group(i)

    return name, last_name_group


def filter_from_regex(dir_to_filter, regex, out_dir='unmatched_files'):
    """ Separate files that match a given regex from files that don't.

    - Spérare les fichiers dont le nom ne match pas avec l'expression régulière du dossier donnée en argument des autres fichiers
    - Créé et retourne un dictionnaire contenant les élément capturés par l'expression régulière.
    - Affiche le nom des fichiers enlevés
    - Renvoie un tuple avec 0: dictionnnaire des analyses, 1: dossier de destination des fichiers non matchés
    """
    # matchs = re.finditer(regex, file_name)

    liste_file_name = os.listdir(dir_to_filter)

    dict_analyses = {}

    for file_name in liste_file_name:
        match = re.match(regex, file_name)
        if match is not None:

            name, last_name_group = concatenate_names(match)

            dict_analyses.setdefault(name, []).append({'name': name, 'last_name_group': last_name_group, 'anapath': match.group(5),
                'bare_code': match.group(6), '..': match.group(7),
                'num_analyse': match.group(8), 'extension': match.group(9), 'file_name': file_name})
        else:
            print("Moved: {file_name}".format(file_name=file_name))
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)
            shutil.move(dir_to_filter + "/" + file_name, out_dir + "/" + file_name)

    return (dict_analyses, out_dir)


def filter_unmatched_regex(dir_to_filter, filtered_dir, dict_regex, dict_analyses):
    """ Filter unmactched files by the previous regex (cf. filer_from_regex()).

    -Le but de cette fonction est de tirer des fichier unmatched les information suivantes: nom, n° anapth, n° analyse, extension
    -La fonction déplace les fichiers nouvellement matchés de dir_to_filter dans filtered_dir
    -La fonction complete le dictionnaire dict_analysis avec les noms de fichiers nouvellement matchés
    -Renvoie dictionnnaire des analyses
    """

    liste_file_name = os.listdir(dir_to_filter)

    for file in liste_file_name:

        match_name = re.match(dict_regex['name'], file)

        if match_name is not None:
            # Concatenation des noms
            name, last_name_group = concatenate_names(match_name)
        else:
            print('Le nom de fichier {file} ne match avec la regex spécial nom'.format(file=file))
            # On tue le script pour le débug
            sys.exit()

        # anapath, attention pour anapath on ne prendra que le 1er match
        iter_anapath = re.finditer(dict_regex['anapath'], file)
        for match_anapath in iter_anapath:
            if match_anapath is not None:
                anapath = match_anapath.group(1)
            else:
                anapath = ''

        # num_analyse
        match_analyse = re.match(dict_regex['num_analyse'], file)
        if match_analyse is not None:
            num_analyse = match_analyse.group(1)
        else:
            num_analyse = ''

        # extension
        match_extension = re.match(dict_regex['extension'], file)
        if match_extension is not None:
            extension = match_extension.group(1)
        else:
            extension = ''
            print('Warning: extension manquante sur un fichier {name}'.format(name=file))

        dict_analyses.setdefault(name, []).append({'name': name, 'last_name_group': last_name_group,
            'anapath': anapath, 'bare_code': None, '..': None,
            'num_analyse': num_analyse, 'extension': extension, 'file_name': file})

        # Déplace le fichier
        if not os.path.exists(filtered_dir):
            print("Attention le dossier de sortie n'existe pas")
            # On tue le script pour le débug
            sys.exit()
            os.mkdir(out_dir)
        shutil.move(dir_to_filter+"/"+file, filtered_dir+"/"+file)

    return dict_analyses


def remove_duplicate_analysis(filtered_dir, dict_analyses):
    """ Remove duplicate analysis files.

        S'il y a plusieurs fichier avec même nom la fonction ne garde qu'un seul fichier:
        1. Les .tsv sont gardés par rapport aux .xsl et .xslx
        2. Le fichier avec le plus grand n° d'analyse est conservé
    """
    nb_doublon = 0
    for key in dict_analyses:
        nb_remove = 0

        names = dict_analyses[key]

        # On détermine l'un des fichiers à une extension .tsv
        tsv = False
        for name in names:
            if name['extension'] == 'tsv':
                tsv = True

        # On détermine le n° d'analyse maximum
        num_maxi = 0
        for name in names:
            if name['num_analyse'] == '':
                temp_num_analyse = 0
            else:
                temp_num_analyse = name['num_analyse']
            if temp_num_analyse > num_maxi:
                num_maxi = temp_num_analyse

        # On applique les deux filtres
        for name in names:
            name['removed'] = False
            if name['num_analyse'] == '':
                temp_num_analyse = 0
            else:
                temp_num_analyse = name['num_analyse']
            if temp_num_analyse != num_maxi:
                if os.path.exists(filtered_dir + '/' + name['file_name']):
                    print("Removed: {file_name}".format(file_name=name['file_name']))
                    os.remove(filtered_dir + '/' + name['file_name'])
                    name['removed'] = True
                    nb_remove += 1
                if tsv:
                    if name['extension'] != 'tsv':
                        if os.path.exists(filtered_dir + '/' + name['file_name']):
                            print("Removed: {file_name}".format(file_name=name['file_name']))
                            os.remove(filtered_dir + '/' + name['file_name'])
                            name['removed'] = True
                            nb_remove += 1

        if len(names) - nb_remove > 1:
            print("Doublons, {nb} fichiers restant ayant le nom {name}".format(name=key, nb=len(names) - nb_remove))
            nb_doublon += len(names) - nb_remove - 1

    print("Nombre de doublons {nb}".format(nb=nb_doublon))


def rename_files(dir, file_list):
    """ Renames files in the list into name give in the list.

        - dir est le dossier contenant les fichiers à renommer
        - list est une liste de correspondance entre l'ancien et le nouveau nom de fichier
    """

    for file in file_list:
        if file[1] != '':
            os.rename(os.path.join(dir, file[0]), os.path.join(dir, file[1]))


def count_anapath(dict_analyses):
    """ Compte les nombres de n° anapath différent par nom.

        Retourne le dictionnaire donné en argument avec une colone nb_anapath_diff en plus
    """

    for key in dict_analyses:
        dict_anapath = {}
        for name in dict_analyses[key]:
            dict_anapath.setdefault(name['anapath'], 0)
            dict_anapath[name['anapath']] += 1

        for name in dict_analyses[key]:
            name.setdefault('nb_diff_anapath', len(dict_anapath))

    return dict_analyses


def sort_colon_lung(dict_analyses, dict_colon_lung, in_dir='files_filtered'):
    """ Trie les fichiers en trois catégorie colon, lung et autre.

        Utilise un dictionnaire donné en argument qui contient la catégorie en fonction
        du n° anapath.
        Cette liste est comparé au n° anapath de dict_analysis
        #Retourne le nom des trois dossiers contenant les fichiers triés
    """

    os.mkdir(os.path.join(in_dir, 'dir_colon'))
    os.mkdir(os.path.join(in_dir, 'dir_lung'))
    os.mkdir(os.path.join(in_dir, 'dir_other'))

    for key in dict_analyses:
        for name in dict_analyses[key]:
            if not name['removed']:
                try:
                    if dict_colon_lung[name['anapath']] == 'colon':
                        shutil.move(os.path.join(in_dir, name['file_name']), os.path.join(in_dir, 'dir_colon', name['file_name']))
                    elif dict_colon_lung[name['anapath']] == 'lung':
                        shutil.move(os.path.join(in_dir, name['file_name']), os.path.join(in_dir, 'dir_lung', name['file_name']))
                except KeyError:
                    shutil.move(os.path.join(in_dir, name['file_name']), os.path.join(in_dir, 'dir_other', name['file_name']))

    return ('dir_colon', 'dir_lung', 'dir_other')


if __name__ == '__main__':

    # Dossier à traiter, donné en 1er argument du script
    in_dir = sys.argv[1]

    # On supprime les fichiers inutiles
    filtered_dir = remove_useless(in_dir)

    # Renomage "manuel" de fichiers particuliers
    files_to_rename = [('BERDESSOULES_KR131- BR90.xls', 'BERDESSOULES_KR131-BC90.xls'),  
    ('MICHEL KR 477 BC32.xls', 'MICHEL-KR477-BC32.xls'),
    ('MICHEL KR 477_IonXpress_032.annotation.1674.tsv','MICHEL-KR477_IonXpress_032.annotation.1674.tsv'),
    ('VIGIER_kw285_IonXpress_053.annotation.2297.tsv','VIGIER_KW285_IonXpress_053.annotation.2297.tsv'),
    ('CIBASSIE_BLOCA_LH892_IonXpress_045.finalReport.4621.xls',"CIBASSIE_LH892_IonXpress_045.finalReport.4621.xls"),
    ('CIBASSIE_BLOCA_LH892_IonXpress_045.annotation.4616.tsv',"CIBASSIE_LH892_IonXpress_045.annotation.4616.tsv"),
    ('GUIGNABERT_BLOCJ_HW764_IonXpress_022.annotation.4315.tsv',"GUIGNABERT_HW764_IonXpress_022.annotation.4315.tsv"),
    ('GUIGNABERT_BLOCJ_HW764_IonXpress_022.finalReport.4318.xls',"GUIGNABERT_HW764_IonXpress_022.finalReport.4318.xls"),
    ('GUIGNABERT_BLOCG_HW764_IonXpress_021.annotation.4315.tsv',"GUIGNABERT_HW764_IonXpress_021.annotation.4315.tsv"),
    ('GUIGNABERT_BLOCG_HW764_IonXpress_021.finalReport.4318.xls',"GUIGNABERT_HW764_IonXpress_021.finalReport.4318.xls"),
    ('8-BRUNE-ADK-acinaire-KW27_IonXpress_089.annotation.2101.tsv','8-BRUNE-KW27_IonXpress_089.annotation.2101.tsv'),
    ('7-BRUNE-ADK-solide-KW27_IonXpress_088.annotation.2101.tsv','7-BRUNE-KW27_IonXpress_088.annotation.2101.tsv'),
    ('7-BRUNE-ADK-solide-KW27_BC88.xls','7-BRUNE-KW27_BC88.xls'),
    ('8-BRUNE-ADK-acinaire-KW27_BC89.xls','8-BRUNE-KW27_BC89.xls'),
    ('TAUZIN_QIACUBE_LH214_IonXpress_083.finalReport.4476.xls','TAUZIN_LH214_IonXpress_083.finalReport.4476.xls'),
    ('TAUZIN_QIACUBE_LH214_IonXpress_083.annotation.4471.tsv','TAUZIN_LH214_IonXpress_083.annotation.4471.tsv'),
    ('DODIN_QIACUBE_LH269_IonXpress_085.annotation.4471.tsv','DODIN_LH269_IonXpress_085.annotation.4471.tsv'),
    ('DODIN_QIACUBE_LH269_IonXpress_085.finalReport.4476.xls','DODIN_LH269_IonXpress_085.finalReport.4476.xls'),
    ('TURAN_QIACUBE_LH121_IonXpress_084.finalReport.4476.xls','TURAN_LH121_IonXpress_084.finalReport.4476.xls'),
    ('TURAN_QIACUBE_LH121_IonXpress_084.annotation.4471.tsv','TURAN_LH121_IonXpress_084.annotation.4471.tsv'),
    ('LANDRIN_QIACUBE_LG861_IonXpress_086.finalReport.4476.xls','LANDRIN_LG861_IonXpress_086.finalReport.4476.xls'),
    ('LANDRIN_QIACUBE_LG861_IonXpress_086.annotation.4471.tsv','LANDRIN_LG861_IonXpress_086.annotation.4471.tsv'),
    ('4-SALLABARY-manip2-BC26.xls','4-SALLABARY-manip2-KT932-BC26.xls'),
    ('DHABI SKALI bloc2 BC57.xls','DHABI SKALI bloc2 KO425 BC57.xls')
    ]
    rename_files(filtered_dir, files_to_rename)

    # old
    # regex = r"^(?:[0-9]{1,3}-)?((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1})(?:((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1}))?(?:((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1}))?(?:((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1}))?([A-Z]{2}[0-9]{1,3})(?:[ \-_]{1})(?:[ \-_]{1})?(IonXpress_[0-9]{1,3}|(?:[-_ ])?(?:BC|bc)_?[0-9]{1,3}|IonXpress_(?:BC|bc)_?[0-9]{1,3})?(\.annotation\.|\.finalReport\.)?([0-9]{0,4})(?:_va|_VA)?\.(tsv|xls|xlsx)?"

    # new
    regex = r"(?:[0-9]{1,3}-)?((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1})(?:((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1}))?(?:((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1}))?(?:((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1}))?([A-Z]{2}[0-9]{1,3})(?:[ \-_]{1})?(IonXpress_[0-9]{1,3}|(?:[-_ ])?(?:BC|bc)_?[0-9]{1,4}|IonXpress_(?:BC|bc)_?[0-9]{1,4})?(\.annotation\.|\.finalReport\.)?([0-9]{0,4})?(?:_va|_VA)?\.(tsv|xls|xlsx)?"

    # Le dossier filtré par filter_from_regex correspond au dossier files_filtered créé par la fonction remove_useless
    dict_analyses, unmatched_files = filter_from_regex(filtered_dir, regex)

    # On refiltre les unmatche avec trois petites regex
    # old
    # 'num_analyse_extension': r"((?:BC|bc)_?[0-9]{1,4})?([0-9]{0,4})?(?:_va|_VA)?\.(tsv|xls|xlsx)"

    dict_regex = {
        'name': r"^(?:[0-9]{1,3}-)?((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1})(?:((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1}))?(?:((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1}))?(?:((?:[A-Z]+)|(?:[A-Z][a-z]+))(?:[ \-_]{1}))?",
        'anapath': r"(?:[ \-_]{1})([A-Za-z]{2}[0-9]{1,3}).*",
        'num_analyse': r".*\.(?:annotation|finalReport)\.([0-9]{0,4})?(?:_va|_VA)?\..*",
        'extension': r".*(tsv|xls|xlsx)$"
    }
    dict_analyses = filter_unmatched_regex(unmatched_files, filtered_dir, dict_regex, dict_analyses)

    # On supprime les duplicats
    remove_duplicate_analysis(filtered_dir, dict_analyses)

    count_anapath(dict_analyses)

    with open('tableau_filtered_files.csv', 'wb') as f:
        w = csv.DictWriter(f, dict_analyses.itervalues().next()[0].keys())
        w.writeheader()
        for name in dict_analyses:
            for i in dict_analyses[name]:
                w.writerow(i)

    # Classement des fichiers en fonction du type d'anapath, lung ou colon
    dict_colon_lung = {}
    with open('NGS colon-lung échantillons COLONS_anapath.txt', 'rb') as f:
        for line in f:
            dict_colon_lung[line.replace("\n", "")] = 'colon'

    with open('NGS colon-lung échantillons POUMONS_anapath.txt', 'rb') as f:
        for line in f:
            dict_colon_lung[line.replace("\n", "")] = 'lung'

    sort_colon_lung(dict_analyses, dict_colon_lung, in_dir='files_filtered')
