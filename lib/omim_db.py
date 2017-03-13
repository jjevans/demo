import MySQLdb as mysql
import re

# use a omim database of their morbidmap file

class Initialize():

	def __init__(self,db,user,passwd,host):
		self.db_obj = mysql.connect(db=db,user=user,passwd=passwd,host=host)

		return
		
class Query():

	def __init__(self,db=None,user=None,passwd=None,host=None,db_obj=None):
		
		if db_obj is None:
			self.db_obj = Initialize(db=db,user=user,passwd=passwd,host=host).db_obj
		else:	
			self.db_obj = db_obj
		
		self.curs = self.db_obj.cursor()
	
	def ask(self,query):
		self.curs.execute(query)
		
		return self.curs.fetchall()

class OMIM():
	
	def __init__(self,db=None,user=None,passwd=None,host=None,db_obj=None):
		
		if db_obj is None:
			self.db_obj = Initialize(db=db,user=user,passwd=passwd,host=host).db_obj
		else:	
			self.db_obj = db_obj
		
		self.query_obj = Query(db_obj=self.db_obj)
		self.series_obj = Series(db_obj=self.db_obj)
	
	def generate_dis(self,ps_keyword=""):
		# get all diseases (phenos) using a table produced by hacking the omim.txt file 
		# making it nice to fit in a database and removing unwanted lines.
		# dict returned with omim id as key, omim disease description as value (str)
		# also finds if the disease is a phenotypicSeries in a case statement populating
		# the third field with "(PS)" if so and "" if not
		query = "select distinct(t.omim),t.term, case when t.omim = s.omimid and s.omimid = s.seriesid and s.omimid is not null then '"+ps_keyword+"' when t.omim = s.omimid and s.omimid != s.seriesid and s.omimid is null then '' end from types t left join series s on t.omim = s.omimid where t.symbol_def = 'phenotype'"
		
		response = self.query_obj.ask(query)
		
		res = dict()
		for dis in response:
			resstr = dis[1]
			
			if dis[2] is not None:
				resstr += " "+str(dis[2])
			
			res[dis[0]] = resstr
			
		return res
	
	def generate_dis_by_name(self,ps_keyword=""):
		# get all diseases (phenos) using a table produced by hacking the omim.txt file 
		# making it nice to fit in a database and removing unwanted lines.
		# dict returned with disease description as key and disease omim id (str)
		# also finds if the disease is a phenotypicSeries in a case statement populating
		# the third field with "(PS)" if so and "" if not
		query = "select distinct(t.omim),t.term, case when t.omim = s.omimid and s.omimid = s.seriesid and s.omimid is not null then '"+ps_keyword+"' when t.omim = s.omimid and s.omimid != s.seriesid and s.omimid is null then '' end from types t left join series s on t.omim = s.omimid where t.symbol_def = 'phenotype'"
		
		response = self.query_obj.ask(query)
		
		res = dict()
		for dis in response:
			resstr = dis[1]
			
			if dis[2] is not None:
				resstr += " "+str(dis[2])

			res[resstr] = dis[0]
			
		return res

		
	def generate_dis_pattern(self):
		# get all omim diseases from omim.txt, returns dict with omimid key, desc val
		# uses sql pattern match
		query = "select line from omimtxt where line like '#%'"
		
		# grab descriptions/term for all phenos (line starts '#')
		response = self.query_obj.ask(query)
		
		res = dict()
		for line in response:
			(id,desc) = line[0].split(" ",1)
			res[id.lstrip("#")] = desc

		return res

	def fill_desc(self,idlst):
		# input is a list of omim phenotype/gene ids, out is a dict with omimid as key, description as val
		
		res = dict()
		for id in idlst:
			res[id.lstrip("#")] = self.desc_by_omim(id)
			
		return res

	def desc_by_id(self,omim):
		# get the description from an omim id, derives from types table (omim.txt)
		query = "select term from types where omim = "+str(omim)
		
		response = self.query_obj.ask(query)
		
		if len(response) != 0:
			return response[0][0]

		return None
	
	def desc_by_gene(self,omim):
		# get the description of a disease from the omimtxt table (omim.txt file)
		query = "select txt.line from omimtxt txt where txt.line like '*"+str(omim)+"%'"
		
		response = self.query_obj.ask(query)
		
		(id,desc) = response[0][0].split(" ",1)
		
		return desc		
	
	def anno_genelst(self,idlst):
		
		anno = list()
		for id in idlst:
			desc = 	self.desc_by_id(id)
			anno.append((id,desc))
			
		return anno
	
	def sym_by_gene(self,omim):
		# get gene symbol for a omim gene id from the omimtxt table
		query = "select term from types where omim = "+str(omim)
		
		response = self.query_obj.ask(query)
		
		sym = str()
		if len(response) != 0:
			try:
				(desc,sym) = response[0][0].split("; ",1)
			except:
				pass
				
		return sym

	def gene_by_sym(self,sym):
		# get omim id for a gene symbol
		query = "select omim from types where term like '%; "+sym+"%'"
		
		response = self.query_obj.ask(query)
		
		gene = list()
		for res in response:
			gene.append(res[0])
			
		return gene

	def gene_by_dis(self,omim):
		# get the genes related to an omim phenotype
		query = "select gene,pheno from morbidmap_pheno_gene where pheno = "+str(omim)
		
		return self.query_obj.ask(query)

	def dis_by_gene(self,omim):
		# get the diseases related to an omim disease
		query = "select pheno from morbidmap_pheno_gene where gene = "+str(omim)
		
		response = self.query_obj.ask(query)
		
		dis = list()
		for res in response:
			dis.append(str(res[0]))
			
		return dis

	def geneset(self):
		# get all gene symbols in omim
		# returns a list, if no gene symbol available, skips it
		query = "select term from types where symbol_def = 'gene' or symbol_def = 'gene_phenoknown'"
		
		response = self.query_obj.ask(query)
		
		gene = list()
		for res in response:
			try:
				(desc,sym) = res[0].split("; ",1)
				gene.append(sym)
			except:
				pass
					
		return gene
		
class Convert():

	def __init__(self,db=None,user=None,passwd=None,host=None,db_obj=None):
		
		if db_obj is None:
			self.db_obj = Initialize(db,user,passwd,host).db_obj
		else:	
			self.db_obj = db_obj
	
		self.query_obj = Query(db_obj=self.db_obj)
		
	# find out if it is a gene or phenotype omim number
	def is_gene(self,omim):
		query = "select count(pheno) from morbidmap_pheno_gene where gene = "+str(omim)
		
		response = self.query_obj.ask(query)
		
		if response[0][0] > 0:
			return True
			
		return False
		
	def is_pheno(self,omim):
		query = "select count(gene) from morbidmap_pheno_gene where pheno = "+str(omim)
		
		response = self.query_obj.ask(query)
		
		if response[0][0] > 0:
			return True
			
		return False
		
	def flip(self,omim):
		
		if self.is_gene(omim):
			query = "select pheno from morbidmap_pheno_gene where gene = "+str(omim)
		elif self.is_pheno(omim):
			query = "select gene from morbidmap_pheno_gene where pheno = "+str(omim)
		else:
			return None
			
		return self.query_obj.ask(query)

	def flip_pheno_to_gene(self,omim):
		query = "select gene from morbidmap_pheno_gene where pheno = "+str(omim)
		
		response = self.query_obj.ask(query)
		
		return self.format_set(response)
		
	def flip_gene_to_pheno(self,omim):
		query = "select pheno from morbidmap_pheno_gene where gene = "+str(omim)
		
		response = self.query_obj.ask(query)

		return self.format_set(response)
	
	def format_set(self,set):
	
		format = list()
		for item in set:
			format.append(item[0])
	
		return format
		
class Series():

	def __init__(self,db=None,user=None,passwd=None,host=None,db_obj=None):
		
		if db_obj is None:
			self.db_obj = Initialize(db=db,user=user,passwd=passwd,host=host).db_obj
		else:
			self.db_obj = db_obj
		
		self.query_obj = Query(db_obj=self.db_obj)

	def is_series(self,omim):
		query = "select count(*) from series where seriesid = "+str(omim)
		
		response = self.query_obj.ask(query)
		
		if response[0][0] > 1:
			return True
			
		return False
		
	def has_series(self,omim):

		query = "select count(*) from series where omimid = "+str(omim)
		
		response = self.query_obj.ask(query)
		
		if response[0][0] > 1:
			return True
			
		return False
				
	def get_ps(self):
		query = "select distinct seriesterm, seriesid from series"
	
		return self.query_obj.ask(query)
		
	def sub_from_ps(self,omim):
		query = "select omimid,omimterm from series where seriesid="+str(omim)
		
		response = self.query_obj.ask(query)
		
		# get rid of duplicate entries having same omim id
		subs = list()
		for res in response:
			if(res[0] != omim):
				subs.append(res)
		
		return tuple(subs)

	def ps_from_sub(self,omim):
		query0 = "select seriesid from series where omimid = "+str(omim)
		response0 = self.query_obj.ask(query0)
		
		query1 = "select omimid,omimterm from series where omimid = "+str(response0[0][0])
		response1 = self.query_obj.ask(query1)
		
		return (response1[0][0],response1[0][1])
		
	def sub_from_sub(self,omim):
		# returns all subdiseases if the omim id is part of a phenotypicSeries
		query = "select distinct(s.omimid),s.omimterm,s.seriesid from series s,(select seriesid from series where omimid = "+str(omim)+") as serselect where serselect.seriesid = s.seriesid"
		
		response = self.query_obj.ask(query)
		
		subs = list() # reformat making tuple of tuples a list of lists
		for res in response:
			subs.append(list(res))
			
		return subs
	
	def omim_no_series(self):
		# pulls out the omim ids that do not belong to a phenotypicSeries
		query = "select gm.omim from genemap gm left join series s on gm.omim = s.omimid where s.omimid is null"
		
		return self.query_obj.ask(query)
	
	def geneset(self):
		# pull out all genes in omim found in the series table
		# only use first gene symbol from all synonyms if multiple
		
		query = "select distinct symbol from series"
		
		response = self.query_obj.ask(query)
		
		genes = list()
		for res in response:
			#genes.append(res[0].split(", ")[0])
			genes.append(res[0])		
		return genes
			
class Info():
	
	def __init__(self,db=None,user=None,passwd=None,host=None,db_obj=None):
	
		if db_obj is None:
			self.db_obj = Initialize(db=db,user=user,passwd=passwd,host=host).db_obj
		else:
			self.db_obj = db_obj
		
		self.query_obj = Query(db_obj=self.db_obj)

	def generic_query(self,query):
		return self.query_obj.ask(query)
