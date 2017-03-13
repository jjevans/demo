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
pheno_obj =  hpo_db.HPO(db_obj=db)









