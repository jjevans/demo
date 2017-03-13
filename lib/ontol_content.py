import omim_db
import hpo_db
import hugo_db
import json
import yaml

"""
	produces main content of ontology webpage
"""

class Content():
	
	def make_link(self,url,id,text):
		return "<a href="+url+str(id)+">"+str(text)+"</a>"

class Disease():

	def __init__(self,db,user,passwd,host,dbs_hpo=None,db_hugo=None): #hpodb is the name of hpo db if needed
	
		omim_db_obj = omim_db.Initialize(db=db,user=user,passwd=passwd,host=host).db_obj
		self.omim_obj = omim_db.OMIM(db_obj=omim_db_obj)
		self.ser_obj = omim_db.Series(db_obj=omim_db_obj)
		self.con_obj = omim_db.Convert(db_obj=omim_db_obj)
		
		self.pheno_obj = None
		if dbs_hpo is not None:
			self.pheno_obj = Phenotype(dbs_hpo,user,passwd,host)

		self.gene_obj = None
		if db_hugo is not None:
			self.gene_obj = Gene(db_hugo,user,passwd,host)

		self.lbl = "<b>Source:</b> OMIM</br>"
		self.psid = None # phenotypicSeries id if part of one
		
	def generate_dis(self,ps_kw=None):
		return self.omim_obj.generate_dis(ps_kw)

	def generate_dis_by_name(self,ps_kw=None):
		return self.omim_obj.generate_dis_by_name(ps_kw)
		
	def dis_info(self,omimid,ps_kw="(PS)"):
		delim = ":::"
		
		self.dissub = self.ser_obj.sub_from_sub(omimid)

		self.desc = self.omim_obj.desc_by_id(omimid)

		# info is a list having dict with key "id" having disease id, 
		# "desc" with description, and any info as string in key "info",
		# at this point "info" has no information and is None
		self.info = list()
		if len(self.dissub) != 0:
			
			self.lbl += "<b>This entry is part of a phenotypicSeries.</b></br>"
			self.psid = self.dissub[0][2] # set phenotypic series id
			
			# create lbl for phenotypicSeries info
			if str(omimid) == str(self.dissub[0][2]):
				# label if this entry is the phenoseries
				self.desc = str(self.desc)+" "+ps_kw
				self.lbl += "<b>This entry is the series entry.</b></br>"
			else:
				self.lbl += "<b>This entry is not the series entry.</b></br>"
			
			self.lbl += "</br><b>Series entry:</b></br>"
		
			# flag if phenotypic series
			# go through each disease in series and label if it is the series entry
			for sub in self.dissub:
				if str(sub[0]) == str(sub[2]):				
					sub[1] +=" "+ps_kw
					self.lbl += sub[1]+" "+str(sub[0])+"</br>"

				# create dictionary for this disease and add to list
				self.info.append({"id":sub[0],"desc":sub[1],"info":list()})
					
		else:
			# put just the entry itself to display with no phenotypicSeries entries
			self.dissubs = [[omimid,self.desc,None]]
			
			# create dictionary for this disease only being the disease of interest
			self.info.append({"id":omimid,"desc":self.desc,"info":list()})
		
		#prepend entry info
		self.lbl = "<b>Entry:</b> "+str(self.desc)+" "+str(omimid)+"</br></br>"+self.lbl
		
		return

	def phenos_by_dis(self,disids):
		# get a unique set of phenotypes for a unique set of disease ids (unique not required)
		# input is a list of disease ids		
		# returns a list of dicts having keys "id" for pheno id, "desc" for pheno description,
		# and "info" having a list of disease ids associated to that pheno
		
		# raise exception if no Phenotype object produced in constructor init
		if self.pheno_obj is None:
			raise Exception("No pheno_obj produced in constructor used by ontol_content.pheno_by_dis")
		
		nonuniq_pheno = list() # list of tuples containing pheno id, pheno desc, and disease id
		for disid in disids:
			nonuniq_pheno += self.pheno_obj.pheno_by_omim(disid)
		
		# go through all nonuniq pheno and combine disease ids belonging to the same pheno
		# make uniq phenos 
		uniq_pheno = dict()
		pheno_desc = dict() # keep track of phenotype descriptions to put in later
		for nup in nonuniq_pheno:
			
			if not nup[0] in uniq_pheno:
				uniq_pheno[nup[0]] = list()
				pheno_desc[nup[0]] = nup[1]

			uniq_pheno[nup[0]].append(nup[2])
			
		# produces list of dict having key of "id" for the pheno id,
		# "desc" for pheno description and a list of dis ids for that pheno in "info" key
		info = list()
		for up in uniq_pheno:
			info.append({"id":up,"desc":pheno_desc[up],"info":uniq_pheno[up]})
		
		return info

	def genes_by_dis(self,disids):
		# get a unique set of genes for a unique set of disease ids (unique not required)
		# returns a list of dicts containing the gene id as key "id", 
		# gene description as key "desc" !!!to be implemented!!!
		# and list of omim ids that link to that gene in key "info"
		
		nonuniq_gene = list() # list of gene ids for this disease
		for disid in disids:
			nonuniq_gene += self.omim_obj.gene_by_dis(disid)
		
		# go through all nonuniq gene and combine disease ids belonging to the same gene
		# make uniq genes by having a dict of ids as keys and the value having a list 
		# of disease ids as its value 
		uniq_gene = dict()
		for nug in nonuniq_gene:
			
			if not nug[0] in uniq_gene:
				uniq_gene[nug[0]] = list()
			
			uniq_gene[nug[0]].append(nug[1])
			
		# produce list of dict with keys "id", "desc", "info"
		info = list() # returned
		for ug in uniq_gene:
			sym = self.sym_by_gene(ug)
			
			genedesc = None
			if sym is not None:
				genedesc = self.gene_obj.desc_by_sym(sym)
				
			info.append({"id":ug,"desc":genedesc,"info":uniq_gene[ug]})
		
		return info

	def desc_by_id(self,id):
		# get omim description by omim id
		return self.omim_obj.desc_by_id(id)
	
	def uniq_structure(self,information):
		# go through a list of dicts (keys "id","desc","info")
		# overwrite duplicates via a dict
		
		uniq = dict()
		for info in information:
			uniq[info["id"]] = info
		
		return uniq.values()
			
	def uniq_id(self,diseases):
		# from a list of dicts of diseases having keys "id" with dis id,
		# "desc" with dis desc, and info which is a list of dictionaries of 
		# the same structure.
		# Returns a list of unique ids derived from the id keys

		non_uniq = list()
		for dis in diseases:
			non_uniq.append(dis["id"])
			
		return set(non_uniq)	
		
	def geneset(self):
		# get all gene symbols represented in omim (omim.txt)
		
		# get only the first symbol if from a string "comma sep" with many sym
		#genes = self.ser_obj.geneset()
		#for gene in geneset:
		
		
		#return self.ser_obj.geneset()
		return self.omim_obj.geneset()

	def desc_by_id(self,id):
		return self.omim_obj.desc_by_id(id)
	
	def dis_by_gene(self,id):
		return self.omim_obj.dis_by_gene(id)

	def gene_by_sym(self,id):
		return self.omim_obj.gene_by_sym(id)

	def sym_by_gene(self,id):
		return self.omim_obj.sym_by_gene(id)

class Phenotype():

	def __init__(self,dbs_hpo,user,passwd,host):
		hpo_db_obj = hpo_db.Initialize(db=dbs_hpo[0],user=user,passwd=passwd,host=host).db_obj
		self.hpo_obj = hpo_db.HPO(db_obj=hpo_db_obj)
		
#		hpo_gene_db_obj = hpo_db.Initialize(db=dbs_hpo[1],user=user,passwd=passwd,host=host).db_obj
#		self.hpo_gene_obj = hpo_db.HPO_Gene(db_obj=hpo_gene_db_obj)

	def label(self):
		pass
		
	def generate_pheno(self):
		return self.hpo_obj.generate_pheno()
	
	def generate_pheno_by_name(self):
		return self.hpo_obj.generate_pheno_by_name()

	def omim_by_acc(self,id):
		# get all omim diseases by an hpo accession id
		return self.hpo_obj.omim_by_acc(id)
	
	def pheno_by_omim(self,omimid):
		return self.hpo_obj.pheno_by_omim(omimid)
	

	def parent(self,acc):
		# get parent phenotypes for a phenotype
		
		termid = self.hpo_obj.term_by_acc(acc)
				
		parentterms = self.hpo_obj.parents(termid)
		
		return self.hpo_obj.annotate_terms(parentterms).values()
	
	def parents(self,acc):
		# get tree of all parents of this hpo accession
		# returns a list of accessions in order of greatest distance node (root, 1)
		# to first parent
		
		termid = self.hpo_obj.term_by_acc(acc)
		
		parent_tree = self.hpo_obj.parent_tree(termid)

		parents = list()
		for distance in sorted(parent_tree,reverse=True):
			parents.append(self.hpo_obj.info_by_term(parent_tree[distance]))

		return parents

	def csweb_net(self,id):
		# from an hpo accession, produce a network for csweb
		return self.hpo_obj.acc_to_net(id)

	def csweb_net_anno(self,id):
		# from an hpo accession, return a tuple having a gml network and a dict 
		# of annotations having the subtree nodes by key hpo accession and value 
		# of hpo description
		return self.hpo_obj.acc_to_net_anno(id)

class Gene():

	def __init__(self,db_hugo,user,passwd,host):
	
		hugo_db_obj = hpo_db.Initialize(db=db_hugo,user=user,passwd=passwd,host=host).db_obj
		self.hugo_obj = hugo_db.HUGO(db_obj=hugo_db_obj)

	def desc_by_sym(self,sym):
		# get gene description for a gene symbol
		return self.hugo_obj.desc_by_sym(sym)

	def entrez_by_sym(self,sym):
		# get entrez id for a gene symbol
		return self.hugo_obj.entrez_by_sym(sym)

	def hgnc_by_sym(self,sym):
		# get hgnc id for a gene symbol
		return self.hugo_obj.hgnc_by_sym(sym)
