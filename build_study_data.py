#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil, sys, csv

""" Créé les metadata et data à insérer dans cbioportal """

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
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # On commence par les data

    # Clinical data . Patients
    # Regroupe tout les patiens de l'étude

    # récolte des données

    patients = {}

    with open(os.path.join(in_dir, 'anapathpatient20161206092905.csv.csv')) as f:
        reader = csv.reader(f, delimiter=';')
        for line in reader:
            patients.setdefault(line[1], []).append(line[0])

    en_tete = "#Patient Identifier\n#Patient identifier\n#STRING\n#1PATIENT_ID\n"

    # écriture
    with open(os.path.join(out_dir, 'data_patients.txt'), 'wb') as f:
        f.write(en_tete)
        for id_patient in patients:
            f.write(id_patient + "\n")

    # Clinical data . Samples
    # Regroupe tout les samples des patients de l'étude

    en_tete = "#Patient Identifier\tSample Identifier\n#Patient Identifier\tSample Identifier\n#STRING\tSTRING\n#1\t1\n"

    # écriture
    with open(os.path.join(out_dir, 'data_samples.txt'), 'wb') as f:
        f.write(en_tete)
        for patient_id in patients:
            for sample_id in patients[patient_id]:
                # Supprime les caractères blancs
                sample_id =  sample_id.translate(None, ' ')
                f.write(patient_id + "\t" + sample_id + "\n")
