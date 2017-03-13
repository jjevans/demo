from mako.template import Template

# integrate creation of ontology content with creation of its html

class Page_Gen():

	def render(self,plate,**kwargs):
		return Template(filename=plate).render(**kwargs)
