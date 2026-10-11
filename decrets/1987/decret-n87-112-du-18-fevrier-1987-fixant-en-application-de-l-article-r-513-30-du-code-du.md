---
title: "Décret n°87-112 du 18 février 1987 fixant, en application de l'article R. 513-30 du code du travail, les normes techniques et les modèles des états relatifs aux déclarations nominatives des salariés et des employeurs et aux demandes des salariés involontairement privés d'emploi *chômeurs* en vue de l'établissement des listes électorales prud'homales"
identifier: "LEGITEXT000006065806"
cid: "JORFTEXT000000884856"
nature: "DECRET"
number: "87-112"
nor: "ASET8703110D"
type: decree
jurisdiction: fr
language: fr
date: 1987-02-18
last_amended: 2005-01-01
consolidated: 2026-10-11
status: in_force
source: "https://www.legifrance.gouv.fr/loda/id/LEGITEXT000006065806"
retrieved: 2026-10-11
---

# Décret n°87-112 du 18 février 1987 fixant, en application de l'article R. 513-30 du code du travail, les normes techniques et les modèles des états relatifs aux déclarations nominatives des salariés et des employeurs et aux demandes des salariés involontairement privés d'emploi *chômeurs* en vue de l'établissement des listes électorales prud'homales

Le Premier ministre,\
Sur le rapport du ministre des affaires sociales et de l'emploi,\
Vu l'article L. 513-3 du code du travail ;\
Vu la loi n° 86-1319 du 30 décembre 1986 relative au conseil de prud'hommes ;\
Vu le décret n° 87-107 du 18 février 1987 modifiant le titre Ier du livre V du code du travail (deuxième partie, décrets en Conseil d'Etat) et relatif aux conseils de prud'hommes ;\
Vu l'article R. 513-3 du code du travail ;\
Vu l'avis du Conseil supérieur de la prud'homie,

## Article 1

Les déclarations mentionnées aux articles R. 513-11 et R. 513-15 ainsi que les demandes dont le maire est saisi en application de l'article R. 513-17 doivent être conformes aux normes techniques ou aux modèles (1) annexés au présent décret.\
(1) Ces modèles sont enregistrés sous les numéros Cerfa 61-2239, 61-2240, 62-2241, 62-2242 et 62-2243 et disponibles dans les mairies et préfectures ainsi qu'au ministère des affaires sociales et de l'emploi (direction des relations du travail, bureau D.S. 1), 1, place de Fontenoy, 75007 Paris.

## Article 2

Le ministre des affaires sociales et de l'emploi est chargé de l'exécution du présent décret, qui sera publié au Journal officiel de la République française.

## Annexes

### NORMES TECHNIQUES DES DECLARATIONS SUR SUPPORT MAGNETIQUE (BANDE OU DISQUETTE) EN VUE DE L'ETABLISSEMENT DES LISTES ELECTORALES PRUD'HOMALES

#### ANNEXE

Déclaration sur bande magnétique\
Le support :\
- Bandes 9 pistes (standard).\
- Codification EBCDIC ou ASCII.\
- Sans aucun label.\
- Densité : 1 600 ou 6 250 bpi.\
- Facteur de blocage inférieur à 10.\
- Un seul fichier physique par bande.\
- Les fichiers multi-volumes sont acceptés.\
Structure du fichier :\
Pour chaque établissement :\
1 enregistrement en tête (020).\
N enregistrements détails (200).\
1 enregistrement fin (300).\
Plusieurs établissements possibles par bande.\
Dessins des enregistrements :\
Lrecl : 300.\
Organisation séquentielle.\
Détail des formats dans le tableau ci-après.\
Déclaration sur disquette 8 pouces\
Le support :\
- 8 pouces au format 3740.\
- Double face, double densité.\
- Label raison sociale.\
- Un seul fichier physique par disquette.\
Structure du fichier :\
Pour chaque établissement :\
1 enregistrement en tête (020).\
N enregistrements détails (200).\
1 enregistrement fin (300).\
Tous ces enregistrements sont tronçonnés en 3 secteurs de 128 octets.\
Chaque enregistrement est complété à 384 par ajout de 84 blancs qui se retrouvent en fin de 3e secteur.\
Plusieurs établissements possibles par disquette.\
Dessins des enregistrements :\
Lrecl: 384.\
Organisation séquentielle.\
Détail des formats dans le tableau ci-après.\
Déclaration sur disquette 5 pouces 1/4\
Le support :\
- 5J 1/4 au format IBM/PC ou vrai compatible.\
- DOS 2.1. et au-dessus.\
- Densité 360 Ko ou 120 Ko.\
Structure du fichier :\
Pour chaque établissement :\
1 enregistrement en tête (020).\
N enregistrements détails (200).\
1 enregistrement fin (300).\
Plusieurs établissements possibles par disquettes.\
Dessins des enregistrements :\
Lrecl : 300.\
Organisation séquentielle.\
Détail des formats dans le tableau ci-après.\
Codification des informations spécifiques\
pour les élections prud'homales\
Suffixe de l'identifiant :\
Pour le cas où l'identifiant de l'entreprise est commun à plusieurs établissements, distinguez chaque établissement à l'aide de ce suffixe, en adoptant une classification numérique et/ou alphabétique.\
Type d'employeur :\
Blanc : Etablissement.\
01 : Exploitation agricole.\
02 : Particulier.\
03 : Autres.\
Collège électoral (pour chaque électeur) :\
1 : Salariés de l'encadrement et autres salariés.\
2 : Employeurs et salariés assimilés à des employeurs.\
Section (pour chaque électeur) :\
1 : Industrie.\
2 : Commerce et services commerciaux.\
3 : Agriculture.\
4 : Activités diverses.\
5 : Encadrement.\
Lieu de vote (pour chaque électeur) :\
1 : Commune de l'établissement.\
2 : Commune du domicile du salarié.

### NORMES TECHNIQUES DES DECLARATIONS SUR SUPPORT MAGNETIQUE (BANDE OU DISQUETTE) EN VUE DE L'ETABLISSEMENT DES LISTES ELECTORALES PRUD'HOMALES *suite* Format des enregistrements

#### ANNEXE

NATURE DE LA ZONE Enregistrement en tête\
Zone indicatif :\
Numéro SIRET (1)\
Longueur : 14 ; Position : 1 à 14 ; Structure : Alpha Suffixe de l'identifiant (2)\
Longueur : 2 ; Position : 15 à 16 ; Structure : Alpha Validité (non utilisé)\
Longueur : 2 ; Position : 17 à 18 ; Structure : Alpha\
Type DADS (non utilisé)\
Longueur : 1 ; Position : 19 ; Structure : Alpha Type d'enregistrement (020)\
Longueur : 3 ; Position : 20 à 22 ; Structure : Alpha Numéro SIRET (1)\
Longueur : 14 ; Position : 23 à 36 ; Structure : Alpha Code APE Longueur : 4 ; Position : 37 à 40 ; Structure : Alpha\
Zone réservée (non utilisé)\
Longueur : 1 ; Position : 41 ; Structure : Alpha SIRET au 1er janvier (si changement)\
Longueur : 14 ; Position : 42 à 55 ; Structure : Alpha Code URSSAF (non utilisé)\
Longueur : 4 ; Position : 56 à 59 ; Structure : Alpha Zone réservée URSSAF (non utilisé)\
Longueur : 20 ; Position : 60 à 79 ; Structure : Alpha\
Zone réservée CRAM (non utilisé)\
Longueur : 17 ; Position : 80 à 96 ; Structure : Alpha Raison sociale Longueur : 50 ; Position : 97 à 146 ; Structure : Alpha\
Adresse :\
Complément d'adresse Longueur : 32 ; Position : 147 à 178 ; Structure : Alpha\
Zone réservée (non utilisé)\
Longueur : 1 ; Position : 179 ; Structure : Alpha Numéro dans la voie Longueur : 4 ; Position : 180 à 183 ; Structure : Alpha Bis ou ter Longueur : 1 ; Position : 184 ; Structure : Alpha Séparateur (non utilisé)\
Longueur : 1 ; Position : 185 ; Structure : Alpha\
Nom de la voie ou lieudit Longueur : 26 ; Position : 186 à 211 ; Structure : Alpha Code I.N.S.E.E. commune (non communiqué)\
Longueur : 5 ; Position : 212 à 216 ; Structure : Alpha Séparateur (non utilisé)\
Longueur : 1 ; Position : 217 ; Structure : Alpha Commune Longueur : 26 ; Position : 218 à 243 ; Structure : Alpha\
Code postal Longueur : 5 ; Position : 244 à 248 ; Structure :\
Alpha Séparateur (non utilisé)\
Longueur : 1 ; Position : 249 ; Structure : Alpha Bureau distributeur Longueur : 26 ; Position : 250 à 275 ; Structure : Alpha Type d'employeur (blanc, 01, 02, 03) (2). 2276 à 277Alpha\
Longueur : 2 ; Position : 276 à 277 ; Structure : Alpha\
Filler Longueur : 23 ; Position : 278 à 300 ; Structure : Alpha\
Enregistrement détail\
Zone indicatif :\
Numéro SIRET (1)\
Longueur : 14 ; Position : 1 à 14 ; Structure : Alpha Suffixe de l'identifiant (2)\
Longueur : 2 ; Position : 15 à 16 ; Structure : Alpha Validité (non utilisé)\
Longueur : 2 ; Position : 17 à 18 ; Structure : Alpha\
Type DADS (non utilisé)\
Longueur : 1 ; Position : 19 ; Structure : Alpha Type d'enregistrement (200)\
Longueur : 3 ; Position : 20 à 22 ; Structure : Alpha Matricule dans l'entreprise ou l'établissement (non utilisé)\
Longueur : 10 ; Position : 23 à 32 ; Structure : Alpha Numéro de sécurité sociale Longueur : 13 ; Position : 33 à 45 ; Structure :\
Alpha\
Clé du numéro de sécurité sociale Longueur : 2 ; Position : 46 à 47 ; Structure : Alpha Date de naissance (J.J.M.M.A.A.)\
Longueur : 6 ; Position : 48 à 53 ; Structure : Alpha Département de naissance Longueur : 2 ; Position : 54 à 55 ; Structure : Alpha Code pays de naissance (non utilisé)\
Longueur : 3 ; Position : 56 à 58 ; Structure : Alpha\
Libellé lieu de naissance Longueur : 26 ; Position : 59 à 84 ; Structure : Alpha Titre (non utilisé)\
Longueur : 3 ; Position : 85 à 87 ; Structure : Alpha Nom de famille (3)\
Longueur : 30 ; Position : 88 à 117 ; Structure : Alpha Prénom Longueur : 20 ; Position : 118 à 137 ; Structure : Alpha\
Nom d'épouse Longueur : 30 ; Position : 138 à 167 ; Structure : Alpha\
Adresse :\
Complément d'adresse Longueur : 32 ; Position : 168 à 199 ; Structure : Alpha Zone réservée (non utilisé)\
Longueur : 1 ; Position : 200 ; Structure : Alpha\
Numéro dans la voie Longueur : 4 ; Position : 201 à 204 ; Structure : Alpha Bis ou ter Longueur : 1 ; Position : 205 ; Structure : Alpha Séparateur Longueur : 1 ; Position : 206 ; Structure : Alpha Nom de la voie ou lieudit Longueur : 26 ; Position : 207 à 232 ; Structure : Alpha\
INSEE commune Longueur : 5 ; Position : 233 à 237 ; Structure :\
Alpha Séparateur (non utilisé)\
Longueur : 1 ; Position : 238 ; Structure : Alpha Commune Longueur : 26 ; Position : 239 à 264 ; Structure : Alpha Code postal Longueur : 5 ; Position : 265 à 269 ; Structure : Alpha\
Séparateur (non utilisé)\
Longueur :1 ; Position : 270 ; Structure : Alpha Bureau distributeur Longueur : 26 ; Position : 271 à 296 ; Structure : Alpha Collège électoral (1 ou 2) (2)\
Longueur : 1 ; Position : 297 ; Structure : Alpha Section (1 à 5) (2)\
Longueur : 1 ; Position : 298 ; Structure : Alpha\
Lieu de vote (1 ou 2) (2)\
Longueur : 1 ; Position : 299 ; Structure : Alpha Filler Longueur : 1 ; Position : 300 ; Structure : Alpha\
Enregistrement fin\
Zone indicatif :\
Numéro SIRET (1)\
Longueur : 14 ; Position : 1 à 14 ; Structure : Alpha Suffixe de l'identifiant (2)\
Longueur : 2 ; Position : 15 à 16 ; Structure : Alpha Validité (non utilisé)\
Longueur : 2 ; Position : 17 à 18 ; Structure : Alpha\
Type DADS (non utilisé)\
Longueur : 1 ; Position : 19 ; Structure : Alpha Type d'enregistrement (300)\
Longueur : 3 ; Position : 20 à 22 ; Structure : Alpha Nombre de DADS (non utilisé)\
Longueur : 5 ; Position : 23 à 27 ; Structure : Alpha Nombre de lignes salariés Longueur : 6 ; Position : 28 à 33 ; Structure : Alpha\
Filler.\
Longueur : 267 ; Position : 34 à 300 ; Structure : Alpha\
(1) Pour les entreprises ayant un identifiant autre que le numéro SIRET (ex. : MSA..) ne dépassant pas 14 caractères, renseigner la zone SIRET avec cet identifiant en cadrant à gauche et en complétant à droite par des blancs.\
(2) Informations spécifiques pour les élections prud'homales (voir codification ci-dessus).\
(3) Nom de jeune fille pour les femmes mariées, veuves ou divorcées.

---

JACQUES CHIRAC Par le Premier ministre :\
Le ministre des affaires sociales et de l'emploi,\
PHILIPPE SÉGUIN
