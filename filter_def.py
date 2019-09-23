#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import sys



def _get_clinsig(clinvar):
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

def _compare_clinsig_voc(list_clinsig, voc):
    """ Compare clinsig worlds list with controlled vocabulary.

        Return False if there is no match
        Else return True
    """

    s = set(list_clinsig) & set(voc)

    if len(s) == 0:
        return False
    else:
        return True

def float_csv(string):
    """ Surcouche du cast float() pour accpeter les valeurs NA commme valeur False. """

    if string == 'NA':
        return 0
    else:
        return float(string)


def general_tsv_legacy(line):
    """
        Dernier filtre avant la mise en place du système de gestion des filtres.
    """

    list_clinsig = _get_clinsig(line['CLINVAR'])

    # 1er cas
    valid = _compare_clinsig_voc(list_clinsig, ['pathogenic', 'drug-response', 'likely-pathogenic'])

    if int(line['Var.freq.']) < 2:
        valid = False

    # 2em cas
    if not valid:

        valid = _compare_clinsig_voc(list_clinsig, ['uncertain-significance',
            'conflicting-interpretations-of-pathogenicity', 'unknown', 'NA', ''])

        if int(line['Var.freq.']) < 5:
            valid = False

    # Conditions communes
    if (int(line['Pos.Cov.']) < 100) | (float_csv(line['1000G_ALL_AF']) > 0.01):
        valid = False

    return valid


def general_tsv_1(line):
    """
       Date de 1er utilisation: 22/09/17
    """

    list_clinsig = _get_clinsig(line['CLINVAR'])

    # 1er cas
    valid = _compare_clinsig_voc(list_clinsig, ['pathogenic', 'drug-response', 'likely-pathogenic'])

    if int(line['Var.freq.']) < 2:
        valid = False

    # 2em cas
    if not valid:
        valid = _compare_clinsig_voc(list_clinsig, ['uncertain-significance', 'unknown', 'NA', ''])

        if int(line['Var.freq.']) < 5:
            valid = False

    # Conditions communes
    if float_csv(line['1000G_ALL_AF']) > 0.01:
        valid = False

    if line['Var.Cov.'] < 50:
        valid = False

    return valid



def general_tsv_2(line):
    """
        Date de 1er utilisation: 15/04/18
    """

    list_clinsig = _get_clinsig(line['CLINVAR'])

    # 1er cas
    valid = _compare_clinsig_voc(list_clinsig, ['pathogenic', 'drug-response', 'likely-pathogenic'])

    if int(line['Var.freq.']) < 2:
        valid = False


    # 2em cas
    if not valid:
        valid = _compare_clinsig_voc(list_clinsig, ['uncertain-significance', 'unknown', 'NA', ''])

        if int(line['Var.freq.']) < 5:
            valid = False

    # Conditions communes
    if float_csv(line['1000G_ALL_AF']) > 0.005:
        valid = False

    if int(line['Var.Cov.']) < 50:
        valid = False

    return valid




def RAS_1(line):
    """
        Filtre pour obtenir les KRAS, NRAS.

        Date de 1er utilisation: 02/10/17

        p.(Mutalyzer)": les données affichées sont aux formats suivant: p.(Gly12Val) ou p.A1046T

        :return: True si la ligne répond aux critères muté RAS.
    """

    # Condition
    if line['Gene'] == 'KRAS' or line['Gene'] == 'NRAS':
        pass
    else:
        if '(' in line['Gene']:
            if line['Gene'].split('(')[0] in ['KRAS', 'NRAS']:
                pass
        # print('Mauvais Gene: {}'.format(line['Gene']))
        return False

    # Condition
    if int(line['Var.freq.']) >= 2:
        pass
    else:
        # print('Var.freq trop bas: {}'.format(line['Var.freq.']))
        return False

    # Condition
    if int(line['Var.Cov.']) >= 50:
        pass
    else:
        return False

    # Condition
    accepted_num = [12, 13, 59, 61, 117, 146]
    try:
        line['p.(Mutalyzer)']
    except KeyError:
        match = re.search(r'^p\.\D*([0-9]*)', line['p.'])
    else:
        match = re.search(r'^p\.\(\D*([0-9]*).*\)$', line['p.(Mutalyzer)'])
    finally:
        if match:
            if match.group(1):
                if not int(match.group(1)) in accepted_num:
                    # print('Mauvaise position d\'intérêt: {}'.format(match.group(1)))
                    return False
            else:
                # print('Pas de match')
                return False
        else:
            # print('Pas de match')
            return False

    # print('-> True')
    return True
