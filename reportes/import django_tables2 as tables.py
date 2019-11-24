import django_tables2 as tables
from reportes.model import Cliente

class ClienteTable(tables.Table):

	class Meta:
		model = Cliente
'''		# se agrega la clase 'paleblue' al tag <table> '''
		attrs = {"class": "paleblue"}