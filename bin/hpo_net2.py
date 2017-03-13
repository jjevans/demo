#!/usr/bin/env python
import hpo_db
import ontol_content
import sys

db = "hpo"
user = "root"
passwd = None
host = "localhost"

db = mysql.connect(db=database,user=username,host=hostname)
curs = db.cursor()

pheno_obj =  hpo_db.HPO(db_obj=db)

# get phenotype info
phenodesc = pheno_obj.desc_by_pheno(id)
phenodesc = "<b>Entry:</b> "+phenodesc
phenotypes = {"id":id,"desc":phenodesc,"info":list(),"type":phenotype_kw}

# put this entry's information in the "info" section
# to make the entry of interest show up in the phenotype panel
phenotypes["info"].append({"id":id,"desc":phenodesc,"info":list(),type:phenotype
_kw})

parent = pheno_obj.parent(id)
parentdesc = "<b>Parent:</b> "+parent[0][1] # add parent word to existing descri
ption
phenotypes["info"].append({"id":parent[0][0],"desc":parentdesc,"info":list(),"ty
pe":phenotype_kw})



#### Diseases
# get all diseases in hpo for this phenotype
pheno_dis = pheno_obj.omim_by_acc(id) # all disease ids for this phenotype



# create cytoscape web html for hpo id
kwargs["csweb"]["network"] = pheno_obj.csweb_net(id)

csweb_html = ontol_site.Page_Gen().render(plate=conf["files"]["csweb"]["template
"],**kwargs)


