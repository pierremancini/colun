#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, re

""" Créé les metadata et data à insérer dans cbioportal """


def make_dict_colon_lung(files_study_type):
    """Ecrit le dictionnaire qui agrège le type d'étude en fonction du n° anapth.

    On supprime les -F à la fin des n° anapath"""

    dict_colon_lung = {}

    for study_type, file in files_study_type.iteritems():
        with open(file, 'rb') as f:
            for line in f:
                anapath = line.replace("\n", "")
                match_iter = re.finditer(r"-F$", anapath)
                for match in match_iter:
                    if match is not None:
                        anapath = anapath.replace("-F", "")
                dict_colon_lung[anapath] = study_type

    return dict_colon_lung


def make_dict_samples(dict_colon_lung):
    """Ecrit le dictionnaire qui classe les sampled_id par patient_id."""

    dict_samples = {'colon': {}, 'lung': {}}

    with open(os.path.join(in_dir, 'anapathpatient20161206092905.csv.csv')) as f:
        reader = csv.reader(f, delimiter=';')
        for line in reader:
            line[0] = line[0].translate(None, ' ')
            # { lung :  {patient_id: [sample_id]}, colon : {patient_id: [sample_id]} }
            patient_id = line[1]
            sample_id = line[0]
            try:
                if dict_colon_lung[line[0]] == 'colon':
                    dict_samples['colon'].setdefault(patient_id, []).append(sample_id)

                elif dict_colon_lung[line[0]] == 'lung':
                    dict_samples['lung'].setdefault(patient_id, []).append(sample_id)

            except KeyError:
                print('Warning: {} n\'est ni colon ni lung'.format(line[0]))

    return dict_samples


def write_meta_files(out_dir, study_dir):

    with open(os.path.join(out_dir, study_dir, 'meta_study.txt'), 'wb') as f:
        if study_type == 'colon':
            f.write('type_of_cancer: coadread\n')
        elif study_type == 'lung':
            f.write('type_of_cancer: nsclc\n')
        f.write('cancer_study_identifier:' + study_dir + '\n')
        f.write('name: ' + name_meta_study + '\n')
        f.write('description: ' + description_meta_study + '\n')
        f.write('short_name: ' + short_name_meta_study + '\n')
        f.write('add_global_case_list: true\n')

    # meta clinical
    with open(os.path.join(out_dir, study_dir, 'meta_samples.txt'), 'wb') as f:
        f.write('cancer_study_identifier:' + study_dir + '\n')
        f.write('genetic_alteration_type: CLINICAL\n')
        f.write('datatype: SAMPLE_ATTRIBUTES\n')
        f.write('data_filename: data_samples.txt\n')

    with open(os.path.join(out_dir, study_dir, 'meta_patients.txt'), 'wb') as f:
        f.write('cancer_study_identifier:' + study_dir + '\n')
        f.write('genetic_alteration_type: CLINICAL\n')
        f.write('datatype: PATIENT_ATTRIBUTES\n')
        f.write('data_filename: data_patients.txt\n')

    with open(os.path.join(out_dir, study_dir, 'meta_mutations_extended.txt'), 'wb') as f:
        f.write('cancer_study_identifier:' + study_dir + '\n')
        f.write('genetic_alteration_type: MUTATION_EXTENDED\n')
        f.write('datatype: MAF\n')
        f.write('show_profile_in_analysis_tab: true\n')
        f.write('profile_name: Mutations\n')
        f.write('profile_description: ' + profile_description + '\n')
        f.write('data_filename: ' + maf_filename + '\n')
        f.write('swissprot_identifier: name\n')


def concatenate_maf_files(in_dir, out_file_path):
    """ Colle le contenu des fichiers sans dupliquer le header.le

        La function doit marcher avec tout les .csv contenant un header
    """
    liste_file_name = os.listdir(in_dir)

    headers = []
    lines = []

    # lecture
    first_file = True
    for file_name in liste_file_name:
        flag_header = True
        """ 1er fichier on copie le header """
        if first_file:
            first_file = False
            with open(os.path.join(in_dir, file_name), 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for line in reader:
                    if line[0][0] == '#':
                        headers.append(line)
                    else:
                        if flag_header:
                            headers.append(line)
                            flag_header = False
                        else:
                            lines.append(line)
        else:
            with open(os.path.join(in_dir, file_name), 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for line in reader:
                    if line[0][0] != '#':
                        if flag_header:
                            flag_header = False
                        else:
                            lines.append(line)

    if not os.path.exists(os.path.dirname(out_file_path)):
        os.mkdir(os.path.dirname(out_file_path))
    with open(out_file_path, 'wb') as f:
        w = csv.writer(f, delimiter='\t')
        for line in headers:
            w.writerow(line)
        for line in lines:
            w.writerow(line)


if __name__ == '__main__':
    """ Dossier à traiter, donné en 1er argument du script

        Ce dossier doit contenir:
        -  anapathpatient20161206092905.csv.csv (n° anapath  / n° patient )
        -  NGS colon-lung échantillons COLONS_anapath.txt (n° anapath / colon)
        -  NGS colon-lung échantillons POUMONS_anapath.txt (n° anapath / lung)
        -  Le dossier de sortie du script filter_trio.py "new_vcf"

        NB: sample_id = n° anapath
    """
    in_dir = sys.argv[1]  # ex: in_build_study

    """ Dossier de sortie: voir architecture_fichiers_cbioportal.txt
    """
    out_dir = 'out_build_study'

    case_list_name = 'nom de case liste'
    case_list_description = 'description de case liste'
    case_list_ids = []

    # meta_study.txt
    name_meta_study = ''
    description_meta_study = ''
    short_name_meta_study = 'colung'
    add_global_case_list = ''

    # meta_mutations_extended.txt
    maf_filename = 'mutations.maf'
    profile_description = 'Mutation description truc bidul'

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    if not os.path.exists(os.path.join(out_dir, 'colon_study')):
        os.mkdir(os.path.join(out_dir, 'colon_study'))
    if not os.path.exists(os.path.join(out_dir, 'lung_study')):
        os.mkdir(os.path.join(out_dir, 'lung_study'))

    # Clinical data . Patients
    # Regroupe tout les patients de l'étude

    # Classement des fichiers en fonction du type d'anapath, lung ou colon
    files_study_type = {'colon': 'NGS colon-lung échantillons COLONS_anapath.txt',
                 'lung': 'NGS colon-lung échantillons POUMONS_anapath.txt'}
    dict_colon_lung = make_dict_colon_lung(files_study_type)

    # Trie les sample_id par patient_id
    dict_samples = make_dict_samples(dict_colon_lung)

    for study_type in dict_samples:
        if study_type == 'colon':
            study_dir = 'colon_study'
        elif study_type == 'lung':
            study_dir = 'lung_study'

        if not os.path.exists(os.path.join(out_dir, study_dir, 'case_lists')):
            os.mkdir(os.path.join(out_dir, study_dir, 'case_lists'))

        # ~~~~ Partie data ~~~~
        # Ici on ouvre trois fichiers à la fois
        with open(os.path.join(out_dir, study_dir, 'data_patients.txt'), 'wb') as fpatients, open(os.path.join(out_dir, study_dir, 'data_samples.txt'), 'wb') as fsamples, open(os.path.join(out_dir, study_dir, 'case_lists', "cases_custom.txt"), 'wb') as fcases:

            en_tete = "#Patient Identifier\n#Patient identifier\n#STRING\n#1\nPATIENT_ID\n"
            fpatients.write(en_tete)

            en_tete = "#Patient Identifier\tSample Identifier\n#Patient Identifier\tSample Identifier\n#STRING\tSTRING\n#1\t1\nPATIENT_ID\tSAMPLE_ID\n"
            fsamples.write(en_tete)

            for patient_id in dict_samples[study_type]:

                fpatients.write(patient_id + "\n")
                case_list_ids.append(patient_id)

                for sample_id in dict_samples[study_type][patient_id]:
                    fsamples.write(patient_id + "\t" + sample_id + "\n")

            fcases.write("cancer_study_identifcasesier: " + study_type + "\n")
            fcases.write("stable_id: " + study_type + "_custom\n")
            fcases.write("case_list_name: " + case_list_name + "\n")
            fcases.write("case_list_description: " + case_list_description + "\n")
            fcases.write("case_list_ids: ")
            fcases.write("\t".join(case_list_ids))

        # Création de fichier d'annotation à partir des fichiers .vcf du dossier trio
        """ #TEST le fichier .maf d'annotation est créé manuelement pour le test d'insertion dans cBioportal,
        c'est à dire que le container vcf2maf n'est pas appelé par le script.
        with open(os.path.join(out_dir, study_dir, 'annotations.maf'), 'wb') as fmaf:
        """

        # ~~~~ Partie meta ~~~~
        write_meta_files(out_dir, study_dir)
