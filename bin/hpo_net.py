#!/usr/bin/env python
import hpo_db
import MySQLdb as mysql
import sys

#termname = "HP:0000118"
#termname = "Dehydration"
termname = "acc"

database = "hpo"
username = "root"
hostname = "localhost"
passwd = ''


db = mysql.connect(db=database,user=username,host=hostname)
curs = db.cursor()
pheno_obj =  hpo_db.HPO(db_obj=db)

#network = hpo_db.Graph().subtree_graph(termname)
network = pheno_obj.subtree_graph(termname)



print  network





