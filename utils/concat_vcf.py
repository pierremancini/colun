#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Concat .vcf from a directory in one .vcf file.

    This script use vcftools : https://vcftools.github.io/perl_module.html """

import os, shutil, re, sys
from subprocess import call

in_dir = sys.argv[1]  # Ex: in_build_study/new_vcf
out_file = 'data/out.vcf.gz'

liste_file_name = os.listdir(in_dir)

for file in liste_file_name:
    with open(os.path.join(in_dir, file), 'rb') as f:
        vcf_reader = vcf.Reader(f)
        for record in vcf_reader:
            print(record)

    # A changer
    with open(os.path.join(out_dir, 'new_vcf', dict_trio[name]['vcf']), 'wb') as new_f:
        vcf_writer = vcf.Writer(new_f, vcf_reader)
        for new_record in lines_new_vcf:
            vcf_writer.write_record(new_record)

# On en compresse qu'une seule fois
if not os.path.exists(os.path.join(in_dir, 'lock')):
    for file in liste_file_name:
        call(["bgzip", os.path.join(in_dir, file)])
    os.mkdir(os.path.join(in_dir, 'lock'))

argument_list = ['vcf-concat']
list_ziped_vcf = os.listdir(in_dir)
for f in list_ziped_vcf:
    argument_list.append(os.path.join(in_dir, f))
argument_list.extend(['| bgzip -c >', out_file])

call(argument_list)
