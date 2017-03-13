import MySQLdb as mysql

# interface to mysql db "hugo" for gene descriptions

class Initialize():

	def __init__(self,db,user,passwd,host):
		self.db_obj = mysql.connect(db=db,user=user,passwd=passwd,host=host)
				
		return
	
class Query():

	def __init__(self,db=None,user=None,host=None,db_obj=None):
		
		if db_obj is None:
			self.db_obj = Initialize(db=db,user=user,passwd=passwd,host=host).db_obj
		else:
			self.db_obj = db_obj
		
		self.curs = self.db_obj.cursor()
		
	def ask(self,query):
		self.curs.execute(query)
		
		return self.curs.fetchall()
	
class HUGO():

	def __init__(self,db=None,user=None,passwd=None,host=None,db_obj=None):
		
		if db_obj is None:
			self.db_obj = Initialize(db,user,passwd,host).db_obj
		else:
			self.db_obj = db_obj

		self.query_obj = Query(db_obj=self.db_obj)
	
	def hgnc_by_sym(self,sym):
		# return the hgnc id for a gene symbol
		query = "select hgnc from genes where symbol = '"+str(sym)+"'"
		
		hgnc = str()
		try:
			hgnc = self.query_obj.ask(query)[0][0]
		except:
			pass
			
		return hgnc	

	def desc_by_sym(self,sym):
		# return the gene description for a gene symbol
		query = "select description from genes where symbol = '"+sym+"'"
		
		desc = str()
		try:
			desc = self.query_obj.ask(query)[0][0]
		except:
			desc = None
			
		return desc
	
	def entrez_by_sym(self,sym):
		# get entrez id from a gene symbol
		query = "select entrez from genes where symbol = '"+str(sym)+"'"
		
		entrez = str()
		try:
			entrez = self.query_obj.ask(query)[0][0]
			
			if entrez == 0:
				entrez = str()
		except:
			pass		
			
		return entrez
