# -*- coding: utf-8 -*-

from django.shortcuts import render,get_object_or_404,redirect,render_to_response
from django.db.models import Q
from django.http import HttpResponse,HttpResponseRedirect
from django_tables2 import RequestConfig
from .models import Cliente,Reporte
from django.template import RequestContext,loader
from django.core.urlresolvers import reverse
from .forms import ClienteForm,FiltraclienteForm
from .tables import ClienteTable, ClienteTableSeleccionados


''' FUNCION PARA LISTAR CLIENTES '''


'''def listaclientes(request):
	cl = Cliente.objects.all()
	context = {'cl':cl,}
	return render(request,'reportes/listaclientes.html',context )'''

def listaclientes(request):
	cl = ClienteTable(Cliente.objects.all())
	mensaje = 'Asi esta la cosa !'
	RequestConfig(request, paginate={"per_page":10}).configure(cl)
	#RequestConfig(request).configure(cl)
	context = {'cl':cl,'mensaje':mensaje,}
	return render(request,'reportes/listaclientes.html',context)

def filtraclientes(request):
	if request.method == 'POST':
		form = FiltraclienteForm(request.POST)
		print form.is_valid()
		if form.is_valid():
			''' limpia datos '''
			buscar_por = form.cleaned_data['buscar_por']
			id_cliente = form.cleaned_data['id_cliente']
			token_to_search = form.cleaned_data['token_to_search']
			
			
			if buscar_por == '1':
				queryset = Cliente.objects.filter(pk=id_cliente)
				cl = ClienteTable(queryset)
			else :
				queryset = Cliente.objects.filter(Q(nombre__icontains=token_to_search) | Q(domicilio__icontains = token_to_search))
				cl = ClienteTable(queryset)
			
			if not queryset.exists():
				mensaje ='No se encontraron registros en la base de datos...'
			else:
				mensaje ="Resultados obtenidos:"

			RequestConfig(request,paginate={"per_page":10}).configure(cl)
			context = {'cl':cl,'mensaje':mensaje}
			return render(request,'reportes/listaclientes.html',context)
		else:
			form = FiltraclienteForm()
	form = FiltraclienteForm()
	return render(request,'reportes/filtraclientes.html',{'form':form,})


''' FUNCION PARA CREAR CLIENTES '''

def creacliente(request):
	mensaje = 'Ingrese datos del cliente'
	if request.method =='POST':
		form = ClienteForm(request.POST)
		if form.is_valid():
			form.save()
			mensaje = "Cliente agregado correctamente.! "
			return HttpResponseRedirect(reverse('reportes:listaclientes',args=()),{'mensaje':mensaje,})
	else:
		form = ClienteForm()
	return render(request,'reportes/creacliente.html',{'form':form,})



''' FUNCION PARA MODIFICAR CLIENTES'''


def modificacliente(request,id_cliente):
	import pdb
	pdb.set_trace()
	cl = get_object_or_404(Cliente,pk=id_cliente)
	print id_cliente
	mensaje ='Cliente aun no modificado !'
	
	if request.method =='POST':
		form = ClienteForm(request.POST)
		if form.is_valid():
			nombre = form.cleaned_data['nombre']
			domicilio = form.cleaned_data['domicilio']
			email = form.cleaned_data['email']
			cl.nombre = nombre.upper()
			cl.domicilio = domicilio.upper()
			cl.email = email
			cl.save()
			mensaje = "Cliente modificado correctamente.! "
			return HttpResponseRedirect(reverse('reportes:listaclientes',args=()))
	else:
		mensaje ='entro aqui'
		form = ClienteForm(initial={'id':cl.id, 'nombre':cl.nombre,'domicilio':cl.domicilio,'email':cl.email,})
		print form
		print mensaje
	return render(request,'reportes/modificacliente.html',{'form':form,'mensaje':mensaje,'id_cliente':id_cliente})


def eliminaclientes(request):
	cl = ''
	mensaje = ''
	if request.method == 'POST':
		mensaje = "Advertencia !  Los siguientes registros han sido seleccionados para ser eliminados:"
		pks = request.POST.getlist("sel")
		cl = ClienteTableSeleccionados(Cliente.objects.filter(pk__in= pks))
		#cl = Cliente.objects.filter(nombre__in = pks)
		RequestConfig(request,paginate ={'per_page':25}).configure(cl)
	return render(request,'reportes/eliminaclientes.html',{'cl':cl,'mensaje':mensaje,'pks':pks,})	

def commitdelclientes(request):
	pks = request.POST.getlist("sel")
	print pks
	#cl= ClienteTableSeleccionados(Cliente.objects.filter(pk__in= pks))
	if request.method == 'POST':
		mensaje = " Clientes eliminados con éxito !"
		for r in pks:
			Cliente.objects.filter(pk=r).delete()
	cl = ClienteTable(Cliente.objects.all())
	return render(request,'reportes/listaclientes.html',{'pks':pks,'cl':cl,})

	

''' FUNCION PARA LISTAR REPORTES DE UN CLIENTE '''


def reportes_por_cliente(request,id_cliente):
	cl = Cliente.objects.get(pk=id_cliente)
	re = Reporte.objects.filter(id_cliente=cl.id)
	template = loader.get_template('reportes/reportes_por_cliente.html')
	context = RequestContext(request,{'re':re,'cl':cl,})
	return HttpResponse(template.render(context))

def clienteactualizado(request):
	mensaje = "Cliente actualizado con exito !"
	return render(request,'reportes/clienteactualizado.html',{'mensaje':mensaje,})

def muestracliente(request,id_cliente):

	cl = Cliente.objects.get(pk=id_cliente)
	response = "Estas en muestracliente viendo el cliente %s, con numero %s" 
	return HttpResponse(response %(cl,id_cliente))

def reportes_por_cliente_alterno(request,id_cliente):

	ReporteFormSet = inlineformset_factory(Cliente, Reporte, fields=('descripcion',))
	cliente = Cliente.objects.get(pk=id_cliente)
	formset = ReporteFormSet(instance=cliente)
	return render(request,'reportes/reportes_por_cliente_alterno.html',{'cl':cliente,'formset':formset,})





