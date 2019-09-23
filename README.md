Dépot figé d'un projet réalisé à l'instut Bergonié entre 2016 et 2018.

# Colun

Aide à l'insertion des données colon et lung dans cBioportal

## Etapes avant de faire l'insertion

*  Phase de tri / 'filter_trio.py'

Le script met de coté les fichiers inutiles (ex: _robot_, test)
Met de coté les non trio pour évité les jeux de data incomplet

* Création des listes avec [get_RAS.py](get_RAS.py) et [get_liste_antoine.py](get_liste_antoine.py)

* Construction des study définie par l'utilisateur dans [build_config.yml](build_config.yml) en utilisant le script [build_study_data.py](build_study_data.py).

Transformation des .vcf en .maf
Le script comprend une partie validation par l'instance de cBioportal

* L'insertion elle même se fait en suivant les instructions dans [commandes cbio import](commandes cbio import) ou en utilisant le wrapper [import_study.py](import_study.py)


---------------------------------------------------------------------------------------------------

## Traitement des nouvelles données génomique

*  Phase de tri / 'filter_trio2.py'

filter_trio.py <=> Traitement du 1er set de fichiers avant import cBioportal
filter_trio2.py <=> Traitement du 2em set de fichiers avant import cBioportal

Nécessité de trier les données différement car organisées différement

On a traitement séparé des nouvelles données (RAS, KW250, échantillons multiples ...):

Pour les côlons  (si possible dans cet ordre):  
-élimination des non trios.  
-élimination de tous les RAS mutés selon les mêmes filtres que je t'avais donné le 08/09/2017 (mail "ERRATUM")  
-élimination des échantillons ultérieurs au KW250 (ceux de l'année 2016)  
-identification des patients aux échantillons multiples (EK sélectionnera manuellement)  
-identification des échantillons aux analyses multiples (EK sélectionnera manuellement)  
 
 
Pour les poumons  (si possible dans cet ordre):  
-élimination des non trios.  
-identification des patients aux échantillons multiples (EK sélectionnera manuellement)  
-identification des échantillons aux analyses multiples (EK sélectionnera manuellement)  


Pour le choix parmis les analyses multiples voir : data/select_multiple_analysis_2em_set/

-(07/12/17) élimination des mutés EGFR car diminuer la charge de recueil de données cliniques:  

Données relatives à cette opération dans data/eliminationEGFR/  
Script utilisé, remove_lung_EGFR_mutated.py  

On fusionnera ensuite les nouvelles et anciennes données pour l'insertion
dans cBioportal.


* Correspondance anapath patient_id

Anapath to IPP  

Application mise à disposition par la DSI pour obtenir la correspondance
n° anapath <-> n° patient_id/NIP  
 
URL de l'application: http://ib26f/ibis/index.php?m=outilsanapath  
Utiliser le login/pw Bergonié  
  

Le 1er fichier de correspondance a été complété:  

corresp_patientid_anapath.txt.csv => corresp_patientid_anapth09-11-17.csv  


Fichiers recensant les patient_id du 1er set à comparer avec le 2em set pour faire ressortir 
des échantillons multiples.  


## Build data 


Pour importer les fichiers .vcf dans cBioportal il faut les organiser dans des dossiers spécifiques, 
les convertir en un fichier .maf et les accompagner de fichiers de métadonnées.

Pour cela on utilise le script build_study_data.py du dépot bitbucket integration/cbioportal.
build_study_data.py ce script peut subir des modifications. La version étiquetée v0.4 fonctionne correctement avec le projet colun.

Le script build_study_data.py construit l'arborescence de fichiers d'importation.


## PGM 

Les n° PGM sont sont tirés des noms de dossier contenant les fichiers de séquençage sur le server
cifs. Pour générer une liste:

- Ouvrir un terminal sur /run/user/1000/gvfs/smb-share:domain=ib.local,server=cifs,share=pgm$,user=p.mancini/results/colun_lung_plus_routine

- Lancer les commandes

```bash
find . -name "*.tsv" > ~/Code/colun/data/PGM/listing_2018-04-13.tsv.txt
find . -name "*.vcf" > ~/Code/colun/data/PGM/listing_2018-04-13.vcf.txt
find . -name "*.xls" > ~/Code/colun/data/PGM/listing_2018-04-13.xls.txt
```