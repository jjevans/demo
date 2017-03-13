#!/usr/bin/env python
import hpo_db
import MySQLdb as mysql
import ontol_content
import sys

database = "hpo"
username = "root"
hostname = "localhost"
passwd = ''

pheno_obj = ontol_content.Phenotype([database,None],username,passwd,hostname)

db = mysql.connect(db=database,user=username,host=hostname)
curs = db.cursor()
hpo_obj =  hpo_db.HPO(db_obj=db)
allphenos = hpo_obj.generate_pheno()
 
for k in allphenos:
    print k+'\t'+allphenos[k]

