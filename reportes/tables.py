# -*- coding: utf-8 -*-


import django_tables2 as tables
from reportes.models import Cliente

class ClienteTable(tables.Table):

	id = tables.TemplateColumn('<a href="/reportes/modificacliente/{{record.id}}">{{record.id}}</a>')
	sel = tables.CheckBoxColumn(accessor='pk',orderable='False')
	  
	
	class Meta:
	    model = Cliente
	    attrs = {"class": "paleblue"}
	    sequence = ("sel","id","nombre","domicilio","email")


class ClienteTableSeleccionados(tables.Table):
	
	''' La siguiente columna 'sel' es virtual y la agregue para por ella hacer ella
	filtro en el queryset de la funcion commitdelcliente, porque si no uso una 
	columna virtual no hace el queryset, de hecho intenté usar la columa id de la tabla.
	real pero no funciono. Otra cosa, la columna que funciono para el queryset a 
	fuerza tuvo que ser del tipo CheckBoxColumn, hay que seguir probando con otros
	tipos o leer mas sobre table2..por ahora funciona. '''

	sel = tables.CheckBoxColumn(accessor='pk',orderable='False',default='True')
	
	class Meta:
	    model = Cliente
	    attrs = {"class": "paleblue"}
	    