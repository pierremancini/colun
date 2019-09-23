#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import os
import sys
import csv
import string


in_dir = 'in_build_study'

default_file = "build_config.yml"

dict_samples = {}

# with open(os.path.join(in_dir, 'corresp_patientid_anapath.txt.csv')) as f:
#     reader = csv.reader(f, delimiter=';')
#     for line in reader:
#         line[0] = line[0].replace(' ', '')
#         # {patient_id: [sample_id]}
#         patient_id = line[1]
#         sample_id = line[0]

#         dict_samples.setdefault(patient_id, []).append(sample_id)

# multiples_new = {patient_id: dict_samples[patient_id] for patient_id in dict_samples if len(dict_samples[patient_id]) > 1}


with open(os.path.join(in_dir, 'anapathpatient20161206092905.csv.csv')) as f:
    reader = csv.reader(f, delimiter=';')
    for line in reader:
        line[0] = line[0].replace(' ', '')
        # {patient_id: [sample_id]}
        patient_id = line[1]
        sample_id = line[0]

multiples_old = {patient_id: dict_samples[patient_id] for patient_id in dict_samples if len(dict_samples[patient_id]) > 1}


list_new = [patient_id for patient_id in multiples_new]
list_old = [patient_id for patient_id in multiples_old]

print(len(set(list_old)))
print(set(list_new))