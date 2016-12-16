#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil, sys, csv, re

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
    out_dir = 'cancer_study_data'

    nom_dir_colon = 'colon'
    nom_dir_lung = 'lung'

    case_list_name = 'nom de case liste'
    case_list_description = 'description de case liste'

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # Clinical data . Patients
    # Regroupe tout les patients de l'étude

    # Classement des fichiers en fonction du type d'anapath, lung ou colon
    files_study_type = {'colon': 'NGS colon-lung échantillons COLONS_anapath.txt',
                 'lung': 'NGS colon-lung échantillons POUMONS_anapath.txt'}
    dict_colon_lung = make_dict_colon_lung(files_study_type)

    dict_samples = {'colon': {}, 'lung': {}}

    with open(os.path.join(in_dir, 'anapathpatient20161206092905.csv.csv')) as f:
        reader = csv.reader(f, delimiter=';')
        for line in reader:
            line[0] = line[0].translate(None, ' ')
            # {patient_id: [{sample_id, study_type}]}
            # ou { lung :  {patient_id: [sample_id]}, colon : {patient_id: [sample_id]} }
            patient_id = line[1]
            sample_id = line[0]
            try:
                if dict_colon_lung[line[0]] == 'colon':
                    dict_samples['colon'].setdefault(patient_id, []).append(sample_id)

                elif dict_colon_lung[line[0]] == 'lung':
                    dict_samples['lung'].setdefault(patient_id, []).append(sample_id)

                # ancien patients.setdefault(line[1], []).append({'sample_id': line[0], 'study_type': dict_colon_lung[line[0]]})
            except KeyError as e:
                print('Warning: {} n\'est ni colon ni lung'.format(line[0]))

    # Embranchement colon ou lung $study_name

    #  patients -> dict_samples
    for study_type in dict_samples:
        if study_type == 'colon':

        elif study_type == 'lung':


        with open(os.path.join(out_dir, , 'data_patients.txt'), 'wb') as fpatients, open(os.path.join(out_dir, 'data_samples.txt'), 'wb') as fsamples, open(os.path.join(out_dir, "cases_custom.txt")) as fcases:
            # écriture data_patients.txt
            en_tete = "#Patient Identifier\n#Patient identifier\n#STRING\n#1PATIENT_ID\n"
            fpatients.write(en_tete)
            fpatients.write(id_patient + "\n")

            # Clinical data . Samples
            # Regroupe tout les samples des patients de l'étude
            en_tete = "#Patient Identifier\tSample Identifier\n#Patient Identifier\tSample Identifier\n#STRING\tSTRING\n#1\t1\n"

            # écriture data_samples.txt
            fsamples.write(en_tete)
            for patient_id in patients:
                for sample in patients[patient_id]:
                    fsamples.write(patient_id + "\t" + sample['sample_id'] + "\n")

            # écriture des fichiers cases_lists
            if not os.path.exists(os.path.join(out_dir, 'case_lists')):
                os.path.exists(os.path.join(out_dir, 'case_lists'))
                fcases.write("cancer_study_identifcasesier: " + study_name + "\n")
                fcases.write("stable_id: " + study_name + "_custom\n")
                fcases.write("case_list_name: "+ case_list_name + "\n")
                fcases.write("case_list_description: " + case_list_description + "\n")
                fcases.write("case_list_ids: ")
                fcases.write("\t".join(case_list_ids))
