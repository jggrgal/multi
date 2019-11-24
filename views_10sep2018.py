
#-*- encoding: utf-8 -*-

from django.shortcuts import render,redirect,render_to_response
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.template import RequestContext,loader
from django.core.urlresolvers import reverse
from django.core import serializers
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.contrib.auth.decorators import login_required,permission_required
from .forms import AccesoForm,BuscapedidosForm,PedidosForm,RegsocwebForm,Forma_RegistroForm,BuscapedidosporsocioForm,Calzadollego_gralForm,Calzadollego_detalleForm,Consulta_colocacionesForm,Consulta_ventasForm,Consulta_comisionesForm
from pedidos.models import Asociado,Articulo,Proveedor,Configuracion
from django.db import connection,DatabaseError,Error,transaction,IntegrityError
from datetime import datetime,date,time,timedelta
from django.conf import settings
import pdb
import unicodedata
import json
from collections import namedtuple
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# Las siguiente 3 lineas son para que se indicar a python que hagas las conversiones
# de unicode a utf-8 en lugar de hacerlas a ascii.
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# Para serializar objetos decimales con json, porque si se serializan directamente no funciona.
# ahorita no se utiliza..pero hay que ver como utilizarla, tambien hay que probar si json puede serializar fechas 
# y otros tipos de objeto.

'''
class DecimalEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)
'''

'''
def falselogin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
           	redirect('pedidos/autenticacion_exitosa.html')
        else:
            # Return a 'disabled account' error message
            redirect('pedidos/cuenta_desactivada.html')
    else:
        # Return an 'invalid login' error message.
        	redirect('pedidos/autenticacion_fallida.html')
'''

def index(request):

	request.session.set_test_cookie()

	return render(request,'pedidos/index.html')


def logout_view(request):
   	logout(request)
   	return redirect('http://www.multimarcaslaredo.com')# Redirect to a success page.


''' La siguiente variable global se utiliza para guardar el numero de socio en zapcat se actualiza en la rutina "acceso", 
este valor sera utilizado por  la rutina busca_pedidos  para las consultas sql.'''

#g_numero_socio_zapcat = 0




def acceso(request):
	global g_numero_socio_zapcat
	
	
	mensaje=""
	if request.session.test_cookie_worked():
		request.session.delete_test_cookie()
		
	else:
		
		if request.session.session_key is None:
			return HttpResponse("Por favor active cookies en su navegador e intente nuevamente.")

	# Se trae la session
	session_id = request.session.session_key

	print "SESION:"
	print session_id

	print "USUARIO:"
	print request.user
	usuario_en_session = request.user
	
	# elimina registros de tabla temporal de pedidos.
	cursor = connection.cursor()
	cursor.execute("DELETE FROM pedidos_pedidos_tmp WHERE session_key=%s;",[session_id])
	
	
	if request.method =='POST':
		
		

		form = AccesoForm(request.POST)
		if form.is_valid():
			
						

			username = request.POST.get('username')
			password = request.POST.get('password')
			
						
			user = authenticate(username=username, password=password)
			
			if user is not None:
			
				if user.is_active:
					login(request, user)
					mensaje = 'Bienvenido a su sistema de pedidos !'
					cursor.execute("SELECT asociadono FROM asociado where num_web=%s;",[request.user.id])

					socio_datos = dictfetchall(cursor)
					
					if not socio_datos:
						print "Ud. no tiene asignado un numero de socio, por favor consulte al administrador el sistema"					
					else:
						for r in socio_datos:
							g_numero_socio_zapcat = r['asociadono']

							request.session['socio_zapcat'] = r['asociadono']
											
					# Con la siguiente linea cierra la session al cerrar el navegador.		
					request.session.set_expiry(0)
					print ("por  aqui paso segurito")
					form = BuscapedidosForm()
					return render(request,'pedidos/busca_pedidos.html',{'form':form,'usuario':request.user},)
				else:
					# Return a 'disabled account' error message
					mensaje = 'Usuario y contraseña correctos pero su cuenta está desactivada, comuniquese por favor con el equipo de ES Shoes Multimarcas. !'
					
			else:
				# Return an 'invalid login' error message.
				mensaje = 'Usuario y/o contraseña incorrectos, intente de nuevo !'
		else:			 
			return render(request,'pedidos/acceso.html',{'form':form})
	request.session.set_test_cookie()
	form=AccesoForm()
	return render(request,'pedidos/acceso.html',{'form':form,'mensaje':mensaje,})

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    	]



def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]



def crea_tabla_pedidos_temporal():

	try:

		cursor = connection.cursor()
		cursor.execute('CREATE TEMPORARY TABLE IF NOT EXISTS pedidos_tmp (id int AUTO_INCREMENT,idproducto char(16),idprovedor int, catalogo char(12),precio decimal(8,2),nolinea int, PRIMARY KEY(id));')
		print "Entro a crear tabla temporal de pedidos"

	except Error as e:	
		print "NO creo tabla de pedidos %s" %e
		

	return()

def lista_asociados(request):
	cursor=connection.cursor()
	cursor.execute('SELECT asociadono,nombre,appaterno,apmaterno,telefono1 from Asociado limit 20;')
	asociados = dictfetchall(cursor)
	for a in asociados:
		print a
	context = {'asociados': asociados}
	return render(request, 'pedidos/asociados.html', context)	
		
def ok(request):
	
	return render(request, 'pedidos/autencitacion_exitosa.html')	


def busca_pedidos(request):

	try:
	
		g_numero_socio_zapcat = request.session['socio_zapcat']	
	except KeyError :

		return	HttpResponse("Ocurrió un error de conexión con el servidor, Por favor salgase completamente y vuelva a entrar a la página !")

	if request.user.is_authenticated():		
		
		if request.method == 'POST':
			form = BuscapedidosForm(request.POST)
			'''
			Si la forma es valida se normalizan los campos numpedido, status y fecha,
			de otra manera se envia la forma con su contenido erroreo para que el validador
			de errores muestre los mansajes correspondientes '''

			if form.is_valid():
			
				# limpia datos 
				numpedido = form.cleaned_data['numpedido']
				status = form.cleaned_data['status']
				fecha = form.cleaned_data['fecha']
				print "fecha es"
				print fecha
				# Convierte el string '1901-01-01' a una fecha valida en python
				# para ser comparada con la fecha ingresada 

				fecha_1901 =datetime.strptime('1901-01-01', '%Y-%m-%d').date()
				hoy = date.today()
				print "hoy es "
				print hoy

				# Establece conexion con la base de datos
				cursor=connection.cursor()
				
				# Comienza a hacer selects en base a criterios 


				if numpedido != 0:
					cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,h.fechapedido,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) where h.asociadono=%s and h.pedidono=%s;", (g_numero_socio_zapcat,numpedido))
					
				else :
					if  status == 'Todos' and fecha != fecha_1901:
						cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,h.fechapedido,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) where h.asociadono=%s and h.fechapedido>=%s and h.fechapedido<=%s ORDER BY h.pedidono DESC;", (g_numero_socio_zapcat,fecha-timedelta(days=21),fecha))
						print "Entro en status=Todos y fecha != 19010101"
					else:
						if status !='Todos' and fecha == fecha_1901:
							cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,h.fechapedido,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) where h.asociadono=%s and l.status=%s and h.fechapedido>=%s and h.fechapedido<=%s ORDER BY h.pedidono DESC;", (g_numero_socio_zapcat,status,hoy-timedelta(days=21),hoy))
							print "Entro en status != Todos y fecha=1901/01/01"
						else:
	 						if status != 'Todos' and fecha != fecha_1901:
								cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,h.fechapedido,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) where h.asociadono=%s and l.status=%s and h.fechapedido>=%s and h.fechapedido<=%s ORDER BY h.pedidono DESC;", (g_numero_socio_zapcat,status,fecha-timedelta(days=21),fecha))			
								print "Entro en status != Todos y fecha != 1901/01/01"
							else:
								mensaje ='No se encontraron registros !'
				
				# El contenido del cursor se convierte a diccionario para poder
				# ser enviado como parte del contexto y sea manipulable.				
				pedidos = dictfetchall(cursor)
				for pun in pedidos:
					print pun

				elementos = len(pedidos)
				

				if not pedidos:
					mensaje = 'No se encontraron registros !'
				else:
					mensaje ='Registros encontrados:'
				
				context = {'pedidos':pedidos,'mensaje':mensaje,'elementos':elementos,}

				# Cierra la conexion a la base de datos
				cursor.close()
				
				return render(request,'pedidos/lista_pedidos.html',context)
			
		else:
			form = BuscapedidosForm()
			#cursor.close()
			
		return render(request,'pedidos/busca_pedidos.html',{'form':form,})
	else:
		redirect('/pedidos/acceso/') 




def lista_pedidos(request):
	context = {'asociados': asociados,'form':form}
	return render(request, 'pedidos/asociados.html', context,{'form':form})


# La siguiente funcion es utilizada para seleccionar 
# los proveedores y que se puedan mostrar en el combo de proveedor al hacer un
# pedido, dicho combo debe tener como valor inicial esta lista para que de ahi
# se pueda hacer la seleccion.

def lista_Proveedores():
	cursor=connection.cursor()
	cursor.execute('SELECT proveedorno,razonsocial from Proveedor where trim(razonsocial)<>"";')
	
	pr=() # Inicializa una tupla para llenar combo de Proveedores
	
	for row in cursor:
		elemento = tuple(row)
		pr=pr+elemento
	x=[]
	y=[]
	
	for i in range(0,len(pr)):
		if i % 2 != 0:
			x.append(pr[i])
			x.append(pr[i])
			y.append(x)
			x=[]
	
	# tuple_of_tuples = tuple(tuple(x) for x in list_of_lists)
	lsuc = tuple(tuple(x) for x in y)
	
	return (lsuc)

def lista_Sucursales():
	cursor=connection.cursor()
	cursor.execute("SELECT nombre from sucursal where SucursalNo >= %s;",[0])
	lsuc = ()
	for row in cursor:
		elemento = tuple(row)
		lsuc=lsuc+elemento
	#lsuc=('SELECCIONE...',)+lsuc
	
	return (lsuc)	
	


@login_required(login_url = "/pedidos/acceso/")
def crea_pedidos(request):
	#import pdb; pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	
	mensaje = " "

	# elimina cualquier registro de la session.
	session_id = request.session.session_key
	cursor = connection.cursor()
	cursor.execute("DELETE FROM pedidos_pedidos_tmp where session_key= %s;",[session_id])	
	cursor.close()


	#for key,value in pr_dict.items():
	#	print key,value 
	
	 
	if request.method =='POST':
		
		form = PedidosForm(request.POST)

		if form.is_valid():
			
			
			proveedor = form.cleaned_data['proveedor']
			temporada =  form.cleaned_data['temporada']
			catalogo = form.cleaned_data['catalogo']
			pagina = form.cleaned_data['pagina']
			estilo = form.cleaned_data['estilo']
			marca = form.cleaned_data['marca']
			color = form.cleaned_data['color']
			talla = form.cleaned_data['talla']	



			#cursor=connection.cursor()
			#registro_encontrado = 0
			#cursor.execute("SELECT a.codigoarticulo from articulo a where a.proveedor=%s and a.temporada=%s and a.catalogo=%s and a.pagina=%s and a.estilo=%s and a.marca=%s and a.color=%s and a.talla=%s", (proveedor,temporada,catalogo,pagina,estilo,marca,color,talla))
			#articulo=dictfetchall(cursor);
			mensaje = "El articulo encontrado fue:abcd " #+ articulo.codigoarticulo
			return render(request,'pedidos/crea_pedido.html',{'form':form,'mensaje':mensaje,})
		else:	
			print " forma Invalida !!!!!"
			print form	
			mensaje = "Error en la forma"
			return render(request,'pedidos/crea_pedidos.html',{'form':form,'mensaje':mensaje,})

	form = PedidosForm()
	mensaje = "Entrando de nuevo a la forma"
	print form
	return render(request,'pedidos/crea_pedidos.html',{'form':form,'mensaje':mensaje,})	

#  LOGICA PARA COMBO DE TEMPORADAS

def lista_Temporadas(id_prov):
	
	cursor=connection.cursor()
	cursor.execute("SELECT clasearticulo from Catalogostemporada where proveedorno=%s and anio=%s;",[id_prov,id_temp])
	
	listacat=() # Inicializa una tupla para llenar combo de Proveedores
			
	# Convierte el diccionario en tupla
	for row in cursor:
		elemento = tuple(row)
		listacat=listacat+elemento
	listacat=('SELECCIONE...',)+listacat
	
	return (listacat)	

def combo_temporadas(request,*args,**kwargs):
	if request.is_ajax() and request.method == 'GET':
		id_prov = request.GET['id_prov']
		
		
		
		# Trae la lista de catalogos con los parametros indicados:
		l = (('0','SELECCIONE...'),('1','Primavera/Verano'),('2','Otoño/Invierno'))
		
		#data = serializers.serialize('json',r,fields=('clasearticulo',))
		
		# La siguiente instruccion genera una variable data con los datos en formato json.
		# En la linea anterior ( que esta comentada ), trataba de usar
		# serielizers para convertir a json pero no funciono.

		
		data = {'Mensaje':"El id proveedor recibido fue %s" % request.POST.get['id_prov']}
		#data = json.dumps(l)
		
		# En el siguiente return utilizo content_type. Intente usar 'mimetype'
		# en lugar de 'content_type' y no funciono.

		return HttpResponse(data)
	else:
		raise Http404
		print "No hallo pagina para combo temporada"







#  LOGICA PARA COMBO DE CATALOGOS

def lista_Catalogos(id_prov,id_temp,g_numero_socio_zapcat):

	
	print "El socio zapcata es :"
	print g_numero_socio_zapcat
	cursor=connection.cursor()
	#cursor.execute("SELECT clasearticulo from catalogostemporada where proveedorno=%s and anio=%s;",(id_prov,id_temp))
	cursor.execute("SELECT s.clasearticulo from sociocatalogostemporada s inner join catalogostemporada c on (s.ProveedorNo=c.ProveedorNo and s.Periodo=c.Periodo and s.Anio=c.Anio and s.ClaseArticulo=c.ClaseArticulo)  where s.proveedorno=%s and s.anio=%s and s.AsociadoNo=%s and s.Activo=1 and c.Activo=1;",[id_prov,id_temp,g_numero_socio_zapcat])
	
	listacat=() # Inicializa una tupla para llenar combo de Proveedores
			
	# Convierte el diccionario en tupla
	for row in cursor:
		elemento = tuple(row)
		listacat=listacat+elemento
	listacat=('SELECCIONE...',)+listacat
	
	return (listacat)	

def combo_catalogos(request,*args,**kwargs):
	g_numero_socio_zapcat = request.session['socio_zapcat']

	if request.is_ajax() and request.method == 'GET':
		id_prov = request.GET['id_prov']
		id_temp = request.GET['id_temp']
		
		
		# Trae la lista de catalogos con los parametros indicados:
		l = lista_Catalogos(id_prov,id_temp,g_numero_socio_zapcat)
		
		#data = serializers.serialize('json',r,fields=('clasearticulo',))
		
		# La siguiente instruccion genera una variable data con los datos en formato json.
		# En la linea anterior ( que esta comentada ), trataba de usar
		# serielizers para convertir a json pero no funciono.

		data = json.dumps(l)
		#data = {'Mensaje':"El id proveedor recibido fue %s" % request.GET['id_prov']}
				
		# En el siguiente return utilizo content_type. Intente usar 'mimetype'
		# en lugar de 'content_type' y no funciono.

		return HttpResponse(data,content_type='application/json')
	else:
		raise Http404
		

#  LOGICA PARA COMBO DE ESTILO

def lista_Estilos(id_prov,id_temp,id_pag,id_cat):
	
	cursor=connection.cursor()
	cursor.execute("SELECT estilo from preciobase where empresano=1 and proveedorid=%s and temporada=%s and pagina=%s and catalogo=%s GROUP BY estilo;",[id_prov,id_temp,id_pag,id_cat])
	
	listaest=() # Inicializa una tupla para llenar combo de Estilos
			
	# Convierte el diccionario en tupla
	for row in cursor:
		elemento = tuple(row)
		listaest=listaest+elemento
	listaest=('SELECCIONE...',)+listaest
	
	return (listaest)	

def combo_estilos(request,*args,**kwargs):
	if request.is_ajax() and request.method == 'GET':
		id_prov = request.GET['id_prov']
		id_temp = request.GET['id_temp']
		id_pag = request.GET['id_pag']
		id_cat = request.GET['id_cat']
		
		# Trae la lista de catalogos con los parametros indicados:
		l = lista_Estilos(id_prov,id_temp,id_pag,id_cat)
		
		#data = serializers.serialize('json',r,fields=('clasearticulo',))
		
		# La siguiente instruccion genera una variable data con los datos en formato json.
		# En la linea anterior ( que esta comentada ), trataba de usar
		# serielizers para convertir a json pero no funciono.

		data = json.dumps(l)
		#data = {'Mensaje':"El id proveedor recibido fue %s" % request.GET['id_prov']}
				
		# En el siguiente return utilizo content_type. Intente usar 'mimetype'
		# en lugar de 'content_type' y no funciono.

		return HttpResponse(data,content_type='application/json')
	else:
		raise Http404
		
#  LOGICA PARA COMBO DE MARCAS

def lista_Marcas(id_prov,id_temp,id_pag,id_cat,id_est):
	
	cursor=connection.cursor()
	cursor.execute("SELECT idmarca from preciobase where empresano=1 and proveedorid=%s and temporada=%s and pagina=%s and catalogo=%s and estilo=%s GROUP BY idmarca;",[id_prov,id_temp,id_pag,id_cat,id_est])
	
	listamar=() # Inicializa una tupla para llenar combo de Estilos
			
	# Convierte el diccionario en tupla
	for row in cursor:
		elemento = tuple(row)
		listamar=listamar+elemento
	listamar=('SELECCIONE...',)+listamar
	
	return (listamar)	



def combo_marcas(request,*args,**kwargs):
	if request.is_ajax() and request.method == 'GET':
		id_prov = request.GET['id_prov']
		id_temp = request.GET['id_temp']
		id_pag = request.GET['id_pag']
		id_cat = request.GET['id_cat']
		id_est = request.GET['id_est']

			
		# Trae la lista de catalogos con los parametros indicados:
		l = lista_Marcas(id_prov,id_temp,id_pag,id_cat,id_est)
		
		#data = serializers.serialize('json',r,fields=('clasearticulo',))
		
		# La siguiente instruccion genera una variable data con los datos en formato json.
		# En la linea anterior ( que esta comentada ), trataba de usar
		# serielizers para convertir a json pero no funciono.

		data = json.dumps(l)
		#data = {'Mensaje':"El id proveedor recibido fue %s" % request.GET['id_prov']}
				
		# En el siguiente return utilizo content_type. Intente usar 'mimetype'
		# en lugar de 'content_type' y no funciono.

		return HttpResponse(data,content_type='application/json')
	else:
		raise Http404
		
#  LOGICA PARA COMBO DE COLOR

def lista_Colores(id_prov,id_temp,id_pag,id_cat,id_est,id_mar):
	
	
	
	cursor=connection.cursor()
	cursor.execute("SELECT idcolor from preciobase where empresano=1 and proveedorid=%s and temporada=%s and pagina=%s and catalogo=%s and estilo=%s and idmarca=%s GROUP BY idcolor;",[id_prov,id_temp,id_pag,id_cat,id_est,id_mar])
	
	listacol=() # Inicializa una tupla para llenar combo de Estilos
			
	# Convierte el diccionario en tupla
	for row in cursor:
		elemento = tuple(row)
		listacol=listacol+elemento
	listacol=('SELECCIONE...',)+listacol
	
	return (listacol)	



def combo_colores(request,*args,**kwargs):
	if request.is_ajax() and request.method == 'GET':
		id_prov = request.GET['id_prov']
		id_temp = request.GET['id_temp']
		id_pag = request.GET['id_pag']
		id_cat = request.GET['id_cat']
		id_est = request.GET['id_est']
		id_mar = request.GET['id_mar']

		
		
		# Trae la lista de catalogos con los parametros indicados:
		l = lista_Colores(id_prov,id_temp,id_pag,id_cat,id_est,id_mar)
		
		#data = serializers.serialize('json',r,fields=('clasearticulo',))
		
		# La siguiente instruccion genera una variable data con los datos en formato json.
		# En la linea anterior ( que esta comentada ), trataba de usar
		# serielizers para convertir a json pero no funciono.

		data = json.dumps(l)
		#data = {'Mensaje':"El id proveedor recibido fue %s" % request.GET['id_prov']}
				
		# En el siguiente return utilizo content_type. Intente usar 'mimetype'
		# en lugar de 'content_type' y no funciono.

		return HttpResponse(data,content_type='application/json')
	else:
		raise Http404
		print "pagina no encontrada"



#  LOGICA PARA COMBO DE TALLAS

def lista_Tallas(id_prov,id_temp,id_pag,id_cat,id_est,id_mar,id_col):
	
	
	
	cursor=connection.cursor()
	cursor.execute("SELECT talla from preciobase where empresano=1 and proveedorid=%s and temporada=%s and pagina=%s and catalogo=%s and estilo=%s and idmarca=%s and idcolor=%s;",[id_prov,id_temp,id_pag,id_cat,id_est,id_mar,id_col])
	listatall=() # Inicializa una tupla para llenar combo de Estilos
			
	# Convierte el diccionario en tupla
	for row in cursor:
		elemento = tuple(row)
		listatall=listatall+elemento
	listatall=('SELECCIONE...',)+listatall
	
	return (listatall)	



def combo_tallas(request,*args,**kwargs):
	if request.is_ajax() and request.method == 'GET':
		id_prov = request.GET['id_prov']
		id_temp = request.GET['id_temp']
		id_pag = request.GET['id_pag']
		id_cat = request.GET['id_cat']
		id_est = request.GET['id_est']
		id_mar = request.GET['id_mar']
		id_col = request.GET['id_col']
		
		
		# Trae la lista de tallas con los parametros indicados:
		l = lista_Tallas(id_prov,id_temp,id_pag,id_cat,id_est,id_mar,id_col)
		
		#data = serializers.serialize('json',r,fields=('clasearticulo',))
		
		# La siguiente instruccion genera una variable data con los datos en formato json.
		# En la linea anterior ( que esta comentada ), trataba de usar
		# serielizers para convertir a json pero no funciono.

		data = json.dumps(l)
		#data = {'Mensaje':"El id proveedor recibido fue %s" % request.GET['id_prov']}
		# En el siguiente return utilizo content_type. Intente usar 'mimetype'
		# en lugar de 'content_type' y no funciono.

		return HttpResponse(data,content_type='application/json')
	else:
		raise Http404
		print "pagina no encontrada"





def llena_combo_sucursal(request,*args,**kwargs):

	print "Entra a llena combo sucursal"
	if request.is_ajax() and request.method == 'GET':
		print "llena combo suc, es ajax y get"		
		lsuc = lista_Sucursales()
		print "Las sucursales son:"
		for j in lsuc:
			print j
		
		data = json.dumps(lsuc)
		
		return HttpResponse(data,content_type='application/json')
	else:
		raise Http404
		print "pagina no encontrada"

# Graba en tabla temporal cada articulo seleccionando

def grabar_pedidos(request):

	# Guarda la llave de la session para su posterior manipulacion.
	session_id = request.session.session_key


	if request.is_ajax() and request.method == 'POST':

		

		id_prov = request.POST.get('id_prov')
		id_temp = request.POST.get('id_temp')
		id_pag = request.POST.get('id_pag')
		id_cat = request.POST.get('id_cat')
		id_est = request.POST.get('id_est')
		id_mar = request.POST.get('id_mar')
		id_col = request.POST.get('id_col')
		id_talla = request.POST.get('id_talla')
		id_tallaalt = request.POST.get('id_tallaalt')
		descontiunado =  request.POST.get('descontinuado')
		
		print id_prov
		print id_temp
		

		# inicializa data unicamente con la talla, esto permitira verificar 
		# con jquery que hayan ingresado un valor valido para todos los campos,
		# dado que si la talla tiene un valor distinto de blanco es porque ya 
		# el resto de los campos tiene un valor valido.
		# Si el usuario da click al boton 'elegir' y la talla es cero, el registro no 
		# se grabara, y jquery mandara el mensaje correspondiente.

		data = {'id_talla':id_talla,}

		if id_prov == '0' or  id_temp == '0':
			mensaje = "Error en proveedor o temporada !"
			
		else:
			 
			if (id_cat == 'SELECCIONE...' or id_est == 'SELECCIONE...' or id_mar == 'SELECCIONE...' or id_col == 'SELECCIONE...' or id_talla == 'SELECCIONE...'):
				data = {'id_talla':id_talla,}
				
			else:
				
				# Realiza la busqueda del codigo de producto y lo guarda 
				# tabla temporal.

				cursor = connection.cursor()
				registro_encontrado = 0

				#El select con la tabla 'articulo' 

				#cursor.execute("SELECT a.codigoarticulo, a.precio from articulo a where a.idproveedor=%s and a.catalogo=%s and a.pagina=%s and a.idestilo=%s and a.idmarca=%s and a.idcolor=%s and a.talla=%s;", (id_prov,id_cat,id_pag,id_est,id_mar,id_col,id_talla))
				#cursor.execute("SELECT b.codigoarticulo, a.precio from preciobase b inner join articulo a on (a.codigoarticulo=b.codigoarticulo and a.catalogo=b.catalogo and b.proveedorid=a.idproveedor ) where a.idproveedor=%s and b.temporada =%s and a.catalogo=%s and a.pagina=%s and a.idestilo=%s and a.idmarca=%s and a.idcolor=%s and a.talla=%s;", [id_prov,id_temp,id_cat,id_pag,id_est,id_mar,id_col,id_talla])
				cursor.execute("SELECT b.codigoarticulo, b.precio,if(a.descontinuado,'1','0') as descont From preciobase b inner join articulo a  on ( b.empresano=a.empresano and b.codigoarticulo=a.codigoarticulo and b.catalogo=a.catalogo) where b.proveedorid=%s and b.temporada =%s and b.catalogo=%s and b.pagina=%s and b.estilo=%s and b.idmarca=%s and b.idcolor=%s and b.talla=%s limit 1;", [id_prov,id_temp,id_cat,id_pag,id_est,id_mar,id_col,id_talla])
				#NoArt = dictfetchall(cursor)

				num_art = cursor.fetchone()

				if num_art == None:
					print "No existe articulo !!!!!"
				else:
					print "Existe articulo !"

				print "El Codigo, su precio y su estatus de descontinuado"; 
				print num_art[0]
				print num_art[1]
				if num_art[2] == '1':

					print "descontinuado"
					print num_art[2]
				else:
					print "vigente"
					print num_art[2	]

				try:
					# pdb.set_trace()
															
					cursor.execute("INSERT INTO pedidos_pedidos_tmp (session_key,idproveedor,idproducto,catalogo,precio,temporada,tallaalt) VALUES(%s,%s,%s,%s,%s,%s,%s)", [session_id,id_prov,num_art[0],id_cat,num_art[1],id_temp,id_tallaalt])
					
					cursor.execute("SELECT id FROM pedidos_pedidos_tmp ORDER BY id DESC LIMIT 1")
					id_rec = cursor.fetchone()
					
					# recoge el id del producto insertado y retorna nuevamente los datos recibidos
					# tanto el precio son decimales y se convierten a string para que puedan ser serializados por json.dump, de lo contrario
					# se genera un error de serializacion.

					data = {'id':id_rec[0],'id_prov':id_prov,'id_temp':id_temp,'id_cat':id_cat,'id_pag':id_pag,'id_est':id_est,'id_mar':id_mar,'id_col':id_col,'id_talla':str(id_talla),'precio': str(num_art[1]),'id_tallaalt':id_tallaalt,'descontinuado': num_art[2],}
					
				except Error as e:
					
					data = "Error en la ejecucion de la insercion: "+e.message		

				cursor.close()
				
		#pdb.set_trace()	
		return HttpResponse(json.dumps(data),content_type='application/json')

		
	else:
		raise Http404
		print "pagina no encontrada"

# ELIMINACION DE ARTICULOS DE LA TABLA TEMPORAL DE PEDIDOS.

def eli_reg_tmp(request):

	session_id = request.session.session_key

	if request.is_ajax() and request.method =='POST':

		id_item = request.POST.get('id_art')

		cursor = connection.cursor()
		
		cursor.execute("delete from pedidos_pedidos_tmp where id = %s and session_key = %s;",[id_item,session_id])

		cursor.close()
		data = "ok"

		return HttpResponse(json.dumps(data),content_type='application/json')	



	else:

		raise Http404


def procesar_pedido(request):

	global g_numero_socio_zapcat
	
	# Se asigna elnumero de socio

	socio_zapcat = request.session['socio_zapcat']

	# se asigna la sesion activa para este socio	
	session_id = request.session.session_key

	if request.is_ajax() and request.method =='POST':

		lsuc = request.POST.get('lsuc')
		
		cursor = connection.cursor()

		# trae el numero de sucursal donde se recogera el pedido
		cursor.execute("SELECT SucursalNo from sucursal where nombre = %s;",[lsuc])
		id_suc = cursor.fetchone()
		print "el id de la sucursal convertido es"
		print id_suc
		print id_suc[0]
		cursor.close()

		
		# Inicia la transaccion
		try:
			cursor = connection.cursor()
			cursor.execute("START TRANSACTION;")


			# Se busca el ultimo pedido registrado para hacer y se le suma uno para crear el nuevo
			cursor.execute("SELECT PedidoNo from pedidosheader ORDER BY PedidoNo DESC LIMIT 1;")
			#cursor.callproc('TraeUltimoPedido',)
			

			UltimoPedido = cursor.fetchone()
			
			if UltimoPedido > 0:
				# Si la tabla tiene pedidos registrados incrementa en 1 el PedidoNuevo

				PedidoNuevo = UltimoPedido[0] + 1
			else:

				# Si la tabla esta vacia asigna el numero 1.
				PedidoNuevo = 1
				

			
			
			# Se convierte la fecha de hoy a formatos manejables para insertarlos en el registro.
			hoy = datetime.now()
			fecha_hoy = hoy.strftime("%Y-%m-%d")
			hora_hoy = hoy.strftime("%H:%M:%S") 
			

				
			#cursor.execute("SET @counter = 0")
			
			# Se actualiza el encabezado del pedido.
			cursor.execute("INSERT INTO pedidosheader (EmpresaNo,PedidoNo,FechaPedido,HoraPedido,Saldototal,VtaTotal,UsuarioCrea,FechaUltimaModificacion,FechaCreacion,HoraCreacion,HoraModicacion,UsuarioModifica,idSucursal,AsociadoNo,tiposervicio,viasolicitud) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (1,PedidoNuevo,fecha_hoy,hora_hoy,0,0,99,fecha_hoy,fecha_hoy,hora_hoy,hora_hoy,99,id_suc[0],socio_zapcat,'MOSTRADOR',3))
			
			# Determina la cantidad de registros en temporal para la session en curso.
			cursor.execute("SELECT COUNT(*) FROM pedidos_pedidos_tmp where session_key = %s;",[session_id])
			Tot_reg_tmp = cursor.fetchone()

			print "total registros tmp"
			print Tot_reg_tmp[0]

			#Selecciona registro por registro de la tabla temporal (delimitada por la sesion en curso) y actualiza el detalle del pedido.
			
			cursor.execute("SELECT idproducto,catalogo, precio,temporada,tallaalt FROM pedidos_pedidos_tmp where session_key= %s;",[session_id])
			datos = namedtuplefetchall(cursor)

			count = 1
			while (count <= Tot_reg_tmp[0]):
				#print datos[count-1].idproducto
				#print datos[count-1].catalogo
				#print datos[count-1].precio
				cursor.execute("INSERT INTO pedidoslines (EmpresaNo,Pedido,ProductoNo,CantidadSolicitada,precio,subtotal,PrecioOriginal,Status,RemisionNo,NoNotaCreditoPorPedido,NoNotaCreditoPorDevolucion,NoRequisicionAProveedor,NoNotaCreditoPorDiferencia,catalogo,NoLinea,plazoentrega,OpcionCompra,FechaMaximaEntrega,FechaTentativaLLegada,FechaMaximaRecoger,Observaciones,AplicarDcto) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", [1,PedidoNuevo,datos[count-1].idproducto,1,datos[count-1].precio,datos[count-1].precio,datos[count-1].precio,'Por Confirmar',0,0,0,0,0,datos[count-1].catalogo,count,2,'1ra.','19010101','19010101','19010101',datos[count-1].tallaalt,0])
				cursor.execute("INSERT INTO pedidoslinestemporada (EmpresaNo,Pedido,ProductoNo,catalogo,NoLinea,Temporada) VALUES(%s,%s,%s,%s,%s,%s)",[1,PedidoNuevo,datos[count-1].idproducto,datos[count-1].catalogo,count,datos[count-1].temporada])
				cursor.execute("INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,ProductoNo,Status,catalogo,NoLinea,FechaMvto,HoraMvto,Usuario) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",[1,PedidoNuevo,datos[count-1].idproducto,'Por Confirmar',datos[count-1].catalogo,count,fecha_hoy,hora_hoy,99])
				cursor.execute("INSERT INTO pedidos_encontrados(EmpresaNo,Pedido,ProductoNo,Catalogo,NoLinea,FechaEncontrado,BodegaEncontro,FechaProbable,`2`,`3`,`4`,`5`,`6`,`7`,`8`,`9`,`10`,encontrado,id_cierre,causadevprov,observaciones) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[1,PedidoNuevo,datos[count-1].idproducto,datos[count-1].catalogo,count,'19010101',0,'19010101','','','','','','','','','','',0,0,''])
				count = count + 1


			
			cursor.execute("DELETE FROM pedidos_pedidos_tmp where session_key= %s;",[session_id])	
			
			# Graba cambios.
			cursor.execute("COMMIT;")
			status_operacion = 'ok'

		# Si hay error en base de datos hace rollback:	
		except DatabaseError:
			status_operacion = 'fail'
			cursor.execute("ROLLBACK;")

		cursor.close()
		data = {'PedidoNuevo':PedidoNuevo,'status_operacion':status_operacion,}
		return HttpResponse(json.dumps(data),content_type='application/json')	




	else:

		raise Http404


def verifica_socio(request):


	session_id = request.session.session_key

	if request.is_ajax() and request.method =='POST':

		num_socio = request.POST.get('NoSocio')

		cursor = connection.cursor()
		
		cursor.execute("SELECT nombre,appaterno,apmaterno from Asociado where asociadono=%s;"[num_socio])

		asociado_data = cursor.fetchone()

		cursor.close()
		data = "ok"

		return HttpResponse(json.dumps(data),content_type='application/json')	



	else:

		

		raise Http404


''' La siguiente variable de numero de socio es global y se actualiza en "busca_socio"  para
	despues ser utilizada en la rutina "registra_socio" '''

global_numero_socio_zapcat = 0


@permission_required('auth.add_user',login_url=None,raise_exception=True)
def busca_socio(request):
    # if this is a POST request we need to process the form data
	global global_numero_socio_zapcat
	if request.method == 'POST':
        # create a form instance and populate it with data from the request:
		form = RegsocwebForm(request.POST)
        # check whether it's valid:
		if form.is_valid():

			socio_a_dar_de_alta = request.POST.get('numero')
			request.session['socio_a_dar_de_alta'] = socio_a_dar_de_alta

			cursor = connection.cursor()
		
			cursor.execute("SELECT asociadono,nombre,appaterno,apmaterno,num_web from asociado where asociadono=%s;",[socio_a_dar_de_alta])

			socio_datos = dictfetchall(cursor)
			for r in socio_datos:
				num_web_data = r['num_web']

			if not socio_datos:
					mensaje = 'El número de socio proporcionado no fué encontrado, intente nuevamente !'
					return render(request,'pedidos/error_en_socio.html', {'mensaje':mensaje})
			else:

				if num_web_data != 0:
					mensaje = "Este socio ya está registrado en el sitio Web con el número "+str(num_web_data)+"."
					return render(request,'pedidos/error_en_socio.html',{'mensaje':mensaje})
				# Ojo con la siguite linea, Para que ?	
				global_numero_socio_zapcat = socio_a_dar_de_alta 

				mensaje ='Tenemos a '
				context = {'socio_datos':socio_datos,'mensaje':mensaje}
				return render(request,'pedidos/socio_encontrado.html',context)



			cursor.close()

	else:
		form = RegsocwebForm()

	return render(request,'pedidos/busca_socio.html',{'form':form})


def registro_socio(request):
	
	socio_a_dar_de_alta = request.session['socio_a_dar_de_alta']

	if request.method == 'POST':
		form = Forma_RegistroForm(request.POST)
		
		if form.is_valid():
			new_user = form.save()
			nombre_usuario_Web = new_user.username

			''' Graba en la tabla de asociodo el id que le correspondio en la Web'''
			cursor = connection.cursor()
			cursor.execute("UPDATE asociado SET num_web = %s where asociadono = %s;",[new_user.id,socio_a_dar_de_alta])
			cursor.close()
			
			para = [request.POST.get('email')]

			email_host_user = getattr(settings, "EMAIL_HOST_USER", None)

			mensaje = """Estimado socio:

			 Ha sido habilitado para usar el sistema de Pedidos por Internet, su usuario es """ + nombre_usuario_Web.encode('utf-8') + """ . Por favor ingrese al sistema
			 con este usuario y la contraseña que eligió y cámbiela para mayor seguridad.

			 De ahora en adelante puede Ud. consultar sus pedidos y realizar nuevos pedidos desde su computadora o celular.

			 
			 Podrá ingresar al sistema en http://www.esshoesmultimarcas.com/pedidos/index/

			 Atentamente.
			 ES Shoes Multimarcas. """
			
			envia_mail(para,email_host_user,'Su registro en ES Shoes mulitimarcas WEB',mensaje)			  

			request.session['socio_a_dar_de_alta']=0

			return render(request,'pedidos/registro_exitoso.html',{'nombre_usuario_Web':nombre_usuario_Web,})
	else:
		form = Forma_RegistroForm()
	return render(request,'pedidos/registration_form.html',{'form':form,})

@login_required
def cambiar_password(request):
    form = PasswordChangeForm(user=request.user)
    nombre_usuario_Web = request.user

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return render(request,'pedidos/cambio_password_exitoso.html',{'nombre_usuario_Web':nombre_usuario_Web,})

    return render(request, 'pedidos/cambio_password_form.html', {
        'form': form,
    })

def envia_mail(v_para,v_de,v_asunto,v_mensaje):
				
	send_mail(v_asunto,v_mensaje,'atencion.clientes@multimarcaslaredo.com',v_para,fail_silently=False,)

	return


@permission_required('auth.add_user',login_url=None,raise_exception=True)
def empleados(request):

	
	return render(request,'pedidos/empleados.html')


def consulta_menu(request):

	return render(request,'pedidos/consulta_menu.html')

def con_calzado_que_llego_global(request):
	return render(request,'pedidos/404.html')

def con_calzado_que_llego_detallado(request):
	return render(request,'pedidos/404.html')

def con_colocaciones(request):
	return render(request,'pedidos/404.html')
def con_confirmaciones(request):
	return HttpResponse('Opcion en desarrollo...')


def con_pedidos_por_socio_status(request):

	'''try:
	
		g_numero_socio_zapcat = request.session['socio_zapcat']	
	except KeyError :

		return	HttpResponse("Ocurrió un error de conexión con el servidor, Por favor salgase completamente y vuelva a entrar a la página !")

	if request.user.is_authenticated():'''		
		
	if request.method == 'POST':
		form = BuscapedidosporsocioForm(request.POST)
		'''
		Si la forma es valida se normalizan los campos numpedido, status y fecha,
		de otra manera se envia la forma con su contenido erroreo para que el validador
		de errores muestre los mansajes correspondientes '''

		if form.is_valid():
		
			# limpia datos 
			socio = form.cleaned_data['socio']
			numpedido = form.cleaned_data['numpedido']
			status = form.cleaned_data['status']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']

			
			# Convierte el string '1901-01-01' a una fecha valida en python
			# para ser comparada con la fecha ingresada 

			fecha_1901 =datetime.strptime('1901-01-01', '%Y-%m-%d').date()
			hoy = date.today()


			# Establece conexion con la base de datos
			cursor=connection.cursor()

		
			# Comienza a hacer selects en base a criterios 


			if numpedido != 0:
				cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,psf.fechamvto,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) inner join pedidos_status_fechas psf on (psf.empresano=l.empresano and psf.pedido=l.pedido and psf.productono=l.productono and psf.catalogo=l.catalogo and psf.nolinea=l.nolinea and psf.status=l.status) where h.pedidono=%s;",[numpedido])
				socio = 0 # Si acaso el usuario asigno un numero de socio,  este se hace cero para mas delante 
						  # asignar el socio que  nos arroja la consulta por pedido. 
			else :

				if  status == 'Todos':
					cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,psf.fechamvto,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) inner join pedidos_status_fechas psf on (psf.empresano=l.empresano and psf.pedido=l.pedido and psf.productono=l.productono and psf.catalogo=l.catalogo and psf.nolinea=l.nolinea and psf.status=l.status) where h.asociadono=%s and psf.fechamvto>=%s and psf.fechamvto<=%s ORDER BY h.pedidono DESC;", (socio,fechainicial,fechafinal))
					print "Entro en status=Todos y fecha != 19010101"
				else:
					if status !='Todos':
						cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,psf.fechamvto,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo)  inner join pedidos_status_fechas psf on (psf.empresano=l.empresano and psf.pedido=l.pedido and psf.productono=l.productono and psf.catalogo=l.catalogo and psf.nolinea=l.nolinea and psf.status=l.status) where h.asociadono=%s and l.status=%s and psf.fechamvto>=%s and psf.fechamvto<=%s ORDER BY h.pedidono DESC;", (socio,status,fechainicial,fechafinal))
						print "Entro en status != Todos y fecha=1901/01/01"
					else:
 						if status != 'Todos':
							cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,psf.fechamvto,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) inner join pedidos_status_fechas psf on (psf.empresano=l.empresano and psf.pedido=l.pedido and psf.productono=l.productono and psf.catalogo=l.catalogo and psf.nolinea=l.nolinea and psf.status=l.status) where h.asociadono=%s and l.status=%s and psf.fechamvto>=%s and psf.fechamvto<=%s ORDER BY h.pedidono DESC;", (socio,status,fechainicial,fechafinal))			
							print "Entro en status != Todos y fecha != 1901/01/01"
						else:
							mensaje ='No se encontraron registros !'
			
			# El contenido del cursor se convierte a diccionario para poder
			# ser enviado como parte del contexto y sea manipulable.				
			pedidos = dictfetchall(cursor)
			for pedido in pedidos:
				print "ASI ESTAN LOS ELEMENTOS DEL DICCIONARIO PEDIDOS:"
				print pedido

			elementos = len(pedidos)

			if socio == 0:
				socio =pedido['asociadono']


				# Comienza por seleccionar el nombre del socio
			cursor.execute("SELECT a.appaterno, a.apmaterno,a.nombre from asociado a where a.asociadono=%s;",[socio])
			
			nombre_socio = cursor.fetchone()

			

			if not pedidos or not socio:# or not nombre_socio[0]:
				mensaje = 'No se encontraron registros !'
				
				return render(request,'pedidos/lista_pedidos_socio_status.html',{'form':form,'mensaje':mensaje,})
			else:
				mensaje ='Registros encontrados:'
				context = {'pedidos':pedidos,'mensaje':mensaje,'elementos':elementos,'socio':socio,'socio_appaterno':nombre_socio[0],'socio_apmaterno':nombre_socio[1],'socio_nombre':nombre_socio[2],}
			

			

			# Cierra la conexion a la base de datos
			cursor.close()
			
			return render(request,'pedidos/lista_pedidos_socio_status.html',context)
		
	else:
		form = BuscapedidosporsocioForm()
		#cursor.close()
		
	return render(request,'pedidos/con_pedidos_por_socio_status.html',{'form':form,})
	'''else:
		redirect('/pedidos/acceso/')''' 


def existe_socio(request):


	if request.is_ajax() and request.method =='POST':
		id_socio = request.POST.get('id_socio')
		cursor = connection.cursor()

		cursor.execute("SELECT nombre,appaterno,apmaterno from asociado where asociadono=%s;",[id_socio])
		asociado_data = cursor.fetchone()
		cursor.close()
		
		if asociado_data is None:
			data = "NO"
		else:
			data = "SI"

		return HttpResponse(json.dumps(data),content_type='application/json')	



	else:

		

		raise Http404


def picklist_socio(request):
	
	string_a_buscar = request.GET.get('string_a_buscar',None)
	
	if request.is_ajax() and request.method == 'GET':
		
		valor ="'%"+string_a_buscar.strip()+"%'"

		id_a_buscar='0'	
		
		if string_a_buscar.isdigit(): # verifica si la cadena a buscar es un digito, de ser asi, usara esa cadana para buscar por id.

			id_a_buscar = string_a_buscar
		

		cursor=connection.cursor()
		
		
		cursor.execute("SELECT o.AsociadoNo,o.ApPaterno,o.ApMaterno,o.Nombre from asociado o WHERE o.AsociadoNo="+id_a_buscar+" or trim(o.Nombre) like "+valor+" or o.ApPaterno like "+valor+" or o.ApMaterno like "+valor+";")
		l = dictfetchall(cursor)
		
		
		data= json.dumps(l)

		
		cursor.close()
				
		return HttpResponse(data,content_type='application/json')


def calzadollego_gral(request):

	mensaje =''
	if request.method == 'POST':

		form = Calzadollego_gralForm(request.POST)

		if form.is_valid():

			
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']

			cursor=connection.cursor()

			
			cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,psf.fechatentativallegada AS FTL,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia,k.razonsocial as provnombre FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre)  left join  pedidoslines psf on (p.empresano=psf.empresaNo and p.pedido=psf.pedido and p.productono=psf.productono and p.catalogo=psf.catalogo and p.nolinea=psf.nolinea) inner join proveedor k on (k.proveedorno=c.prov_id and k.empresano=1) left join almacen j on (j.proveedorno=c.prov_id and j.empresano=1 ) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by c.id,psf.fechatentativallegada;",(fechainicial,fechafinal))

			'''cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia,k.razonsocial as provnombre FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre) inner join proveedor k on (k.proveedorno=c.prov_id and k.empresano=1) inner join almacen j on (j.proveedorno=c.prov_id and j.empresano=1) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by psf.fechatentativallegada;",(fechainicial,fechafinal))'''

			pedidos = dictfetchall(cursor)
			
			elementos = len(pedidos)

			


			"""cursor.execute("SELECT p.razonsocial,a.razonsocial from proveedor p inner join almacen a on (p.empresano=a.empresano and p.proveedorno=a.proveedorno) where p.proveedorno=%s;",(ped['prov_id'],))
			
			prov_alm = cursor.fetchone()"""

			if not pedidos:
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_calzadollego_gral.html',{'mensaje':mensaje,})

			else:
				print "lo que hay en pedidos"
				for ped in pedidos:
					print ped
				prov_a_buscar = ped["prov_id"]

				print "proveedor buscado"
				print prov_a_buscar
				mensaje ="Registros encontrados == > "

				context = {'form':form,'mensaje':mensaje,'pedidos':pedidos,'elementos':elementos,}	
			
				return render(request,'pedidos/lista_calzadollego_gral.html',context)

		
	else:

		form = Calzadollego_gralForm()
	return render(request,'pedidos/calzadollego_gral.html',{'form':form,})


	
def calzadoquellego_detalle(request):

	mensaje =''
	if request.method == 'GET':

		

		form = Calzadollego_detalleForm(request.GET)

		if form.is_valid():

			
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']

			cursor=connection.cursor()

			
			"""cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,psf.fechatentativallegada,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre)  left join  pedidoslines psf on (p.empresano=psf.empresaNo and p.pedido=psf.pedido and p.productono=psf.productono and p.catalogo=psf.catalogo and p.nolinea=psf.nolinea) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by c.id,psf.fechatentativallegada;",(fechainicial,fechafinal))"""


			cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.Nolinea,e.BodegaEncontro,e.encontrado,p.fechapedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,e.observaciones,p.idSucursal,e.id_cierre,l.observaciones,pro.razonsocial as provnom,aso.nombre,aso.appaterno,aso.apmaterno,suc.nombre as sucnom,alm.razonsocial as almnom FROM pedidoslines l INNER JOIN   pedidosheader p ON (l.EmpresaNo= p.EmpresaNo and l.Pedido=p.PedidoNo) INNER JOIN articulo a ON (l.EmpresaNo=a.EmpresaNo and l.ProductoNo=a.codigoarticulo and l.Catalogo=a.catalogo)  INNER JOIN pedidos_encontrados e on (l.EmpresaNo=e.empresaNo and l.pedido=e.pedido and e.productono=l.productono and l.catalogo=e.catalogo and e.nolinea=l.nolinea) inner join proveedor pro on (pro.empresano=1 and pro.proveedorno=a.idproveedor) inner join asociado aso on (aso.empresano=1 and aso.asociadono=p.asociadono) inner join sucursal suc on (suc.empresano=1 and suc.sucursalno=p.idsucursal) inner join almacen alm on (alm.empresano=1 and alm.proveedorno=a.idproveedor and e.BodegaEncontro=alm.Almacen) WHERE  l.fechatentativallegada>=%s and l.fechatentativallegada<=%s and e.id_cierre<>0 order by e.id_cierre;",(fechainicial,fechafinal))

			 
			lista_pedidos = dictfetchall(cursor)

			

			elementos = len(lista_pedidos)

			


			"""cursor.execute("SELECT p.razonsocial,a.razonsocial from proveedor p inner join almacen a on (p.empresano=a.empresano and p.proveedorno=a.proveedorno) where p.proveedorno=%s;",(ped['prov_id'],))
			
			prov_alm = cursor.fetchone()"""

			if not lista_pedidos:
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_calzadollego_detalle.html',{'mensaje':mensaje,})

			else:
				print "lo que hay en pedidos"
				for ped in lista_pedidos:
					print ped

				
				mensaje ="Registros encontrados == > "

				context = {'form':form,'mensaje':mensaje,'elementos':elementos,'lista_pedidos':lista_pedidos,}	
			
				return render(request,'pedidos/lista_calzadollego_detalle.html',context)

		
	else:

		form = Calzadollego_detalleForm()
	return render(request,'pedidos/calzadollego_detalle.html',{'form':form,})



	return



def consultacolocaciones(request):

	mensaje =''
	if request.method == 'POST':

		form = Consulta_colocacionesForm(request.POST)

		if form.is_valid():

			proveedor = form.cleaned_data['proveedor']
			tipoconsulta = form.cleaned_data['tipoconsulta']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']

			cursor=connection.cursor()

			
			"""cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,psf.fechatentativallegada,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre)  left join  pedidoslines psf on (p.empresano=psf.empresaNo and p.pedido=psf.pedido and p.productono=psf.productono and p.catalogo=psf.catalogo and p.nolinea=psf.nolinea) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by c.id,psf.fechatentativallegada;",(fechainicial,fechafinal))"""

			if tipoconsulta == '1':
				print "Entro a consulta opcion 1"
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal, l.Observaciones FROM pedidoslines l LEFT JOIN  pedidos_encontrados e on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo)  INNER JOIN pedidos_status_fechas f on  ( e.EmpresaNo=f.EmpresaNo and e.Pedido=f.Pedido and e.ProductoNo=f.ProductoNo and e.Catalogo=f.catalogo and e.NoLinea=f.NoLinea) WHERE a.idProveedor=%s and  p.FechaPedido>=%s and p.FechaPedido<=%s  and l.Status='Por Confirmar'  and f.Status='Por Confirmar' and  (trim(e.encontrado)='' or  trim(e.encontrado)='P' or e.encontrado IS NULL);",(proveedor,fechainicial,fechafinal))
			else:
				print "Entro a consulta opcion 2"
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal, l.Observaciones FROM pedidoslines l LEFT JOIN  pedidos_encontrados e on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo)  INNER JOIN pedidos_status_fechas f on  ( e.EmpresaNo=f.EmpresaNo and e.Pedido=f.Pedido and e.ProductoNo=f.ProductoNo and e.Catalogo=f.catalogo and e.NoLinea=f.NoLinea) WHERE a.idProveedor=%s and  p.FechaPedido>=%s and p.FechaPedido<=%s  and l.Status='Por Confirmar'  and f.Status='Por Confirmar';",(proveedor,fechainicial,fechafinal))	
			

			pedidos = dictfetchall(cursor)

			elementos = len(pedidos)

			


			"""cursor.execute("SELECT p.razonsocial,a.razonsocial from proveedor p inner join almacen a on (p.empresano=a.empresano and p.proveedorno=a.proveedorno) where p.proveedorno=%s;",(ped['prov_id'],))
			
			prov_alm = cursor.fetchone()"""

			if not pedidos:
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_colocaciones.html',{'mensaje':mensaje,'tipoconsulta':tipoconsulta,})

			else:

				
				for ped in pedidos:
					print ped
				
				
				mensaje ="Registros encontrados == > "

				context = {'form':form,'mensaje':mensaje,'pedidos':pedidos,'elementos':elementos,'tipoconsulta':tipoconsulta,}	
			
				return render(request,'pedidos/lista_colocaciones.html',context)

		
	else:

		form = Consulta_colocacionesForm()
	return render(request,'pedidos/consultacolocaciones.html',{'form':form,})


def consultaventas(request):
	''' Inicializa Variables '''

	VentaCalzado = 0.0
	TotalVtaBruta = 0.0
	TotalCargos = 0.0
	TotalCreditos = 0.0
	TotalDescuentos = 0.0
	TotalRegistros = 0.0
	TotalVtaCatalogos = 0.0
	TotalVtaNeta = 0.0



	mensaje =''
	if request.method == 'POST':

		form = Consulta_ventasForm(request.POST)

		if form.is_valid():

			sucursal = form.cleaned_data['sucursal']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']

			cursor=connection.cursor()

			if sucursal == '0':
				sucursalinicial =1
				sucursalfinal = 9999
				sucursal_nombre ='GENERAL'
			else:
				sucursalinicial =  sucursal
				sucursalfinal =  sucursal
				cursor.execute("SELECT nombre from sucursal WHERE EmpresaNo=1 and SucursalNo=%s;",(sucursal))
				sucursalencontrada = cursor.fetchone()
				sucursal_nombre = sucursalencontrada[0]


			

			
			"""cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,psf.fechatentativallegada,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre)  left join  pedidoslines psf on (p.empresano=psf.empresaNo and p.pedido=psf.pedido and p.productono=psf.productono and p.catalogo=psf.catalogo and p.nolinea=psf.nolinea) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by c.id,psf.fechatentativallegada;",(fechainicial,fechafinal))"""

			
			cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones > d.Saldo,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado,0) as VtaComisionSaldo FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			
			

			registros_venta = dictfetchall(cursor)

			elementos = len(registros_venta)

			


			"""cursor.execute("SELECT p.razonsocial,a.razonsocial from proveedor p inner join almacen a on (p.empresano=a.empresano and p.proveedorno=a.proveedorno) where p.proveedorno=%s;",(ped['prov_id'],))
			
			prov_alm = cursor.fetchone()"""

			if not registros_venta:
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_ventas.html',{'mensaje':mensaje,})

			else:

				
				for docto in registros_venta:
										
					if (docto['Cancelado'] == '\x00'):  # pregunta si cancelado es '0' en hex o bien falso
						
						TotalVtaBruta = TotalVtaBruta + float(docto['venta'])
						esvta =docto['Concepto'].strip()
						if esvta == 'Venta':
							
							TotalCreditos = TotalCreditos + float(docto['Saldo'])		
							TotalCargos = TotalCargos + float(docto['comisiones'])	
							TotalDescuentos =  TotalDescuentos + float(docto['descuentoaplicado'])	
							VentaCalzado = VentaCalzado + float(docto['venta'])

							if (TotalVtaBruta + TotalCargos > TotalCreditos):

								TotalVtaNeta =TotalVtaBruta-TotalCreditos+TotalCargos-TotalDescuentos
							else:
								TotalVtaNeta = 0;

						if docto['VtaDeCatalogo'] == '\x01' :
							TotalVtaCatalogos = TotalVtaCatalogos + float(docto['Monto'])
						TotalRegistros = TotalRegistros + 1
						TotalVtaProductos = TotalVtaBruta - TotalVtaCatalogos -TotalDescuentos
				
				mensaje ="Registros encontrados == > "



				context = {'form':form,'mensaje':mensaje,'registros_venta':registros_venta,'TotalRegistros':TotalRegistros,'sucursal_nombre':sucursal_nombre,'TotalCreditos':TotalCreditos,'TotalCargos':TotalCargos,'TotalDescuentos':TotalDescuentos,'VentaCalzado':VentaCalzado,'TotalVtaCatalogos':TotalVtaCatalogos,'TotalVtaBruta':TotalVtaBruta,'TotalVtaNeta':TotalVtaNeta,'TotalVtaProductos':TotalVtaProductos}	
			
				return render(request,'pedidos/lista_ventas.html',context)

		
	else:

		form = Consulta_ventasForm()
	return render(request,'pedidos/consultaventas.html',{'form':form,})



def consultacomisiones(request):
	''' Inicializa Variables '''

	VentaCalzado = 0.0
	TotalVtaBruta = 0.0
	TotalCargos = 0.0
	TotalCreditos = 0.0
	TotalDescuentos = 0.0
	TotalRegistros = 0.0
	TotalVtaCatalogos = 0.0
	TotalVtaNeta = 0.0



	mensaje =''
	if request.method == 'POST':

		form = Consulta_comisionesForm(request.POST)

		if form.is_valid():

			sucursal = form.cleaned_data['sucursal']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']

			cursor=connection.cursor()

			if sucursal == '0':
				sucursalinicial =1
				sucursalfinal = 9999
				sucursal_nombre ='GENERAL'
			else:
				sucursalinicial =  sucursal
				sucursalfinal =  sucursal
				cursor.execute("SELECT nombre from sucursal WHERE EmpresaNo=1 and SucursalNo=%s;",(sucursal))
				sucursalencontrada = cursor.fetchone()
				sucursal_nombre = sucursalencontrada[0]

			
			"""cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,psf.fechatentativallegada,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre)  left join  pedidoslines psf on (p.empresano=psf.empresaNo and p.pedido=psf.pedido and p.productono=psf.productono and p.catalogo=psf.catalogo and p.nolinea=psf.nolinea) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by c.id,psf.fechatentativallegada;",(fechainicial,fechafinal))"""

			
			cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones > d.Saldo,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado,0) as VtaComisionSaldo FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Cargo' and not(d.Cancelado) and d.FechaUltimaModificacion>=%s and d.FechaUltimaModificacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			
			

			registros_comisiones = dictfetchall(cursor)

			
			elementos = len(registros_comisiones)

			


			"""cursor.execute("SELECT p.razonsocial,a.razonsocial from proveedor p inner join almacen a on (p.empresano=a.empresano and p.proveedorno=a.proveedorno) where p.proveedorno=%s;",(ped['prov_id'],))
			
			prov_alm = cursor.fetchone()"""

			if not registros_comisiones:
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_comisiones.html',{'mensaje':mensaje,})

			else:

				
				for docto in registros_comisiones:
										
					if (docto['Cancelado'] == '\x00'):  # pregunta si cancelado es '0' en hex o bien falso
						
						TotalVtaBruta = TotalVtaBruta + float(docto['Monto'])
						TotalRegistros = TotalRegistros + 1
						
						mensaje ="Registros encontrados == > "


				
				context = {'form':form,'mensaje':mensaje,'registros_comisiones':registros_comisiones,'TotalRegistros':int(TotalRegistros),'sucursal_nombre':sucursal_nombre,'TotalVtaBruta':TotalVtaBruta,}	
			
				return render(request,'pedidos/lista_comisiones.html',context)

		
	else:

		form = Consulta_comisionesForm()

	return render(request,'pedidos/consultacomisiones.html',{'form':form,})