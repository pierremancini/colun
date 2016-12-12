#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil, re, sys, csv, itertools
import vcf
from filters_pierre import remove_useless

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


def rewrite_tsv(file_name, in_dir, out_dir):
    """ Selectionne des lignes valide du .tsv et réécrit le fichier dans out_dir."""

    # dictionnaire contenant les infos lignes par lignes du .tsv
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


class NameRemovedFromDict(Exception):
    """ Déclaration d'une exception pour être utilisée comme break de plusieur boucles."""
    pass


def check_trio(liste_file_name):
    """ Vérifie que dans une liste de fichiers on a 1 .vcf / 1 xls variant color / 1 .tsv.

    Retourne un dictionnaire contenant le nom du fichier indexé en fonction de sont extension """

    # Structure, {'name':{'nb_tsv':0, 'nb_vcf': 0, 'nb_xls':0}}
    dict_nb_files = {}
    dict_trio = {}

    for file_name in liste_file_name:

        iter = re.finditer(r"([^\.]*)((?:\.annotation\.)|(?:\.variantcaller\.))[0-9]{4}\.(.*)$", file_name)
        for match in iter:

            if match is not None:

                name = match.group(1)
                extension = match.group(3)

                dict_nb_files.setdefault(name, {'nb_tsv': 0, 'nb_vcf': 0, 'nb_xls': 0})

                if extension == 'tsv':
                    dict_nb_files[name]['nb_tsv'] += 1

                if extension == 'vcf':
                    dict_nb_files[name]['nb_vcf'] += 1

                if extension == 'xls':
                    dict_nb_files[name]['nb_xls'] += 1

                # Il ne faut pas de doublon (pour l'instant)
                # NB: Cette partie de code pourra être suprrimée

                if (dict_nb_files[name]['nb_tsv'] > 1) | (dict_nb_files[name]['nb_vcf'] > 1) | (dict_nb_files[name]['nb_xls'] > 1):
                    # On supprime tout les fichiers fesant partie de doublon, le file_name de la boucle et ses doublons
                    liste_file_out = os.listdir(out_dir)
                    for file_name_bis in liste_file_out:
                        if name in file_name_bis:
                            os.remove(os.path.join(out_dir, file_name_bis))
                    dict_trio.pop(name, None)

                else:
                    if extension == 'tsv':
                        rewrite_tsv(file_name, in_dir, out_dir)
                    else:
                        # bouge les .vcf et .xls attachés au .tsv
                        shutil.copy(os.path.join(in_dir, file_name), os.path.join(out_dir, file_name))

                    dict_trio.setdefault(name, {'tsv': '', 'vcf': '', 'xls': ''})
                    dict_trio[name][extension] = file_name

    #  On regarde qu'on a bien un trio et pas un duo ou un seul fichier
    dict_trio_bis = {}
    for name in dict_trio:
        flag = False
        for file_name in dict_trio[name]:
            # S'il manque un fichier on supprime les fichiers de out_dir et de fict_tri
            if dict_trio[name][file_name] == '':
                print('Warning: {name}, il y a un fichier seul ou un duo de fichier'.format(name=name))
                flag = True
                for file_name_bis in dict_trio[name]:
                    if dict_trio[name][file_name_bis] != '':
                        os.remove(os.path.join(out_dir, dict_trio[name][file_name_bis]))

        if not flag:
            dict_trio_bis.setdefault(name, dict_trio[name])


    return dict_trio_bis


if __name__ == '__main__':

    # Dossier à traiter, donné en 1er argument du script
    in_dir = sys.argv[1]  # Ex: files_trio
    out_dir = 'filter_tsv_out'

    remove_useless(in_dir, out_dir)

    liste_file_name = os.listdir(in_dir)

    dict_trio = check_trio(liste_file_name)

    """ on doit réécrire le .vcf en fonction des lignes restantes dans .tsv et de la
     correspondance position dans .vcf <-> position dans .tsv dans .xls  """

    for name in dict_trio:

        # 1. la ligne n'est plus présente dans .tsv on la supprime dans le .vcf
        list_pos_tsv = []
        lines_new_vcf = []
        # caller = VCF Position : Position
        caller = {}

        with open(os.path.join(out_dir, dict_trio[name]['xls']), 'rb') as f:
            xls_reader = csv.DictReader(f, delimiter='\t')
            for line_xls in xls_reader:
                caller.setdefault(line_xls['VCF Position'], line_xls['Position'])

        with open(os.path.join(out_dir, dict_trio[name]['tsv']), 'rb') as f:
            tsv_reader = csv.DictReader(f, delimiter='\t')
            for line_tsv in tsv_reader:
                list_pos_tsv.append(line_tsv['Start_Position'])

        with open(os.path.join(out_dir, dict_trio[name]['vcf']), 'rb') as f:
            vcf_reader = vcf.Reader(f)
            for record in vcf_reader:
                # On enregistre le record si n° correspondant est dans le .tsv
                if caller[str(record.POS)] in list_pos_tsv:
                    # Remplacement du n° pos
                    record.POS = caller[str(record.POS)]
                    lines_new_vcf.append(record)

            # creation du dossier pour mettre les .vcf réécrit à part des anciens .vcf
            if not os.path.exists(os.path.join(out_dir, 'new_vcf')):
                os.mkdir(os.path.join(out_dir, 'new_vcf'))

            with open(os.path.join(out_dir, 'new_vcf', dict_trio[name]['vcf']), 'wb') as new_f:
                vcf_writer = vcf.Writer(new_f, vcf_reader)
                for new_record in lines_new_vcf:
                    vcf_writer.write_record(new_record)
