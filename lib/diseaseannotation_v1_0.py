from das import app
from flask import request

#import json
import os
import sys
import yaml

from flask.ext.mako import render_template
from flask.ext.mako import MakoTemplates

import ontol_content
import ontol_site

## command-line argument for config file path
try:
	config = sys.argv[1]
except:
	print "usage: runserver.py path_to_config_file"
	exit(0)




# root directory of this app
root_dir = os.path.dirname(os.path.abspath(__file__))

# temporary images for demo, may put in instructions later, put on mainpage
# !!! REMOVE WHEN BETTER INFO FOR START PAGE !!!
searchdiaglnk = "../../img/search_diagram.png"
disdiaglnk = "../../img/disease_diag.png"
phenodiaglnk = "../../img/pheno_diag.png"
genediaglnk = "../../img/gene_diag.png"
diag_lnks = [searchdiaglnk,disdiaglnk,phenodiaglnk,genediaglnk] # put on mainpage


# flask-mako templating obj
MakoTemplates().init_app(app)


## results page
#@app.route("/mainpage/<type>/<id>",methods=["GET","POST"])
#def mainpage(type,id):
@app.route("/mainpage")
def mainpage():
	
	#process form data
	type = request.args["type"]
	id = request.args["id"]

	## debugging string, assign any string and shows up in upper left hand corner of page
	testlbl = str()
	
	
	####
	# settings from configuration file
	####
	
	#jje,02042014,commented out, config will have to come from somewhere else
	#conf = settings(req)
	with open(config) as handle:
		conf = yaml.load(handle.read())

	

	#kwargs = dict() # to pass into render template to html
	kwargs = conf # add all settings attributes and then add more fields

	####
	# init keyword arguments for mako template to reference
	####
	
	# assign values to variables
	##

	# db	
	db_omim = conf["db"]["omim"]
	db_hugo = conf["db"]["hugo"]
	db_hpo0 = conf["db"]["hpo"]
	db_hpo1 = conf["db"]["hpo_gene"]
	dbs_hpo = [db_hpo0,db_hpo1]
	
	user = conf["db"]["user"]
	passwd = conf["db"]["password"]
	host = conf["db"]["host"]
	
	plate = conf["files"]["main"]["template"]	
	
	disease_kw = conf["keyword"]["disease"]
	phenotype_kw = conf["keyword"]["phenotype"]
	gene_kw = conf["keyword"]["gene"]
	form_kw = {"disease":disease_kw,"phenotype":phenotype_kw,"gene":gene_kw}
	
	
	####
	# init local vars
	####	
	lbl = None
	diseases = None
	phenotypes = None
	genes = None
	csweb_html = "<html></html>" # initial html provided if no CSWeb graph wanted or available

	
	####
	# init objects
	####
	content_obj = ontol_content.Content()
	dis_obj = ontol_content.Disease(db_omim,user,passwd,host,dbs_hpo,db_hugo) # include hpo db for getting phenos
	pheno_obj = ontol_content.Phenotype(dbs_hpo,user,passwd,host)
	gene_obj = ontol_content.Gene(db_hugo,user,passwd,host)

	"""
	####
	# process form submission
	####
	form = mod_python.util.FieldStorage(req,keep_blank_values=1) #need keep_blank_values?

	id = form.getfirst("id")
	desc = form.getfirst("description") #needed? perhaps when same gene symbol with diff sources
	"""


	####
	# if query is for a disease
	####
	
	#if form.has_key(form_kw['disease']):
	#if 0:#!!!jje,02042014,commented out form check, going to just make if that can't be fulfilled (pheno will be)
	if type == "disease":
		
		kwargs["bg"] = conf["image"]["disease"]
				
		# generate phenotypic series info with label, phenoseries set along 
		# with information for this disease
		# IN FUTURE, use uniq_structure to build data struct.
		dis_obj.dis_info(id,conf["keyword"]["phenotype_series"])
		
		# go through each structure in info list of main dict, insert link to omim in 
		# the second tier structure info section
		# otherwise leave empty list in "info" section
		if conf["variable"]["make_link"]:
			for di in dis_obj.info:
				link = content_obj.make_link(conf["url"]["omim"],di["id"],"OMIM")
				di["info"].append(link)
	
		# diseases is a dict
		# having keys of "id" having dis id, and "desc" with disease description, 
		# info has a list of diseases associated to that disease (PS), 
		# info is a list containing dicts of this same structure
		diseases = {"id":id,"desc":dis_obj.desc,"info":dis_obj.info}

		# information for the 3rd column, the "info" key refers 
		# to diseases so set "type" key to disease form kw
		diseases["type"] = disease_kw
		
		lbl = dis_obj.lbl
		
		# get a unique list of disease ids for all diseases in info section
		subid = list()
		for sub in dis_obj.info:
			subid.append(sub["id"])
		
		uniq_disid = set(subid)
		#uniq_disid = dis_obj.uniq_id(diseases) # Get rid of??? also get rid of in ontol_content
		
		# get all phenotypes and genes related to any of the list of diseases
		
		# phenotypes is a dict having keys "id", "desc" and "info", id has pheno id
		# the desc key has the pheno description as its value
		# and in info key a list of dis ids associated to that pheno, 
		# !!!SINCE phenotypes is for id of disease the id and desc key are None!!!
		phenotypes = {"id":id,"desc":dis_obj.desc}
		phenotypes["info"] = dis_obj.phenos_by_dis(uniq_disid)
				
		# information for the 3rd column, the "info" key refers 
		# to diseases so set "type" key to disease form kw
		phenotypes["type"] = disease_kw
		
		# genes is a dict having keys "id", "desc" and "info", id has gene id
		# the desc key has the gene description as its value,
		# and in info key a list of dicts having this same structure,
		# in those dicts are dis ids, desc, and any info associated to that gene, 
		# !!!SINCE genes is for id of disease the id and desc key are None!!!
		# !!!placeholder of None in desc until can get gene descriptions!!!
		genes = {"id":id,"desc":dis_obj.desc}
		
		# genes_by_dis returns list of dicts with same structure as this dict
		disgene = dis_obj.genes_by_dis(uniq_disid)
		
		dissym = list()
		for dg in disgene:
			
			sym = dis_obj.sym_by_gene(dg["id"])

			entrez = gene_obj.entrez_by_sym(sym)
			hgnc = gene_obj.hgnc_by_sym(sym)
			
			if conf["variable"]["make_link"]:
				if entrez is not "":
					entrez = content_obj.make_link(conf["url"]["entrez"],entrez,"Entrez")
				
				if hgnc is not "":
					hgnc = content_obj.make_link(conf["url"]["hgnc"],hgnc,"HGNC")
					
			dissym.append({"id":sym,"desc":dis_obj.desc_by_id(dg["id"]),"info":[entrez,hgnc],"type":disease_kw})
		
		genes["info"] = dissym
		

	####
	# if query is for a phenotype
	####
	#elif form.has_key(form_kw['phenotype']):
	#elif 1:#!!!jje,02042014,commented out form check, this will enter into if (phenotype)
	elif type == "phenotype":
	
		kwargs["bg"] = conf["image"]["phenotype"]
		
		#### Phenotypes 		

		# get phenotype info
		phenodesc = pheno_obj.desc_by_pheno(id)
		phenodesc = "<b>Entry:</b> "+phenodesc
		phenotypes = {"id":id,"desc":phenodesc,"info":list(),"type":phenotype_kw}
		
		# put this entry's information in the "info" section 
		# to make the entry of interest show up in the phenotype panel
		phenotypes["info"].append({"id":id,"desc":phenodesc,"info":list(),type:phenotype_kw})
		
		#get parent in ontology tree
		if id != "HP:0000001":#not top of ontology
			parent = pheno_obj.parent(id)
			parentid = parent[0][0]
			parentdesc = "<b>Parent:</b> "+parent[0][1] # add parent word to existing description
		else:
			parentid = str()#creates empty link (no link since string len is 0)
			parentdesc = "<b>Parent:</b> "+str(None)
		
		phenotypes["info"].append({"id":parentid,"desc":parentdesc,"info":list(),"type":phenotype_kw})

		
		"""
		# get parents all the way up to root
		parents = pheno_obj.parents(id)
	
		# format parent_tree into data structure
		parent_info = list()
		for parent in parents:
			#parents.append({"id":parent[0],"desc":parent[1],"info":list(),"type":phenotype_kw})
			parents.append({"id":str(parent),"desc":str(parent),"info":list(),"type":phenotype_kw})
		
		phenotypes["info"] = parents
		"""
		

		#### Diseases
		# get all diseases in hpo for this phenotype
		pheno_dis = pheno_obj.omim_by_acc(id) # all disease ids for this phenotype
		
		# get all disease subs for all found diseases
		nonuniq_dis = list()
		for pd in pheno_dis:
			# generate phenotypic series info with label, phenoseries set
			dis_obj.dis_info(pd,conf["keyword"]["phenotype_series"])
	
			# filter out any disease with a description of None		
			if dis_obj.desc is not None:
				nonuniq_dis += dis_obj.info

		uniq_dis = dis_obj.uniq_structure(nonuniq_dis)
		
		if conf["variable"]["make_link"]:
			for ud in uniq_dis:
				ud["info"].append(content_obj.make_link(conf["url"]["omim"],ud["id"],"OMIM"))

		# diseases is a dict
		# having keys of "id" having dis id, and "desc" with disease description, 
		# info has a list of diseases associated to that disease (PS), 
		# info is a list containing dicts of this same structure
		# information for the 3rd column, the "info" key refers 
		# to diseases so set "type" key to disease form kw
		diseases = {"id":id,"desc":str(),"info":uniq_dis,"type":disease_kw}

	
		#### Genes
		genes = {"id":id,"desc":phenodesc,"info":list(),"type":gene_kw}
		
		# get genes from pheno_genes db table
		pheno_gene = pheno_obj.genes_by_pheno(id)

		# format genes into dict of key "id" having list of phenotypes and key "desc" gene desc
		# for now only a single phenotype for third column
		gene_item = list()
		for pg in pheno_gene:
		
			entrez = gene_obj.entrez_by_sym(pg)
			hgnc = gene_obj.hgnc_by_sym(pg)
			
			if conf["variable"]["make_link"]:
				if entrez is not "":
					entrez = content_obj.make_link(conf["url"]["entrez"],entrez,"Entrez")
				
				if hgnc is not "":
					hgnc = content_obj.make_link(conf["url"]["hgnc"],hgnc,"HGNC")

			gene_item.append({"id":pg,"desc":gene_obj.desc_by_sym(pg),"info":[entrez,hgnc],"type":gene_kw})
				
		genes["info"] = gene_item
		
		
		# produce label, changed label to not have "Entry:" in it as 
		# this is already in the description from above
		#lbl = "<b>Source:</b> Human Phenotype Ontology</br><b>Entry:</b> "+phenodesc+" "+id+"</br>"
		lbl = "<b>Source:</b> Human Phenotype Ontology</br>"+phenodesc+" "+id+"</br>"
		

		# create cytoscape web html for hpo id
		kwargs["csweb"]["network"] = pheno_obj.csweb_net(id)
		
		csweb_html = ontol_site.Page_Gen().render(plate=conf["files"]["csweb"]["template"],**kwargs)
		
	####
	# if query is for a gene
	####
	#elif form.has_key(form_kw['gene']):
	#elif 0:#!!!jje,02042014,commented out form check, going to just make if that can't be fulfilled (pheno will be)
	elif type == "gene":
		
		kwargs["bg"] = conf["image"]["gene"]
		
		
		disgene = dis_obj.gene_by_sym(id) # not a symbol when coming from disease previous page, need to convert omim gene id to gene symbol(s)
		
		genedesc = gene_obj.desc_by_sym(id)
		
		#### Diseases
		diseases = {"id":id,"desc":genedesc,"type":disease_kw,"info":list()}

		
		# get descriptions
		dis = list()		
		for dg in disgene:
			
			# get list of omim ids for this gene
			dis = dis_obj.dis_by_gene(str(dg))
			
			# get descriptions, make html links as id
			anno = list()
			for entry in dis:

				link = content_obj.make_link(conf["url"]["omim"],entry,"OMIM")

				desc = dis_obj.desc_by_id(entry)
				
				anno.append({"id":entry,"desc":desc,"info":[link]})				
			
			diseases["info"] = anno
	
		#### Phenotypes
		pheno = pheno_obj.pheno_by_gene(id) # successful, next need to get pheno desc
		
		phenodesc = "jasonevans"#jje02102014, quick fix for now, long fix needed!!!
		
		phenotypes = {"id":id,"desc":phenodesc,"type":phenotype_kw,"info":pheno}
	
	
		#### Genes
		
		entrez = gene_obj.entrez_by_sym(id)
		hgnc = gene_obj.hgnc_by_sym(id)
			
		if conf["variable"]["make_link"]:
			if entrez is not "":
				entrez = content_obj.make_link(conf["url"]["entrez"],entrez,"Entrez")
				
			if hgnc is not "":
				hgnc = content_obj.make_link(conf["url"]["hgnc"],hgnc,"HGNC")
		
		entry_struct = {"id":id,"desc":genedesc,"info":[entrez,hgnc],"type":gene_kw}
		
		genes = {"id":id,"desc":genedesc,"info":[entry_struct],"type":gene_kw}
	
		
		# produce label
		lbl = "<b>Source:</b> Gene</br><b>Entry:</b> "+str(genedesc)+" "+id+"</br>"
	
	
	####
	# no query, just at mainpage
	####
	else: # handle mainpage
		kwargs["bg"] = conf["image"]["disease"]
	
		kwargs["doc_img"] = diag_lnks # get rid of these diagrams and paths at beginning of this file
		
		
	####
	# assign content to kwargs
	####
	kwargs["lbl"] = lbl
	kwargs["diseases"] = diseases
	kwargs["phenotypes"] = phenotypes	
	kwargs["genes"] = genes
	kwargs["csweb"] = csweb_html
		
	
	####
	## test label for debugging
	####
	
	testlbl += "</br></br>"

	
	kwargs["testlbl"] = testlbl
	

	####
	# render html and publish request
	####

	#jje,02042014,commented out render of mako directly
	#html = ontol_site.Page_Gen().render(plate=plate,**kwargs)
	
	#jje,02042014,commented out mod_py req obj
	#req.content_type = "text/html"
	#req.write(html)


	#return

	#return render_template('jje.mako',jje="jasonevans yeah!")
	return render_template(plate,**kwargs)


## search page (root)
@app.route("/")
@app.route("/search")	
def search():
	
	####
	# get configuration settings
	####
	#jje,02042014,commented out, config will have to come from somewhere else
	#conf = settings(req)
	with open(config) as handle:
		conf = yaml.load(handle.read())

	# add all settings properties and add other fields
	kwargs = conf
	
	# assign values to variables
	##
	
	# db	
	db_omim = conf["db"]["omim"]
	db_hugo = conf["db"]["hugo"]
	db_hpo0 = conf["db"]["hpo"]
	db_hpo1 = conf["db"]["hpo_gene"]
	dbs_hpo = [db_hpo0,db_hpo1]
	
	user = conf["db"]["user"]
	passwd = conf["db"]["password"]
	host = conf["db"]["host"]
	
	# html template and keywords for form (name of args passed back through form)
	plate = conf["files"]["search"]["template"]
	
	disease_kw = conf["keyword"]["disease"]
	phenotype_kw = conf["keyword"]["phenotype"]
	gene_kw = conf["keyword"]["gene"]
	form_kw = {"disease":disease_kw,"phenotype":phenotype_kw,"gene":gene_kw}
	kwargs["form_kw"] = form_kw

	####
	# init objects
	####
	####remove content_obj = ontol_content.Content()
	dis_obj = ontol_content.Disease(db_omim,user,passwd,host,dbs_hpo,db_hugo) # include hpo db for getting phenos
	pheno_obj = ontol_content.Phenotype(dbs_hpo,user,passwd,host)
	gene_obj = ontol_content.Gene(db_hugo,user,passwd,host)

	
	####
	# find eligible terms for autocomplete search fields (dis,pheno,gene forms)
	####
	# pull out entire list of 1.omim diseases, 2.hpo phenos, and 3.genes in both omim and hpo
	
	kwargs["form_dis"] = dis_obj.generate_dis_by_name(conf["keyword"]["phenotype_series"]) # dict of dis
	kwargs["form_pheno"] = pheno_obj.generate_pheno_by_name() # dict of pheno
	
	form_gene = list() # list of gene tuples, tuple uses first element to describe gene origin
	form_gene = dis_obj.geneset()
	form_gene += pheno_obj.geneset()
	kwargs["form_gene"] = set(form_gene) # unique list (set)
	
	# use disease colored background
	kwargs["bg"] = conf["image"]["disease"]
	
	
	#html = ontol_site.Page_Gen().render(plate=plate,**kwargs)
	
	#req.content_type = "text/html"
	#req.write(html)

	return render_template(plate,**kwargs)


def settings(req):
	
	####
	# init keyword arguments for mako template to reference
	####
	kwargs = dict() # to pass into render template to html

	####
	# settings from configuration file
	####
	
	# from apache config (file http.conf), 
	# variable denoting location of config file
	##
	env_vars = req.subprocess_env.copy()
	config = env_vars["CONFIG_PATH"]
		
	with open(config) as handle:
		conf = yaml.load(handle.read())

	return conf
