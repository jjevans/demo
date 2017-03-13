import MySQLdb as mysql
#import matplotlib.pyplot as plt
import networkx as nx
#import pygraphviz as pgv
import copy
import re
import StringIO

# query hpo database for phenos based on omim/umls

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
	
class HPO():

	def __init__(self,db=None,user=None,passwd=None,host=None,db_obj=None):
		
		if db_obj is None:
			self.db_obj = Initialize(db=db,user=user,passwd=passwd,host=host).db_obj
		else:
			self.db_obj = db_obj

		self.query_obj = Query(db_obj=self.db_obj)

	def generate_pheno(self):
		# get all phenotypes
		# returns dict with hpo id as key, hpo description as value
		query = ''' select t.acc,t.name from term t, annotation an where t.id = an.term_id'''
		
		response = self.query_obj.ask(query)
		
		res = dict()
		for pheno in response:
			res[pheno[0]] = pheno[1]
			
		return res
	
	def generate_pheno_by_name(self):
		# get all phenotypes
		# returns dict with hpo description as key, hpo id as value
		query = ''' select t.acc,t.name from term t, annotation an where t.id = an.term_id'''
		
		response = self.query_obj.ask(query)
		
		res = dict()
		for pheno in response:
			res[pheno[1]] = pheno[0]
			
		return res

	def info_by_term(self,termid):
		# returns a tuple of accession and name for hpo term id
		query = ''' select t.acc,t.name from term t where t.id = "'''+str(termid)+'"'
		
		response = self.query_obj.ask(query)

		return 
	def pheno_by_omim(self,omimid):
		query = '''select t.acc,t.name,eo.external_id 
				from term t, external_object eo, annotation an 
				where eo.id = an.external_object_disease_id 
				and t.id = an.term_id and eo.external_id = "'''+str(omimid) + '"'

		return self.query_obj.ask(query)

	def pheno_by_umls(self,cuid):
		query = '''select t.acc,t.name,eo.external_id 
				from external_object eo, term2external_object t2eo, term t 
				where eo.id=t2eo.external_object_id 
				and t2eo.term_id=t.id 
				and t.is_obsolete=0 
				and eo.external_id = "'''+cuid+'"'

		return self.query_obj.ask(query)

	def term_by_omim(self,omimid):
		query = '''select t.id,t.acc,t.name,eo.external_id 
				from term t, external_object eo, annotation an 
				where eo.id = an.external_object_disease_id 
				and t.id = an.term_id and eo.external_id = "'''+str(omimid) + '"'
				
		return self.query_obj.ask(query)
	
	def omim_by_term(self,hpoid):
		query = '''select t.acc,eo.external_id
					from term t, external_object eo, annotation an 
					where eo.id = an.external_object_disease_id 
					and t.id = an.term_id and t.acc = "'''+str(hpoid)+'"'

		return self.query_obj.ask(query)
	
	def omim_by_acc(self,hpoid):
		query = '''select eo.external_id
					from term t, external_object eo, annotation an 
					where eo.id = an.external_object_disease_id 
					and t.id = an.term_id and t.acc = "'''+str(hpoid)+'"'
		
		answer = self.query_obj.ask(query)
		
		dis = list()
		for ans in answer:
			dis.append(ans[0])
			
		return dis
		
	def print_ans(self,answer):
		
		for ans in answer:
			
			line = str()
			for col in ans:
				line += str(col)+"\t"
				
			print line.rstrip("\t")
			
		return

	def parent_tree(self,term):
		query = '''select gp.term1_id, gp.distance 
				from graph_path gp where gp.term2_id = "'''+str(term)+'"'
				
		answer = self.query_obj.ask(query)

		nodes = dict()
		for ans in answer:
			nodestr = str(ans[0])
			diststr = str(ans[1])
			
			if diststr not in nodes:
				nodes[diststr] = list()
			
			nodes[diststr].append(nodestr)
		
		return nodes

	def child_tree(self,term):
		query = '''select gp.term2_id, gp.distance 
				from graph_path gp where gp.term1_id = "'''+str(term)+'"'
				
		answer = self.query_obj.ask(query)

		nodes = dict()
		for ans in answer:
			nodestr = str(ans[0])
			diststr = str(ans[1])
			
			if diststr not in nodes:
				nodes[diststr] = list()
			
			nodes[diststr].append(nodestr)
		
		return nodes				
	
	def parents(self,term):
		query = '''select gp.term1_id 
				from graph_path gp where gp.distance = 1 and gp.term2_id = '''+str(term)
				
		answer = self.query_obj.ask(query)
		
		parents = list()
		for ans in answer:
			parents.append(str(ans[0]))
			
		return parents
		
	def children(self,term):
		query = '''select gp.term2_id 
				from graph_path gp where gp.distance = 1 and gp.term1_id = '''+str(term)
		
		answer = self.query_obj.ask(query)
		
		children = list()
		for ans in answer:
			children.append(str(ans[0]))
		
		return children
	
	def subtree_graph(self,term):
		# get graph of subtree from hpo term, input
		# is a term id
		
		kids = self.subtree(dict(),term)

		graph_obj = Graph()
		
		graph = graph_obj.make_graph(kids)

		atts = self.annotate_terms(graph.nodes())
		graph_obj.annotate_nodes(graph,atts)
		
		return graph

	def subtree(self,kids,term):
		# get all children of a term and find those children's children, etc
	
		for child in self.children(term):
			
			if term not in kids:
				kids[term] = list()
		
			kids[term].append(child)
			self.subtree(kids,child)
			
		return kids
									
	def combo_tree(self,treelst):
			
		whole = nx.Graph()
		for tree in treelst:
			whole = nx.compose(whole,tree)
		
		return whole
	
	def term_by_acc(self,acc):
		# reports the first term for an hpo accession (HP:0000001) (should only be 1)
		
		query = ''' select t.id from term t where t.acc = "''' + acc + '"'
		
		return str(self.query_obj.ask(query)[0][0])
	
	def anno_by_term(self,term):
		# gets accession id, description for a hpo term id
		
		query = '''select t.acc, t.name from term t where t.id = ''' + str(term)
		
		return self.query_obj.ask(query)

	def annotate_terms(self,termlst):
		# creates a dict of hpo accessions and names based on a list of terms
		
		res = dict()
		for term in termlst:
			annotation = self.anno_by_term(term)
			
			if len(annotation) != 0:
				res[term] = [annotation[0][0],annotation[0][1]]

		return res
			
	def acc_to_net(self,acc):
		# input is an hpo accession id
		
		term = self.term_by_acc(acc)

		kids = self.subtree(dict(),term)

		graph_obj = Graph()
		
		graph = graph_obj.sub_graph(kids,term)

		atts = self.annotate_terms(graph.nodes())
		graph_obj.annotate_nodes(graph,atts)

		graph_stream = StringIO.StringIO()
		graph_obj.write_gml(graph,graph_stream)

		net = graph_stream.getvalue()

		net = re.sub("[\n\t\s]+"," ",net)
		net = re.sub("'",'"',net)
		
		return net

class Graph():
	
	def make_digraph(self,tree):
		T = nx.DiGraph()
		
		lasts = list()
		for dist in sorted(tree):
			
			for node in tree[dist]:
				T.add_node(node)
			
				for last in lasts:
					T.add_edge(last,node)
			
			lasts = tree[dist]
		
		#print T.degree(["0"])
		#print nx.topological_sort(T)
		
		return T
	
	def make_graph(self,tree,len=None):
		G = nx.Graph()
		
		lasts = list()
		for dist in sorted(tree):
			
			for node in tree[dist]:
				G.add_node(node)
			
				for last in lasts:
					if len is None:
						G.add_edge(last,node)
					else:
						G.add_edge(last,node,length=len)
		
			lasts = tree[dist]
		
		return G

	def sub_graph(self,tree,root):
		G = nx.DiGraph()

		for parent in tree:
			if not G.has_node(parent):
				G.add_node(parent)
				
			for child in tree[parent]:
				if not G.has_node(child):
					G.add_node(child)
				
				G.add_edge(parent,child)
				
		return G

	def annotate_nodes(self,G,attributes):
		# pull out the node names (hpo term ids) and get associated
		# information in a dict with key of term id and value as 
		# a list having hpo accession and name/description.
		
		for node in G.nodes():
			acc = attributes[node][0]
			name = attributes[node][1]
			
			G.node[node]["accession"] = acc
			G.node[node]["name"] = name
			G.node[node]["label"] = name
			
		return
	
	def plot_digraph(self,graph):
		#labels=dict((n,d['accession']) for n,d in graph.nodes(data=True))
		labels = dict((n,d['name']) for n,d in graph.nodes(data=True))
		
		pos=nx.graphviz_layout(graph,prog='neato')
		nx.draw(graph,pos,labels=labels)
		#nx.draw(graph,labels=labels)
		
		plt.show()
		
		return
	
	def plot_graph(self,graph):
	
		labels=dict((n,d['accession']) for n,d in graph.nodes(data=True))
		#labels=dict((n,d['name']) for n,d in graph.nodes(data=True))
		
		#pos=nx.graphviz_layout(graph,prog='dot')
		#nx.draw(graph,pos,labels=labels)
		
		nx.draw(graph,labels=labels)
		
		plt.show()
		
		return

	def write_gml(self,graph,gmlfile):
	
		nx.write_graphml(graph,gmlfile)
		
		return

class HPO_Gene():

	def __init__(self,db=None,user=None,passwd=None,host=None,db_obj=None):
		
		if db_obj is None:
			self.db_obj = Initialize(db=db,user=user,passwd=passwd,host=host).db_obj
		else:
			self.db_obj = db_obj

		self.query_obj = Query(db_obj=self.db_obj)

	def entrez_by_pheno(self,pheno):
		query = "select entrez,symbol from pheno_to_gene where hpo = '"+pheno+"'"
		
		response = self.query_obj.ask(query)
		
		genes = dict()
		for res in response:
			genes[str(res[0])] = res[1]
			
		return genes
	
	def genes_by_pheno(self,pheno):
		query = "select symbol,entrez from pheno_to_gene where hpo = '"+pheno+"'"
		
		response = self.query_obj.ask(query)
		
		genes = dict()
		for res in response:
			genes[res[0]] = res[1]
			
		return genes
	
	'''def pheno_by_gene(self,gene):
		query = "select hpo from pheno_to_gene where symbol = '"+sym+"'"
		
		response = self.query_obj.ask(query)
		
		phenos	'''
			
	def num_gene(self,pheno):
		query = "select count(symbol) from pheno_to_gene where hpo = '"+pheno+"'"
		
		return self.query_obj.ask(query)

	def desc_by_pheno(self,pheno):
		query = "select description from pheno_to_gene where hpo = '"+pheno+"'"
		
		response = self.query_obj.ask(query)
		
		if len(response) != 0:
			return response[0][0]
		
		return str()
		
	def geneset(self):
		# pull out all genes for each phenotype
		query = "select distinct symbol from pheno_to_gene"
		
		response = self.query_obj.ask(query)
		
		genes = list()
		for res in response:
			# if comma delimited list, take only first gene symbol
			genes.append(res[0].split(", ")[0])
			
		return genes

	def pheno_by_gene(self,id):
		# pull out all phenotypes for a gene
		query = "select hpo from pheno_to_gene where symbol = '"+id+"'"
		
		return self.query_obj.ask(query)
