#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil, re, sys, csv

in_dir = sys.argv[1]
liste_file_name = os.listdir(in_dir)

no_emty = True

for file in liste_file_name:

    iter = re.finditer(r"tsv$", file)
    for match in iter:
        if match is not None:
            with open(os.path.join(in_dir, file), 'rb') as csvfile:
                dict_reader = csv.DictReader(csvfile, delimiter='\t')
                header = dict_reader.fieldnames
                vide = True
                for line in dict_reader:
                    vide = False

        if vide:
            no_empty = False
            print("Error: {file} est vide".format(file=file))

if no_emty:
    print("Ok: Pas de vide")
else:
    print("Fail: Il ya au moins un .tsv sans données")