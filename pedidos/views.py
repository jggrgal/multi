
#-*- encoding: utf-8 -*-

from django.shortcuts import render,redirect,render_to_response
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.template import RequestContext,loader
from django.core.urlresolvers import reverse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder # Permite decodificar fecha y hora con formato mysql obtenido con dictfetchall
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.contrib.auth.decorators import login_required,permission_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail
from smtplib import SMTPException,SMTPSenderRefused,SMTPAuthenticationError,SMTPRecipientsRefused,SMTPServerDisconnected
from . forms import (AccesoForm,\
					BuscapedidosForm,\
					PedidosForm,\
					RegsocwebForm,\
					Forma_RegistroForm,\
					BuscapedidosporsocioForm,\
					Calzadollego_gralForm,\
					Calzadollego_detalleForm,\
					Consulta_colocacionesForm,\
					Consulta_ventasForm,\
					Consulta_comisionesForm,\
					BuscapedidosposfechaForm,\
					PedidosgeneralForm,\
					Entrada_sistemaForm,\
					CancelaproductoForm,\
					Ingresa_socioForm,\
					ColocacionesForm,\
					ElegirAlmacenaCerrarForm,\
					SeleccionCierreRpteCotejoForm,\
					SeleccionCierreRecepcionForm,\
					DocumentosForm,\
					DetalleDocumentoForm,\
					CreaDocumentoForm,\
					CierresForm,\
					Crea_devolucionForm,\
					Genera_BaseBonoForm,\
					RpteVtaNetaSocioxMarcaForm,\
					CanceladocumentoForm,\
					RpteCreditosForm,
					Recepcion_dev_provForm,\
					Dev_proveedorForm,\
					FiltroDevProvForm,\
					Edicion_devprovForm,\
					#DatosProveedorForm,
					Lista_dev_recepcionadasForm,\
					ventasporcajeroForm,\
					RpteStatusDePedidosForm,
					DatosProveedorForm, # MODIFICA DATOS DEL PROVEEDOR
					CreaProveedorForm,
					DatosCatalogoForm, # MODIFICA DATOS DEL CATALOGO
					CreaCatalogoForm,
					Lista_dev_recepcionadasForm,
					BuscaEstiloForm,
					PiezasNoSolicitadasForm,
					DatosAsociadoForm,
					EditaDescuentoAsociadoForm,
					CreaDescuentoAsociadoForm,
					RpteArtNoSolicitadosForm,
					FiltroSocioCatalogoForm,
					FiltroProveedorForm,
					CreaAlmacenForm,
					remisionesespecialesForm,
					DatosUsuarioForm,
					DerechosFaltantesUsuarioForm,
					EliminaUsuarioDerechoForm,
					DatosUsuarioWebForm,
					RpteStatusxMarcaForm,
					UsuarioLogForm,
					UploadFileForm)



from pedidos.models import Asociado,Articulo,Proveedor,Configuracion
from django.db import connection,DatabaseError,Error,transaction,IntegrityError,OperationalError,InternalError,ProgrammingError,NotSupportedError
from datetime import datetime,date,time,timedelta
import calendar
from django.conf import settings
import pdb
import unicodedata
import json
from collections import namedtuple
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,letter
from reportlab.lib.units import inch,cm 
import csv
from decimal import Decimal,getcontext
import locale  # Se usa para representar cantidades monetarias
  # move the origin up and to the left
from django.utils.crypto import get_random_string  # genera un string de 3 caract. para password da paso
from django.contrib import messages 

getcontext().prec = 6# esta linea establece la precision de decimales para numeros decimales,
					  # leer la funcion getcontext de decimales.

#from reportlab.lib.pagesizes import inch

# PARA REPORTLABS (usar un font FreeSans, pero no cambiaba mucho, asi que no se uso)

#from reportlab.pdfbase import pdfmetrics
#from reportlab.pdfbase.ttfonts import TTFont

#pdfmetrics.registerFont(TTFont('FreeSans', '/usr/share/fonts/truetype/freefont/FreeSans.ttf'))

class NoHayRegistrosError(Exception):

	''' Clase para manejar errores cuando no hay registros en consultas'''
	pass


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
''' VISTA_1 INICIA ACCESO A SISTEMA '''

def index(request):

	request.session.set_test_cookie()

	return render(request,'pedidos/index.html')

'''VISTA_2 SALIDA DEL SISTEMA '''
def logout_view(request):
   	
   	logout(request)

   	return redirect('pedidos:index')# Redirect to a success page.


''' La siguiente variable global se utiliza para guardar el numero de socio en zapcat se actualiza en la rutina "acceso", 
este valor sera utilizado por  la rutina busca_pedidos  para las consultas sql.'''

#g_numero_socio_zapcat = 0



'''VISTA_3 TRAE FECHA_HORA ACTUAL EN FORMATO ADECUADO'''
def trae_fecha_hora_actual(fecha_hoy,hora_hoy):
	hoy = datetime.now()
	fecha_hoy = hoy.strftime("%Y-%m-%d")
	hora_hoy = hoy.strftime("%H:%M:%S") 
	return (fecha_hoy,hora_hoy)

def days_between(d1, d2):

    return abs(d2 - d1).days



"""LA SIGUIENTE RUTINA ACTUALIZA EL PRECIOORIGINAL EN PEDIDOSLINES YA QUE
SE PIERDE, MIENTRAS SE HACE DETERMINA EL ORIGEN DEL ERROR SE IMPLEMENTA ESTA ( REVISAR BIEN
RUTINA DE RECEPCION DE MERCANCIA, AL PARECER AHI HAY PROBLEMA.

ESTA RUTINA ES LLAMADA CADA VEZ QUE ALGUIEN ENTRA AL SISTEMA """

def actualiza_preciooriginal():

	#pdb.set_trace() 	
		
	hoy = date.today()
	
	fechainicial = hoy - timedelta(days=150)

	cursor = connection.cursor()
	
	try:
		cursor.execute("UPDATE pedidoslines l INNER JOIN pedidosheader h on (l.empresano=h.empresano and l.pedido=h.pedidono) INNER JOIN articulo a ON (a.empresano=l.empresano and l.productono=a.codigoarticulo and l.catalogo =a.catalogo) SET l.preciooriginal=a.precio WHERE h.fechapedido >=%s and l.preciooriginal=0;",(fechainicial,))
		
	except DatabaseError as e:
		print e
	

	return






'''VISTA_4 CONTINUA ACCESO AL SISTEMA'''
def acceso(request):

	#pdb.set_trace() 
	global g_numero_socio_zapcat
	
	
	mensaje=""
	if request.session.test_cookie_worked():
		request.session.delete_test_cookie()
		
	else:
		
		return HttpResponse("Por favor active cookies en su navegador e intente nuevamente.")


	if request.session.session_key is None:

		error_msg ="Su sesión terminó !, por favor ingrese nuevamente al sistema con sus credenciales !"
		return render(request,'pedidos/error.html',{'error_msg':error_msg,})
	# Se trae la session
	session_id = request.session.session_key

	print "SESION:"
	print session_id

	print "USUARIO:"
	print request.user
	usuario_en_session = request.user
	request.session['sucursal_activa'] = 0
	request.session['sucursal_nombre'] = ''
	request.session['is_staff'] = request.user.is_staff

	
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
					cursor.execute("SELECT asociadono,EsSocio FROM asociado where num_web=%s;",[request.user.id])
					socio_datos = dictfetchall(cursor)

					cursor.execute("SELECT * FROM configuracion WHERE empresano = 1;")
					configuracion = cursor.fetchone()

					# Asignacion de otras variables de entorno 

					request.session['cnf_ejercicio_vigente'] = configuracion[1]
					request.session['cnf_periodo_vigente'] = configuracion[2]
					request.session['cnf_razon_social'] = configuracion[3]
					request.session['cnf_direccion'] = configuracion[4]
					request.session['cnf_colonia'] = configuracion[5]
					request.session['cnf_ciudad'] = configuracion[6]
					request.session['cnf_estado'] = configuracion[7]	
					request.session['cnf_codigo_postal'] = configuracion[9]
					request.session['cnf_telefono'] = configuracion[10]
					request.session['cnf_rfc'] = configuracion[11]
					request.session['cnf_iva'] = configuracion[13]
					request.session['cnf_porcentaje_anticipo'] = configuracion[14]
					request.session['cnf_max_dias_extemp'] = configuracion[19]
					request.session['cnf_cuota_dias_extemp'] = configuracion[20]	
					request.session['cnf_dias_vigencia_credito'] = configuracion[21]
					request.session['cnf_comision_por_calzado_no_recogido'] = configuracion[22]
					request.session['cnf_dias_plazo_vmvto_aqui_socio_credito'] = configuracion[23]
					request.session['cnf_dias_plazo_vmto_aqui_socio_sincredito'] = configuracion[24]	
					request.session['cnf_mostrar_socio_en_ticket'] = configuracion[25]
					
					
					if not socio_datos:
						return HttpResponse("Ud. no tiene asignado un numero de socio, por favor consulte al administrador el sistema")					
					else:
						for r in socio_datos:
							g_numero_socio_zapcat = r['asociadono']

							request.session['socio_zapcat'] = r['asociadono']

							request.session['EsSocio'] = r['EsSocio']

					request.session['is_staff']	= user.is_staff			
					# Con la siguiente linea cierra la session al cerrar el navegador.		
					request.session.set_expiry(0)
					
					if user.is_staff:
						actualiza_preciooriginal()
						form = Entrada_sistemaForm()
						return render(request,'pedidos/entrada_sistema.html',{'form':form,'usuario':request.user,'is_staff':True},)
					else:
						form = BuscapedidosForm()
						return render(request,'pedidos/busca_pedidos.html',{'form':form,'usuario':request.user,'is_staff':request.session['is_staff']},)
	
				else:
					# Return a 'disabled account' error message
					mensaje = 'Usuario y contraseña correctos pero su cuenta está desactivada, comuniquese por favor con el equipo de ES Shoes Multimarcas. !'
					
			else:
				# Return an 'invalid login' error message.
				mensaje = 'Usuario y/o contraseña incorrectos, intente de nuevo !'
		else:			 
			return render(request,'pedidos/acceso.html',{'form':form,'is_staff':False,})
	
	request.session.set_test_cookie()
	form=AccesoForm()
	return render(request,'pedidos/acceso.html',{'form':form,'mensaje':mensaje,'is_staff':False,})

'''VISTA_5 DICCIONARIO DE DATOS '''


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


def traePrimerUltimoDiasMesAnterior():
	
	#pdb.set_trace() 

	# La rutina calcula la fecha del primero y el ultimo dia del mes anterior
	# al actual y las devuelve como strings en el formato
	# '20190501' y '20190531', (por ejemplo para el mes de Mayo del 2019)



	

	hoy = datetime.now()  # se obtiene la fecha de hoy como tupla
	anio = hoy.year                # se obtiene el anio actuales
	mes = hoy.month                # se obtiene el mes actuales
	dia = hoy.day                  # se obtiene el dia actueles

	anio_anterior = anio-1 if mes==1 else anio # se obtiene el anio anterior
	mes_anterior = 12 if mes ==1 else ( mes -1) # se obtiene el mes anterior

						   


	num_days = calendar.monthrange(anio_anterior, mes_anterior)  # trae una tupla con el rango
	                                                             # de dias del mes
	                                                             # del mes, ejemplo (1,31), si es Enero.

	primer_dia = date(anio_anterior, mes_anterior, 1)   # trae el valor del primer dia
	ultimo_dia = date(anio_anterior, mes_anterior, num_days[1]) # trae el valor del ultimo dia (31, para el ejemplo)
	fecha_inicial = primer_dia.strftime('%Y%m%d') # se convierte a formato 'YYYYmmdd'
	fecha_final = ultimo_dia.strftime('%Y%m%d')   # Se convierte a formato 'YYYYmmdd'
	return(fecha_inicial,fecha_final)







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
	cursor.execute('SELECT nocontrol as numcontrol,asociadono,nombre,appaterno,apmaterno,telefono1,celular,direccionelectronica from asociado;')
	asociados = dictfetchall(cursor)
	cursor.close()
	context = {'asociados': asociados}
	return render(request, 'pedidos/asociados.html', context)

def asociado_proveedor(request,asociadono):
	#pdb.set_trace()
	cursor=connection.cursor()
	
	cursor.execute('SELECT sd.idsocio as asociadono, sd.idproveedor as proveedorno,p.razonsocial,sd.descuento_porc from socio_descuento sd INNER JOIN proveedor p on (p.empresano=1 and sd.idproveedor=p.proveedorno) where sd.idsocio=%s;',(asociadono,))
	asociado_proveedor = dictfetchall(cursor)

	cursor.execute("SELECT nombre,appaterno,apmaterno from asociado where asociadono=%s;",(asociadono,))
	nombre_socio = cursor.fetchone()
	k=0
	ns=str(asociadono)+''
	while k<=2:
		ns=ns+' '+nombre_socio[k]
		k+=1	
	#nombre_socio[0].strip()+' '+socio_nombre[1].strip()+' 'socio_nombre[2].strip()

	cursor.close()
	context = {'asociado_proveedor': asociado_proveedor,'asociadono':asociadono,'nombre_socio':ns,}
	return render(request, 'pedidos/asociado_proveedor.html', context)	


def ok(request):
	
	return render(request, 'pedidos/autencitacion_exitosa.html')	


def busca_pedidos(request):
	#pdb.set_trace() 


	try:
		g_numero_socio_zapcat = request.session['socio_zapcat']	
		is_staff = request.user.is_staff

	except KeyError :
		
		#print "llave:",request.session['socio_zapcat']
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
						cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,h.fechapedido,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) where h.asociadono=%s and h.fechapedido>=%s and h.fechapedido<=%s ORDER BY h.pedidono DESC;", (g_numero_socio_zapcat,fecha-timedelta(days=60),fecha))
						print "Entro en status=Todos y fecha != 19010101"
					else:
						if status !='Todos' and fecha == fecha_1901:
							cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,h.fechapedido,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) where h.asociadono=%s and l.status=%s and h.fechapedido>=%s and h.fechapedido<=%s ORDER BY h.pedidono DESC;", (g_numero_socio_zapcat,status,hoy-timedelta(days=60),hoy))
							print "Entro en status != Todos y fecha=1901/01/01"
						else:
	 						if status != 'Todos' and fecha != fecha_1901:
								cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,h.asociadono,h.fechapedido,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.Observaciones from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) where h.asociadono=%s and l.status=%s and h.fechapedido>=%s and h.fechapedido<=%s ORDER BY h.pedidono DESC;", (g_numero_socio_zapcat,status,fecha-timedelta(days=60),fecha))			
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
				
				context = {'pedidos':pedidos,'mensaje':mensaje,'elementos':elementos,'is_staff':is_staff,}

				# Cierra la conexion a la base de datos
				cursor.close()
				
				return render(request,'pedidos/lista_pedidos.html',context)
			
		else:
			form = BuscapedidosForm()
			#cursor.close()
			
		return render(request,'pedidos/busca_pedidos.html',{'form':form,'is_staff':is_staff})
	else:
		redirect('/pedidos/acceso/') 


def lista_pedidos(request):
	context = {'asociados': asociados,'form':form}
	return render(request, 'pedidos/asociados.html', context,{'form':form})


# La siguiente funcion es utilizada para seleccionar 
# los () y que se puedan mostrar en el combo de proveedor al hacer un
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
	tipo = 'P'
	# elimina cualquier registro de la session.
	session_id = request.session.session_key
	# Asigna is_staff para validacines
	is_staff = request.session['is_staff']

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
			return render(request,'pedidos/crea_pedido.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})
		else:	
			
			mensaje = "Error en la forma"
			return render(request,'pedidos/crea_pedidos.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})

	form = PedidosForm(request)
	mensaje = "Entrando de nuevo a la forma"
	return render(request,'pedidos/crea_pedidos.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,'tipo':tipo,'num_socio':0,})	

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

def lista_Catalogos(id_prov,id_temp,g_numero_socio_zapcat,is_staff):

	#pdb.set_trace()
	#print "g_numero_socio_zapcat trae",g_numero_socio_zapcat
	
	# Si el socio activo es de staff entonces se debe buscar por
	# los catalogos del socio_pidiendo, de otra manera significa que
	# no hay ningun socio pidiendo calzado y quien esta firmado es 
	# quien pide g_numero_socio_zapcat

	# Esto hara que la busqueda se haga por la variable socio_que_pide

	adquirio_catalogo = 1

	cursor=connection.cursor()
	#cursor.execute("SELECT clasearticulo from catalogostemporada where proveedorno=%s and anio=%s;",(id_prov,id_temp))
	
	# Hace un primer select de catalogos considerando al socio y si esta activo para estos catalogos
	cursor.execute("SELECT s.clasearticulo from sociocatalogostemporada s left join catalogostemporada c on (s.ProveedorNo=c.ProveedorNo and s.Periodo=c.Periodo and s.Anio=c.Anio and s.ClaseArticulo=c.ClaseArticulo)  where s.proveedorno=%s and s.anio=%s and s.AsociadoNo=%s and s.Activo and c.Activo;",[id_prov,id_temp,g_numero_socio_zapcat,])
	registros = cursor.fetchall()


	listacat=() # Inicializa una tupla para llenar combo de Proveedores
	
	
	# Si el primer select no arroja registros, hace un segundo select sin considerar al socio
	# solo para que se traiga la lista de catalogos del proveedor
	# y la bandera de adquirio_catalogo la hace falsa ( le pone cero )
	

	if not registros or is_staff:
		try:

			cursor.execute("SELECT c.clasearticulo from catalogostemporada c  where c.proveedorno=%s and c.anio=%s  and c.Activo=1 group by c.proveedorno,c.anio,c.clasearticulo  ;",[id_prov,id_temp,])
					
			
			adquirio_catalogo = 0
		
		except Error as e:
			print e
	


	# Convierte el diccionario en tupla
	for row in cursor:
		elemento = tuple(row)
		listacat=listacat+elemento
	listacat=('SELECCIONE...',)+listacat

	return (listacat,adquirio_catalogo)	

def combo_catalogos(request,*args,**kwargs):
	#pdb.set_trace()

	g_numero_socio_zapcat = request.session['socio_zapcat']
	print "el socio es ", g_numero_socio_zapcat

	is_staff = request.session['is_staff']

	adquirio_catalogo = 1


	if request.session['is_staff']:


		socio_a_validar = request.session['socio_pidiendo']

		print "Socio staff pidiendo",socio_a_validar
		
	else:
		socio_a_validar = g_numero_socio_zapcat

		print "Socio no staff pidiendo",socio_a_validar


	if request.is_ajax() and request.method == 'GET':
		id_prov = request.GET['id_prov']
		id_temp = request.GET['id_temp']
		
		
		print "llego hasta antes de l"
		print "socio a validar:",socio_a_validar
		# Trae la lista de catalogos con los parametros indicados:
		
		l,adquirio_catalogo = lista_Catalogos(id_prov,id_temp,socio_a_validar,is_staff)
		
		#data = serializers.serialize('json',r,fields=('clasearticulo',))
		
		# La siguiente instruccion genera una variable data con los datos en formato json.
		# En la linea anterior ( que esta comentada ), trataba de usar
		# serielizers para convertir a json pero no funciono.

		h = {'l':l,'adquirio_catalogo':adquirio_catalogo,'is_staff':is_staff}

		data = json.dumps(h)
		
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
		#print "pagina no encontrada"



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
		#print "pagina no encontrada"


# LOGICA PARA COMBO DE ALMACENES


def lista_almacenes(id_prov):
	
	cursor=connection.cursor()
	cursor.execute("SELECT almacen,razonsocial from almacen where empresano=1 and proveedorno=%s;",[id_prov,])
	
	listaalm=() # Inicializa una tupla para llenar combo de Estilos
			
	# Convierte el diccionario en tupla
	for row in cursor:
		elemento = tuple(row)
		listaalm=listaalm+elemento
	listaalm=('SELECCIONE...',)+listaalm
	
	return (listaalm)	

"""def lista_almacenes(id_prov):
		cursor=connection.cursor()
		cursor.execute("SELECT almacen,razonsocial from almacen where empresano=1 and proveedorno=%s;",[id_prov,])
		pr=() # Inicializa una tupla para llenar combo de Proveedores
		
		# Convierte el diccionario en tupla
		for row in cursor:
			elemento = tuple(row)
			pr=pr+elemento
		pr = (0L,u'Seleccione ') + pr
		

		# Inicializa dos listas para calculos intermedios
		x=[]
		y=[]	

		# Forma una lista unicamente con valores
		# significativos (nombres de proveedores y su numero)

		for i in range(0,len(pr)):
			if i % 2 != 0:
				x.append(pr[i-1])
				x.append(pr[i])
				y.append(x)
				x=[]


		# tuple_of_tuples = tuple(tuple(x) for x in list_of_lists)
		lprov = tuple(tuple(x) for x in y)

		
		
		return (lprov)"""


def combo_almacenes(request,*args,**kwargs):
	#pdb.set_trace()

	if request.is_ajax() and request.method == 'GET':
		id_prov = request.GET['id_prov']
		
		
		# Trae la lista de catalogos con los parametros indicados:
		l = lista_almacenes(id_prov)
		
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





def llena_combo_sucursal(request,*args,**kwargs):

	#print "Entra a llena combo sucursal"
	if request.is_ajax() and request.method == 'GET':
		#print "llena combo suc, es ajax y get"		
		lsuc = lista_Sucursales()
		#print "Las sucursales son:"
		#for j in lsuc:
		#	print j
		
		data = json.dumps(lsuc)
		
		return HttpResponse(data,content_type='application/json')
	else:
		raise Http404
		#print "pagina no encontrada"

# Graba en tabla temporal cada articulo seleccionando

def grabar_pedidos(request):
	#pdb.set_trace()
	# Guarda la llave de la session para su posterior manipulacion.
	session_id = request.session.session_key
	socio_zapcat =  request.session['socio_zapcat']
	EsSocio = request.session['EsSocio']


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
		opcioncompra = request.POST.get('opcioncompra')
		plazoentrega = request.POST.get('plazoentrega')
		fechamaximaentrega = request.POST.get('fechamaximaentrega')
		precio_cliente = request.POST.get('precio_cliente')
		almacen = request.POST.get('almacen') # Almacen del cliente, se agrega para recibir 
											  # el almacen seleccionado solamente en pantalla de piezas no solicitadas (proveedor 3)
											  # para pedidos normales, esta campo trae un valor de cero que se asigna en pedidos.js
		# convierte la fecha a formato adecuado para poder ser grabada en base de datos		
		if fechamaximaentrega is not None:
			f_convertida = datetime.strptime(fechamaximaentrega, "%d/%m/%Y").date()
 		else:
 			f_convertida = '1901/01/01'
		
			

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


				
				cursor.execute("SELECT b.codigoarticulo, b.precio,if(a.descontinuado,'1','0') as descont From preciobase b inner join articulo a  on ( b.empresano=a.empresano and b.codigoarticulo=a.codigoarticulo and b.catalogo=a.catalogo) where b.proveedorid=%s and b.temporada =%s and b.catalogo=%s and b.pagina=%s and b.estilo=%s and b.idmarca=%s and b.idcolor=%s and b.talla=%s limit 1;", [id_prov,id_temp,id_cat,id_pag,id_est,id_mar,id_col,id_talla])
				num_art = cursor.fetchone()


				cursor.execute("SELECT b.precio From preciosopcionales b  where b.empresano=1  and b.Proveedor=%s and b.Temporada=%s and b.catalogo=%s and b.Articuloid=%s and b.TipoPrecio=%s limit 1;",(id_prov,id_temp,id_cat,num_art[0],'Cliente',))
				precio_opcional = cursor.fetchone()
			
				
				
				'''cursor.execute("SELECT b.precio From preciosopcionales b where b.Empresano=1 and b.articuloid=%s and  b.proveedor=%s and b.temporada =%s and b.catalogo=%s and b.tipoprecio='Cliente' limit 1;", [num_art[0],id_prov,id_temp,id_cat,])
				precio_cliente = cursor.fetchone()'''

				#Selecciona el precio dependiendo de si se es socio o cliente:

				try:

					precio_cliente = precio_opcional[0] # en ocaciones precio[0] trae un None por eso se maneja esta excepcion.

				except TypeError:

					precio_cliente = num_art[1]


				precio_final = num_art[1] if EsSocio else precio_cliente
	
				try:
					#pdb.set_trace()

														
					cursor.execute("INSERT INTO pedidos_pedidos_tmp (session_key,idproveedor,idproducto,catalogo,precio,temporada,tallaalt,opcioncompra,plazoentrega,fechamaximaentrega,almacen_prov) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (session_id,id_prov,num_art[0],id_cat,precio_final,id_temp,id_tallaalt,opcioncompra,plazoentrega,f_convertida,almacen,))
					
					cursor.execute("SELECT id FROM pedidos_pedidos_tmp ORDER BY id DESC LIMIT 1")
					id_rec = cursor.fetchone()
					
					# recoge el id del producto insertado y retorna nuevamente los datos recibidos
					# tanto el precio son decimales y se convierten a string para que puedan ser serializados por json.dump, de lo contrario
					# se genera un error de serializacion.

					data = {'id':id_rec[0],'id_prov':id_prov,'id_temp':id_temp,'id_cat':id_cat,'id_pag':id_pag,'id_est':id_est,'id_mar':id_mar,'id_col':id_col,'id_talla':str(id_talla),'precio': str(precio_final),'id_tallaalt':id_tallaalt,'descontinuado': num_art[2],'is_staff':request.session['is_staff'],}
					
				except DatabaseError as e:
					
					data = "Error en la ejecucion de la insercion: "
					print e		
					
				cursor.close()
			
		#pdb.set_trace()	
		return HttpResponse(json.dumps(data),content_type='application/json')

		
	else:
		raise Http404
		

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

def fecha_hora_conv(fecha_hoy,hora_hoy):
	# probar esta funcion porque no funciona,
	# no devuelve parametros.	

	hoy = datetime.now()
	fecha_hoy = hoy.strftime("%Y-%m-%d")
	hora_hoy = hoy.strftime("%H:%M:%S") 
	return 

def genera_documento(cursor,
	p_tipodedocumento,
	p_tipodeventa,
	p_asociado,
	p_fechacreacion,
	p_horacreacion,
	p_usuarioquecreodcto,
	p_fechaultimamodificacion,
	p_horaultimamodificacion,
	p_usuariomodifico,
	p_concepto,
	p_monto,
	p_saldo,
	p_descuentoaplicado,
	p_vtadecatalogo,
	p_cancelado,
	p_comisiones,
	p_pagoaplicadoaremisionno,
	p_lo_recibido,
	p_venta,
	p_idsucursal,
	p_bloquearnotacredito):
	#pdb.set_trace()
	# Trae el ultimo documento
	cursor.execute("SELECT nodocto from documentos WHERE empresano=1 ORDER BY nodocto DESC LIMIT 1;")
	ultimo_docto = cursor.fetchone()
	nuevo_docto = ultimo_docto[0]+1

	# Trae el ultimo documento
	cursor.execute("SELECT consecutivo from documentos WHERE empresano=1 and tipodedocumento=%s  ORDER BY consecutivo DESC LIMIT 1;",(p_tipodedocumento,))
	ultimo_consec = cursor.fetchone()
	Nuevo_consec = ultimo_consec[0]+1


	# Genera el documento.
	# Ojo: observar que el campo `UsuarioQueCreoDcto.` se coloco entre apostrofes inversos y el nombre del campo tal y como esta definido en la tabla (casesensitive) dado que si
	# se pone sin apostrofes marca error!
	cursor.execute("INSERT INTO documentos (`EmpresaNo`,`NoDocto`,`Consecutivo`,`TipoDeDocumento`,`TipoDeVenta`,`Asociado`,`FechaCreacion`,`HoraCreacion`,`UsuarioQueCreoDcto.`,`FechaUltimaModificacion`,`HoraUltimaModificacion`,`UsuarioModifico`,`Concepto`,`monto`,`saldo`,`DescuentoAplicado`,`VtaDeCatalogo`,`Cancelado`,`comisiones`,`PagoAplicadoARemisionNo`,`Lo_recibido`,`venta`,`idsucursal`,`BloquearNotaCredito`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(1,nuevo_docto,Nuevo_consec,p_tipodedocumento,p_tipodeventa,p_asociado,p_fechacreacion,p_horacreacion,p_usuarioquecreodcto,p_fechaultimamodificacion,p_horaultimamodificacion,p_usuariomodifico,p_concepto,float(p_monto),float(p_saldo),float(p_descuentoaplicado),p_vtadecatalogo,p_cancelado,float(p_comisiones),p_pagoaplicadoaremisionno,float(p_lo_recibido),float(p_venta),p_idsucursal,p_bloquearnotacredito,))
	return nuevo_docto


	''' ********** DOCUMENTOS ****************'''
@login_required(login_url = "/pedidos/acceso/")
def documentos(request):
	documentos = {}
	tipo='D'
	if request.method == 'POST':
		
		form = DocumentosForm(request.POST)
		
		if form.is_valid():

			'''documento_num = request.POST.get('documento_num').encode('latin_1')
			tipo_movimiento = request.POST.get('tipo_movimiento').encode('latin_1')
			fechainicial = request.POST.get('fechainicial').encode('latin_1')
			fechafinal = request.POST.get('fechafinal').encode('latin_1')
			socio_num = request.POST.get('socio_num').encode('latin_1')

			fechainicial = fechainicial.strftime("%Y-%m-%d")
			fechafinal = fechafinal.strftime("%Y-%m-%d")'''
			documento_num = form.cleaned_data['documento_num']
			tipo_movimiento = form.cleaned_data['tipo_movimiento']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']
			socio_num = form.cleaned_data['socio_num']
			

			# filtra por documento

			if documento_num != 0 :
				
				consulta = """SELECT d.NoDocto,
									d.TipoDeDocumento,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.venta,
									d.saldo,
									d.comisiones,
									d.DescuentoAplicado,
									if(d.Cancelado='\x00','Activo','Cancelado') as Cancelado,if((not(d.tipodedocumento="Remision" and trim(d.concepto)='Venta') and not((d.tipodedocumento='Credito' or d.tipodedocumento='Cargo') and d.saldo=0)) and not(d.Cancelado),1,0) as cancelar FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1
									and d.nodocto =%s;"""
				parms = [documento_num]

			#filtra por socio y todos sus movimientos

			elif documento_num == 0 and tipo_movimiento == 'Todos' and socio_num !=0:
				
				consulta = """SELECT d.NoDocto,
									d.TipoDeDocumento,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.venta,
									d.saldo,
									d.comisiones,
									d.DescuentoAplicado,
									if(d.Cancelado='\x00','Activo','Cancelado') as Cancelado,if((not(d.tipodedocumento="Remision" and trim(d.concepto)='Venta') and not((d.tipodedocumento='Credito' or d.tipodedocumento='Cargo') and d.saldo=0)) and not(d.Cancelado),1,0) as cancelar FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1
									and d.asociado =%s and fechacreacion >= %s and fechacreacion<=%s;"""
				parms =[socio_num,fechainicial,fechafinal]
			
			
			# filtra por todos los movimientos sin importar el socio
			elif documento_num == 0 and tipo_movimiento == 'Todos' and socio_num == 0:
				
				consulta = """SELECT d.NoDocto,
									d.TipoDeDocumento,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.venta,
									d.saldo,
									d.comisiones,
									d.DescuentoAplicado,
									if(d.Cancelado='\x00','Activo','Cancelado') as Cancelado,if((not(d.tipodedocumento="Remision" and trim(d.concepto)='Venta') and not((d.tipodedocumento='Credito' or d.tipodedocumento='Cargo') and d.saldo=0)) and not(d.Cancelado),1,0) as cancelar FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1
									and fechacreacion >= %s and fechacreacion<=%s;"""
				parms = [fechainicial,fechafinal]

			# filtra por un solo tipo de movimiento de un socio en particular

			elif documento_num == 0 and tipo_movimiento != 'Todos' and socio_num != 0:
				
				consulta = """SELECT d.NoDocto,
									d.TipoDeDocumento,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.venta,
									d.saldo,
									d.comisiones,
									d.DescuentoAplicado,
									if(d.Cancelado='\x00','Activo','Cancelado') as Cancelado,if((not(d.tipodedocumento="Remision" and trim(d.concepto)='Venta') and not((d.tipodedocumento='Credito' or d.tipodedocumento='Cargo') and d.saldo=0)) and not(d.Cancelado),1,0) as cancelar FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1
									and d.asociado =%s and fechacreacion >= %s and fechacreacion<=%s and d.TipoDeDocumento=%s;"""
				parms = [socio_num,fechainicial,fechafinal,tipo_movimiento]
			
			# filtra un solo tipo de movimiento para todos los socios
			else:

				consulta = """SELECT d.NoDocto,
									d.TipoDeDocumento,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.venta,
									d.saldo,
									d.comisiones,
									d.DescuentoAplicado,
									if(d.Cancelado='\x00','Activo','Cancelado') as Cancelado,if((not(d.tipodedocumento="Remision" and trim(d.concepto)='Venta') and not((d.tipodedocumento='Credito' or d.tipodedocumento='Cargo') and d.saldo=0)) and not(d.Cancelado),1,0) as cancelar FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1
									and fechacreacion >= %s and fechacreacion<=%s and d.TipoDeDocumento=%s;"""
				parms = [fechainicial,fechafinal,tipo_movimiento]


			try:
				cursor = connection.cursor()
		
				cursor.execute(consulta,parms) # observar que se uso parms como parte de una lista en lugar de una tupla, si se usa una tupla marca error

				documentos = dictfetchall(cursor)

				if not documentos:
					e = "No se encontraron registros !"
				else:
					e = ''
				context = {'documentos':documentos,'mensaje':e,}
				return render (request,'pedidos/muestra_documentos.html',context)
			
			except DatabaseError as e:
				print e

			
			cursor.close()
		
	else:
		form = DocumentosForm()

	return render (request,'pedidos/documentos.html',{'form':form,'tipo':tipo})
			
		
def muestra_documentos(request):
	return HttpResponse("falta esto")

	

def procesar_pedido(request):

	#pdb.set_trace()
	global g_numero_socio_zapcat
	
	# Se asigna elnumero de socio

	socio_zapcat = request.session['socio_zapcat']

	# se asigna la sesion activa para este socio	
	session_id = request.session.session_key

	if request.is_ajax() and request.method =='POST':


		total = request.POST.get('total') # Este total esta mal redondeado, se cambia por el de la siguiete linea v_total
		v_total = Decimal(0.0,2) # Lo convierte a decimal para que pueda acumular las ctds de precio en pedidoslines ( que las trae de la bd como tipo decimal)

		if request.session['is_staff']:

			# Toma como socio a validar el socio que pide, no el usuaro que captura.
			# y, lsuc toma el numero de la sucursal_activa en la session.
			
			socio_a_validar = request.session['socio_pidiendo']
			
			# Si es un pedido para el socio 3 (Devoluciones a provedor) directamente
			# debe asignar el status RecepEnDevol.

			if socio_a_validar != 3:

				status_a_asignar='Por Confirmar'
			else:
				status_a_asignar='RecepEnDevol'
			
			#capturista = request.session['socio_zapcat'] # toma el valor del empleado que captura
			tiposervicio = request.POST.get('tiposervicio')
			
			viasolicitud = request.POST.get('viasolicitud')
			viasolicitud = int(viasolicitud) #  se convierte a entero	
	
			psw_paso = request.POST.get('psw_paso')

			try:
				if float(request.POST.get('anticipo')):
					anticipo = int(request.POST.get('anticipo').encode('latin_1'))
				else:
					anticipo = 0	
			except ValueError:
				data = {'status_operacion':'fail',}
				return HttpResponse(json.dumps(data),content_type='application/json',)	
			
			
		else:
			
			# De otra manera toma como socio, el usuario que captura (socio normal).
			# luego busca el numero de sucursal usando el nombre de la sucursal seleccionada 
			
			socio_a_validar = socio_zapcat
			capturista = 99 # toma el valor de capurista en internet
			anticipo = 0
			viasolicitud = 3
			tiposervicio = request.POST.get('tiposervicio')
			status_a_asignar='Por Confirmar'
		
		# trae el numero de sucursal donde se recogera el pedido
		lsuc = request.POST.get('lsuc')

		cursor = connection.cursor()
		
		cursor.execute("SELECT SucursalNo from sucursal where nombre = %s;",[lsuc])
		sucursal_registro = cursor.fetchone()
		id_suc = sucursal_registro[0]


		if request.session['is_staff']:
			
			cursor.execute("SELECT usuariono from usr_extend where pass_paso=%s;",(psw_paso,))
			usr_existente =cursor.fetchone()
			usr_existente =usr_existente[0]
			capturista = usr_existente

		else:
			usr_existente = 99
			capturista = 99


		cursor.close()

		
		# Inicia la transaccion
		try:
			cursor = connection.cursor()
			cursor.execute("START TRANSACTION;")





			# Se busca el ultimo pedido registrado para hacer y se le suma uno para crear el nuevo
			cursor.execute("SELECT PedidoNo from pedidosheader ORDER BY PedidoNo DESC LIMIT 1;")
			#cursor.callproc('TraeUltimoPedido',)
			
			#pdb.set_trace()
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
			
			cursor.execute("INSERT INTO pedidosheader (EmpresaNo,PedidoNo,FechaPedido,HoraPedido,Saldototal,VtaTotal,UsuarioCrea,FechaUltimaModificacion,FechaCreacion,HoraCreacion,horamodicacion,UsuarioModifica,idSucursal,AsociadoNo,tiposervicio,viasolicitud) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (1,PedidoNuevo,fecha_hoy,hora_hoy,total,total,capturista,fecha_hoy,fecha_hoy,hora_hoy,hora_hoy,capturista,id_suc,socio_a_validar,tiposervicio,viasolicitud))
			
			# Si hay anticipo, genera el documento correspondiente

			if anticipo > 0:
				print "hay anticipo"	

			#	El sigiuente comentario es para ubicar los parametros con el llamado que viene despues..es solo guia.	
			#	genera_documento(p_tipodedocumento,p_tipodeventa,p_asociado,p_fechacreacion,p_horacreacion,p_usuarioquecreodcto,p_fechaultimamodificacion,p_horaultimamodificacion,p_usuariomodifico,p_concepto,p_monto,p_saldo,p_descuentoaplicado,p_vtadecatalogo,p_cancelado,p_comisiones,p_pagoaplicadoaremisionno,p_lo_recibido,p_venta,p_idsucursal,p_bloquearnotacredito):
			
				nuevo_docto = genera_documento(cursor,"Credito","Contado",socio_a_validar,fecha_hoy,hora_hoy,capturista,fecha_hoy,hora_hoy,capturista,"Anticipo a pedido Num. "+str(PedidoNuevo),anticipo,anticipo,0,False,False,0,0,0,0,id_suc,False)		
			else:
				print "No hay anticipo"
				nuevo_docto = 0

			# Determina la cantidad de registros en temporal para la session en curso.
			cursor.execute("SELECT COUNT(*) FROM pedidos_pedidos_tmp where session_key = %s;",[session_id])
			Tot_reg_tmp = cursor.fetchone()

			print "total registros tmp"
			print Tot_reg_tmp[0]

			#Selecciona registro por registro de la tabla temporal (delimitada por la sesion en curso) y actualiza el detalle del pedido.
			
			cursor.execute("SELECT idproducto,catalogo, precio,temporada,tallaalt,opcioncompra,almacen_prov FROM pedidos_pedidos_tmp where session_key= %s;",[session_id])
			datos = namedtuplefetchall(cursor)

			count = 1
			while (count <= Tot_reg_tmp[0]):
				#print datos[count-1].idproducto
				#print datos[count-1].catalogo
				#print datos[count-1].precio
				if datos[count-1].opcioncompra == '1':
					opcioncompra = '1ra.'
				elif datos[count-1].opcioncompra == '2':
					opcioncompra = '2da.'
				else:
					opcioncompra = '3ra'
		
				# Se asegura que el campo 'temporada' tenga un valor valido(1 o 2)
				if not(datos[count-1].temporada ==1 or datos[count-1].temporada==2):

					raise ValueError("Hay un valor invalido para el campo 'temporada' no se grabara la transaccion !")
				
				if not(datos[count-1].precio>0):	
				
					raise ValueError("Hay un valor invalido para el campo 'precio' no se grabara la transaccion !")

				v_total = v_total + datos[count-1].precio # acumula el total del pedido para grabarlo en pedidosheader
				
				cursor.execute("INSERT INTO pedidoslines (EmpresaNo,Pedido,ProductoNo,CantidadSolicitada,precio,subtotal,PrecioOriginal,Status,RemisionNo,NoNotaCreditoPorPedido,NoNotaCreditoPorDevolucion,NoRequisicionAProveedor,NoNotaCreditoPorDiferencia,catalogo,NoLinea,plazoentrega,OpcionCompra,FechaMaximaEntrega,FechaTentativaLLegada,FechaMaximaRecoger,Observaciones,AplicarDcto) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", [1,PedidoNuevo,datos[count-1].idproducto,1,datos[count-1].precio,datos[count-1].precio,datos[count-1].precio,status_a_asignar,0,nuevo_docto,0,0,0,datos[count-1].catalogo,count,2,opcioncompra,'19010101','19010101','19010101',datos[count-1].tallaalt,0])
				cursor.execute("INSERT INTO pedidoslinestemporada (EmpresaNo,Pedido,ProductoNo,catalogo,NoLinea,Temporada) VALUES(%s,%s,%s,%s,%s,%s)",[1,PedidoNuevo,datos[count-1].idproducto,datos[count-1].catalogo,count,datos[count-1].temporada])
				cursor.execute("INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,ProductoNo,Status,catalogo,NoLinea,FechaMvto,HoraMvto,Usuario) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",[1,PedidoNuevo,datos[count-1].idproducto,status_a_asignar,datos[count-1].catalogo,count,fecha_hoy,hora_hoy,capturista])
				
				#Si el socio es 3 se crea un registro con status de 'Aqui', esto para que puedan los productos no solicitados 
				# imprimirse en reportes de devoluciones al proveedor. 
				if socio_a_validar ==3:
					cursor.execute("INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,ProductoNo,Status,catalogo,NoLinea,FechaMvto,HoraMvto,Usuario) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",[1,PedidoNuevo,datos[count-1].idproducto,'Aqui',datos[count-1].catalogo,count,fecha_hoy,hora_hoy,capturista])

				cursor.execute("INSERT INTO pedidos_encontrados(EmpresaNo,Pedido,ProductoNo,Catalogo,NoLinea,FechaEncontrado,BodegaEncontro,FechaProbable,`2`,`3`,`4`,`5`,`6`,`7`,`8`,`9`,`10`,encontrado,id_cierre,causadevprov,observaciones) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[1,PedidoNuevo,datos[count-1].idproducto,datos[count-1].catalogo,count,'19010101',datos[count-1].almacen_prov,'19010101','','','','','','','','','','',0,0,''])
				cursor.execute("INSERT INTO pedidos_notas(EmpresaNo,Pedido,ProductoNo,Catalogo,NoLinea,Observaciones) VALUES (%s,%s,%s,%s,%s,%s)",[1,PedidoNuevo,datos[count-1].idproducto,datos[count-1].catalogo,count,''])
				
				count = count + 1

			# La siguiente linea se agrega para actualizar la vta totalcorrectamenteya que el valor que se trea del browser no es correcto, esta mal redondeado.	
			cursor.execute("UPDATE pedidosheader SET vtatotal=%s WHERE pedidono=%s;",(v_total,PedidoNuevo,))	

			# crea log de pedido
			if request.session['is_staff']:
				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,35 if socio_a_validar == 3 else 5,fecha_hoy,hora_hoy,'Creó el pedido: '+str(PedidoNuevo) if socio_a_validar != 3 else 'Capturó pieza no solicitada con pedido: '+str(PedidoNuevo)))		
		


			cursor.execute("DELETE FROM pedidos_pedidos_tmp where session_key= %s;",[session_id])	
			
			# Graba cambios.
			cursor.execute("COMMIT;")
			status_operacion = 'ok'

		# Si hay error en base de datos hace rollback:	
		except DatabaseError as e:
			print "el error de base de datos es ",e
			status_operacion = 'fail'
			cursor.execute("ROLLBACK;")
		except ValueError as e:
			status_operacion =' fail '

		cursor.close()

		#imprime_ticket(request,PedidoNuevo)
	
		data = {'PedidoNuevo':PedidoNuevo,'status_operacion':status_operacion,}
		return HttpResponse(json.dumps(data),content_type='application/json',)	




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
	
	#pdb.set_trace()

	socio_a_dar_de_alta = request.session['socio_a_dar_de_alta']
	is_staff =  request.session['is_staff']
	if request.method == 'POST':
		form = Forma_RegistroForm(request.POST)
		
		if form.is_valid():
			new_user = form.save()
			nombre_usuario_Web = new_user.username

			''' Graba en la tabla de asociado el id que le correspondio en la Web'''
			cursor = connection.cursor()
			cursor.execute("UPDATE asociado SET num_web = %s where asociadono = %s;",[new_user.id,socio_a_dar_de_alta])
			cursor.close()
			
			para = [request.POST.get('email')]


			mensaje = """Estimado socio:

			 Ha sido habilitado para usar el sistema de Pedidos por Internet, su usuario es """ + nombre_usuario_Web.encode('utf-8') + """ . Por favor ingrese al sistema
			 con este usuario y la contraseña que eligió y cámbiela para mayor seguridad.

			 De ahora en adelante puede Ud. consultar sus pedidos y realizar nuevos pedidos desde su computadora o celular.

			 
			 Podrá ingresar al sistema en http://www.esshoesmultimarcas.com/pedidos/index/

			 Atentamente.
			 ES Shoes Multimarcas. """
			
			envio_mail_exitoso,error_envio_msg = envia_mail(para,'Su registro en ES Shoes mulitimarcas WEB',mensaje)			  

			request.session['socio_a_dar_de_alta']=0

			return render(request,'pedidos/registro_exitoso.html',{'nombre_usuario_Web':nombre_usuario_Web,'is_staff':is_staff})
	else:
		form = Forma_RegistroForm()
	return render(request,'pedidos/registration_form.html',{'form':form,'is_staff':is_staff,})

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

def envia_mail(v_para,v_asunto,v_mensaje):

	''' La presente rutina retorna un codigo de error (0=Error, 1=Exito)
		en la variable envio_mail_exitoso.
		Tambien devuelve el mensaje de error si lo hay en la variable error_envio
	'''


	# TRAE PARAMETROS DE settings.py

	email_host_user = getattr(settings, "EMAIL_HOST_USER", None)
	default_from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
	auth_user = getattr(settings, "EMAIL_HOST_USER", None)
	auth_password = getattr(settings,"EMAIL_HOST_PASSWORD",None)

	#send_mail('prueba','prueba de envio de  message por segunda vez','soporte@esshoesmultimarcas.com',['jggalvandlr@gmail.com'], fail_silently=False, auth_user='pedidos_multimarcas', auth_password='pedidos1', connection=None, html_message=None)
	
	envio_mail_exitoso=0
	error_envio=''

	try:
		envio_mail_exitoso= send_mail(v_asunto,v_mensaje,default_from_email,[v_para], fail_silently=False, auth_user=auth_user, auth_password=auth_password, connection=None, html_message=None)

		
	except SMTPServerDisconnected as e:
		error_envio = "Posiblemente el servidor de correo esta caido: "+str(e)

	except SMTPSenderRefused as e:
		error_envio ="La direccion de quién envía fue rechazada por el servidor: "+str(e)

	except SMTPRecipientsRefused as e:
		error_envio ="La dirección de destino no fué encontrada por el servidor: "+str(e)

	except SMTPAuthenticationError as e:
		error_envio ="La combinacion Usuario / Password no fue aceptada por el servidor: "+str(e)

	return (envio_mail_exitoso,error_envio)


#@permission_required('auth.add_user',login_url=None,raise_exception=True)
def empleados(request):

	return render(request,'pedidos/empleados.html')

@login_required
def entrada_sistema(request):
	
	if request.session['is_staff']:

		if request.method == 'POST':


			form = Entrada_sistemaForm(request.POST)
			
			if form.is_valid():
			
				sucursal = form.cleaned_data['sucursal']
			
				# Con la siguientes linea guarda el numero de sucursal  y su nombre en el framework de sesiones 
				# para poder utilizarlos en otros procesos.

				request.session['sucursal_activa'] = sucursal 

				# Se trae el nombre de la sucursal
				cursor=connection.cursor()
				cursor.execute('SELECT SucursalNo,nombre,direccion,colonia,ciudad,estado,pais,telefono1 from sucursal where Sucursalno=%s',(sucursal))
				nombresuc = cursor.fetchone()
				
				request.session['sucursal_nombre']= nombresuc[1]
				request.session['sucursal_direccion']= nombresuc[2]
				request.session['sucursal_colonia']= nombresuc[3]
				request.session['sucursal_ciudad']= nombresuc[4]
				request.session['sucursal_estado']= nombresuc[5]
				request.session['sucursal_telefono']= nombresuc[7]

				return render(request,'pedidos/consulta_menu.html',{'is_staff':request.user.is_staff,})
			else:
				return render(request,'pedidos/entrada_sistema.html',{'form':form,'is_staff':request.session['is_staff'],})
	
		else:
			form=Entrada_sistemaForm()
	
	else:
		return redirect('pedidos:busca_pedidos')

	return render(request,'pedidos/entrada_sistema.html',{'form':form,'is_staff':request.session['is_staff'],})

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

def trae_nombre_socio(request):


	if request.is_ajax() and request.method =='POST':
		id_socio = request.POST.get('id_socio')
		cursor = connection.cursor()

		cursor.execute("SELECT nombre,appaterno,apmaterno from asociado where asociadono=%s;",[id_socio])
		asociado_data = cursor.fetchone()
		cursor.close()
		
		if asociado_data is None:
			data = "Socio inexistente !"
		else:

			try:	
				data = asociado_data[0]+' '+ asociado_data[1]+' '+asociado_data[2]
			except TypeError as e:
				error_msg="Parte del nombre del socio, ya sea el propio nombre o alguno de los apellidos viene vacio, edite sus datos y corrija !"
				return render(request,'pedidos/error.html',{'error_msg':error_msg,})

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


def picklist_estilopagina(request):

	#pdb.set_trace()
	
	string_a_buscar = request.GET.get('estilo_a_buscar',None)
	proveedor = request.GET.get('proveedor',None)
	temporada = request.GET.get('temporada',None)
	catalogo = request.GET.get('catalogo',None)
	
	if request.is_ajax() and request.method == 'GET':
		
		valor =string_a_buscar.strip()
		
		try:

			cursor=connection.cursor()
			
			
			cursor.execute("SELECT a.estilo,a.pagina,max(a.precio) as precio from preciobase a WHERE a.empresano=1 and a.proveedorid=%s and a.temporada=%s  and a.catalogo=%s and  a.Estilo=%s group by a.estilo,a.pagina;",(proveedor,temporada,catalogo,valor,))
			l = dictfetchall(cursor)
			
			
			data= json.dumps(l,cls=DjangoJSONEncoder)

			
			cursor.close()
		except DatabaseError as d:

			print d
			data={'Error':'Error al acceder a base de datos...'}
					
		return HttpResponse(data,content_type='application/json')





def calzadollego_gral(request):

	mensaje =''

	total_articulos = 0
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
					total_articulos += ped['total_articulos']
				prov_a_buscar = ped["prov_id"]

				print "proveedor buscado"
				print prov_a_buscar
				mensaje ="Registros encontrados == > "

				context = {'form':form,'mensaje':mensaje,'pedidos':pedidos,'elementos':elementos,'total_articulos':total_articulos,}	
			
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
			op = form.cleaned_data['op']

			cursor=connection.cursor()

			
			"""cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,psf.fechatentativallegada,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre)  left join  pedidoslines psf on (p.empresano=psf.empresaNo and p.pedido=psf.pedido and p.productono=psf.productono and p.catalogo=psf.catalogo and p.nolinea=psf.nolinea) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by c.id,psf.fechatentativallegada;",(fechainicial,fechafinal))"""


			cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.Nolinea,e.BodegaEncontro,e.encontrado,p.fechapedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,if(a.talla='NE',l.observaciones,a.talla) as talla,l.precio,a.idProveedor,e.observaciones,p.idSucursal,e.id_cierre,l.observaciones,pro.razonsocial as provnom,concat(trim(aso.nombre),' ',trim(aso.appaterno),' ',trim(aso.apmaterno)) as nombre,suc.nombre as sucnom,alm.razonsocial as almnom FROM pedidoslines l INNER JOIN   pedidosheader p ON (l.EmpresaNo= p.EmpresaNo and l.Pedido=p.PedidoNo) INNER JOIN articulo a ON (l.EmpresaNo=a.EmpresaNo and l.ProductoNo=a.codigoarticulo and l.Catalogo=a.catalogo)  INNER JOIN pedidos_encontrados e on (l.EmpresaNo=e.empresaNo and l.pedido=e.pedido and e.productono=l.productono and l.catalogo=e.catalogo and e.nolinea=l.nolinea) inner join proveedor pro on (pro.empresano=1 and pro.proveedorno=a.idproveedor) inner join asociado aso on (aso.empresano=1 and aso.asociadono=p.asociadono) inner join sucursal suc on (suc.empresano=1 and suc.sucursalno=p.idsucursal) inner join almacen alm on (alm.empresano=1 and alm.proveedorno=a.idproveedor and e.BodegaEncontro=alm.Almacen) WHERE  l.fechatentativallegada>=%s and l.fechatentativallegada<=%s and e.id_cierre<>0 order by e.id_cierre;",(fechainicial,fechafinal))

			 
			lista_pedidos = dictfetchall(cursor)

			

			elementos = len(lista_pedidos)

			


			"""cursor.execute("SELECT p.razonsocial,a.razonsocial from proveedor p inner join almacen a on (p.empresano=a.empresano and p.proveedorno=a.proveedorno) where p.proveedorno=%s;",(ped['prov_id'],))
			
			prov_alm = cursor.fetchone()"""

			if not lista_pedidos:
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_calzadollego_detalle.html',{'mensaje':mensaje,})

			else:

				if op == 'Pantalla':

					print "lo que hay en pedidos"
					for ped in lista_pedidos:
						print ped

					
					mensaje ="Registros encontrados == > "

					context = {'form':form,'mensaje':mensaje,'elementos':elementos,'lista_pedidos':lista_pedidos,}	
				
					return render(request,'pedidos/lista_calzadollego_detalle.html',context)
				else:

					response = HttpResponse(content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename="calzadollego_detalle.csv"'

					writer = csv.writer(response)
					writer.writerow(['ID_CIERRE','PEDIDO','FECHA_PEDIDO','PROVEEDOR','MARCA','ESTILO','COLOR','TALLA','PRECIO','SUCURSAL','BODEGA','SOCIO_NUM','SOCIO_NOMBRE'])
					
					for registro in lista_pedidos:
						print registro
						# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
						llaves_a_mostrar = ['id_cierre','Pedido','fechapedido','provnom','idmarca','idestilo','idcolor','talla','precio','sucnom','almnom','AsociadoNo','nombre'] 
						# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
						lista = [registro[x] for x in llaves_a_mostrar]					
						writer.writerow(lista)
					cursor.close()
					return response			

		
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
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal, l.Observaciones FROM pedidos_encontrados e INNER JOIN pedidoslines l on ( e.EmpresaNo=l.empresano and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p  ON (p.EmpresaNo=l.empresano and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (p.EmpresaNo=e.empresano and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo and a.idProveedor=%s and a.empresano=1) WHERE e.empresano=1 and  e.id_cierre=0 and (e.encontrado='' or  e.encontrado='P')  and  p.FechaPedido>=%s and p.FechaPedido<=%s  and l.Status='Por Confirmar';",(proveedor,fechainicial,fechafinal))
			else:
				print "Entro a consulta opcion 2"
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal, l.Observaciones FROM pedidos_encontrados e INNER JOIN pedidoslines l on ( e.EmpresaNo=l.empresano and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p  ON (p.EmpresaNo=l.empresano and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (p.EmpresaNo=e.empresano and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo and a.idProveedor=%s and a.empresano=1) WHERE e.empresano=1 and  p.FechaPedido>=%s and p.FechaPedido<=%s  and l.Status='Por Confirmar';",(proveedor,fechainicial,fechafinal))

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


	#pdb.set_trace()
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

			
			#cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones > d.Saldo,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado,0) as VtaComisionSaldo FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones-d.descuentoaplicado <= d.Saldo,0,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado) as VtaComisionSaldo,if(d.venta + d.comisiones - d.descuentoaplicado <= d.Saldo,d.venta+d.comisiones-d.descuentoaplicado,d.Saldo) as cred_aplicado FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
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
						tipodedocumento = docto['TipoDeDocumento']
						TotalVtaBruta = TotalVtaBruta + float(docto['venta'])
						esvta =docto['Concepto'].strip()
						vtadecatalogo = docto['VtaDeCatalogo']

						# calcula para ventas normales y ventas de catalogo
						if esvta == 'Venta' or vtadecatalogo =='\x01':

						#if tipodedocumento == 'Remision':

							#Excluye las ventas de catalogo para totales de creditos cargos y descuento
							if vtadecatalogo =='\x00':
								TotalCreditos = TotalCreditos + float(docto['cred_aplicado'])															
								TotalCargos = TotalCargos + float(docto['comisiones'])	
								TotalDescuentos =  TotalDescuentos + float(docto['descuentoaplicado'])	
								VentaCalzado = VentaCalzado + float(docto['venta'])
							print float(docto['venta']),float(docto['comisiones']),float(docto['cred_aplicado'])
							print "acumulados:"
							print TotalVtaBruta,TotalCargos,TotalCreditos

						if (TotalVtaBruta + TotalCargos > TotalCreditos):
							print "entro por vtabruta+cargos > creditos"

							TotalVtaNeta = TotalVtaBruta-TotalCreditos+TotalCargos-TotalDescuentos
						else:
							print "entro por el otro lado"
							TotalVtaNeta = 0;

						if vtadecatalogo == '\x01' :
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


def buscapedidosposfecha(request):

	mensaje =''
	if request.method == 'GET':

		

		form = BuscapedidosposfechaForm(request.GET)

		if form.is_valid():

			
			socio = form.cleaned_data['socio']
			
			cursor=connection.cursor()

			cursor.execute("SELECT asociadono,nombre,appaterno,apmaterno from asociado WHERE EmpresaNo=1 and asociadono=%s;",(socio,))
			socioencontrado = cursor.fetchone()
			socio_codigo = socioencontrado[0]
			socio_nombre = socioencontrado[1]
			socio_appaterno = socioencontrado[2]
			socio_apmaterno = socioencontrado[3]

			
			"""cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,psf.fechatentativallegada,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre)  left join  pedidoslines psf on (p.empresano=psf.empresaNo and p.pedido=psf.pedido and p.productono=psf.productono and p.catalogo=psf.catalogo and p.nolinea=psf.nolinea) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by c.id,psf.fechatentativallegada;",(fechainicial,fechafinal))"""


			cursor.execute("SELECT l.Pedido,l.ProductoNo,l.Catalogo,l.Nolinea,p.fechapedido,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,l.observaciones,aso.asociadono,aso.nombre,aso.appaterno,aso.apmaterno,pro.razonsocial FROM pedidoslines l INNER JOIN   pedidosheader p ON (l.EmpresaNo= p.EmpresaNo and l.Pedido=p.PedidoNo) INNER JOIN articulo a ON (l.EmpresaNo=a.EmpresaNo and l.ProductoNo=a.codigoarticulo and l.Catalogo=a.catalogo) inner join proveedor pro on (pro.empresano=1 and pro.proveedorno=a.idproveedor) inner join asociado aso on (aso.empresano=1 and aso.asociadono=p.asociadono) WHERE  p.fechapedido>='20180910' and p.asociadono=%s and l.status='Aqui' and a.idproveedor=2;",(socio,))

			 
			lista_pedidos = dictfetchall(cursor)

			

			elementos = len(lista_pedidos)

			


			"""cursor.execute("SELECT p.razonsocial,a.razonsocial from proveedor p inner join almacen a on (p.empresano=a.empresano and p.proveedorno=a.proveedorno) where p.proveedorno=%s;",(ped['prov_id'],))
			
			prov_alm = cursor.fetchone()"""

			if not lista_pedidos:
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_pedidosposfecha.html',{'mensaje':mensaje,})

			else:
				print "lo que hay en pedidos"
				for ped in lista_pedidos:
					print ped

				
				mensaje ="Registros encontrados == > "

				context = {'form':form,'mensaje':mensaje,'elementos':elementos,'lista_pedidos':lista_pedidos,'socio_codigo':socio_codigo,'socio_nombre':socio_nombre,'socio_appaterno':socio_appaterno,}	
			
				return render(request,'pedidos/lista_pedidosposfecha.html',context)

		
	else:

		form = Calzadollego_detalleForm()
	return render(request,'pedidos/buscapedidosposfecha.html',{'form':form,})



	return


@login_required()
@permission_required('auth.add_user',login_url=None,raise_exception=True)
def pedidosgeneral(request):
	tipo='P'
	try:
	
		g_numero_socio_zapcat = request.session['socio_zapcat']	
		sucursal_activa = request.session['sucursal_activa']
		is_staff = request.user.is_staff

		
	except KeyError :

		return	HttpResponse("Ocurrió un error de conexión con el servidor, Por favor salgase completamente y vuelva a entrar a la página !")

	if request.user.is_authenticated():		
		
		if request.method == 'POST':
			form = PedidosgeneralForm(request.POST)
			'''
			Si la forma es valida se normalizan los campos numpedido, status y fecha,
			de otra manera se envia la forma con su contenido erroreo para que el validador
			de errores muestre los mansajes correspondientes '''

			if form.is_valid():
			
				# limpia datos 
				socionum = form.cleaned_data['socionum']
				numpedido = form.cleaned_data['numpedido']
				status = form.cleaned_data['status']
				estiloalt = form.cleaned_data['estiloalt']
				fechainicial = form.cleaned_data['fechainicial']
				fechafinal = form.cleaned_data['fechafinal']
				
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
					cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,l.nolinea,h.asociadono,psf.fechamvto,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.FechaMaximaEntrega,l.Observaciones,concat(aso.nombre,' ',aso.appaterno,' ',aso.apmaterno) as socionomb,z.Observaciones as notas from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) INNER JOIN asociado aso on (h.asociadono=aso.asociadono) inner join pedidos_status_fechas psf on (l.empresano=psf.empresano and l.pedido=psf.pedido and l.productono=psf.productono and l.catalogo=psf.catalogo and l.nolinea=psf.nolinea) left join pedidos_notas z on (l.empresano=z.empresano and l.pedido=z.pedido and l.productono=z.productono and l.catalogo=z.catalogo and l.nolinea=z.nolinea) where h.empresano = 1 and h.idsucursal=%s and  psf.status=l.status and h.pedidono=%s;", (sucursal_activa,numpedido,))
					
				else:
					
					if socionum != 0:

						if  status == 'Todos':
							cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,l.nolinea,h.asociadono,psf.fechamvto,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.FechaMaximaEntrega,l.Observaciones,concat(aso.nombre,' ',aso.appaterno,' ',aso.apmaterno) as socionomb,z.Observaciones as notas from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) INNER JOIN asociado aso on (h.asociadono=aso.asociadono) inner join pedidos_status_fechas psf on (l.empresano=psf.empresano and l.pedido=psf.pedido and l.productono=psf.productono and l.catalogo=psf.catalogo and l.nolinea=psf.nolinea) left join pedidos_notas z on (l.empresano=z.empresano and l.pedido=z.pedido and l.productono=z.productono and l.catalogo=z.catalogo and l.nolinea=z.nolinea) where h.empresano = 1 and h.idsucursal=%s and h.asociadono=%s and  psf.fechamvto>=%s and psf.fechamvto<=%s and l.status=psf.status ORDER BY h.pedidono DESC;", (sucursal_activa,socionum,fechainicial,fechafinal))
							
						else:
							cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,l.nolinea,h.asociadono,psf.fechamvto,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.FechaMaximaEntrega,l.Observaciones,concat(aso.nombre,' ',aso.appaterno,' ',aso.apmaterno) as socionomb,z.Observaciones as notas  from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) INNER JOIN asociado aso on (h.asociadono=aso.asociadono) inner join pedidos_status_fechas psf on (l.empresano=psf.empresano and l.pedido=psf.pedido and l.productono=psf.productono and l.catalogo=psf.catalogo and l.nolinea=psf.nolinea) left join pedidos_notas z on (l.empresano=z.empresano and l.pedido=z.pedido and l.productono=z.productono and l.catalogo=z.catalogo and l.nolinea=z.nolinea) where h.empresano = 1 and h.idsucursal=%s and h.asociadono=%s and l.status=%s and psf.fechamvto>=%s and psf.fechamvto<=%s and l.status=psf.status ORDER BY h.pedidono DESC;", (sucursal_activa,socionum,status,fechainicial,fechafinal))

					else:
						if estiloalt.strip() == '':

							cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,l.nolinea,h.asociadono,psf.fechamvto,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.FechaMaximaEntrega,l.Observaciones,concat(aso.nombre,' ',aso.appaterno,' ',aso.apmaterno) as socionomb,z.Observaciones as notas  from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo)  INNER JOIN asociado aso on (h.asociadono=aso.asociadono) inner join pedidos_status_fechas psf on (l.empresano=psf.empresano and l.pedido=psf.pedido and l.productono=psf.productono and l.catalogo=psf.catalogo and l.nolinea=psf.nolinea) left join pedidos_notas z on (l.empresano=z.empresano and l.pedido=z.pedido and l.productono=z.productono and l.catalogo=z.catalogo and l.nolinea=z.nolinea) where h.empresano = 1 and h.idsucursal=%s and l.status=%s and psf.fechamvto>=%s and psf.fechamvto<=%s and l.status=psf.status ORDER BY h.pedidono DESC;", (sucursal_activa,status,fechainicial,fechafinal))
						else:
							if status != 'Todos':
								cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,l.nolinea,h.asociadono,psf.fechamvto,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.FechaMaximaEntrega,l.Observaciones,concat(aso.nombre,' ',aso.appaterno,' ',aso.apmaterno) as socionomb,z.Observaciones as notas  from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo)  INNER JOIN asociado aso on (h.asociadono=aso.asociadono) inner join pedidos_status_fechas psf on (l.empresano=psf.empresano and l.pedido=psf.pedido and l.productono=psf.productono and l.catalogo=psf.catalogo and l.nolinea=psf.nolinea) left join pedidos_notas z on (l.empresano=z.empresano and l.pedido=z.pedido and l.productono=z.productono and l.catalogo=z.catalogo and l.nolinea=z.nolinea) where h.empresano = 1 and h.idsucursal=%s and l.status=%s and a.idestilo=%s and psf.fechamvto>=%s and psf.fechamvto<=%s and l.status=psf.status ORDER BY h.pedidono DESC;", (sucursal_activa,status,estiloalt,fechainicial,fechafinal))
							else:
								cursor.execute("SELECT l.pedido,l.productono,l.catalogo,l.precio,l.status,l.nolinea,h.asociadono,psf.fechamvto,h.pedidono,h.fechaultimamodificacion,a.codigoarticulo,a.catalogo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.FechaTentativallegada,l.FechaMaximaEntrega,l.Observaciones,concat(aso.nombre,' ',aso.appaterno,' ',aso.apmaterno) as socionomb,z.Observaciones as notas  from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo)  INNER JOIN asociado aso on (h.asociadono=aso.asociadono) inner join pedidos_status_fechas psf on (l.empresano=psf.empresano and l.pedido=psf.pedido and l.productono=psf.productono and l.catalogo=psf.catalogo and l.nolinea=psf.nolinea) left join pedidos_notas z on (l.empresano=z.empresano and l.pedido=z.pedido and l.productono=z.productono and l.catalogo=z.catalogo and l.nolinea=z.nolinea) where h.empresano = 1 and h.idsucursal=%s and a.idestilo=%s and psf.fechamvto>=%s and psf.fechamvto<=%s and psf.status=l.status ORDER BY h.pedidono DESC;", (sucursal_activa,estiloalt,fechainicial,fechafinal))


									
				# El contenido del cursor se convierte a diccionario para poder
				# ser enviado como parte del contexto y sea manipulable.				
				pedidos = dictfetchall(cursor)
				

				if not pedidos:
					mensaje = 'No se encontraron registros !'
				else:
					
					mensaje ='Registros encontrados:'
				elementos = len(pedidos)
					
				
				context = {'pedidos':pedidos,'mensaje':mensaje,'elementos':elementos,'is_staff':is_staff,}

				# Cierra la conexion a la base de datos
				cursor.close()
				
				return render(request,'pedidos/lista_pedidosgeneral.html',context)
			
		else:
			form = PedidosgeneralForm()
			#cursor.close()
			
		return render(request,'pedidos/pedidosgeneral.html',{'form':form,'is_staff':is_staff,'tipo':tipo,})
	else:
		redirect('/pedidos/acceso/') 


def pedidosgeneraldetalle(request,pedido,productono,catalogo,nolinea):
	#pdb.set_trace()
	pedidono = pedido
	#print (pedido,productono,catalogo,nolinea)
	#print("la linea es ",nolinea)
	

	cursor=connection.cursor()


	
	cursor.execute("SELECT h.fechapedido,a.codigoarticulo,pe.fechaencontrado,pe.bodegaencontro,pe.encontrado,pe.id_cierre,pe.causadevprov,pe.observaciones,h.tiposervicio,via.descripcion as via_solicitud from pedidoslines l inner join pedidosheader h inner join articulo a on (l.pedido=h.pedidono and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) INNER JOIN asociado aso on (h.asociadono=aso.asociadono) INNER JOIN pedidos_encontrados pe on (l.empresano=pe.empresano and l.pedido=pe.pedido and l.productono=pe.productono and l.catalogo=pe.catalogo and l.nolinea=pe.nolinea) INNER JOIN viasolicitud via  on (via.id=h.viasolicitud) where l.empresano=1 and l.pedido=%s and l.productono=%s and l.catalogo=%s and l.nolinea=%s;", (pedidono,productono,catalogo,nolinea))

	if cursor.rowcount:
		
		datos_cierre = cursor.fetchone()

		cursor.execute("SELECT proveedorno,almacen,razonsocial from almacen where empresano=1 and almacen =%s;",(datos_cierre[3],))
		
		if cursor.rowcount:

			datos_almacen = cursor.fetchone()
		else:
			datos_almacen = ('1','1','1','1','1')

	else:
		# asigna valores default a la tupla para
		# que pueda hacer joins en los selects y traer informacion
		# pese a que no haya almacen relacionado.
		datos_cierre = ('19010101','','19010101','N',0,'','','','','')
		datos_almacen = ('1','1','1','1','1')

	cursor.execute("SELECT psf.status, psf.fechamvto,psf.horamvto,u.usuario from pedidos_status_fechas psf left join usuarios u on (u.usuariono=psf.usuario) WHERE psf.empresano=1 and psf.pedido=%s and psf.productono=%s and psf.catalogo=%s and psf.nolinea=%s order by psf.fechamvto,psf.horamvto;",(pedidono,productono,catalogo,nolinea) )
	v_PedidosStatusFechas = dictfetchall(cursor)


	context={'fechapedido':datos_cierre[0],'productono':datos_cierre[1],'fechaencontrado':datos_cierre[2],'encontrado':datos_cierre[4],'id_cierre':datos_cierre[5],'tiposervicio':datos_cierre[8],'via_solicitud':datos_cierre[9],'almacen':datos_almacen[2],'psf':v_PedidosStatusFechas,}
	'''else:
		context={'mensaje':"No existe informacion suficiente para la consulta..!"}	
	'''
	return render(request,'pedidos/lista_pedidosgeneraldetalle.html',context)


################ CANCELACION DE PEDIDOS ###########
"""AHORITA NO ESTA EN USO..QUIZAS SE BORRE """

def cancelarpedidoadvertencia(request,pedido,productono,catalogo,nolinea):
	#no esta en 
	#pdb.set_trace()
	
	status_operation='fail'

	form=CancelaproductoForm()
	context={}
	
	print request.is_ajax()
	if request.method == 'POST'  and not (request.is_ajax()):

			form = CancelaproductoForm(request.POST)
			
			if form.is_valid():
				print " pasa por aqui"
				cursor = connection.cursor()
				# limpia datos 
				motivo_cancelacion = form.cleaned_data['motivo_cancelacion']
				status_operation = cancela_producto(request,pedido,productono,catalogo,nolinea,motivo_cancelacion)			
				cursor.close()
				
	
				return render(request,'pedidos/msj_cancelacion_resultado.html',{'status_operation':status_operation,})
				
			
	elif request.method == 'POST'  and (request.is_ajax()):

		status_operation = cancela_producto(request,pedido,productono,catalogo,nolinea,'CANCELACION')
				
				
	else:			
		
		pass	
	context={'pedido':pedido,'productono':productono,'catalogo':catalogo,'nolinea':nolinea,'status_operation':status_operation,'form':form}
	return render(request,'pedidos/cancelarpedidoadvertencia.html',context,)


# RUTINA PARA CANCELAR UN PRODUCTO

def cancela_producto(request,pedido,productono,catalogo,nolinea,motivo_cancelacion,psw_paso):

	#pdb.set_trace()
	cursor = connection.cursor()
	if psw_paso == '':
		psw_paso = request.POST.get('psw_paso')
	hoy = datetime.now()
	fecha_hoy = hoy.strftime("%Y-%m-%d")
	hora_hoy = hoy.strftime("%H:%M:%S") 
	error = ''

	# La siguiente consulta trae el status para luego actualizar en pedidos_encontrados solo
	# aquellos registros que no hayan sido encontrados.

	cursor.execute("SELECT status from pedidoslines WHERE empresano=1 and pedido=%s and productono=%s and catalogo=%s and nolinea=%s;",(pedido,productono,catalogo,nolinea,))
	v_status = cursor.fetchone()
	 
	try:
		cursor.execute("SELECT usuariono FROM usr_extend WHERE pass_paso=%s;",(psw_paso,))
		usr_existente =cursor.fetchone()
		usr_existente = usr_existente[0]

		cursor.execute("START TRANSACTION;")
		cursor.execute("UPDATE pedidoslines l set l.status='Cancelado' WHERE l.empresano=1 and  l.pedido=%s and l.productono=%s and l.catalogo=%s and l.nolinea=%s;",(pedido,productono,catalogo,nolinea,))
		
		# Actualiza pedidos_econtrados si y solo si el status previo no es 'Encontrado'
		
		if v_status[0] != 'Encontrado':
			cursor.execute("UPDATE pedidos_encontrados set BodegaEncontro=0,encontrado='' WHERE empresano=1 and pedido=%s and productono=%s and catalogo=%s and nolinea=%s;",(pedido,productono,catalogo,nolinea,))
	
		cursor.execute("INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,ProductoNo,Status,catalogo,NoLinea,FechaMvto,HoraMvto,Usuario) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);",(1,pedido,productono,'Cancelado',catalogo,nolinea,fecha_hoy,hora_hoy,usr_existente))
		cursor.execute("INSERT INTO pedidoscancelados (Empresano,pedido,productono,catalogo,nolinea,motivo) values(1,%s,%s,%s,%s,%s);",(pedido,productono,catalogo,nolinea,motivo_cancelacion))			
		
		# Actualiza log
		cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,7,fecha_hoy,hora_hoy,'Canceló un articulo del catalogo '+catalogo+' con id '+productono+' del pedido '+str(pedido)))		






		status_operation='ok'
		cursor.execute("COMMIT;")

	except DatabaseError as err:
		cursor.execute("ROLLBACK;")
		status_operation='fail'
		error=str(err)
	cursor.close()
	return status_operation,error


"""ESTA RUTINA CANCELA UN PEDIDO, ES LLAMADA TANTO DE PEDIDOS GENERAL
COMO DE LA PANTALLA DE VENTAS."""
def cancelar_pedido(request):
	
	#pdb.set_trace()
	
	pedido = request.POST['pedido']
	productono = request.POST['productono']
	catalogo = request.POST['catalogo']
	nolinea = request.POST['nolinea']
	motivo = request.POST['motivo']
	psw_paso = request.POST['psw_paso']

	status_operation='fail'
	error = ''
	
	context={}
	
	status_operacion,error = cancela_producto(request,pedido,productono,catalogo,nolinea,motivo,psw_paso)
				
	data = {'status_operacion':status_operacion,'error':error}
	return HttpResponse(json.dumps(data),content_type='application/json',)	

	

@login_required()
def ingresa_socio(request,tipo): # el parametro 'tipo' toma los valores 'P' de pedido o 'D' de documento y se pasa a los templates 
	#pdb.set_trace()

	form = Ingresa_socioForm()
	context ={}	
	asociado_data =()

	try:

		existe_socio = True
		is_staff =  request.session['is_staff']
		id_sucursal = 0
		session_id = request.session.session_key
		
	except KeyError:
		
		context={'error_msg':"Se perdio su sesion, por favor cierre su navegador completamente e ingrese nuevamente al sistema !",}
		return render(request, 'pedidos/error.html',context)

	if request.method == 'POST':
		

		form = Ingresa_socioForm(request.POST)

		if form.is_valid():

			
			socio = form.cleaned_data.get('socio')
			
			
			
			cursor = connection.cursor()
			
			cursor.execute("SELECT asociadono,nombre,appaterno,apmaterno,EsSocio,telefono1 from asociado where asociadono=%s;",(socio,))
			
			asociado_data = cursor.fetchone()
			'''			
			print asociado_data	
			print asociado_data'''

			
			# Si el asociado no existe...se notifica.
			if asociado_data is None:
				existe_socio = False

			# de otra manera se actualiza 'socio_que_pide' en session
			else:

				request.session['socio_pidiendo'] = asociado_data[0]
				request.session['EsSocio'] = asociado_data[4]
				num_socio = asociado_data[0]
				telefono_socio = asociado_data[5]
				nombre_socio = str(asociado_data[0])+' '+asociado_data[1]+ ' '+asociado_data[2]+' '+(asociado_data[3] if (asociado_data[3] is not None) else 'sin apellido')+'          TELEFONO: '+asociado_data[5]
				
				form=PedidosForm(request)

				
				# trae catalogo de viasolicitud

				cursor.execute("SELECT id,descripcion FROM viasolicitud;")
				vias_solicitud = dictfetchall(cursor)

				# trae catalogo de tipos de servicio

				cursor.execute("SELECT tiposervicio from tiposervicio;")
				tipo_servicio = dictfetchall(cursor)

				cursor.close()

				# Si el tipo recibe una 'P' es un pedido lo que se procesa
				# entonces se invoca el template adecuado
				if tipo == 'P':
					# Elimina los registros de la sesion en curso antes de continuar solicitando pedidos
					# para el nuevo socio
					cursor = connection.cursor()
					cursor.execute("DELETE FROM pedidos_pedidos_tmp where session_key= %s;",[session_id])	
					cursor.close()


					context = {'form':form,'nombre_socio':nombre_socio,'num_socio':num_socio,'tipo_servicio':tipo_servicio,'vias_solicitud':vias_solicitud,'id_sucursal':id_sucursal,'is_staff':is_staff,'tipo':tipo,}
					return render(request,'pedidos/crea_pedidos.html',context,)
				
				# De otra manera se recibe una 'V' es un documento el que se procesa
				# se invoca la forma de documento y se invoca el template adecuado
				elif tipo == 'V':

					# Invoca que traera datos de ventas, comisiones y creditos del socio asi 
					# como porcentajes de descuento, etc.	

					ventas,creditos,cargos,porconfs_confs = trae_inf_venta(request,num_socio)
					context ={'ventas':ventas,'creditos':creditos,'cargos':cargos,'is_staff':is_staff,'num_socio':num_socio,'nombre_socio':nombre_socio,'porconfs_confs':porconfs_confs,}
					return render(request,'pedidos/despliega_venta.html',context)
					
				else:
					pass
					#documentos(request)
					"""form = CreaDocumentoForm()
					context = {'form':form,'nombre_socio':nombre_socio,'num_socio':num_socio,'tipo_servicio':tipo_servicio,'vias_solicitud':vias_solicitud,'id_sucursal':id_sucursal,'is_staff':is_staff,'tipo':tipo,}
					return render(request,'pedidos/crea_documento.html',context,)"""
			

			cursor.close()
	context={'existe_socio':existe_socio,'form':form,'is_staff':is_staff,'tipo':tipo,}	
	return render(request,'pedidos/ingresa_socio.html',context,)		
																																																					

		
def imprime_ticket(request):
	#pdb.set_trace()
	tot_art = 0
	try:
		is_staff = request.session['is_staff']
		suc_ok = request.session['sucursal_nombre']
		tel = request.session['sucursal_telefono']
	except KeyError:
		context={'error_msg':"Se perdio su sesion, por favor cierre su navegador completamente e ingrese nuevamente al sistema !",}
		return render(request, 'pedidos/error.html',context)

	if request.method =='GET':
		p_num_pedido = request.GET.get('p_num_pedido')
	else:
		p_num_pedido = request.POST.get('p_num_pedido')

	# se encodifica como 'latin_1' ya que viene como unicode.

	p_num_pedido = p_num_pedido.encode('latin_1')
	
	
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

	#Trae informacion del pedido.
	cursor =  connection.cursor()
	#pdb.set_trace()

	pedido_header,pedido_detalle,usuario,NotaCredito = None,None,None,0

	try:
			
		cursor.execute("SELECT PedidoNo,FechaPedido,HoraPedido,UsuarioCrea,idSucursal,AsociadoNo,vtatotal FROM pedidosheader where EmpresaNo=1 and PedidoNo = %s;",[p_num_pedido])
		pedido_header = cursor.fetchone()
		
		cursor.execute("SELECT appaterno,apmaterno,nombre,EsSocio FROM asociado where asociadono=%s;",(pedido_header[5],))
		datos_socio = cursor.fetchone()

		
		cursor.execute("SELECT l.subtotal,l.NoNotaCreditoPorPedido,l.Observaciones,l.Status,a.pagina,a.idmarca,a.idestilo,a.idcolor,a.talla,a.catalogo,so.nombre,so.appaterno,so.apmaterno,suc.nombre,a.precio FROM pedidoslines l INNER JOIN articulo a ON (l.empresano = a.empresano and l.productono = a.codigoarticulo and l.catalogo = a.catalogo) INNER JOIN asociado so ON (so.empresano=1 and so.asociadono = %s) INNER JOIN sucursal suc ON (suc.empresano=1 and suc.sucursalno = %s) WHERE l.pedido = %s;",(pedido_header[5],pedido_header[4],p_num_pedido))
		pedido_detalle = dictfetchall(cursor)
		# la siguiente variable  se asigna para ser pasada a la rutina que 
		# imprimira la nota de credito ( en caso de que exista )


		
		if pedido_detalle is not(None):

			for elem in  pedido_detalle:
				NotaCredito = elem['NoNotaCreditoPorPedido']
				if elem['talla'] != 'NE':
					talla = elem['talla']
				else:
					talla = elem['Observaciones']
				tot_art = tot_art + 1


		cursor.execute("SELECT usuario from usuarios where usuariono=%s;",[pedido_header[3]])
		
		usuario = cursor.fetchone()

		mensaje=""
		
		if usuario is None:
			usuario=['ninguno']
		if (not pedido_header or not pedido_detalle):
			mensaje = "No se encontro informacion del pedido !"

	except DatabaseError as e:
		print "Ocurrio de base datos"
		print e
		
		mensaje = "Ocurrio un error de acceso a la bd. Inf. tecnica: "
	except Exception as e:
		mensaje = "Ocurrio un error desconocido. Inf. tecnica: "
		print "error desconocido: "
		print e
		
	cursor.close()

	'''COMIENZA IMPRESION EN PDF'''
	
	linea = 2400
	
	
    # Create a file-like buffer to receive PDF data.
	buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
	pagesize = (8.5*inch, 33*inch)
	p = canvas.Canvas(buffer,pagesize=pagesize)
	#p.setPageSize("inch")
	p.translate(0.0,0.0)
	p.setFont("Helvetica",10)
	#p.drawString(1,linea,inicializa_imp)
	

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
	#p.drawString(20,810,mensaje)

	if (pedido_header and pedido_detalle and usuario):
		p.drawString(50,linea, request.session['cnf_razon_social'])
		linea -=20
		p.drawString(60,linea, 'SUC. '+request.session['sucursal_nombre'])
		linea -=20
		p.setFont("Helvetica",12)
		p.drawString(20,linea, "*** PEDIDO NUM."+p_num_pedido+" ***")
		linea -=20
		p.setFont("Helvetica",10)
		p.drawString(20,linea,request.session['sucursal_direccion'])
		linea -= 10
		p.drawString(20,linea,"COL. "+request.session['sucursal_colonia'])
		linea -= 10
		p.drawString(20,linea,request.session['sucursal_ciudad']+", "+request.session['sucursal_estado'])
		linea -= 20
		p.drawString(20,linea,pedido_header[1].strftime("%d-%m-%Y")+' '+pedido_header[2].strftime("%H:%M:%S")+' '+'Tel '+str(request.session['sucursal_telefono']))
		#p.drawString(100,linea,)
		linea -= 10
		p.drawString(20,linea,"CREADO POR: ")
		#p.drawString(100,linea,request.user.username)
		p.drawString(100,linea,usuario[0])
		linea -= 20
		p.drawString(20,linea,"SOCIO NUM: ")
		type(pedido_header[5])
		p.drawString(100,linea,str(pedido_header[5]))
		linea -= 10
		
		var_socio = datos_socio[0]+" "+datos_socio[1]+" "+datos_socio[2]

		p.drawString(20,linea,var_socio[0:28])
		linea -= 10

		p.drawString(20,linea,"--------------------------------------------------")
		
		linea -= 10
		p.drawString(20,linea,"Descrpcion")
		p.drawString(130,linea,"Precio")
		linea -= 10
		p.drawString(20,linea,"--------------------------------------------------")
		linea -= 10
		#p.setFont("Helvetica",8)
		i,paso=1,linea-10
		monto_total = 0.0
		for elemento in pedido_detalle:
			print(paso)
			if elemento['talla'] != 'NE':
				talla = elemento['talla']
			else:
				talla = elemento['Observaciones']
			
			if datos_socio[3] != 1:
				precio_imprimir = elemento['subtotal']
			else:
				precio_imprimir = elemento['precio']	
			monto_total += float(precio_imprimir)
			#pdb.set_trace()
			p.drawString(20,paso,elemento['pagina']+' '+elemento['idmarca']+' '+elemento['idestilo']) 
			p.drawString(20,paso-10,elemento['idcolor'][0:7]+' '+talla)
			p.drawString(130,paso-10,'$ '+str(precio_imprimir))
			paso -= 30
			
		p.drawString(20,paso-10,"Total ==>")
		p.drawString(130,paso-10,'$ '+str(round(monto_total,0)))
		
		p.drawString(20,paso-20,'Ctd. articulos => ')
		p.drawString(130,paso-20,str(tot_art))

		p.drawString(20,paso-50,"Para sugerencias o quejas")
		p.drawString(20,paso-60,"llame al 867 132 9697")
		linea = paso-120
	#pdb.set_trace()	
	if NotaCredito != 0:
		imprime_documento(NotaCredito,'Credito',False,request.session['cnf_razon_social'],request.session['cnf_direccion'],request.session['cnf_colonia'],request.session['cnf_ciudad'],request.session['cnf_estado'],p,buffer,response,True,linea,request)
		return response	
	else:

	# Close the PDF object cleanly, and we're done.
		p.showPage()
		p.save()


		pdf = buffer.getvalue()
		buffer.close()

		response.write(pdf)

    # FileResponse sets the Content-Disposition header so that browsers
	    # present the option to save the file.
	    #return FileResponse(buffer, as_attachment=True,filename='hello.pdf')
		return response



def imprime_documento(p_num_documento=0,
	p_tipo_documento='',
	p_notacreditopordev=False,
	p_cnf_razon_social='',
	p_cnf_direccion='',
	p_cnf_colonia='',
	p_cnf_ciudad='',
	p_cnf_estado='',
	p=None,
	buffer = None,
	response= None,
	llamada_interna=False,
	linea=800,
	request=None,):
	#inicializa_imp = bytes(b'\x1b\x40')
	#inputHex = binascii.unhexlify("1b\40")
	

	#pdb.set_trace()
	if request is not None:
		cnf_dias_vigencia_credito = request.session['cnf_dias_vigencia_credito']	
		sucursal_activa = request.session['sucursal_activa']
		

		sucursal_nombre = request.session['sucursal_nombre']
		sucursal_direccion = request.session['sucursal_direccion']
		sucursal_colonia =	request.session['sucursal_colonia']
		sucursal_ciudad =	request.session['sucursal_ciudad']
		sucursal_estado = request.session['sucursal_estado']
		sucursal_telefono =	request.session['sucursal_telefono']


		

	#pdb.set_trace()
	
	# se encodifica como 'latin_1' ya que viene como unicode.

	#p_num_documento = p_num_documento.encode('latin_1')
	#p_tipo_documento = p_tipo_documento.encode('latin_1')
	
	if not llamada_interna:
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'
	
			
	
	#Trae informacion del pedido.
	cursor =  connection.cursor()
	
	documento,usuario = None,None
	e = None
	mensaje=""
	try:

		# trae documento
		cursor.execute("SELECT asociado,fechacreacion,horacreacion,`UsuarioQueCreoDcto.`,concepto,monto,saldo,descuentoaplicado,vtadecatalogo,cancelado,pagoaplicadoaremisionno,lo_recibido,venta,idsucursal from documentos where empresano=1 and nodocto=%s and tipodedocumento=%s;",[p_num_documento,p_tipo_documento])
		#cursor.execute("SELECT asociado,fechacreacion,horacreacion,`UsuarioQueCreoDcto.`,concepto,monto,saldo,descuentoaplicado,vtadecatalogo,cancelado,pagoaplicadoaremisionno,lo_recibido,venta,idsucursal from documentos where empresano=1 and nodocto=%s;",[p_num_documento,])

		documento = cursor.fetchone()
		
					# trae socio
		cursor.execute("SELECT nombre,appaterno,apmaterno from asociado where asociadono=%s;",[documento[0]])
		socio = cursor.fetchone()
		# trae ped


		#cursor.execute("SELECT PedidoNo,FechaPedido,HoraPedido,UsuarioCrea,idSucursal,AsociadoNo,vtatotal FROM pedidosheader where EmpresaNo=1 and PedidoNo = %s;",[p_num_pedido])
		#pedido_header = cursor.fetchone()
		
		# Si el documento es remision o credito y hay credito por dev busca el detalle
		if p_tipo_documento=='Remision':
			
			cursor.execute("SELECT l.precio,l.NoNotaCreditoPorPedido,l.Observaciones,l.Status,a.pagina,a.idmarca,a.idestilo,a.idcolor,a.talla,a.catalogo,so.nombre,so.appaterno,so.apmaterno,suc.nombre FROM pedidoslines l INNER JOIN articulo a ON (l.empresano = a.empresano and l.productono = a.codigoarticulo and l.catalogo = a.catalogo) INNER JOIN asociado so ON (so.empresano=1 and so.asociadono = %s) INNER JOIN sucursal suc ON (suc.empresano=1 and suc.sucursalno = %s) WHERE l.RemisionNo = %s;",(documento[0],documento[13],p_num_documento))

		else:
			if p_tipo_documento == 'Credito':

				if p_notacreditopordev:
				
					cursor.execute("SELECT l.precio,l.NoNotaCreditoPorPedido,l.Observaciones,l.Status,a.pagina,a.idmarca,a.idestilo,a.idcolor,a.talla,a.catalogo,so.nombre,so.appaterno,so.apmaterno,suc.nombre FROM pedidoslines l INNER JOIN articulo a ON (l.empresano = a.empresano and l.productono = a.codigoarticulo and l.catalogo = a.catalogo) INNER JOIN asociado so ON (so.empresano=1 and so.asociadono = %s) INNER JOIN sucursal suc ON (suc.empresano=1 and suc.sucursalno = %s) WHERE l.NoNotaCreditoPorDevolucion = %s;",(documento[0],documento[13],p_num_documento))
				
				else:

					cursor.execute("SELECT l.precio,l.NoNotaCreditoPorPedido,l.Observaciones,l.Status,a.pagina,a.idmarca,a.idestilo,a.idcolor,a.talla,a.catalogo,so.nombre,so.appaterno,so.apmaterno,suc.nombre FROM pedidoslines l INNER JOIN articulo a ON (l.empresano = a.empresano and l.productono = a.codigoarticulo and l.catalogo = a.catalogo) INNER JOIN asociado so ON (so.empresano=1 and so.asociadono = %s) INNER JOIN sucursal suc ON (suc.empresano=1 and suc.sucursalno = %s) WHERE l.NoNotaCreditoPorPedido = %s;",(documento[0],documento[13],p_num_documento))

		pedido_detalle = dictfetchall(cursor)
		
		cursor.execute("SELECT usuario from usuarios where usuariono=%s;",[documento[3]])
		
		usuario = cursor.fetchone()

		
		
		if usuario is None:
			usuario=['ninguno']
		
		
	except DatabaseError as e:
		print "Ocurrio de base datos"
		print e
		
		mensaje = "Ocurrio un error de acceso a la bd. Inf. tecnica: "
	except Exception as e:
		print "error desconocido ! ", e
		
	cursor.close()
	
    # Create a file-like buffer to receive PDF data.
	if not llamada_interna:
		buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
		p = canvas.Canvas(buffer)

	
	p.setFont("Helvetica",10)

	
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
	#p.drawString(1,linea,inicializa_imp)
	p.drawString(20,linea,mensaje)

	if (documento and usuario and not e):

		# Convierte la fechacreacion a formato adecuado y le agrega
		# los dias de vigencia de credito
		
		
		fechaFinVigenciaCredito = documento[1] + timedelta(days=cnf_dias_vigencia_credito)
		
		p.drawString(60,linea, p_cnf_razon_social)
		linea -=20
		p.drawString(60,linea," SUC. "+sucursal_nombre)
		linea -=20
		p.setFont("Helvetica",12)
		p.drawString(20,linea,"** Nota de "+p_tipo_documento+" "+str(p_num_documento)+" **")
		p.setFont("Helvetica",8)
		linea -= 20
		p.drawString(20,linea,sucursal_direccion)
		linea -= 10
		p.drawString(20,linea,"COL. "+sucursal_colonia)
		linea -= 10
		p.drawString(20,linea,sucursal_ciudad+", "+sucursal_estado)
		linea -= 15
		#p.setFont("Helvetica",6)
		p.drawString(20,linea,"CREADO POR: ")
		#p.drawString(100,linea,request.user.username)
		p.drawString(100,linea,usuario[0])
		linea -= 15
		p.drawString(20,linea,"SOCIO NUM: ")
		p.drawString(100,linea,str(documento[0]))


		linea -= 10
		
		if socio[0] !='':
			p.drawString(20,linea,socio[0].strip()+' '+socio[1].strip()+' '+socio[2].strip())
			linea -= 15

		p.drawString(20,linea,documento[1].strftime("%d-%m-%Y")+' '+documento[2].strftime("%H:%M:%S")+' Tel '+str(sucursal_telefono))
		#p.drawString(100,linea,)
		linea -= 10
	 	
		p.setFont("Helvetica",8)
		p.drawString(20,linea,"--------------------------------------------------")
		linea -= 10

		p.drawString(20,linea,"Concepto: ")
		linea -= 10
		p.drawString(20,linea,documento[4][slice(0,40,None)])
		linea -= 10

		p.drawString(20,linea,"Monto: $ "+str(documento[5]))
		linea -= 15
		
		if documento[4][slice(0,43,None)]=="Credito generado por concepto de devolucion":
			p.drawString(20,linea,"Productos devueltos:")
			p.drawString(130,linea,"")
			
			linea -=10
			p.drawString(20,linea,"--------------------------------------------------")
			linea -= 10
			
		p.setFont("Helvetica",8)
		i,paso = 1,linea
		if pedido_detalle and (documento[4][slice(0,43,None)].find("Anticipo a pedido")==-1):# Iprime el detalle siempre que no sea un anticipo a pedido.

			for elemento in pedido_detalle:
				
				p.drawString(20,paso,(elemento['pagina']+' '+elemento['idmarca']+' '+elemento['idestilo']).lower()) 
				p.drawString(20,paso-10,(elemento['idcolor']+' '+elemento['talla']).lower())
				p.drawString(130,paso-10,('$ '+str(elemento['precio'])).lower())
				paso -= 20
		
		#paso = linea
		paso -= 30
		p.drawString(20,paso,"Valido hasta el "+ fechaFinVigenciaCredito.strftime('%d-%m-%Y'))
		paso -=10
		p.drawString(20,paso,"es INDISPENSABLE presentarlo en su compra.")
		paso -= 20

		p.drawString(20,paso,"Para sugerencias o quejas llame")
		paso-=10
		p.drawString(20,paso,"al 867 132 9697")

		paso -=10

		p.setFont("Helvetica",8)
		#p.drawString(20,paso-10,"Total ==>")
		#p.drawString(130,paso-10,str(pedido_header[6]))

	# Close the PDF object cleanly, and we're done.
	
	'''if llamada_interna:

		p.showPage()
	
		p.save()

		pdf = buffer.getvalue()
		buffer.close()

		response.write(pdf)
		return response
	else:

		return	'''
	p.showPage()
	
	p.save()

	pdf = buffer.getvalue()
	buffer.close()

	response.write(pdf)
	return response


# **************** COLOCACIONES **********************************

@login_required(login_url = "/pedidos/acceso/")
def colocaciones(request):
	#import pdb; pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	
	mensaje = " "

	# elimina cualquier registro de la session.
	session_id = request.session.session_key
	# Asigna is_staff para validacines
	is_staff = request.session['is_staff']

	"""cursor = connection.cursor()
	cursor.execute("DELETE FROM pedidos_pedidos_tmp where session_key= %s;",[session_id])	
	
	cursor.close()"""


	#for key,value in pr_dict.items():
	#	print key,value 
	
	 
	if request.method =='POST':
		
		form = ColocacionesForm(request.POST)
		
		if form.is_valid():
			
			
			

			mensaje = "ok" #+ articulo.codigoarticulo
			return render(request,'pedidos/colocaciones.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})
		else:	
			
			mensaje = "Error en la forma"
			return render(request,'pedidos/colocaciones.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})

	form = ColocacionesForm()
	mensaje = ""
	return render(request,'pedidos/colocaciones.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})	


#@ensure_csrf_cookie
def muestra_colocaciones(request):

	#pdb.set_trace()	
		
	#if request.method == 'GET':
	#if request.is_ajax() and request.method == 'GET':

	proveedor = request.GET['proveedor']
	try:
		almacen = request.GET['almacen']
	except:
		return HttpResponse("Requiere ingresar el almacen, la lista de almacenes se refresca al cambiar de proveedor !")
		
	tipo_consulta = request.GET['tipo_consulta']
	ordenado_por = request.GET['ordenado_por']
	
	fechainicial = request.GET['fechainicial']
	fechafinal = request.GET['fechafinal']
	

	# Convierte tipo_consulta a un formato legible por python, ya que entra como unicode
	tipo_consulta = tipo_consulta.encode('latin_1')
	tipo_consulta = int(tipo_consulta)

	# Convierte el tipo de ordenamiento a entero
	ordenado_por = ordenado_por.encode('latin_1')
	ordenado_por = int(ordenado_por)

	try:
		# Igualmente, las fechas se convierten a un formato adecuado para ser grabadas en la BD
		fechainicial = datetime.strptime(fechainicial, "%d/%m/%Y").date()
		fechafinal = datetime.strptime(fechafinal, "%d/%m/%Y").date()
	except ValueError:

		error_msg="Fechas con formato incorrecto, use dd/mm/AAAA"
		return render(request,'pedidos/error.html',{'error_msg':error_msg},)

	hay_cancelados = False
	cursor = connection.cursor()

	try:
		# Cuenta articulos encontrados ya en el almacen.
		#cursor.execute("SELECT COUNT(*) FROM pedidos_encontrados e INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) on (a.EmpresaNo=1 and e.ProductoNo=a.CodigoArticulo and e.Catalogo=a.Catalogo)  WHERE e.empresano=1 and e.encontrado='S' and  trim(e.observaciones)<>'Cancelado' and  e.id_cierre=0 and a.idproveedor=%s and e.BodegaEncontro=%s;",(proveedor,almacen))
		#cursor.execute("SELECT COUNT(*) FROM pedidos_encontrados e INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) on (a.EmpresaNo=1 and e.ProductoNo=a.CodigoArticulo and e.Catalogo=a.Catalogo)  WHERE e.empresano=1 and e.encontrado='S' and  trim(e.observaciones)<>'Cancelado' and  e.id_cierre=0 and a.idproveedor=%s and e.BodegaEncontro=%s;",(proveedor,almacen))
		
		cursor.execute("SELECT razonsocial from proveedor where proveedorno=%s;",(proveedor))
		prov_nombre=cursor.fetchone()

		cursor.execute("SELECT razonsocial from almacen where proveedorno=%s and almacen=%s;",(proveedor,almacen,))
		almacen_nombre=cursor.fetchone()

		cursor.execute("SELECT COUNT(*) FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo)  WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY a.idestilo;",(proveedor,almacen))

		encontrados = cursor.fetchone()
		reg_encontrados = encontrados[0]
		
		# Detecta algun cancelado en el conjunto.
		
		cursor.execute("SELECT COUNT(*) FROM pedidos_encontrados e INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) on (a.EmpresaNo=1 and e.ProductoNo=a.CodigoArticulo and e.Catalogo=a.Catalogo) WHERE e.empresano=1 and e.observaciones ='Cancelado' and  e.id_cierre=0 and e.BodegaEncontro=%s and a.idProveedor=%s;",(almacen,proveedor))
		encontrados = cursor.fetchone()
		reg_cancelados = encontrados[0]
		#reg_cancelados = 1




		# '1','Nuevos'),('2','Por Confirmar'),('3','Encontrados'),('4','Colocados'),('5','Descontinuados'),('6','Cancelados'))
		# PEDIDOS NUEVOS
		if tipo_consulta == 1: 

			cursor.execute("SELECT count(*) as total_registros FROM pedidoslines l LEFT JOIN  pedidos_encontrados e on ( e.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo = 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo = 1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE l.empresano = 1 and a.idProveedor= %s and l.Status='Por Confirmar'  and (e.encontrado='' or e.encontrado='P' or e.encontrado IS NULL);",(proveedor,))
			total_registros =cursor.fetchone()
			tot_reg = total_registros[0]

			# Ejecuta segun ordenamiento solicitado (1= estilo, 2=socio,3=fechapedido )
			if ordenado_por == 1:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal, l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidoslines l LEFT JOIN  pedidos_encontrados e on ( e.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo = 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo = 1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE l.empresano = 1 and a.idProveedor= %s and l.Status='Por Confirmar'  and (e.encontrado='' or e.encontrado='P' or e.encontrado IS NULL) ORDER BY a.idestilo;",(proveedor,))
			elif ordenado_por == 2:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal, l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidoslines l LEFT JOIN  pedidos_encontrados e on ( e.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo = 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo = 1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE l.empresano = 1 and a.idProveedor= %s and l.Status='Por Confirmar'  and (e.encontrado='' or e.encontrado='P' or e.encontrado IS NULL) ORDER BY p.asociadono;",(proveedor,))
			else:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal, l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidoslines l LEFT JOIN  pedidos_encontrados e on ( e.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo = 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo = 1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE l.empresano = 1 and a.idProveedor= %s and l.Status='Por Confirmar'  and (e.encontrado='' or e.encontrado='P' or e.encontrado IS NULL) ORDER BY p.FechaPedido;",(proveedor,))

		# PEDIODS POR CONFIRMAR
		elif tipo_consulta == 2:

			cursor.execute("SELECT count(*) as total_registros FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo = 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano =1 and a.idProveedor=%s and e.encontrado='N'   and l.Status='Por Confirmar'  and p.FechaPedido>=%s and p.FechaPedido<=%s;",(proveedor,fechainicial,fechafinal))
			total_registros = cursor.fetchone()
			tot_reg = total_registros[0]

			# Ejecuta segun ordenamiento solicitado (1= estilo, 2=socio,3=fechapedido )

			if ordenado_por == 1:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo = 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano =1 and a.idProveedor=%s and e.encontrado='N'   and l.Status='Por Confirmar'  and p.FechaPedido>=%s and p.FechaPedido<=%s ORDER BY a.idestilo;",(proveedor,fechainicial,fechafinal))
			elif ordenado_por == 2:	
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo = 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano =1 and a.idProveedor=%s and e.encontrado='N'   and l.Status='Por Confirmar'  and p.FechaPedido>=%s and p.FechaPedido<=%s ORDER BY p.asociadono;",(proveedor,fechainicial,fechafinal))
			else:					
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo = 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano =1 and a.idProveedor=%s and e.encontrado='N'   and l.Status='Por Confirmar'  and p.FechaPedido>=%s and p.FechaPedido<=%s ORDER BY p.FechaPedido;",(proveedor,fechainicial,fechafinal))
	
		# PEDIDOS ENCONTRADOS		
		elif tipo_consulta == 3:

			cursor.execute("SELECT count(*) as total_registros FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY a.idestilo;",(proveedor,almacen))
			total_registros =cursor.fetchone()
			tot_reg = total_registros[0]

			# Ejecuta segun ordenamiento solicitado (1= estilo, 2=socio,3=fechapedido )

			if ordenado_por == 1:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY a.idestilo;",(proveedor,almacen))
			elif ordenado_por == 2:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY p.asociadono;",(proveedor,almacen))
			else:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY p.FechaPedido;",(proveedor,almacen))

		# COLOCADOS		
		elif tipo_consulta == 4:

			cursor.execute("SELECT count(*) as total_registros FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and  e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo= 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano =1 and a.idProveedor=%s and e.encontrado='X'   and ( (l.Status='Por Confirmar' ) )  and p.FechaPedido>=%s and p.FechaPedido<=%s and e.BodegaEncontro=%s ORDER BY a.idestilo;",(proveedor,fechainicial,fechafinal,almacen,))
			total_registros = cursor.fetchone()
			tot_reg = total_registros[0]


			# Ejecuta segun ordenamiento solicitado (1= estilo, 2=socio,3=fechapedido )

			if ordenado_por == 1:			
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and  e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo= 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano =1 and a.idProveedor=%s and e.encontrado='X'   and ( (l.Status='Por Confirmar' ) )  and p.FechaPedido>=%s and p.FechaPedido<=%s and e.BodegaEncontro=%s ORDER BY a.idestilo;",(proveedor,fechainicial,fechafinal,almacen,))
			elif ordenado_por == 2:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and  e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo= 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano =1 and a.idProveedor=%s and e.encontrado='X'   and ( (l.Status='Por Confirmar' ) )  and p.FechaPedido>=%s and p.FechaPedido<=%s and e.BodegaEncontro=%s ORDER BY p.asociadono;",(proveedor,fechainicial,fechafinal,almacen,))
			else:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and  e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo= 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano =1 and a.idProveedor=%s and e.encontrado='X'   and ( (l.Status='Por Confirmar' ) )  and p.FechaPedido>=%s and p.FechaPedido<=%s and e.BodegaEncontro=%s ORDER BY p.FechaPedido;",(proveedor,fechainicial,fechafinal,almacen,))
	

		# DESCONTINUADOS		
		elif tipo_consulta == 5:
			# Ejecuta segun ordenamiento solicitado (1= estilo, 2=socio,3=fechapedido )
			cursor.execute("SELECT count(*) as total_registros FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo= 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON  (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s and e.encontrado='D'    and p.FechaPedido>=%s and p.FechaPedido<=%s ORDER BY a.idestilo;",(proveedor,fechainicial,fechafinal))
			total_registros = cursor.fetchone()
			tot_reg = total_registros[0]

			if ordenado_por == 1:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo= 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON  (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s and e.encontrado='D'    and p.FechaPedido>=%s and p.FechaPedido<=%s ORDER BY a.idestilo;",(proveedor,fechainicial,fechafinal))
			elif ordenado_por == 2:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo= 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON  (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s and e.encontrado='D'    and p.FechaPedido>=%s and p.FechaPedido<=%s ORDER BY p.asociadono;",(proveedor,fechainicial,fechafinal))

			else:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo= 1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (`ind_emp_prov_cat_codpro`) ON  (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s and e.encontrado='D'    and p.FechaPedido>=%s and p.FechaPedido<=%s ORDER BY p.FechaPedido;",(proveedor,fechainicial,fechafinal))

		# CANCELADOS

		else:
			
			#cursor.execute("SELECT count(*) as total_registros FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY a.idestilo;",(proveedor,almacen))
			cursor.execute("SELECT count(*) as total_registros FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) inner join pedidos_status_fechas psf on (e.empresano=psf.empresano and e.pedido=psf.pedido and e.productono=psf.productono and e.catalogo=psf.catalogo and e.nolinea=psf.nolinea and psf.status='Encontrado') WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s and l.Status='Cancelado' and e.id_cierre=0  and psf.fechamvto >=%s and psf.fechamvto<=%s;",(proveedor,almacen,fechainicial,fechafinal))

			total_registros =cursor.fetchone()
			tot_reg = total_registros[0]

			# Ejecuta segun ordenamiento solicitado (1= estilo, 2=socio,3=fechapedido )

			if ordenado_por == 1:
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) inner join pedidos_status_fechas psf on (e.empresano=psf.empresano and e.pedido=psf.pedido and e.productono=psf.productono and e.catalogo=psf.catalogo and e.nolinea=psf.nolinea and psf.status='Encontrado') WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s and l.Status='Cancelado' and e.id_cierre=0  and psf.fechamvto >=%s and psf.fechamvto<=%s ORDER BY a.idestilo;",(proveedor,almacen,fechainicial,fechafinal))
			elif ordenado_por == 2:
				#cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY p.asociadono;",(proveedor,almacen))
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) inner join pedidos_status_fechas psf on (e.empresano=psf.empresano and e.pedido=psf.pedido and e.productono=psf.productono and e.catalogo=psf.catalogo and e.nolinea=psf.nolinea and psf.status='Encontrado') WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s and l.Status='Cancelado' and e.id_cierre=0  and psf.fechamvto >=%s and psf.fechamvto<=%s ORDER BY p.asociadono;",(proveedor,almacen,fechainicial,fechafinal))

			else:
				#cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY p.FechaPedido;",(proveedor,almacen))
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones as encon_obser,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status,CONCAT(aso.nombre,' ',aso.ApPaterno,' ',aso.ApMaterno) as nombre_socio,n.observaciones as notas FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN asociado as aso on (aso.asociadono=p.asociadono) left join pedidos_notas n on (e.empresano=n.empresano and e.pedido=n.pedido and e.productono=n.productono and e.catalogo=n.catalogo and e.nolinea=n.nolinea) inner join pedidos_status_fechas psf on (e.empresano=psf.empresano and e.pedido=psf.pedido and e.productono=psf.productono and e.catalogo=psf.catalogo and e.nolinea=psf.nolinea and psf.status='Encontrado') WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s and l.Status='Cancelado' and e.id_cierre=0  and psf.fechamvto >=%s and psf.fechamvto<=%s ORDER BY p.FechaPedido;",(proveedor,almacen,fechainicial,fechafinal))

	except DatabaseError as e:

		print "Error en base de datos"
		print e
		mensaje ="Se  produjo un error al acceder a base de datos"

	try:

		registros = dictfetchall(cursor)
		if tipo_consulta != 6:
			mensaje ="Lista de articulos  a colocar:"
		else:
			mensaje ="Articulos cancelados que previamente fueron encontrados en este almacen:"
		cursor.close()
		return render(request,'pedidos/colocaciones_detalle.html',{'registros':registros,'mensaje':mensaje,'reg_encontrados':reg_encontrados,'almacen':almacen,'reg_cancelados':reg_cancelados,'tipo_consulta':tipo_consulta,'prov_nombre':prov_nombre[0],'almacen_nombre':almacen_nombre[0],'tot_reg':tot_reg,})
	except:
		registros ={}
		mensaje = "Registros no encontrados para esta consulta !"
		cursor.close()
		return render(request,'pedidos/colocaciones_detalle.html',{'registros':registros,'mensaje':mensaje,})
	#return render(request,'pedidos/colocaciones_detalle.html',{'registros':registros,'mensaje':mensaje,'reg_encontrados':reg_encontrados,'almacen':almacen,'reg_cancelados':reg_cancelados,'tipo_consulta':tipo_consulta,})

	"""data = serializers.serialize('json', registros)
	return HttpResponse(data, mimetype='application/json')"""	

	#return HttpResponse(json.dumps(data),content_type='application/json')


	 	

'''
def muestra_colocaciones(request):

	pdb.set_trace()	
	if request.method == 'GET':
	#if request.is_ajax() and request.method == 'GET':
		proveedor = request.GET['proveedor']
		almacen = request.GET['almacen']
		tipo_consulta = request.GET['tipo_consulta']
		
		fechainicial = request.GET['fechainicial']
		fechafinal = request.GET['fechafinal']

		# Convierte tipo_consulta a un formato legible por python, ya que entra como unicode
		tipo_consulta = tipo_consulta.encode('latin_1')
		tipo_consulta = int(tipo_consulta)
		# Igualmente, las fechas se convierten a un formato adecuado para ser grabadas en la BD
		fechainicial = datetime.strptime(fechainicial, "%m/%d/%Y").date()
		fechafinal = datetime.strptime(fechafinal, "%m/%d/%Y").date()

		cursor = connection.cursor()

		try:
			if tipo_consulta == 1: 
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal, l.Observaciones FROM pedidoslines l LEFT JOIN  pedidos_encontrados e on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo)  INNER JOIN pedidos_status_fechas f on  ( e.EmpresaNo=f.EmpresaNo and e.Pedido=f.Pedido and e.ProductoNo=f.ProductoNo and e.Catalogo=f.catalogo and e.NoLinea=f.NoLinea) WHERE e.empresano = 1 and a.idProveedor= %s and  p.FechaPedido>=%s and p.FechaPedido<=%s   and l.Status='Por Confirmar'  and f.Status='Por Confirmar' and  (trim(e.encontrado)='' or  trim(e.encontrado)='P' or e.encontrado IS NULL);",(proveedor,fechainicial,fechafinal))
			else:
				if tipo_consulta == 2:
						cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.Nolinea,e.BodegaEncontro,e.encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal,l.Observaciones FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN pedidos_status_fechas f on  ( e.EmpresaNo=f.EmpresaNo and e.Pedido=f.Pedido and e.ProductoNo=f.ProductoNo and e.Catalogo=f.catalogo and e.NoLinea=f.NoLinea) WHERE e.empresano =1 and a.idProveedor=%s and e.encontrado='N'   and (l.Status='Por Confirmar' and f.Status='Por Confirmar') and p.FechaPedido>=%s and p.FechaPedido<=%s;",(proveedor,fechainicial,fechafinal))
				else:
					if tipo_consulta == 3:
						cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal,l.Observaciones FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN pedidos_status_fechas f on  ( e.EmpresaNo=f.EmpresaNo and e.Pedido=f.Pedido and e.ProductoNo=f.ProductoNo and e.Catalogo=f.catalogo and e.NoLinea=f.NoLinea and trim(f.Status='Encontrado')) WHERE (e.empresano=1 and a.idProveedor=%s and e.BodegaEncontro=%s and trim(l.Status)='Encontrado' and e.id_cierre=0) or (e.empresano=1 and a.idProveedor=%s and e.BodegaEncontro=%s and  trim(l.Status)='Cancelado' and e.encontrado='S' and trim(e.observaciones='Cancelado' )  and e.id_cierre=0 );",(proveedor,almacen,proveedor,almacen))
					else:
						if tipo_consulta == 4:
							cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.Nolinea,e.BodegaEncontro,e.encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal,l.Observaciones FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN pedidos_status_fechas f on  ( e.EmpresaNo=f.EmpresaNo and e.Pedido=f.Pedido and e.ProductoNo=f.ProductoNo and e.Catalogo=f.catalogo and e.NoLinea=f.NoLinea) WHERE a.empresano =1 and a.idProveedor=%s and e.encontrado='X'   and ( (l.Status='Por Confirmar' and f.Status='Por Confirmar') or (l.Status='Cancelado' and f.status='Cancelado') )  and p.FechaPedido>=%s and p.FechaPedido<=%s and e.BodegaEncontro=%s;",(proveedor,fechainicial,fechafinal,almacen,))
						else:
							cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.Nolinea,e.BodegaEncontro,e.encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal,l.Observaciones FROM pedidos_encontrados e INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.Nolinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN pedidos_status_fechas f on  ( e.EmpresaNo=f.EmpresaNo and e.Pedido=f.Pedido and e.ProductoNo=f.ProductoNo and e.Catalogo=f.catalogo and e.NoLinea=f.NoLinea) WHERE a.empresano=1 and a.idProveedor=%s and e.encontrado='D'    and p.FechaPedido>=%s and p.FechaPedido<=%s;",(proveedor,fechainicial,fechafinal))
		except DatabaseError as e:

			print "Error en base de datos"
			print e

		if cursor:

			registros = dictfetchall(cursor)
		else:
			registros ={}
		cursor.close()
		return render(request,'pedidos/colocaciones_detalle.html',{'registros':registros,'mensaje':mensaje,})	

		"""data = serializers.serialize('json', registros)
		return HttpResponse(data, mimetype='application/json')"""	

		#return HttpResponse(json.dumps(data),content_type='application/json')
	return '''

# PROCESAMIENTO DE COLOCACIONES

#@ensure_csrf_cookie
def procesar_colocaciones(request):
	
	#pdb.set_trace()
	if request.is_ajax()  and request.method == 'POST':
		# Pasa a una variable la tabla  recibida en json string
		TableData = request.POST.get('TableData')
		
		# carga la tabla ( la prepara con el formato de lista adecuado para leerla)
		datos = json.loads(TableData)

		# Se define una lista para guardar los elementos con error.

		estilos_con_error = []


		try:

			psw_paso =  request.POST.get('psw_paso') # toma el id  de confirmacion del empleado que captura 
		
			fecha_probable = request.POST.get('fecha_probable')
			proveedor_nombre = request.POST.get('proveedor_nombre')
			almacen_nombre = request.POST.get('almacen_nombre')


			
		except:
			print "error en usr_id"
			pass
			#HttpResponse('div class="alert alert-warning" role="alert"><strong>Operacion fallida !</strong> Hubo un error de sesion al procesar, la transacción no pudo ser completada, cierre su navegador, ingrese nuevamente e intente otra vez !</div>')
		





		almacen = request.POST.get('almacen')
		almacen = almacen.encode('latin_1')

		cursor = connection.cursor()

		''' INICIALIZACION DE VARIABLES '''

		pedidos_cambiados = 0 # inicializa contador de pedidos que sufrieron cambios entre la lectura inicial y el commit.
		
		nuevo_status_pedido = '' # variable que servira para  guardar el status de pedido segun se vayan cumpliendo condiciones,
							# posteriomente se utilizara par actualizar el status del pedido en pedidoslines y pedidos_status_confirmacion.

		error = False # Si existe algun error de base de datos o de otro tipo se pondra en True

		''' FIN DE INCIALIZACION DE VARIABLES '''


		# Se convierte la fecha de hoy a formatos manejables para insertarlos en el registro.
		hoy = datetime.now()
		fecha_hoy = hoy.strftime("%Y-%m-%d")
		hora_hoy = hoy.strftime("%H:%M:%S") 



		cursor.execute("SELECT usuariono from usr_extend WHERE pass_paso=%s;",(psw_paso,))
		usr_existente = cursor.fetchone()
		usr_existente = usr_existente[0]
		capturista = usr_existente


        # Recupera cada diccionario y extrae los valores de la llave a buscar.
		for j in datos:
			
			pedido = j.get("Pedido")

			productono = j.get('ProductoNo').strip()
			catalogo =j.get('Catalogo').strip()
			nolinea = j.get('Nolinea')
			encontrado = j.get('encontrado').strip()
			#version_original_pedidos_encontrados = j.get('ver_ant_encontrado').encode('latin_1').strip() # Traemos version anterior del registro pedidos_encontrados, para esto usamos el campo 'encontrado' con el que haremos una  futura comparacion con una nueva lectura al mismo para ver si cambio
			#version_original_pedidos_lines = j.get('status').encode('latin_1').strip() # Traemos version anterior del registro pedidoslines, para esto usamos el campo 'status' con el que hacemos una comparacion con una nueva lectura al mismo para ver si cambio
			version_original_pedidos_encontrados = j.get('ver_ant_encontrado').strip() # Traemos version anterior del registro pedidos_encontrados, para esto usamos el campo 'encontrado' con el que haremos una  futura comparacion con una nueva lectura al mismo para ver si cambio
			version_original_pedidos_lines = j.get('status').strip() # Traemos version anterior del registro pedidoslines, para esto usamos el campo 'status' con el que hacemos una comparacion con una nueva lectura al mismo para ver si cambio

			notas = j.get('notas').strip()
			notas = notas.encode('latin_1')

			if encontrado != '':

				# Comienza acceso a BD.

				
				try:
					
					# verifica version actual pedidos_encontrados y de una vez traemos id_cierre que se usara mas adelante
					cursor.execute("SELECT encontrado,id_cierre from pedidos_encontrados WHERE EmpresaNo=1 and Pedido=%s and  ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(pedido,productono,catalogo,nolinea))
					registro = cursor.fetchone()

					# Creea variable version_actual e id_cierre para pedidos_encontrados
					version_actual_pedidos_encontrados=registro[0].strip()
					id_cierre = registro[1]

					# verifica version actual pedidoslines y de una vez se trae el estatus actual para ser mostrado en caso de que la version actual difiera de la anterior
					cursor.execute("SELECT status from pedidoslines WHERE EmpresaNo=1 and Pedido=%s and  ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(pedido,productono,catalogo,nolinea))
					registro = cursor.fetchone()

					# Crea variables de  version actual asi como el actual_estatus para pedidoslines
					
					version_actual_pedidos_lines =  registro[0].strip()

					# Si las versiones no concuerdan crea contador de pedidos_cambiados y sus lista respectiva para ser mostrados al usuario.
					if (version_actual_pedidos_encontrados != version_original_pedidos_encontrados) or (version_actual_pedidos_lines != version_original_pedidos_lines):
						pedidos_cambiados += 1 # actualiza contador de pedidos cambiados durante el proceso
					
					else:

						if fecha_probable == u'':
							fecha_probable =u'19010101'
						fecha_probable = fecha_probable.encode('latin_1')


						# ACTUALIZA pedidoslines
						
						if encontrado == 'S':
								nuevo_status_pedido = 'Encontrado'
						else:
							
							fecha_probable = u'19010101'
							fecha_probable = fecha_probable.encode('latin_1')

						if version_actual_pedidos_lines != u'Cancelado':

							if (encontrado == '' or encontrado =='N' or encontrado == 'P' or encontrado=='X'):
								
								nuevo_status_pedido ='Por confirmar'	
							else:
								if encontrado =='D':

									nuevo_status_pedido = 'Descontinuado'

					

						# Abre transaccion
						cursor.execute("START TRANSACTION")
						
						# Actualiza pedidos_encontrados

						cursor.execute("UPDATE pedidos_encontrados SET encontrado=%s,BodegaEncontro=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(encontrado,almacen,pedido,productono,catalogo,nolinea))
						
						# Marca articulo como descontinuado si encontrado ='D'
						if encontrado =='D':
								cursor.execute("UPDATE articulo SET descontinuado=1 WHERE EmpresaNo=1 and CodigoArticulo=%s and Catalogo=%s;",(productono,catalogo))


						if almacen == '2':
							cursor.execute("UPDATE pedidos_encontrados SET `2`=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(encontrado,pedido,productono,catalogo,nolinea))
						elif almacen =='3':
							cursor.execute("UPDATE pedidos_encontrados SET `3`=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(encontrado,pedido,productono,catalogo,nolinea))
						elif almacen == '4':
							cursor.execute("UPDATE pedidos_encontrados SET `4`=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(encontrado,pedido,productono,catalogo,nolinea))
						elif almacen == '5':
							cursor.execute("UPDATE pedidos_encontrados SET `5`=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(encontrado,pedido,productono,catalogo,nolinea))
						elif almacen == '6':
							cursor.execute("UPDATE pedidos_encontrados SET `6`=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(encontrado,pedido,productono,catalogo,nolinea))
						elif almacen == '7':
							cursor.execute("UPDATE pedidos_encontrados SET `7`=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(encontrado,pedido,productono,catalogo,nolinea))
						elif almacen == '8':
							cursor.execute("UPDATE pedidos_encontrados SET `8`=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(encontrado,pedido,productono,catalogo,nolinea))
						elif almacen == '9':
							cursor.execute("UPDATE pedidos_encontrados SET `9`=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(encontrado,pedido,productono,catalogo,nolinea))
						else:
							cursor.execute("UPDATE pedidos_encontrados SET `10`=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(encontrado,pedido,productono,catalogo,nolinea))

						# Actualiza pedidos

						cursor.execute("UPDATE pedidosheader SET FechaUltimaModificacion=%s,horamodicacion=%s WHERE EmpresaNo=1 and pedidono=%s;",[fecha_hoy,hora_hoy,pedido,])							
						cursor.execute("UPDATE pedidoslines SET status=%s,FechaTentativaLLegada=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(nuevo_status_pedido,fecha_probable,pedido,productono,catalogo,nolinea))
						cursor.execute("UPDATE pedidos_notas set Observaciones=%s where EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(notas,pedido,productono,catalogo,nolinea))

						# Crea o bien actualiza pedidos_status_fechas

						if encontrado != 'X' and version_actual_pedidos_lines != 'Cancelado':

							# Verifica que no existe el registro, si existe actualiza, caso contrario crea.
							print pedido,productono,nuevo_status_pedido,catalogo,nolinea
							cursor.execute("SELECT Pedido FROM pedidos_status_fechas WHERE EmpresaNo=%s and Pedido=%s and ProductoNo=%s and Status=%s and catalogo=%s and NoLinea=%s;",(1,pedido,productono,nuevo_status_pedido,catalogo,nolinea))
							

							
							if (encontrado == 'S' or encontrado == 'D'):

								# Si no existe registro, crea
								if cursor.fetchone() is None:

									cursor.execute("INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,ProductoNo,Status,catalogo,NoLinea,FechaMvto,HoraMvto,Usuario) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",[1,pedido,productono,nuevo_status_pedido,catalogo,nolinea,fecha_hoy,hora_hoy,capturista])
								
								# De otra manera, actualiza
								else:	
									cursor.execute("UPDATE pedidos_status_fechas SET FechaMvto=%s,HoraMvto=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s and status='Por Confirmar';",(fecha_hoy,hora_hoy,pedido,productono,catalogo,nolinea))




						cursor.execute("COMMIT;")

				

				except DatabaseError as error_msg:
			
					cursor.execute("ROLLBACK;")
					data = {'status_operacion':'fail','error':error_msg,}
					print error_msg
					error = True
				except IntegrityError as error_msg:
					cursor.execute("ROLLBACK;")
					data = {'status_operacion':'fail','error':error_msg,}
					print error_msg
					error = True
				except OperationalError as error_msg:
					cursor.execute("ROLLBACK;")
					data = {'status_operacion':'fail','error':error_msg,}
					error = True
				except NotSupportedError as error_msg:
			
					cursor.execute("ROLLBACK;")
					data = {'status_operacion':'fail','error':error_msg,}
					error = True
					print error_msg

				except ProgrammingError as error_msg:

					cursor.execute("ROLLBACK;")
					data = {'status_operacion':'fail','error':error_msg,}
					error = True
					print error_msg

				except (RuntimeError, TypeError, NameError) as error_msg:
					#error_msg = 'Error no relativo a base de datos'
					data = {'status_operacion':'fail','error':error_msg,}
					error = True
					print error_msg
				except:
					error_msg = "Error desconocido"
					data = {'status_operacion':'fail','error':error_msg,}
					error = True
		

		cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,36,fecha_hoy,hora_hoy,"Colocó artículos del proveedor "+proveedor_nombre+" en el almacén "+almacen_nombre))



		cursor.close()

		# Si no hay error, nos devolvera la lista de pedidos cambiados
		# o bien un 'ok' y si hay error nos devolvera el mensaje de error.
		if not error:
			data={'status_operacion':'ok'}
			data['pedidos_no_procesados']=' '

			if pedidos_cambiados > 0:
				# Agrega una clave mas al dict indicando que algunos productos no se procesaron
				data['pedidos_no_procesados']='Algunos registros no fueron procesados, debido a que fueron modificados por otra transaccion mientras Ud los marcaba !'
			
		return HttpResponse(json.dumps(data),content_type='application/json',)

# PROCESAR CIERRE DE PEDIDOS

def procesar_cierre_pedido(request):
	
	#pdb.set_trace()
	if request.is_ajax()  and request.method == 'POST':
		# Pasa a una variable la tabla  recibida en json string
		TableData = request.POST.get('TableData')
		
		# carga la tabla ( la prepara con el formato de lista adecuado para leerla)
		datos = json.loads(TableData)

		try:
			request.POST.get('psw_paso')
			psw_paso = request.POST.get('psw_paso')

			cursor = connection.cursor()
			cursor.execute("SELECT usuariono FROM usr_extend WHERE pass_paso=%s;",(psw_paso,))
			usr_existente = cursor.fetchone()
			usr_existente = usr_existente[0]
			capturista = usr_existente
			cursor.close()
		except:
			psw_paso = '999'
			capturista = 99

		datos_cierre_invalidos = False
		errores_datos_cierre=[]
		

		''' TRAE VARIABLE CON POST '''

		almacen = request.POST.get('almacen')
		almacen = almacen.encode('latin_1')

		referencia = request.POST.get('referencia')
		referencia= referencia.encode('latin_1')

		if len(referencia)<10:
			#datos_cierre_invalidos = True
			#errores_datos_cierre.append('Referencia invalida !')
			pass
		total_articulos = request.POST.get('total_articulos')
		total_articulos = total_articulos.encode('latin_1')


		colocado_via = request.POST.get('colocado_via')
		colocado_via = colocado_via.encode('latin_1')


		tomado_por = request.POST.get('tomado_por')
		tomado_por = tomado_por.encode('latin_1')

		if (tomado_por)<3:
			datos_cierre_invalidos = True
			errores_datos_cierre.append('El campo "Tomado por" debe tener minimo 3 caracteres !')

		confirmado_por = request.POST.get('confirmado_por')
		confirmado_por = confirmado_por.encode('latin_1')

		if (confirmado_por)<3:
			datos_cierre_invalidos = True
			errores_datos_cierre.append('El campo "Confirmado por" debe tener minimo 3 caracteres !')

		'''fecha_cierre = request.POST.get('fecha_cierre')
		fecha_cierre = fecha_cierre.encode('latin_1')

		hora_cierre = request.POST.get('hora_cierre')
		hora_cierre = hora_cierre.encode('latin_1')

		fecha_cierre,hora_cierre = trae_fecha_hora_actual(fecha_cierre,hora_cierre)'''

		fecha_llegada = request.POST.get('fecha_llegada')
		fecha_llegada = fecha_llegada.encode('latin_1')

		if not fecha_llegada:
			datos_cierre_invalidos = True
			errores_datos_cierre.append('Fecha de llegada incorrecta !')



		pedido = request.POST.get('pedido')
		pedido = pedido.encode('latin_1')

		if pedido == 0:
			datos_cierre_invalidos = True
			errores_datos_cierre.append('El numero de pedido debe ser distinto de cero !')

		importe = request.POST.get('importe')
		importe = importe.encode('latin_1')

		if importe == 0:
			datos_cierre_invalidos = True
			errores_datos_cierre.append('El importe debe ser mayor a cero !')



		importe_nc = request.POST.get('importe_nc')
		importe_nc = importe_nc.encode('latin_1')

		monto_pagar = request.POST.get('monto_pagar')
		monto_pagar = monto_pagar.encode('latin_1')

		paqueteria = request.POST.get('paqueteria')
		paqueteria = paqueteria.encode('latin_1')

		if len(paqueteria)<3:
			datos_cierre_invalidos = True
			errores_datos_cierre.append('Paqueteria debe tener una logitud de al menos 3 caracteres !')

		no_de_guia = request.POST.get('no_de_guia')
		no_de_guia = no_de_guia.encode('latin_1')

		if len(no_de_guia)<3:
			#datos_cierre_invalidos = True
			#errores_datos_cierre.append('Numero de guia debe tener una longitud de al menos 3 caracteres !')
			pass
		proveedor = request.POST.get('proveedor')
		proveedor = proveedor.encode('latin_1')
        

		if datos_cierre_invalidos:
			error = errores_datos_cierre
			data = {'error':error,}
			return HttpResponse(json.dumps(data),content_type='application/json',)



		cursor = connection.cursor()

		''' INICIALIZACION DE VARIABLES '''

		nuevo_status_pedido ='Confirmado' # Para el cierre todos los pedidos toman este status
		error = False
		pedidos_cambiados = 0  

		''' FIN DE INCIALIZACION DE VARIABLES '''


		# Se convierte la fecha de hoy a formatos manejables para insertarlos en el registro.
		hoy = datetime.now()
		fecha_hoy = hoy.strftime("%Y-%m-%d")
		hora_hoy = hoy.strftime("%H:%M:%S") 


		try:

			cursor.execute("START TRANSACTION")
						
			cursor.execute("SELECT id FROM prov_ped_cierre ORDER BY id DESC LIMIT 1 FOR UPDATE;")

			registro = cursor.fetchone()
			id_nuevo_cierre = registro[0]+1



			# Crea nuevo cierre en tabla de cierres !

			
                                                                                                                                                                                                                                                                                                                                                                                               
			cursor.execute("INSERT INTO prov_ped_cierre (id,referencia,total_articulos,FechaColocacion,HoraColocacion,ColocadoVia,TomadoPor,ConfirmadoPor,CerradoPor,FechaCierre,HoraCierre,NumPedido,Importe,ImporteNC,MontoPagar,Paqueteria,NoGuia,prov_id,almacen,Totartrecibidos,Cerrado,Recepcionado) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(id_nuevo_cierre,referencia,total_articulos,fecha_llegada,hora_hoy,colocado_via,tomado_por,confirmado_por,capturista,fecha_hoy,hora_hoy,pedido,importe,importe_nc,monto_pagar,paqueteria,no_de_guia,proveedor,almacen,total_articulos,True,False))

			# Registra el evento en log de eventos

			cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values (%s,%s,%s,%s,%s);",(usr_existente,37,fecha_hoy,hora_hoy,"Cerró colocación con cierre número "+str(id_nuevo_cierre)))

	        # Recupera cada diccionario y extrae los valores de la llave a buscar.
			for j in datos:
				
				if j is not None: # Procesa solo los registros con contenido
			
				
					print "elegido:", j.get('elegido')
					pedido = j.get("Pedido").encode('latin_1')

					productono = j.get('ProductoNo').strip()
					catalogo =j.get('Catalogo').strip()
					nolinea = j.get('Nolinea').encode('latin_1')
					elegido = j.get('elegido')
					version_original_pedidos_encontrados = j.get('ver_ant_encontrado').strip() # Traemos version anterior del registro pedidos_encontrados, para esto usamos el campo 'encontrado' con el que haremos una  futura comparacion con una nueva lectura al mismo para ver si cambio
					version_original_pedidos_lines = j.get('status').strip() # Traemos version anterior del registro pedidoslines, para esto usamos el campo 'status' con el que hacemos una comparacion con una nueva lectura al mismo para ver si cambio

					# Comienza acceso a BD.

					
					# verifica version actual pedidos_encontrados y de una vez traemos id_cierre que se usara mas adelante
					cursor.execute("SELECT encontrado,id_cierre from pedidos_encontrados WHERE EmpresaNo=1 and Pedido=%s and  ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(pedido,productono,catalogo,nolinea))
					registro = cursor.fetchone()

					# Creea variable version_actual e id_cierre para pedidos_encontrados
					version_actual_pedidos_encontrados=registro[0].strip()
					id_cierre = registro[1]

					# verifica version actual pedidoslines y de una vez se trae el estatus actual para ser mostrado en caso de que la version actual difiera de la anterior
					cursor.execute("SELECT status from pedidoslines WHERE EmpresaNo=1 and Pedido=%s and  ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(pedido,productono,catalogo,nolinea))
					registro = cursor.fetchone()

					# Crea variables de  version actual asi como el actual_estatus para pedidoslines
					
					version_actual_pedidos_lines =  registro[0].strip()

					# Si las versiones no concuerdan crea contador de pedidos_cambiados y sus lista respectiva para ser mostrados al usuario.
					if (version_actual_pedidos_encontrados != version_original_pedidos_encontrados) or (version_actual_pedidos_lines != version_original_pedidos_lines):
						pedidos_cambiados += 1 # actualiza contador de pedidos cambiados durante el proceso
						
					else:

						cursor.execute("UPDATE pedidos_encontrados SET id_cierre=%s,FechaProbable=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and Nolinea=%s;",(id_nuevo_cierre,fecha_llegada,pedido,productono,catalogo,nolinea))

						
						# Actualiza pedidos

						cursor.execute("UPDATE pedidosheader SET FechaUltimaModificacion=%s,horamodicacion=%s WHERE EmpresaNo=1 and pedidono=%s;",[fecha_hoy,hora_hoy,pedido])							
						cursor.execute("UPDATE pedidoslines SET status=%s,FechaTentativaLLegada=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(nuevo_status_pedido,fecha_llegada,pedido,productono,catalogo,nolinea))


						# Crea o bien actualiza pedidos_status_fechas

						cursor.execute("INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,ProductoNo,Status,catalogo,NoLinea,FechaMvto,HoraMvto,Usuario) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",[1,pedido,productono,nuevo_status_pedido,catalogo,nolinea,fecha_hoy,hora_hoy,capturista])




			cursor.execute("COMMIT;")


		except DatabaseError as error_msg:
		
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			
			error = True
		except IntegrityError as error_msg:
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except OperationalError as error_msg:
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except NotSupportedError as error_msg:
	
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except ProgrammingError as error_msg:

			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except (RuntimeError, TypeError, NameError) as error_msg:
			cursor.execute("ROLLBACK;")
			#error_msg = 'Error no relativo a base de datos'
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except:
			cursor.execute("ROLLBACK;")
			error_msg = "Error desconocido"
			data = {'status_operacion':'fail','error':error_msg,}
			error = True

		cursor.close()

		# Si no hay error, nos devolvera la lista de pedidos cambiados
		# o bien un 'ok' y si hay error nos devolvera el mensaje de error.
		if not error:
			if pedidos_cambiados != 0:
				data={'status_operacion':'ok','error':'Algunos registros no fueron procesados, debido a que fueron modificados por otra transaccion mientras Ud los marcaba !'}
			else:
				data={'status_operacion':'ok',}
		return HttpResponse(json.dumps(data),content_type='application/json',)



@login_required(login_url = "/pedidos/acceso/")
def elegir_almacen_a_cerrar(request):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	
	mensaje = " "
	reg_encontrados = 0

	# elimina cualquier registro de la session.
	session_id = request.session.session_key
	# Asigna is_staff para validacines
	is_staff = request.session['is_staff']

	hoy = date.today()
	hace_un_mes = hoy + timedelta(-120)





	"""cursor = connection.cursor()
	cursor.execute("DELETE FROM pedidos_pedidos_tmp where session_key= %s;",[session_id])	
	
	cursor.close()"""


	#for key,value in pr_dict.items():
	#	print key,value 
	
	 
	if request.method =='POST':
		
		form = ElegirAlmacenaCerrarForm(request.POST)
		print form.is_valid()
		print form.errors
		if form.is_valid():
		

		#proveedor = form.cleaned_data['proveedor']
		#almacen = form.cleaned_data['almacen']'''

			proveedor = request.POST.get('proveedor')
			almacen = request.POST.get('almacen')

			try:
				cursor =connection.cursor()
			 	#cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a a USE INDEX (`ind_emp_prov_cat_codpro`) ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) WHERE e.empresano=1 and a.idProveedor=%s and e.BodegaEncontro=%s and l.Status='Encontrado' and e.id_cierre=0;",(proveedor,almacen))
				#cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status FROM pedidos_encontrados e USE INDEX (ind_bodega_encontrado_cierre)  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) WHERE e.empresano=1 and a.idProveedor=%s  and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY a.idestilo;",(proveedor,almacen))
				#cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo)  WHERE e.empresano=1 and a.idProveedor=%s and p.FechaPedido>=%s and p.FechaPedido<=%s and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY a.idestilo;",(proveedor,hace_un_mes,hoy,almacen))
				cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( l.EmpresaNo=1 and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p USE INDEX (ind_emp_fechapedido_numped) ON (p.EmpresaNo=1 and e.Pedido=p.PedidoNo) INNER JOIN articulo a USE INDEX (ind_emp_prov_cat_codpro) ON (a.EmpresaNo=1 and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo)  WHERE e.empresano=1 and a.idProveedor=%s and e.BodegaEncontro=%s  and e.encontrado='S' and l.Status='Encontrado' and e.id_cierre=0 ORDER BY a.idestilo;",(proveedor,almacen))

			except DatabaseError as e:
				mensaje = "Error de base de datos: "+str(e)


			if cursor:

				registros = dictfetchall(cursor)
				mensaje ="Lista de registros ya colocados en el almacen seleccionado que no han sido cerrados."

				for j in cursor:
					reg_encontrados +=1
				cursor.close()	
			else:
				registros ={}
				mensaje = "Registros no encontrados para esta consulta !"
				cursor.close()
				return render(request,'pedidos/elegir_almacen_a_cerrar.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})

			#return render(request,'pedidos/muestra_colocados_a_cerrar.html',{'registros':registros,'mensaje':mensaje,'reg_encontrados':reg_encontrados,'almacen':almacen,})	
			return render(request,'pedidos/muestra_colocados_a_cerrar.html',{'registros':registros,'mensaje':mensaje,'almacen':almacen,'reg_encontrados':reg_encontrados,'proveedor':proveedor,})	

			#return render(request,'pedidos/elegir_almacen_a_cerrar.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})

		else:	
			
			return render(request,'pedidos/elegir_almacen_a_cerrar.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})

	form = ElegirAlmacenaCerrarForm()
	return render(request,'pedidos/elegir_almacen_a_cerrar.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})	

"""def muestra_encontrados_almacen(request):
	#pdb.set_trace()	
	if request.method == 'GET':
	#if request.is_ajax() and request.method == 'GET':
		proveedor = request.GET['proveedor']
		almacen = request.GET['almacen']

		try:
			cursor =connection.cursor()
		 	cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,e.encontrado as ver_ant_encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,l.OpcionCompra,e.observaciones,p.idSucursal,l.Observaciones,e.`2`,e.`3`,e.`4`,e.`5`,e.`6`,e.`7`,e.`8`,e.`9`,e.`10`,l.status FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) WHERE e.empresano=1 and a.idProveedor=%s and e.BodegaEncontro=%s and l.Status='Encontrado' and e.id_cierre=0;",(proveedor,almacen))
		
		except DatabaseError as e:
			mensaje = e


		if cursor:

		registros = dictfetchall(cursor)
		mensaje ="ok"
		else:
			registros ={}
			mensaje = "Registros no encontrados para esta consulta !"
		cursor.close()
		return render(request,'pedidos/muestra_colocados_a_cerrar.html',{'registros':registros,'mensaje':mensaje,'reg_encontrados':reg_encontrados,'almacen':almacen,})	"""
def pruebaImprime(request):
		a = '<html><p class="imprime"><font size="6"> ES SHOES MULTIMARCAS </font></p>'
		b = '<p class="imprime"><font size="6"> prueba de impresion</font> </p><br>'
		c = '<p class="imprime"><font size="5"> ES SHOES MULTIMARCAS </font></p>'
		d = '<p class="imprime"><font size="5"> prueba de impresion</font> </p><br>'
		e = '<p class="imprime"><font size="4"> ES SHOES MULTIMARCAS </font></p>'
		f = '<p class="imprime"><font size="4"> prueba de impresion</font> </p><br>'
		g = '<p class="imprime"><font size="0.5"> prueba </font></p>'
		h = '<p class="imprime"><font size="1"> prueba de impresion</font> </p><br></html>'
		
		
		
		return HttpResponse(a+b+c+d+e+f+g+h)

@login_required(login_url = "/pedidos/acceso/")
def seleccion_cierre_rpte_cotejo(request):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..

	
	mensaje = " "
	reg_encontrados = 0

	# elimina cualquier registro de la session.
	session_id = request.session.session_key
	# Asigna is_staff para validacines
	is_staff = request.session['is_staff']


	
	 
	if request.method == 'POST':

		form = SeleccionCierreRpteCotejoForm(request.POST)

		if form.is_valid():
		
			

			proveedor = request.POST.get('proveedor_rpte_cotejo')
			cierre =  request.POST.get('cierre_rpte_cotejo')

			#proveedor = proveedor.encode('latin_1')
			#cierre = cierre.encode('latin_1')

			print cierre
			
			try:
				cursor =connection.cursor()
			 	#cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,e.BodegaEncontro,e.encontrado,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,a.idProveedor,l.FechaMaximaEntrega,p.idSucursal,l.Observaciones,suc.nombre as sucnom,concat(trim(soc.nombre),' ',trim(soc.appaterno),' ',trim(soc.apmaterno)) as socnom FROM pedidoslines l LEFT JOIN  pedidos_encontrados e on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo)  INNER JOIN pedidos_status_fechas f on  ( e.EmpresaNo=f.EmpresaNo and e.Pedido=f.Pedido and e.ProductoNo=f.ProductoNo and e.Catalogo=f.catalogo and e.NoLinea=f.NoLinea) inner join sucursal suc on (suc.empresano=1 and suc.SucursalNo=p.idsucursal) inner join asociado soc on (soc.EmpresaNo=1 and soc.AsociadoNo=p.AsociadoNo) WHERE a.idProveedor=%s and  l.Status='Confirmado'  and f.Status='Confirmado' and id_cierre=%s;",(proveedor,cierre))
			 	cursor.execute("SELECT e.id_cierre,suc.nombre as sucnom,e.Pedido,p.AsociadoNo,concat(trim(soc.nombre),'_',trim(soc.appaterno),'_',trim(soc.apmaterno)) as socnom,p.FechaPedido,e.Catalogo,a.idmarca,a.idestilo,a.idcolor,if (trim(a.talla)<>'NE',a.talla,l.observaciones) as talla ,l.precio,alm.razonsocial as bodega FROM pedidoslines l LEFT JOIN  pedidos_encontrados e on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo)  INNER JOIN pedidos_status_fechas f on  ( e.EmpresaNo=f.EmpresaNo and e.Pedido=f.Pedido and e.ProductoNo=f.ProductoNo and e.Catalogo=f.catalogo and e.NoLinea=f.NoLinea) inner join sucursal suc on (suc.empresano=1 and suc.SucursalNo=p.idsucursal) inner join asociado soc on (soc.EmpresaNo=1 and soc.AsociadoNo=p.AsociadoNo) inner join almacen alm on (alm.empresano=1 and alm.ProveedorNo=a.idProveedor and alm.Almacen=e.BodegaEncontro) WHERE a.idProveedor=%s and  l.Status='Confirmado'  and f.Status='Confirmado' and id_cierre=%s;",(proveedor,cierre))
			except DatabaseError as e:
				mensaje = e
				print "error de base de datos:",e

			registros = dictfetchall(cursor)
			
			if registros:
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="CIERRE.csv"'

				writer = csv.writer(response)
				writer.writerow(['ID_CIERRE', 'SUCURSAL', 'PEDIDO', 'NUM_SOCIO','NOMBRE_SOCIO','FECHA','CATALOGO','MARCA','ESTILO','COLOR','TALLA','PRECIO','BODEGA'])

			    
				for registro in registros:
					print registro
					'''if (registro[talla]).strip()=='NE':

						talla = registro[Observaciones]
					else:
						talla = registro[talla]'''

					# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
					llaves_a_mostrar = ['id_cierre','sucnom','Pedido','AsociadoNo','socnom','FechaPedido','Catalogo','idmarca','idestilo','idcolor','talla','precio','bodega'] 
					# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
					lista = [registro[x] for x in llaves_a_mostrar]
				
					writer.writerow(lista)
				cursor.close()
				return response			
				
			else:
				mensaje='No se encontraron registros con estos parametros !'
				cursor.close()
				return render(request,'pedidos/seleccion_cierre_rpte_cotejo.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})



		else:
			return render(request,'pedidos/seleccion_cierre_rpte_cotejo.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})
				

				


				

		
			#return render(request,'pedidos/elegir_almacen_a_cerrar.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})

		

	form = SeleccionCierreRpteCotejoForm()
	print form
	return render(request,'pedidos/seleccion_cierre_rpte_cotejo.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})	



def lista_cierres(id_prov):
	#pdb.set_trace()
	try:
		cursor=connection.cursor()
		# En la siguiente linea, la FechaColocaicion guarda en realidad la fecha tentativa de llegada.
		cursor.execute("SELECT c.id,c.NumPedido,c.referencia,c.FechaCierre,c.FechaColocacion,c.HoraCierre,c.total_articulos,c.importe, a.RazonSocial from prov_ped_cierre c inner join almacen a on (c.almacen=a.almacen and a.ProveedorNo=c.prov_id and a.empresano=1) where c.Cerrado and not (c.Recepcionado) and  c.prov_id=%s order by c.id desc;",[id_prov,])
	
	except DatabaseError as db_err:
	
		print "error en db:",db_err
	
	listaalm = dictfetchall(cursor)

	print listaalm
	
	
	return (listaalm)	



def combo_proveedor_rpte_cotejo(request,*args,**kwargs):
	#pdb.set_trace()

	if request.is_ajax() and request.method == 'GET':
		id_prov = request.GET['id_prov']
		
		
		# Trae la lista de catalogos con los parametros indicados:
		l = lista_cierres(id_prov)
		
		#data = serializers.serialize('json',r,fields=('clasearticulo',))
		
		# La siguiente instruccion genera una variable data con los datos en formato json.
		# En la linea anterior ( que esta comentada ), trataba de usar
		# serielizers para convertir a json pero no funciono.

		data = json.dumps(l,cls=DjangoJSONEncoder)
		return HttpResponse(data,content_type='application/json')
	else:
		raise Http404


# PROCESAMIENTO DE RECEPCIONES


def procesar_recepcion(request):
	
	#pdb.set_trace()
	# rutina para grabar header y lines 
	def graba_header_lines():

		cursor.execute("UPDATE pedidosheader SET FechaUltimaModificacion=%s,horamodicacion=%s WHERE EmpresaNo=1 and pedidono=%s;",[fecha_hoy,hora_hoy,pedido])							
		cursor.execute("UPDATE pedidoslines SET status=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(nuevo_status_pedido,pedido,productono,catalogo,nolinea))
		return


	contador_productos_recibidos = 0



	if request.is_ajax()  and request.method == 'POST':
		# Pasa a una variable la tabla  recibida en json string
		TableData = request.POST.get('TableData')
		
		# carga la tabla ( la prepara con el formato de lista adecuado para leerla)
		datos = json.loads(TableData)

		#capturista = request.session['socio_zapcat'] Esta linea se cambio por la que sigue..porque no se grababa el usuario que hacia la operacion.


		psw_paso =  request.POST.get('psw_paso')

		almacen = request.POST.get('almacen')
		almacen = almacen.encode('latin_1')
		marcartodo_nollego = request.POST.get('marcartodo_nollego')
		cierre = request.POST.get('cierre').encode('latin_1')
	

		try:

			nueva_fecha_llegada = request.POST.get('nueva_fecha_llegada').encode('latin_1')
			
			if nueva_fecha_llegada == u'None': 

	 			f_convertida = '1901/01/01'
	 		else:
	 			f_convertida = datetime.strptime(nueva_fecha_llegada, "%d/%m/%Y").strftime("%Y%m%d")
				#f_convertida = datetime.strptime(nueva_fecha_llegada, "%d/%m/%Y").date()
		except ValueError:

			error_msg="El campo de Nueva Fecha de llegada tiene un formato incorrecto, use dd/mm/AAAA"
			return render(request,'pedidos/error.html',{'error_msg':error_msg},)


			error_msg="Fecha "


		cursor = connection.cursor()


		cursor.execute("SELECT usuariono FROM usr_extend WHERE pass_paso=%s;",(psw_paso,))
		usr_existente = cursor.fetchone()
		usr_existente = usr_existente[0]
		capturista = usr_existente








		''' INICIALIZACION DE VARIABLES '''

		pedidos_cambiados = 0 # inicializa contador de pedidos que sufrieron cambios entre la lectura inicial y el commit.
		
		nuevo_status_pedido = '' # variable que servira para  guardar el status de pedido segun se vayan cumpliendo condiciones,
							# posteriomente se utilizara par actualizar el status del pedido en pedidoslines y pedidos_status_confirmacion.

		error = False

		''' FIN DE INCIALIZACION DE VARIABLES '''


		# Se convierte la fecha de hoy a formatos manejables para insertarlos en el registro.
		hoy = datetime.now()
		fecha_hoy = hoy.strftime("%Y-%m-%d")
		fecha_nollego = hoy.strftime("%d-%m-%Y")
		hora_hoy = hoy.strftime("%H:%M:%S") 

		cursor.execute("START TRANSACTION;")


        # Recupera cada diccionario y extrae los valores de la llave a buscar.
		
		try:
		
			for j in datos:
				
				pedido = j.get("Pedido").encode('latin_1')

				productono = j.get('ProductoNo').strip()
				catalogo =j.get('Catalogo').strip()
				nolinea = j.get('Nolinea').encode('latin_1')
				version_original_pedidos_lines = j.get('status').strip() # Traemos version anterior del registro pedidoslines, para esto usamos el campo 'status' con el que hacemos una comparacion con una nueva lectura al mismo para ver si cambio, no lo pasamos por encode (se queda en utf)
				incidencia = j.get('incidencia').encode('latin_1')
				# Comienza acceso a BD.

				
				# verifica version actual pedidos_encontrados y de una vez traemos id_cierre que se usara mas adelante
				cursor.execute("SELECT id_cierre from pedidos_encontrados WHERE EmpresaNo=1 and Pedido=%s and  ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(pedido,productono,catalogo,nolinea))
				registro = cursor.fetchone()

				# Creea variable version_actual e id_cierre para pedidos_encontrados
				id_cierre = registro[0]

				# verifica version actual pedidoslines y de una vez se trae el estatus actual para ser mostrado en caso de que la version actual difiera de la anterior
				cursor.execute("SELECT status from pedidoslines WHERE EmpresaNo=1 and Pedido=%s and  ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(pedido,productono,catalogo,nolinea))
				registro = cursor.fetchone()

				# Crea variables de  version actual asi como el actual_estatus para pedidoslines
				
				version_actual_pedidos_lines =  registro[0].strip()

				
				# Si las versiones no concuerdan crea contador de pedidos_cambiados y sus lista respectiva para ser mostrados al usuario.
				if (version_actual_pedidos_lines != version_original_pedidos_lines):
					pedidos_cambiados += 1 # actualiza contador de pedidos cambiados durante el proceso
				else:

					print marcartodo_nollego
					# Si el pedido es correcto y llego.
					if incidencia == '1':
						nuevo_status_pedido = 'Aqui'
					
						graba_header_lines()

						

						cursor.execute("""INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,
										ProductoNo,Status,
										catalogo,NoLinea,
										FechaMvto,HoraMvto,Usuario)
										VALUES (%s,%s,%s,%s,
											%s,%s,%s,%s,%s);""",
										[1,pedido,productono,nuevo_status_pedido,
										catalogo,nolinea,fecha_hoy,hora_hoy,capturista])




						contador_productos_recibidos += 1





					# Si el pedido No llego

					elif incidencia == '2' and marcartodo_nollego != 'on':
						
						nuevo_status_pedido='Por Confirmar'
						# Actualiza (pone en blancos registro de pedidos_encontrados)
						cursor.execute("UPDATE pedidos_encontrados SET id_cierre=0,FechaEncontrado='19010101',FechaProbable='19010101',BodegaEncontro=0,`2`='',`3`='',`4`='',`5`='',`6`='',`7`='',`8`='',`9`='',`10`='',encontrado='' WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(pedido,productono,catalogo,nolinea))
					
						cursor.execute("UPDATE pedidos_notas SET observaciones=CONCAT('No llegó: ',%s) WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(fecha_nollego,pedido,productono,catalogo,nolinea))


						# Actualiza header y lines con nuevo status
						graba_header_lines()
						
						# Elimina todos los status del articulo excepto el de 'Por Confirmar'
						cursor.execute("DELETE FROM pedidos_status_fechas WHERE empresano=1 and pedido=%s and productono=%s and catalogo=%s and nolinea=%s and not (status='Por Confirmar');",(pedido,productono,catalogo,nolinea))

					# Si el pedido completo no llego, se deja como esta y solo se cambia fecha tentativa de llegada
					
					elif incidencia == '2' and marcartodo_nollego == 'on':
					

						cursor.execute("SELECT FechaColocacion from prov_ped_cierre WHERE id=%s;",(cierre,))
						
						fecha_anterior_llegada= cursor.fetchone()

						cursor.execute("UPDATE pedidosheader SET FechaUltimaModificacion=%s,horamodicacion=%s WHERE EmpresaNo=1 and pedidono=%s;",[fecha_hoy,hora_hoy,pedido])							
						cursor.execute("UPDATE pedidoslines SET FechaTentativaLLegada=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(f_convertida,pedido,productono,catalogo,nolinea))
						
						
						#if f_convertida > fecha_anterior_llegada[0].strftime('%Y%m%d'):
						if datetime.strptime(nueva_fecha_llegada, '%d/%m/%Y').date() > fecha_anterior_llegada[0]:
							cursor.execute("UPDATE pedidos_notas SET observaciones=CONCAT('No llegó: ',%s) WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(fecha_nollego,pedido,productono,catalogo,nolinea))
						

						else:
							cursor.execute("UPDATE pedidos_notas SET observaciones=' ' WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(pedido,productono,catalogo,nolinea))


					elif incidencia > '2':
						# Si el producto llego pero no pasa el control de calidad

						# GENERA UN NUEVO PRODUCTO CON STATUS DE 'Por Confirmar'
						# Y CAMBIA EL STATUS DEL ACTUAL A "Por Devolver"

						# Trae PedidoNuevo
						cursor.execute("SELECT pedidono  from pedidosheader WHERE empresano=1 order by pedidono desc limit 1 FOR UPDATE;")
						registro = cursor.fetchone()
						PedidoNuevo = registro[0]+1

						# Trae  datos de pedidosheader para replicarlos en un nuevov registro con el nuevo numero de pedido;
						cursor.execute("SELECT EmpresaNo,PedidoNo,FechaPedido,HoraPedido,Saldototal,VtaTotal,UsuarioCrea,FechaUltimaModificacion,FechaCreacion,HoraCreacion,horamodicacion,UsuarioModifica,idSucursal,AsociadoNo,tiposervicio,viasolicitud  from pedidosheader WHERE empresano=1 and pedidono=%s;",[pedido])
						
						registroh = cursor.fetchone()
						
						reg_fecha_pedido = registroh[2]
						reg_Hora_pedido = registroh[3]
						reg_Saldototal= registroh[4]
						reg_VtaTotal = registroh[5]
						reg_UsuarioCrea = registroh[6]
						reg_FechaUltimaModificacion = registroh[7]
						reg_FechaCreacion = registroh[8]
						reg_HoraCreacion = registroh[9]
						reg_horamodificacion = registroh[10]
						reg_UsuarioModifica = registroh[11]
						reg_idSucursal = registroh[12]
						reg_AsociadoNo = registroh[13]
						reg_tiposervicio = registroh[14]
						reg_viasolicitud = registroh[15]

						cursor.execute("SELECT EmpresaNo,\
							Pedido,ProductoNo,CantidadSolicitada,\
							precio,subtotal,PrecioOriginal,Status,\
							RemisionNo,NoNotaCreditoPorPedido,\
							NoNotaCreditoPorDevolucion,NoRequisicionAProveedor,\
							NoNotaCreditoPorDiferencia,catalogo,NoLinea,\
							plazoentrega,OpcionCompra,FechaMaximaEntrega,\
							FechaTentativaLLegada,FechaMaximaRecoger,Observaciones,\
							AplicarDcto FROM pedidoslines WHERE empresano=1 and pedido=%s\
							 and productono=%s and catalogo=%s and nolinea=%s;",\
							 (pedido,productono,catalogo,nolinea))
						
						registrol = cursor.fetchone()
						
						reg_ProductoNo = registrol[2]
						reg_CantidadSolicitada = registrol[3]
						reg_precio =registrol[4]
						reg_subtotal =  registrol[5]
						reg_PrecioOriginal =  registrol[6]
						reg_Status = registrol[7]
						reg_RemisionNo = registrol[8]
						reg_NoNotaCreditoPorPedido = registrol[9]
						reg_NoNotaCreditoPorDevolucion = registrol[10]
						reg_NoRequisicionAProveedor =  registrol[11]
						reg_NoNotaCreditoPorDiferencia = registrol[12]
						reg_catalogo = registrol[13]
						reg_NoLinea = registrol[14]
						reg_plazoentrega = registrol[15]
						reg_OpcionCompra = registrol[16]
						reg_FechaMaximaEntrega = registrol[17]
						reg_FechaTentativaLLegada = registrol[18]
						reg_FechaMaximaRecoger = registrol[19]
						reg_Observaciones = registrol[20]
						reg_AplicarDcto = registrol[21]


						cursor.execute("SELECT temporada from pedidoslinestemporada\
						 WHERE empresano=1 and pedido = %s and productono=%s\
						  and catalogo=%s and nolinea=%s;",\
						  (pedido,productono,catalogo,nolinea))
						
						registrot = cursor.fetchone()

						reg_temporada = registrot[0] 


						# Las siguientes dos lineas modifican totales de pedidosheader con el precio del articulo.
						reg_VtaTotal = reg_PrecioOriginal
						reg_Saldototal = reg_PrecioOriginal

						cursor.execute("""INSERT INTO pedidosheader (EmpresaNo,PedidoNo,
																FechaPedido,HoraPedido,
																Saldototal,VtaTotal,
																UsuarioCrea,FechaUltimaModificacion,
																FechaCreacion,HoraCreacion,
																horamodicacion,UsuarioModifica,
																idSucursal,AsociadoNo,
																tiposervicio,viasolicitud)
																VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
																(1,PedidoNuevo,reg_fecha_pedido,reg_Hora_pedido,
																reg_Saldototal,reg_VtaTotal,
																reg_UsuarioCrea,reg_FechaUltimaModificacion,
																reg_FechaCreacion,reg_HoraCreacion,
																reg_horamodificacion,reg_UsuarioModifica,
																reg_idSucursal,reg_AsociadoNo,
																reg_tiposervicio,reg_viasolicitud))

						cursor.execute("""INSERT INTO pedidoslines (EmpresaNo,Pedido,
																ProductoNo,CantidadSolicitada,
																precio,subtotal,PrecioOriginal,
																Status,RemisionNo,NoNotaCreditoPorPedido,
																NoNotaCreditoPorDevolucion,NoRequisicionAProveedor,
																NoNotaCreditoPorDiferencia,catalogo,
																NoLinea,plazoentrega,OpcionCompra,
																FechaMaximaEntrega,FechaTentativaLLegada,
																FechaMaximaRecoger,Observaciones,AplicarDcto)
																VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
																(1,PedidoNuevo,reg_ProductoNo,
																reg_CantidadSolicitada,
																reg_precio,
																reg_subtotal,
																reg_PrecioOriginal,
																'Por Confirmar',
																reg_RemisionNo,
																reg_NoNotaCreditoPorPedido,
																reg_NoNotaCreditoPorDevolucion,
																reg_NoRequisicionAProveedor,
																reg_NoNotaCreditoPorDiferencia,
																reg_catalogo,
																reg_NoLinea,
																reg_plazoentrega,
																reg_OpcionCompra,
																reg_FechaMaximaEntrega,
																reg_FechaTentativaLLegada,
																reg_FechaMaximaRecoger,
																reg_Observaciones,
																reg_AplicarDcto))



						cursor.execute("""INSERT INTO pedidoslinestemporada (EmpresaNo,Pedido,
																ProductoNo,catalogo,
																NoLinea,Temporada)
																VALUES(%s,%s,%s,%s,%s,%s);""",[1,PedidoNuevo,productono,
																catalogo,nolinea,reg_temporada])
															
						cursor.execute("""INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,
																ProductoNo,Status,
																catalogo,NoLinea,
																FechaMvto,HoraMvto,Usuario)
																VALUES (%s,%s,%s,%s,
																	%s,%s,%s,%s,%s);""",
																[1,PedidoNuevo,reg_ProductoNo,'Por Confirmar',
																catalogo,nolinea,reg_FechaCreacion,reg_HoraCreacion,reg_UsuarioCrea])
						
						cursor.execute("""INSERT INTO pedidos_notas (EmpresaNo,Pedido,
																ProductoNo,catalogo,
																NoLinea,observaciones)
																VALUES(%s,%s,%s,%s,%s,%s);""",[1,PedidoNuevo,productono,
																catalogo,nolinea,''])									






						cursor.execute("""INSERT INTO pedidos_encontrados(EmpresaNo,Pedido,
							ProductoNo,Catalogo,
							NoLinea,FechaEncontrado,
							BodegaEncontro,FechaProbable,
							`2`,`3`,`4`,`5`,`6`,`7`,`8`,
							`9`,`10`,encontrado,id_cierre,
							causadevprov,observaciones)
							VALUES (%s,%s,%s,%s,%s,%s,%s,%s,
								%s,%s,%s,%s,%s,%s,%s,%s,%s,
								%s,%s,%s,%s);""",
							[1,PedidoNuevo,reg_ProductoNo,catalogo,
							nolinea,'19010101',0,'19010101',
							'','','','','','','','','','',0,0,''])

						# CAMBIA STATUS AL PRODUCTO ACTUAL
						cursor.execute("UPDATE pedidoslines SET status='Por Devolver' WHERE empresano=1 and pedido=%s and productono=%s and catalogo=%s and nolinea=%s;",[pedido,productono,catalogo,nolinea])
						cursor.execute("UPDATE pedidosheader SET FechaUltimaModificacion=%s,horamodicacion=%s WHERE EmpresaNo=1 and pedidono=%s;",[fecha_hoy,hora_hoy,pedido])							
						cursor.execute("""INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,
																ProductoNo,Status,
																catalogo,NoLinea,
																FechaMvto,HoraMvto,Usuario)
																VALUES (%s,%s,%s,%s,
																	%s,%s,%s,%s,%s);""",
																[1,pedido,reg_ProductoNo,'Por Devolver',
																catalogo,nolinea,fecha_hoy,hora_hoy,capturista])
					else:
						pass	
					

				
			''' En caso de que la incidencia sea 2 y se haya asignado una nueva fecha de lleda a todo el pedido, la siguinte linea sirve para altualizar esa
			nueva fecha de llegada en prov_ped_cierre'''	

			
			if nueva_fecha_llegada != u'None':
				if datetime.strptime(nueva_fecha_llegada, "%d/%m/%Y").date() > datetime.strptime("01/01/1901","%d/%m/%Y").date():
					cursor.execute("UPDATE prov_ped_cierre set TotArtRecibidos=%s, recepcionado=0,fechacolocacion=%s WHERE id=%s;",(0,f_convertida,cierre))




			cursor.execute("COMMIT;")


		except DatabaseError as error:
			print error
		
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':'Error en base de datos',}
			cursor.close()
			return HttpResponse(json.dumps(data),content_type='application/json',)
		except ValueError as x:
			print str(x)
			data = {'status_operacion':'fail','error':'Error no relativo a db.'}
			cursor.close()
			return HttpResponse(json.dumps(data),content_type='application/json',)

		#pdb.set_trace()
		
		# Verifica que no existan registros del cierre con status de Confirmado, caso contrario es que faltan por cerrar
		cursor.execute("SELECT count(*) as reg_sin_recepcionar FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) WHERE e.empresano=1 and l.Status='Confirmado' and e.id_cierre=%s;",(cierre,))
		reg_sin_recepcionar = cursor.fetchone()
				
		try:




			"""Si no hay una nueva_fecha_de_llegada, es decir que (f_convertida sea igual a 1901/01/01) no se marca como
			recepcionado el cierre, de otra manera se marca como recepcionado """


			if f_convertida == '1901/01/01': 

				cursor.execute("START TRANSACTION;")
				# Si ya se recepcionaron todos, marca el cierre como recepcionado
				if reg_sin_recepcionar[0] == 0:

					cursor.execute("UPDATE prov_ped_cierre set recepcionado=1,TotArtRecibidos=%s WHERE id=%s;",(contador_productos_recibidos,cierre,))
				else:
				# De otra manera solo incremeta el contador de recepcionados

					cursor.execute("UPDATE prov_ped_cierre set TotArtRecibidos=%s WHERE id=%s;",(contador_productos_recibidos,cierre))
					cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) VALUES(%s,%s,%s,%s,%s);",(usr_existente,12,fecha_hoy,hora_hoy,'Recepciono el cierre '+str(cierre)))


				cursor.execute("COMMIT;")

		except DatabaseError as error_bd_actualizar_total_cierres:
			
			cursor.execute("ROLLBACK;")
			print error_bd_actualizar_total_cierres
			error = True

		cursor.close()

		# Si no hay error, nos devolvera la lista de pedidos cambiados
		# o bien un 'ok' y si hay error nos devolvera el mensaje de error.
		if not error:
			if pedidos_cambiados != 0:
				data={'status_operacion':'ok','error':'Algunos registros no fueron procesados, debido a que fueron modificados por otra transaccion mientras Ud los marcaba !'}
			else:
				data={'status_operacion':'ok',}
		return HttpResponse(json.dumps(data),content_type='application/json',)



# SELECCION DEL CIERRE PARA RECEPEPCION

@login_required(login_url = "/pedidos/acceso/")
def seleccion_cierre_recepcion(request):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..

	
	mensaje = " "
	reg_encontrados = 0

	# elimina cualquier registro de la session.
	session_id = request.session.session_key
	# Asigna is_staff para validacines
	is_staff = request.session['is_staff']


	
	 
	if request.method == 'POST':

		form = SeleccionCierreRecepcionForm(request.POST)

		if form.is_valid():

			proveedor = request.POST.get('proveedor_rpte_cotejo')
			cierre =  request.POST.get('cierre_rpte_cotejo')
			marcartodo_nollego = request.POST.get('marcartodo_nollego')
			nueva_fecha_llegada =request.POST.get('nueva_fecha_llegada')
			ordenado_por = request.POST.get('ordenado_por')

			cursor = connection.cursor()

			try:
				if ordenado_por == u'1':
					cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,l.status,e.BodegaEncontro,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,p.idSucursal,l.Observaciones,suc.nombre,concat(trim(aso.nombre),' ',trim(aso.appaterno),' ',trim(aso.apmaterno)) as nombre_socio FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN sucursal suc on (p.idSucursal=suc.SucursalNo) inner join asociado aso on (p.empresano=1 and aso.asociadono=p.asociadono) WHERE e.empresano=1 and a.idProveedor=%s and  l.Status='Confirmado' and e.id_cierre=%s order by a.idestilo;",(proveedor,cierre))
				elif ordenado_por == u'2':
					cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,l.status,e.BodegaEncontro,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,p.idSucursal,l.Observaciones,suc.nombre,concat(trim(aso.nombre),' ',trim(aso.appaterno),' ',trim(aso.apmaterno)) as nombre_socio FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN sucursal suc on (p.idSucursal=suc.SucursalNo) inner join asociado aso on (p.empresano=1 and aso.asociadono=p.asociadono) WHERE e.empresano=1 and a.idProveedor=%s and  l.Status='Confirmado' and e.id_cierre=%s order by p.asociadono,a.idestilo;",(proveedor,cierre))
				else:
					cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,l.status,e.BodegaEncontro,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,p.idSucursal,l.Observaciones,suc.nombre,concat(trim(aso.nombre),' ',trim(aso.appaterno),' ',trim(aso.apmaterno)) as nombre_socio FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN sucursal suc on (p.idSucursal=suc.SucursalNo) inner join asociado aso on (p.empresano=1 and aso.asociadono=p.asociadono) WHERE e.empresano=1 and a.idProveedor=%s and  l.Status='Confirmado' and e.id_cierre=%s order by p.idsucursal,p.asociadono,a.idestilo;",(proveedor,cierre))

			except DatabaseError as e:
				print "Error base de datos"

			
			if cursor:

				registros = dictfetchall(cursor)
				cursor.close()
				mensaje = "Recepcion de articulos del cierre " + str(cierre) +"  :"		
				return render(request,'pedidos/muestra_registros_recepcionar.html', {'registros':registros,'mensaje':mensaje,'is_staff':is_staff,'marcartodo_nollego':marcartodo_nollego,'nueva_fecha_llegada':nueva_fecha_llegada,'cierre':cierre})

				
			else:
				mensaje='No se encontraron registros con estos parametros !'
				cursor.close()
				
				return render(request,'pedidos/seleccion_cierre_recepcion.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})



		else:

			print form.non_field_errors
			#form = SeleccionCierreRecepcionForm()
			return render(request,'pedidos/seleccion_cierre_recepcion.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})
				
	form = SeleccionCierreRecepcionForm()
	print form
	return render(request,'pedidos/seleccion_cierre_recepcion.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})	


''' ***  DETALLE DEL DOCUMENTO O MODIFICACION DE DOCUMENTO *** '''



def detalle_documento(request,NoDocto):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	msg = ''
	if request.method == 'POST':
		form = DetalleDocumentoForm(request.POST)
		if form.is_valid():
			nodocto = request.POST.get('nodocto')
			tipodedocumento =request.POST.get('tipodedocumento')
			#vtadecatalogo = request.POST.get('vtadecatalogo').encode('latin_1')
			asociado = request.POST.get('asociado')
			concepto = request.POST.get('concepto')
			monto = request.POST.get('monto')
			bloquearnotacredito = request.POST.get('bloquearnotacredito')


			''' OJO, los siguientes if's sirven para verificar 
			los campos boleanos 'vtadecatalogo' y 'bloquearnotacredito' 
			dado que el templeate los regresa con valores 'None' y 'on'
			esto hay que investigar porque lo hace, mientras
			se actualizan con calores correctos dependiendo de lo que 
			traigan '''

			
			if bloquearnotacredito is None:
				bloquearnotacredito = False
			if bloquearnotacredito == 'on':
				bloquearnotacredito = True


			cursor =  connection.cursor()
			try:

				cursor.execute('START TRANSACTION')
				cursor.execute('UPDATE documentos SET asociado=%s,concepto=%s,monto=%s,BloquearNotaCredito=%s WHERE nodocto=%s;',(asociado,concepto,monto,bloquearnotacredito,NoDocto,))
				cursor.execute("COMMIT;")
				return HttpResponseRedirect(reverse('pedidos:documentos'))
				

			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				msg = 'Error en base de datos !'
				e=str(e)
				return HttpResponse(e)

		else:
			nodocto = NoDocto

			return render(request,'pedidos/detalle_documento.html',{'form':form,'nodocto':nodocto,})
	else:	
				
		cursor =  connection.cursor()
		cursor.execute("SELECT d.NoDocto,\
			                   d.TipoDeDocumento,\
			                   d.VtaDeCatalogo,\
			                   d.Asociado,\
			                   d.Concepto,\
			                   d.Monto,\
			                   d.BloquearNotaCredito,\
			                   CONCAT(a.nombre,' ',a.appaterno,' ',a.apmaterno) as nombre_socio \
			                   FROM documentos d INNER JOIN asociado a ON (a.empresano=d.empresano and d.asociado=a.asociadono) \
			                   WHERE d.NoDocto=%s and d.empresano=1;",(NoDocto,))	
		datos_documento =  cursor.fetchone()
		
		nodocto = datos_documento[0]
		tipodedocumento = datos_documento[1] 
		
		if bool(datos_documento[2]) is True:
			ventadecatalogo = 'Si' 
		else:
			ventadecatalogo = 'No'
		asociado = datos_documento[3]
		concepto = datos_documento[4]
		monto = datos_documento[5]
		bloquearnotacredito = datos_documento[6]
		
		cursor.close()

		form =  DetalleDocumentoForm(initial= {'nodocto':nodocto,'tipodedocumento':tipodedocumento,'asociado':asociado,'concepto':concepto,'monto':monto,'bloquearnotacredito':bloquearnotacredito,})	
		return render(request,'pedidos/detalle_documento.html',{'form':form,'nodocto':nodocto,'tipodedocumento':tipodedocumento,'ventadecatalogo':ventadecatalogo,'msg':msg})



''' ***** CREACION DEL DOCUMETO **** '''

def crea_documento(request):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	msg = ''

	capturista = request.session['socio_zapcat']
	id_sucursal = request.session['sucursal_activa']

	test_suc = int(id_sucursal)
	
	if test_suc < 1:
		error_msg='Se perdió parte de la información de su sesión, para asegurar que todo vaya bien por favor cierre su navegador completamete y vuelva a entrar al sistema..'
		return render(request,'pedidos/error.html',{'error_msg':error_msg,}) 


	if request.method == 'POST':
		form = CreaDocumentoForm(request.POST)
		if form.is_valid():
			tipodedocumento =request.POST.get('doc_tipodedocumento')
			vtadecatalogo = request.POST.get('doc_ventadecatalogo')
			proveedor = request.POST.get('doc_proveedor')
			anio = request.POST.get('doc_anio')
			temporada = request.POST.get('doc_temporada')
			asociado = request.POST.get('doc_asociado')
			concepto = request.POST.get('doc_concepto')
			monto = request.POST.get('doc_monto')
			psw_paso =request.POST.get('psw_paso')


			fecha_hoy = ''
			hora_hoy =''
			
			# Para el caso de creditos antepone una 'C:' en el concepto.

			if tipodedocumento == 'Credito':
				concepto = "C: " + concepto
				saldo = monto
				venta = 0
			elif tipodedocumento =='Remision':
				venta = monto
				saldo = monto
			else:
				venta=0
				saldo=monto

				
			fecha_hoy,hora_hoy = trae_fecha_hora_actual(fecha_hoy,hora_hoy)
			print fecha_hoy
			print hora_hoy

			

			''' OJO, los siguientes if's sirven para verificar 
			los campos boleanos 'vtadecatalogo' y 'bloquearnotacredito' 
			dado que el templeate los regresa con valores 'None' y 'on'
			esto hay que investigar porque lo hace, mientras
			se actualizan con valores correctos dependiendo de lo que 
			traigan '''

			
			if vtadecatalogo is None:
				vtadecatalogo = u'0'
			
			vtadecatalogo = int(vtadecatalogo.encode('latin_1'))


			cursor =  connection.cursor()

			try:

				usr_existente=0
				permiso_exitoso=0

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,23)

				if permiso_exitoso ==0:

					raise ValueError

			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para crear documentos !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)		

	


			try:		


				cursor.execute('START TRANSACTION')

				cursor.execute('SELECT nodocto from documentos order by nodocto desc limit 1;')
				ultimodocto = cursor.fetchone()

				cursor.execute('SELECT consecutivo from documentos WHERE tipodedocumento=%s ORDER BY tipodedocumento,consecutivo desc limit 1;',(tipodedocumento,))
				ultimoconsec = cursor.fetchone()


				cursor.execute('''INSERT INTO documentos (
					  `EmpresaNo`,
					  `NoDocto`,
					  `Consecutivo`,
					  `TipoDeDocumento`,
					  `TipoDeVenta`,
					  `Asociado`,
					  `FechaCreacion`,
					  `HoraCreacion`,
					  `UsuarioQueCreoDcto.`,
					  `FechaUltimaModificacion`,
					  `HoraUltimaModificacion`,
					  `UsuarioModifico`,
					  `Concepto`,
					  `monto`,
					  `saldo`,
					  `DescuentoAplicado`,
					  `VtaDeCatalogo`,
					  `Cancelado`,
					  `comisiones`,
					  `PagoAplicadoARemisionNo`,
					  `Lo_Recibido`,
					  `venta`,
					  `idsucursal`,
					  `BloquearNotaCredito`)\
					  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					  %s,%s,%s,%s);''',[1,ultimodocto[0]+1,ultimoconsec[0]+1,tipodedocumento,'Contado',
					  	asociado,fecha_hoy,hora_hoy,usr_existente,\
					  	fecha_hoy,hora_hoy,usr_existente,\
					  	concepto,monto,saldo,0,vtadecatalogo,0,0,0,0,venta,id_sucursal,0])
				
				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,23,fecha_hoy,hora_hoy,'Se creó el documento: '+str(ultimodocto[0]+1)))		

				
				


				
			
				"""response = HttpResponse(content_type='application/pdf')
				response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'"""



				if tipodedocumento == 'Remision' or tipodedocumento == 'Cargo':
					
					p_num_venta = ultimodocto[0]+1
					p_num_credito = 0
					
				else:
					p_num_credito = ultimodocto[0]+1
					p_num_venta = 0

				
				if vtadecatalogo == 1:
					
					cursor.execute("SELECT ProveedorNo,Periodo,anio,ClaseArticulo\
					 FROM catalogostemporada\
					 WHERE ProveedorNo=%s\
					 and Periodo=%s and Anio=%s\
					 and Activo=1;",(proveedor,anio,temporada))

					reg_catalogos = dictfetchall(cursor)	

					for reg_catalogo in reg_catalogos:

						cursor.execute("INSERT INTO sociocatalogostemporada\
						                   (proveedorno,periodo,anio,\
						                   clasearticulo,asociadono,activo,nodocto)\
						                   VALUES(%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE activo=activo;"\
						                   ,(proveedor,anio,temporada,reg_catalogo['ClaseArticulo'],asociado,1,ultimodocto[0]+1))

				context ={'p_num_credito':p_num_credito,'p_num_venta':p_num_venta,'tipodedocumento':tipodedocumento,}

				cursor.execute("COMMIT;")


				return render(request,'pedidos/documento_registrado_exito.html',context,)	


				'''
			
				response = HttpResponse(content_type='application/pdf')
				response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

				linea = 800
				
				buffer = io.BytesIO()

			    # Create the PDF object, using the buffer as its "file."
				p = canvas.Canvas(buffer)

				#imprime_documento(ultimodocto[0]+1,tipodedocumento,False,request.session['cnf_razon_social'],request.session['cnf_direccion'],request.session['cnf_colonia'],request.session['cnf_ciudad'],request.session['cnf_estado'],p,buffer,response,True,linea,request)

				#imprime_documento(p_num_credito,'Credito',False,request.session['cnf_razon_social'],request.session['cnf_direccion'],request.session['cnf_colonia'],request.session['cnf_ciudad'],request.session['cnf_estado'],p,buffer,response,True,linea,request)
				'''

				
				#return HttpResponseRedirect(reverse('pedidos:imprime_venta'))
				#return HttpResponseRedirect(reverse('pedidos:documentos'))
				
				
				#return render(request,'pedidos/crea_documento.html',{'form':form,'NoDocto':ultimodocto[0]+1,'tipodedocumento':tipodedocumento})


			except DatabaseError as error_msg:
				
				error_msg = str(error_msg)
				if 'Duplicate' in (error_msg):
					error_msg =" Existe un problema, se intenta grabar un documento ya registrado,su documento no fué grabado !"
				cursor.execute("ROLLBACK;")
				return render(request,'pedidos/error.html',{'error_msg':error_msg,})

			except IntegrityError as error_msg:
				cursor.execute("ROLLBACK;")
				return render(request,'pedidos/error.html',{'error_msg':error_msg,})

			except OperationalError as error_msg:
				cursor.execute("ROLLBACK;")
				return render(request,'pedidos/error.html',{'error_msg':error_msg,})

			except NotSupportedError as error_msg:
				cursor.execute("ROLLBACK;")
				return render(request,'pedidos/error.html',{'error_msg':error_msg,})
		

			except ProgrammingError as error_msg:

				cursor.execute("ROLLBACK;")
				return render(request,'pedidos/error.html',{'error_msg':error_msg,})


			except (RuntimeError, TypeError, NameError) as error_msg:

				cursor.execute("ROLLBACK;")
				return render(request,'pedidos/error.html',{'error_msg':error_msg,})


			except:
				cursor.execute("ROLLBACK;")
				return render(request,'pedidos/error.html',{'error_msg':error_msg,})




			cursor.close()
	





		
	else:	
		form =  CreaDocumentoForm()	
	return render(request,'pedidos/crea_documento.html',{'form':form,})


def calcula_descuento(p_socio,p_idproveedor,p_socio_total_compras_mes_anterior):
	#pdb.set_trace() 

	factor_descuento = 0.0
	
	#if request.is_ajax()  and request.method == 'GET':
		# Pasa a una variable la tabla  recibida en json string
	socio = p_socio
	proveedor = p_idproveedor

	# Calcula la fecha inicial y la final final del mes inmediato anterior
	# para calcular el total de ventas del mes anterior

	fecha_inicial,fecha_final = traePrimerUltimoDiasMesAnterior()

	cursor = connection.cursor()

	# Se asegura que el socio realmente sea socio y no cliente:

	cursor.execute("SELECT EsSocio FROM asociado where AsociadoNo=%s;",(socio,))
	result = cursor.fetchone() # obtiene el resultado en forma de tupla 
	es_socio = result[0]


	# Determina el total de la venta del socio

	'''
	cursor.execute("SELECT SUM(p.precio) AS total\
	 FROM pedidos_status_fechas f  INNER JOIN pedidoslines p \
	  ON (p.EmpresaNo= f.EmpresaNo\
	   and p.Pedido=f.Pedido\
	    and p.ProductoNo=f.ProductoNo\
	     and f.Status=p.Status\
	      and p.catalogo=f.catalogo) INNER JOIN articulo a on \
	      (a.EmpresaNo=p.EmpresaNo\
	       and a.CodigoArticulo=p.ProductoNo\
	        and a.catalogo=p.catalogo) INNER JOIN pedidosheader h on\
	         (h.EmpresaNo= p.EmpresaNo and h.PedidoNo=p.pedido)\
	          WHERE f.FechaMvto>=%s and f.FechaMvto<=%s\
	           and p.Status='Facturado' and h.asociadono=%s\
	            and a.idProveedor=%s;",(fecha_inicial,fecha_final,socio,proveedor,))

	total_vta_xsocio_tupla = cursor.fetchone() # obtiene el resultado en forma de tupla '''

	
	'''if total_vta_xsocio_tupla[0] is None:

		
		total_vta_xsocio_var = 0
	else:

		total_vta_xsocio_var = total_vta_xsocio_tupla[0]'''	


	# **********  CALCULA EL PORCENTAJE DE DESCUENTO   ********	
	
	# Determina el porcentaje de dscto que corresponde
	# segun el total de la venta 

	# (modif.) Se cambia la variable total_vta_xsocio_var por p_socio_total_compras_mes_anterior
	# esto a raiz de que la base de las compras que hizo el socio  (antes ventas que se hicieron al socio) no contemplan las devolucioones.

	cursor.execute("SELECT porcentaje from prov_tarifas_desc\
	 where prove=%s and %s>=lim_inf and %s<=lim_sup;",\
	 (proveedor,p_socio_total_compras_mes_anterior,p_socio_total_compras_mes_anterior,))

	porc_desc_variable_tupla = cursor.fetchone()

	if porc_desc_variable_tupla is None:
		porc_desc_variable_var = 0
	else:
		porc_desc_variable_var = porc_desc_variable_tupla[0]


	# Trae el porcentaje porcentaje de desctuento fijo que tiene asignado al socio
	# para el proveedor en particular

	cursor.execute(" SELECT descuento_porc FROM socio_descuento\
	 WHERE idsocio=%s and idproveedor=%s;",(socio,proveedor,))	

	porc_desc_fijo_tupla = cursor.fetchone()

	if porc_desc_fijo_tupla is None:
		
		porc_desc_fijo_var = 0
	else:
		porc_desc_fijo_var =porc_desc_fijo_tupla[0]


	factor_descuento = 0

	# Calcula el factor de descuento siempre y cuando no sea cliente
	if es_socio:


		if porc_desc_fijo_var > porc_desc_variable_var:

			factor_descuento = porc_desc_fijo_var / 100
		else:
			factor_descuento = porc_desc_variable_var / 100

	cursor.close()

	return(factor_descuento)



def trae_inf_venta(request,num_socio):
	# funcion llamada desde la rutiona 'ingresa_socio'

	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..


	hoy = date.today()
	ejercicio_vigente =request.session['cnf_ejercicio_vigente']
	periodo_vigente = request.session['cnf_periodo_vigente']


	id_sucursal = request.session['sucursal_activa']
	cursor = connection.cursor()


	compras_mes_ant = 0


	# trae pedidos que estan aqui
	# Obervar que en el WHERE se usa un IF para la tamporada, para que se traiga el catalogo correcto
	cursor.execute("SELECT l.pedido,\
							l.productono,\
							l.catalogo,\
							l.nolinea,\
							h.fechacreacion,\
							l.fechatentativallegada,\
							a.idestilo,\
							a.idcolor,\
							a.idmarca,\
							a.talla,\
							l.status,\
							h.viasolicitud,\
							l.observaciones,\
							v.descripcion,\
							l.precio,a.idproveedor,ct.no_maneja_descuentos,if(%s<>h.idsucursal,1,0) as es_de_otra_suc,h.idsucursal FROM pedidoslines l\
							inner join pedidosheader h\
							on l.empresano=h.empresano and\
							l.pedido=h.pedidono\
							inner join articulo a on l.empresano=a.empresano\
							and l.productono=a.codigoarticulo\
							and l.catalogo=a.catalogo\
							left join viasolicitud v on (v.id=h.viasolicitud)\
							inner join pedidoslinestemporada plt on (plt.empresano=l.empresano and plt.pedido=l.pedido and plt.productono=l.productono and plt.catalogo=l.catalogo and plt.nolinea=l.nolinea)\
							left join catalogostemporada ct on (ct.proveedorno=a.idproveedor and ct.periodo=CAST(SUBSTRING(l.catalogo,1,4) as UNSIGNED) and ct.Anio=plt.Temporada and ct.clasearticulo=l.catalogo)\
							WHERE l.status='Aqui' and  h.asociadono=%s;",(id_sucursal,num_socio,))
	ventas = dictfetchall(cursor)

		
	
	''' Como se va a modificar un registro de la lista de diccionarios,se crea
	esta lista temporal'''
	ventas_temp = [ ]

	for venta in ventas: # recorre la lista de diccionarios ()
		
		p_precio = venta['precio']
	
		p_idproveedor = venta['idproveedor']

		
		if venta['no_maneja_descuentos']=='\x01':
		
			venta['precio_dscto']=p_precio
		else:
			
			#pdb.set_trace()		
			#  CALCULA LA BASE PARA COMPRAS DEL MES ANTERIOR

			fi,ff = traePrimerUltimoDiasMesAnterior()
			compras =calcula_compras_socio_por_proveedor(num_socio,hoy,2,p_idproveedor,fi,ff)

			for compra in compras:
				
				if compra['ventabruta']-compra['descuento']-compra['devoluciones']>0:
					'''
					p.drawString(20,linea,str(compra['nombreprov'])[:7])
					p.drawString(55,linea,str(compra['ventabruta']-compra['descuento']))
					p.drawString(86,linea,str(compra['devoluciones'] if compra['ventabruta']-compra['descuento']>compra['devoluciones'] else 0))
					p.drawString(117,linea,str((compra['ventabruta']-compra['descuento']-compra['devoluciones']) if compra['ventabruta']-compra['descuento']>compra['devoluciones'] else 0))
					linea-=10
					'''
					compras_mes_ant = compra['ventabruta']-compra['descuento']-compra['devoluciones']
				else:
					compras_mes_ant = 0

			#   CALCULA EL PORCENTAJE DE DESCUENTO

			p_porcentaje_descuento = Decimal( calcula_descuento(num_socio,p_idproveedor,compras_mes_ant))


			venta['precio_dscto']= p_precio - p_precio * p_porcentaje_descuento # agrega el precio de descuento al diccionario
			venta['precio_dscto']=round(venta['precio_dscto'],2)
			
			venta['porc_dscto'] = p_porcentaje_descuento*100
			venta['porc_dscto'] = round(venta['porc_dscto'],2)
		ventas_temp.append(venta) # Actualiza la lista temporal con el diccionario que ya incluye el precio de descuento
	
	ventas = ventas_temp # vuelve a apuntar a la lista ventas

	# trae informacion de pedidos con estatus de por confirmar, confirmados y encontrados

	#cursor.execute("SELECT p.pedido,p.productono,p.precio,p.status,p.catalogo,p.nolinea,a.pagina,a.idmarca,a.idestilo,a.idcolor,a.talla,h.idsucursal,aso.asociadoNo,aso.Nombre,aso.appaterno,aso.apmaterno, p.fechatentativallegada, f.fechamvto,p.Observaciones,h.fechapedido,if(trim(p.status)='Encontrado' or trim(p.status)='Confirmado',m.razonsocial,'') as razonsocial,n.observaciones as notas FROM pedidoslines p inner join pedidos_encontrados e on (p.empresano=e.empresano and p.pedido=e.pedido and p.productono=e.productono and p.catalogo=e.catalogo and p.nolinea=e.nolinea) inner join pedidosheader h on (p.EmpresaNo=h.EmpresaNo and p.pedido=h.pedidoNo) inner join articulo a on ( p.EmpresaNo=a.empresano and p.productono=a.codigoarticulo and p.catalogo=a.catalogo) inner join asociado aso on (h.asociadoNo=aso.asociadoNo)  inner join pedidos_status_fechas f on ( p.empresano=f.empresano and p.pedido=f.pedido and p.productono=f.productono and p.catalogo=f.catalogo and p.nolinea=f.nolinea and p.status=f.status) left join almacen m on (m.empresano=e.empresano and a.idproveedor=m.proveedorno and m.almacen=e.BodegaEncontro) inner join pedidos_notas n on (n.empresano=p.empresano and n.pedido=p.pedido and n.productono=p.productono and n.catalogo=p.catalogo and n.nolinea=p.nolinea) WHERE h.idsucursal=%s and (p.status='Encontrado' or p.status='Por Confirmar' or p.status='Confirmado' or p.status='Descontinuado') and h.asociadoNo=%s order by p.status;",(id_sucursal,num_socio,))

	cursor.execute("SELECT p.pedido,p.productono,p.precio,p.status,p.catalogo,p.nolinea,a.pagina,a.idmarca,a.idestilo,a.idcolor,a.talla,h.idsucursal,aso.asociadoNo,aso.Nombre,aso.appaterno,aso.apmaterno, p.fechatentativallegada, f.fechamvto,p.Observaciones,h.fechapedido,if(trim(p.status)='Encontrado' or trim(p.status)='Confirmado',m.razonsocial,'') as razonsocial,n.observaciones as notas FROM pedidoslines p inner join pedidos_encontrados e on (p.empresano=e.empresano and p.pedido=e.pedido and p.productono=e.productono and p.catalogo=e.catalogo and p.nolinea=e.nolinea) inner join pedidosheader h on (p.EmpresaNo=h.EmpresaNo and p.pedido=h.pedidoNo) inner join articulo a on ( p.EmpresaNo=a.empresano and p.productono=a.codigoarticulo and p.catalogo=a.catalogo) inner join asociado aso on (h.asociadoNo=aso.asociadoNo)  inner join pedidos_status_fechas f on ( p.empresano=f.empresano and p.pedido=f.pedido and p.productono=f.productono and p.catalogo=f.catalogo and p.nolinea=f.nolinea and p.status=f.status) left join almacen m on (m.empresano=e.empresano and a.idproveedor=m.proveedorno and m.almacen=e.BodegaEncontro) left join pedidos_notas n on (n.empresano=p.empresano and n.pedido=p.pedido and n.productono=p.productono and n.catalogo=p.catalogo and n.nolinea=p.nolinea) WHERE (p.status='Encontrado' or p.status='Por Confirmar' or p.status='Confirmado' or p.status='Descontinuado') and h.asociadoNo=%s order by p.status;",(num_socio,))

	porconfs_confs = dictfetchall(cursor) 


	# trae creditos

	cursor.execute("SELECT nodocto,fechacreacion,\
		concepto,monto FROM documentos WHERE\
		 empresano=1 and asociado=%s and tipodedocumento='Credito' and saldo<>0 and cancelado=0;",(num_socio,))

	creditos = dictfetchall(cursor)

	'''for credito in creditos:
		print credito'''

	# trae cargos

	cursor.execute("SELECT nodocto,fechacreacion,\
		concepto,monto FROM documentos WHERE\
		 empresano=1 and asociado=%s and tipodedocumento='Cargo' and saldo<>0 and cancelado=0;",(num_socio,))

	cargos = dictfetchall(cursor)

	cursor.close()

	return (ventas,creditos,cargos,porconfs_confs)





def nueva_venta(request):
	form = Ingresa_socioForm()
	tipo = 'V'
	existe_socio = True
	try:
		is_staff = request.session['is_staff']
		context={'existe_socio':existe_socio,'form':form,'is_staff':is_staff,'tipo':tipo,}	
		return render(request,'pedidos/ingresa_socio.html',context)
	except KeyError as e:
		return render(request,'pedidos/error.html',{'error_msg':'Caducó la sesión, salga completamente del sistema e ingrese nuevamente !. mensaje tecnico: '+str(e),})

'''
def calcula_descuento(request,*args,**kwargs):
	#pdb.set_trace() 

	factor_descuento = 0
	
	if request.is_ajax()  and request.method == 'GET':
		# Pasa a una variable la tabla  recibida en json string
		socio = request.GET['id_socio']
		proveedor = request.GET['id_prov']

		# Calcula la fecha inicial y la final final del mes inmediato anterior
		# para calcular el total de ventas del mes anterior

		fecha_inicial,fecha_final = traePrimerUltimoDiasMesAnterior()

		cursor = connection.cursor()

		# Se asegura que el socio realmente sea socio y no cliente:

		cursor.execute("SELECT EsSocio FROM asociado where AsociadoNo=%s;",(socio,))
		result = cursor.fetchone() # obtiene el resultado en forma de tupla 
		es_socio = result[0]


		# Determina el total de la venta del socio

		
		cursor.execute("SELECT SUM(p.precio) AS total\
		 FROM pedidos_status_fechas f  INNER JOIN pedidoslines p \
		  ON (p.EmpresaNo= f.EmpresaNo\
		   and p.Pedido=f.Pedido\
		    and p.ProductoNo=f.ProductoNo\
		     and f.Status=p.Status\
		      and p.catalogo=f.catalogo) INNER JOIN articulo a on \
		      (a.EmpresaNo=p.EmpresaNo\
		       and a.CodigoArticulo=p.ProductoNo\
		        and a.catalogo=p.catalogo) INNER JOIN pedidosheader h on\
		         (h.EmpresaNo= p.EmpresaNo and h.PedidoNo=p.pedido)\
		          WHERE f.FechaMvto>=%s and f.FechaMvto<=%s\
		           and p.Status='Facturado' and h.asociadono=%s\
		            and a.idProveedor=%s;",(fecha_inicial,fecha_final,socio,proveedor,))

		total_vta_xsocio_tupla = cursor.fetchone() # obtiene el resultado en forma de tupla 

		if total_vta_xsocio_tupla[0] is None:
			
			total_vta_xsocio_var = 0
		else:

			total_vta_xsocio_var = total_vta_xsocio_tupla[0]	



		# Determina el porcentaje de dscto que corresponde
		# segun el total de la venta 

		cursor.execute("SELECT porcentaje from prov_tarifas_desc\
		 where prove=%s and %s>=lim_inf and %s<=lim_sup;",\
		 (proveedor,total_vta_xsocio_var,total_vta_xsocio_var,))

		porc_desc_variable_tupla = cursor.fetchone()

		if porc_desc_variable_tupla is None:
			porc_desc_variable_var = 0
		else:
			porc_desc_variable_var = porc_desc_variable_tupla[0]


		# Trae el porcentaje porcentaje de desctuento fijo que tiene asignado al socio
		# para el proveedor en particular

		cursor.execute(" SELECT descuento_porc FROM socio_descuento\
		 WHERE idsocio=%s and idproveedor=%s;",(socio,proveedor,))	

		porc_desc_fijo_tupla = cursor.fetchone()

		if porc_desc_fijo_tupla is None:
			
			porc_desc_fijo_var = 0
		else:
			porc_desc_fijo_var =porc_desc_fijo_tupla[0]


		factor_descuento = 0

		# Calcula el factor de descuento siempre y cuando no sea cliente
		if es_socio:
			if porc_desc_fijo_var >= porc_desc_variable_var:

				factor_descuento = porc_desc_fijo_var / 100
			else:
				factor_descuento = porc_desc_variable_var / 100

		cursor.close()
	try:	
		#data = json.dumps({'factor_descuento':factor_descuento,'otracosa':'otracosa',})

		data = json.dumps({'factor_descuento':factor_descuento,'otracosa':'otracosa',},cls=DjangoJSONEncoder)
		#simplejson.dumps(ql, cls=DjangoJSONEncoder)
	except TypeError as e:
		print e			
		# En el siguiente return utilizo content_type. Intente usar 'mimetype'
		# en lugar de 'content_type' y no funciono.

	return HttpResponse(data,content_type='application/json')	
'''


# ***************   PROCESAR VENTA *********************

def procesar_venta(request):
	
	#pdb.set_trace()

	# Inicializa variables

	CreditosPorAplicarSaldados = False
	CargosPorAplicarSaldados = False

	if request.is_ajax()  and request.method == 'POST':
		# Pasa a una variable las tablas  recibidas en json string
		TableData_ventas= request.POST.get('TableData_ventas')
		TableData_creditos= request.POST.get('TableData_creditos')
		TableData_cargos= request.POST.get('TableData_cargos')
		totalgral=request.POST.get('totalgral')
		id_socio = request.POST.get('id_socio')
		totalventas = request.POST.get('totalventas')
		totalcreditos =request.POST.get('totalcreditos')
		totalcargos = request.POST.get('totalcargos')
		totaldsctos = request.POST.get('totaldsctos')
		totalgral = request.POST.get('totalgral')
		recibido = request.POST.get('recibido')
		psw_paso = request.POST.get('psw_paso')


		if int(totalventas) <= 0:
			data = {'status_operacion':'fail','error':'La venta está en ceros, su transacción no puede ser procesada, intente nuevamente !',}
			return HttpResponse(json.dumps(data),content_type='application/json',)


		if float(totalcreditos) > 0:
		
			if float(totalventas) + float(totalcargos) > float(totalcreditos) :

				creditoaplicado = float(totalcreditos)
			else:
			
				creditoaplicado = float(totalventas) + float(totalcargos)
		else:
			creditoaplicado = 0


		
		# carga la tablas ( las prepara con el formato de lista adecuado para leerlas)
		datos_venta = json.loads(TableData_ventas)
		datos_credito =json.loads(TableData_creditos)
		datos_cargos = json.loads(TableData_cargos)

		#capturista = request.session['socio_zapcat']
		#capturista = user_id
		sucursal_activa = request.session['sucursal_activa']



		if sucursal_activa == 0:
			HttpResponse("Al parecer, no selecciono una sucursal, por favor cierre su navegador, vuelva a abrir el navegador e ingrese nuevamente al sistema. !")


		datos_cierre_invalidos = False
		errores_datos_cierre=[]
		
		cursor = connection.cursor()

		''' INICIALIZACION DE VARIABLES '''

		nuevo_status_pedido ='Facturado' # Para el cierre todos los pedidos toman este status
		error = False
		pedidos_cambiados = 0  

		''' FIN DE INCIALIZACION DE VARIABLES '''


		# Se convierte la fecha de hoy a formatos manejables para insertarlos en el registro.
		hoy = datetime.now()
		fecha_hoy = hoy.strftime("%Y-%m-%d")
		hora_hoy = hoy.strftime("%H:%M:%S") 


		try:

			cursor.execute("START TRANSACTION")
						
			#cursor.execute("SELECT id FROM prov_ped_cierre ORDER BY id DESC LIMIT 1 FOR UPDATE;")

			#registro = cursor.fetchone()
			#id_nuevo_cierre = registro[0]+1

			# Trae el usuario para luego grabar el log.
			cursor.execute('SELECT usuariono FROM usr_extend WHERE pass_paso=%s;',(psw_paso,))

			usr_existente = cursor.fetchone()
			usr_existente =usr_existente[0]

			capturista = usr_existente # se actualiza esta variable porque se utiliza en los updates


			# Crea nuevo cierre en tabla de cierres !
                                                                                                                                                                                                                                                                                                                                                                                               
			#cursor.execute("INSERT INTO prov_ped_cierre (id,referencia,total_articulos,FechaColocacion,HoraColocacion,ColocadoVia,TomadoPor,ConfirmadoPor,CerradoPor,FechaCierre,HoraCierre,NumPedido,Importe,ImporteNC,MontoPagar,Paqueteria,NoGuia,prov_id,almacen,Totartrecibidos,Cerrado,Recepcionado) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(id_nuevo_cierre,referencia,total_articulos,fecha_hoy,hora_hoy,colocado_via,tomado_por,confirmado_por,capturista,fecha_hoy,hora_hoy,pedido,importe,importe_nc,monto_pagar,paqueteria,no_de_guia,proveedor,almacen,total_articulos,True,False))


			# Si no hay registros de venta seleccionados manda el mensaje adecuado.
			if not datos_venta:

				data={'status_operacion':'fail','error':'No hay ventas por procesar, seleccione ventas !'}
				return HttpResponse(json.dumps(data),content_type='application/json',)

	        # Recupera cada diccionario y extrae los valores de la llave a buscar.

			for j in datos_venta:

				if j is not None:    # Procesa solo los registros con contenido
					pedido = j.get("Pedido").encode('latin_1')

					productono = j.get('ProductoNo').encode('latin_1').strip()
					catalogo =j.get('Catalogo').strip() # es importante pasar por la funcion strip, de lo contrario no funcionan los queries
					nolinea = j.get('Nolinea').encode('latin_1')
					venta_elegida = j.get('venta_elegida')
					version_original_pedidos_lines = j.get('status').strip() # Traemos version anterior del registro pedidoslines, para esto usamos el campo 'status' con el que hacemos una comparacion con una nueva lectura al mismo para ver si cambio

					# Comienza acceso a BD.

					

					# verifica version actual pedidoslines y de una vez se trae el estatus actual para ser mostrado en caso de que la version actual difiera de la anterior
					cursor.execute("SELECT status from pedidoslines WHERE EmpresaNo=1 and Pedido=%s and  ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(pedido,productono,catalogo,nolinea))
					registro = cursor.fetchone()

					# Crea variables de  version actual asi como el actual_estatus para pedidoslines
					if registro is not None:
						version_actual_pedidos_lines =  registro[0].strip()
					else:	
						version_actual_pedidos_lines = 'Aqui'

					# Si las versiones no concuerdan crea contador de pedidos_cambiados y sus lista respectiva para ser mostrados al usuario.
					if (version_actual_pedidos_lines != version_original_pedidos_lines):
						pedidos_cambiados += 1 # actualiza contador de pedidos cambiados durante el proceso
						
					else:

					
						# Actualiza pedidos

						cursor.execute("UPDATE pedidosheader SET FechaUltimaModificacion=%s,horamodicacion=%s WHERE EmpresaNo=1 and pedidono=%s;",[fecha_hoy,hora_hoy,pedido])							
						cursor.execute("UPDATE pedidoslines SET status=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(nuevo_status_pedido,pedido,productono,catalogo,nolinea))


						# Crea o bien actualiza pedidos_status_fechas

						print pedido
						print productono
						print nuevo_status_pedido
						print catalogo
						print nolinea

						cursor.execute("INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,ProductoNo,Status,catalogo,NoLinea,FechaMvto,HoraMvto,Usuario) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",[1,pedido,productono,nuevo_status_pedido,catalogo,nolinea,fecha_hoy,hora_hoy,capturista])

		 		

			# Trae el ultimo documento
			cursor.execute("SELECT nodocto from documentos WHERE empresano=1 ORDER BY nodocto DESC LIMIT 1 FOR UPDATE;")
			ultimo_docto = cursor.fetchone()
			nuevo_docto = ultimo_docto[0]+1
			nueva_remision = nuevo_docto # se usa nueva_remision para retornala via ajax en diccionario.

			# Trae el ultimo documento
			cursor.execute("SELECT consecutivo from documentos WHERE empresano=1 and tipodedocumento=%s  ORDER BY consecutivo DESC LIMIT 1 FOR UPDATE;",('Remision',))
			ultimo_consec = cursor.fetchone()
			Nuevo_consec = ultimo_consec[0]+1	

			# Genera el documento.
			# Ojo: observar que el campo `UsuarioQueCreoDcto.` se coloco entre apostrofes inversos y el nombre del campo tal y como esta definido en la tabla (casesensitive) dado que si
					# se pone sin apostrofes marca error!
			cursor.execute("INSERT INTO documentos (`EmpresaNo`,`NoDocto`,\
										`Consecutivo`,`TipoDeDocumento`,\
										`TipoDeVenta`,`Asociado`,\
										`FechaCreacion`,`HoraCreacion`,\
										`UsuarioQueCreoDcto.`,`FechaUltimaModificacion`,\
										`HoraUltimaModificacion`,`UsuarioModifico`,\
										`Concepto`,`monto`,`saldo`,\
										`DescuentoAplicado`,`VtaDeCatalogo`,\
										`Cancelado`,`comisiones`,\
										`PagoAplicadoARemisionNo`,`Lo_recibido`\
										,`venta`,`idsucursal`,\
										`BloquearNotaCredito`) VALUES(%s,%s,%s,%s,%s,%s\
										,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
										%s,%s,%s,%s,%s);",(1,nuevo_docto,Nuevo_consec,\
											'Remision','Contado',id_socio,\
											fecha_hoy,hora_hoy,capturista,\
											fecha_hoy,hora_hoy,capturista,\
											"Venta",float(totalgral),float(creditoaplicado),\
											float(totaldsctos),False,False,\
											float(totalcargos),0,float(recibido),\
											float(totalventas),sucursal_activa,False,))



			# Actualiza log
			cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,22,fecha_hoy,hora_hoy,'Creó la venta : '+str(nuevo_docto)))		





			# Asocia cada registro al nuevo documento (remision) generado
			for j in datos_venta:

				if j is not None:   # Procesa solo los registros con contenido

					pedido = j.get("Pedido").encode('latin_1')

					productono = j.get('ProductoNo').encode('latin_1').strip()
					catalogo =j.get('Catalogo').strip() 
					nolinea = j.get('Nolinea').encode('latin_1')
					precio = j.get('precio').encode('latin_1')

					# Asigna la remision y el precio final ( que puede tener descuento)
					cursor.execute("UPDATE pedidoslines SET remisionno=%s,precio=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(nuevo_docto,precio,pedido,productono,catalogo,nolinea))
		


			'''
			# Genera el documento.
			# Ojo: observar que el campo `UsuarioQueCreoDcto.` se coloco entre apostrofes inversos y el nombre del campo tal y como esta definido en la tabla (casesensitive) dado que si
					# se pone sin apostrofes marca error!
			cursor.execute("INSERT INTO documentos (`EmpresaNo`,`NoDocto`,\
										`Consecutivo`,`TipoDeDocumento`,\
										`TipoDeVenta`,`Asociado`,\
										`FechaCreacion`,`HoraCreacion`,\
										`UsuarioQueCreoDcto.`,`FechaUltimaModificacion`,\
										`HoraUltimaModificacion`,`UsuarioModifico`,\
										`Concepto`,`monto`,`saldo`,\
										`DescuentoAplicado`,`VtaDeCatalogo`,\
										`Cancelado`,`comisiones`,\
										`PagoAplicadoARemisionNo`,`Lo_recibido`\
										,`venta`,`idsucursal`,\
										`BloquearNotaCredito`) VALUES(%s,%s,%s,%s,%s,%s\
										,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
										%s,%s,%s,%s,%s);",(1,nuevo_docto,Nuevo_consec,\
											'Remision','Contado',id_socio,\
											fecha_hoy,hora_hoy,capturista,\
											fecha_hoy,hora_hoy,capturista,\
											"Venta",float(totalgral),float(creditoaplicado),\
											float(totaldsctos),False,False,\
											float(totalcargos),0,0,\
											float(totalventas),sucursal_activa,False,))'''
			nueva_nota_credito = 0
			if float(totalgral) < 0:
				nueva_nota_credito = nuevo_docto + 1 # se usa nueva_nota_credito para pasarla via ajax en dict.

				montocredito = float(totalcreditos)-(float(totalventas)-float(totaldsctos)+float(totalcargos))

				# Genera NOTA DE CREDITO EN CASO DE QUE EL TOTAL SEA NEGATIVO.
				# Ojo: observar que el campo `UsuarioQueCreoDcto.` se coloco entre apostrofes inversos y el nombre del campo tal y como esta definido en la tabla (casesensitive) dado que si
						# se pone sin apostrofes marca error!
				cursor.execute("INSERT INTO documentos (`EmpresaNo`,`NoDocto`,\
											`Consecutivo`,`TipoDeDocumento`,\
											`TipoDeVenta`,`Asociado`,\
											`FechaCreacion`,`HoraCreacion`,\
											`UsuarioQueCreoDcto.`,`FechaUltimaModificacion`,\
											`HoraUltimaModificacion`,`UsuarioModifico`,\
											`Concepto`,`monto`,`saldo`,\
											`DescuentoAplicado`,`VtaDeCatalogo`,\
											`Cancelado`,`comisiones`,\
											`PagoAplicadoARemisionNo`,`Lo_recibido`\
											,`venta`,`idsucursal`,\
											`BloquearNotaCredito`) VALUES(%s,%s,%s,%s,%s,%s\
											,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
											%s,%s,%s,%s,%s);",(1,nuevo_docto+1,Nuevo_consec+1,\
												'Credito','Contado',id_socio,\
												fecha_hoy,hora_hoy,capturista,\
												fecha_hoy,hora_hoy,capturista,\
												"Crédito sobrante de Venta con remisión "+str(nuevo_docto),montocredito,montocredito,\
												0,False,False,\
												0,0,0,\
												0,sucursal_activa,False,))
				


			# PROCESA CREDITOS

			for k in datos_credito:
				
				if k is not None: # Procesa solo los registros con contenido
			
				
					no_docto_credito = k.get("no_docto_credito").encode('latin_1')

					monto_credito = k.get('monto_credito').encode('latin_1')


					# Verifica que el credito no haya sido aplicado en otra transaccion
					# mientras el registro estaba en memoria.

					cursor.execute("SELECT saldo from documentos where nodocto=%s",(no_docto_credito,))
					saldo_tmp = cursor.fetchone()
					
					if saldo_tmp[0] <= 0:

						CreditosPorAplicarSaldados  = True
					else:
						# Actualiza el saldo del credito y lo pone en cero para que no pueda volver
						# a aplicarse.
						cursor.execute("UPDATE documentos SET saldo=0,PagoAplicadoARemisionNo=%s where nodocto=%s;",(nuevo_docto,no_docto_credito,))



			# PROCESA CARGOS

			for l in datos_cargos:
				
				if l is not None: # Procesa solo los registros con contenido
			
				
					no_docto_cargo = l.get("no_docto_cargo").encode('latin_1')

					monto_cargo = l.get('monto_cargo').encode('latin_1')


					# Verifica que el cargo no haya sido aplicado en otra transaccion
					# mientras el registro estaba en memoria.

					cursor.execute("SELECT saldo from documentos where nodocto=%s",(no_docto_cargo,))
					saldo_tmp = cursor.fetchone()
					
					if saldo_tmp[0] <= 0:
					
						CargosPorAplicarSaldados = True
					else:
						# Actualiza el saldo del cargo y lo pone en cero para que no pueda volver
						# a aplicarse.
						cursor.execute("UPDATE documentos SET saldo=0 where nodocto=%s;",(no_docto_cargo,))


			# Hace un rollback si  hay pedidos cambiados, creditos o cargos ya aplicados, de otra
			# manera hace el commit a la base de datos.

		
			if pedidos_cambiados != 0 or CreditosPorAplicarSaldados or CargosPorAplicarSaldados:

				cursor.execute("ROLLBACK;")
			else:

				cursor.execute("COMMIT;")


		except DatabaseError as e:
		
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':'Error de base de datos: '+str(e),}
			print e
			error = True
		except InternalError as e:

			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':'Error interno: '+str(e),}
			print e
			error = True
		except TypeError as e:

			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':'Error interno: '+str(e),}
			print e
			error = True
		except IntegrityError as e:
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':'Error de integridad de BD: '+str(e),}
			error = True
		except OperationalError as e:
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':'Error operacional: '+str(e),}
			error = True
		except NotSupportedError as e:
	
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':'Error no soportado: '+str(e),}
			error = True
		except ProgrammingError as e:

			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':'Error de programacion: '+str(e),}
			error = True
		except:
			
			data = {'status_operacion':'fail','error':'Error no identificado.'}
			error = True

		cursor.close()

		# Si no hay error, nos devolvera la lista de pedidos cambiados
		# o bien un 'ok' y si hay error nos devolvera el mensaje de error.
		if not error:
			if pedidos_cambiados != 0 or CreditosPorAplicarSaldados or CargosPorAplicarSaldados:
				data={'status_operacion':'ok','error':'Venta no procesada ! algunos registros fueron ya modificados por otra transaccion !'}
			else:
				data={'status_operacion':'ok','nodocto':nueva_remision,'nueva_nota_credito':nueva_nota_credito,}
		return HttpResponse(json.dumps(data),content_type='application/json',)


def consultadsctos(request):
	''' Inicializa Variables '''

	Descuento  = 0.0
	Totaldscto = 0.0
	TotalRegistros = 0
	



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

			
			cursor.execute("SELECT a.idproveedor,p.razonsocial,sum(if(l.preciooriginal>l.precio,l.preciooriginal-l.precio,0)) as dscto from pedidoslines l inner join pedidosheader h on (h.empresano=1 and h.pedidono=l.pedido) inner join pedidos_status_fechas f on (f.empresano=1 and f.pedido=l.pedido and f.productono=l.productono and f.status='Facturado' and f.catalogo=l.catalogo and f.nolinea=l.nolinea) inner join articulo a on (a.empresano=1 and a.codigoarticulo=l.productono and a.catalogo=l.catalogo) inner join proveedor p on (p.empresano=1 and p.proveedorno=a.idproveedor) where f.fechamvto>=%s and f.fechamvto<=%s and h.idsucursal>=%s and h.idsucursal<=%s group by a.idproveedor; ",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			
			

			registros_venta = dictfetchall(cursor)

			elementos = len(registros_venta)

			


			"""cursor.execute("SELECT p.razonsocial,a.razonsocial from proveedor p inner join almacen a on (p.empresano=a.empresano and p.proveedorno=a.proveedorno) where p.proveedorno=%s;",(ped['prov_id'],))
			
			prov_alm = cursor.fetchone()"""

			if not registros_venta:
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_ventas.html',{'mensaje':mensaje,})

			else:

				
				for docto in registros_venta:
										
					
					Totaldscto = Totaldscto + float(docto['dscto'])
					
					if (float(docto['dscto']) != 0.0):
						TotalRegistros = TotalRegistros + 1
			
			mensaje ="Proveedores donde se otorgo descuentos == > "



			context = {'form':form,'mensaje':mensaje,'registros_venta':registros_venta,'TotalRegistros':TotalRegistros,'sucursal_nombre':sucursal_nombre,'Totaldscto':Totaldscto,'fechainicial':fechainicial,'fechafinal':fechafinal}	
		
			return render(request,'pedidos/lista_dsctos.html',context)

		
	else:

		form = Consulta_ventasForm()
	return render(request,'pedidos/consultadsctos.html',{'form':form,})

# RUTINA PARA GENERAR REPORTE DE DESGLOSE DE VENTA NETA  POR MARCAS

def consultavtasxproveedor(request):
	''' Inicializa Variables '''
	#pdb.set_trace()

	TotalRegVentas = 0
	TotalRegVtaDevMD = 0
	Totaldscto  = 0.0
	TotalVta = 0.0
	Totaldscto = 0.0
	TotalRegistros = 0
	TotalRegDev = 0
	TotalVtaDevMD = 0.0
	registros_devgral = 0.0
	registros_VtasDevMismodia = 0.0
	TotalDevGral = 0.0
	TotalCargos = 0.0
	TotalVtaCatalogos = 0.0

	



	mensaje =''
	if request.method == 'POST':

		form = Consulta_ventasForm(request.POST)

		if form.is_valid():

			sucursal = form.cleaned_data['sucursal']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']

			cursor=connection.cursor()


			# CREA TABLA TEMPORAL
			cursor.execute("DROP TEMPORARY TABLE IF EXISTS vtas_pro_tmp;")
			cursor.execute("CREATE TEMPORARY TABLE vtas_pro_tmp SELECT * FROM vtas_proveedor_imagenbase;")

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


			
			# TRAE VENTA Y DESCUENTOS

			#cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones-d.descuentoaplicado <= d.Saldo,0,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado) as VtaComisionSaldo,if(d.venta + d.comisiones - d.descuentoaplicado <= d.Saldo,d.venta+d.comisiones-d.descuentoaplicado,d.Saldo) as cred_aplicado FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))

			
			cursor.execute("SELECT a.idproveedor,\
				p.razonsocial,\
				sum(l.preciooriginal) as venta,\
				sum(if (l.preciooriginal>l.precio and ct.no_maneja_descuentos=0,l.preciooriginal-l.precio,0 )) as dscto\
				from pedidoslines l inner join pedidosheader h\
				on (h.empresano=1 and h.pedidono=l.pedido)\
				inner join pedidos_status_fechas f\
				on (f.empresano=1 and f.pedido=l.pedido\
				and f.productono=l.productono\
				and f.status='Facturado'\
				and f.catalogo=l.catalogo and f.nolinea=l.nolinea)\
				inner join articulo a\
				on (a.empresano=1 and a.codigoarticulo=l.productono\
				and a.catalogo=l.catalogo)\
				inner join proveedor p\
				on (p.empresano=1 and p.proveedorno=a.idproveedor)\
				inner join pedidoslinestemporada plt on (plt.empresano=l.empresano and plt.pedido=l.pedido and plt.productono=l.productono and plt.catalogo=l.catalogo and plt.nolinea=l.nolinea)\
				left join catalogostemporada ct on (ct.proveedorno=a.idproveedor and ct.periodo=CAST(SUBSTRING(l.catalogo,1,4) as UNSIGNED) and ct.Anio=plt.Temporada and ct.clasearticulo=l.catalogo)\
				inner join documentos doc on (l.empresano=doc.empresano and l.remisionno=doc.NoDocto)\
				where f.fechamvto>=%s and f.fechamvto<=%s\
				and h.idsucursal>=%s and h.idsucursal<=%s\
				group by a.idproveedor ; ",\
				(fechainicial,fechafinal,sucursalinicial,sucursalfinal,))
			
			registros_venta = dictfetchall(cursor)
			#print "descuentos:",registros_venta[3]
			
			elementos = len(registros_venta)

			# TRAE DEVOLUCIONES EN GENERAL
			'''cursor.execute("SELECT a.idproveedor,'',\
				sum(l.precio) as devgral,\
				0 from pedidoslines l inner join pedidosheader h\
				on (h.empresano=1 and h.pedidono=l.pedido)\
				inner join pedidos_status_fechas f\
				on (f.empresano=1 and f.pedido=l.pedido\
				and f.productono=l.productono and f.status='Devuelto'\
				and f.catalogo=l.catalogo and f.nolinea =  l.nolinea) inner join articulo a\
				on (a.empresano=1 and a.codigoarticulo=l.productono\
				and a.catalogo=l.catalogo) inner join proveedor p\
				on (p.empresano=1 and p.proveedorno=a.idproveedor)\
				where f.fechamvto>=%s and f.fechamvto<=%s\
				and h.idsucursal>=%s and h.idsucursal<=%s\
				group by a.idproveedor; ",\
				(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			
			registros_devgral = dictfetchall(cursor)'''

			#TRAE DEVOLUCIONES GRAL
			cursor.execute("SELECT art.idproveedor,'',sum(l.precio) as devgral,0\
			 from (SELECT psf.pedido,\
			 psf.productono,\
			 psf.nolinea,\
			 psf.catalogo,\
			 psf.fechamvto from\
			 pedidos_status_fechas as psf \
			 INNER JOIN pedidosheader as h \
			 ON h.pedidono=psf.pedido WHERE psf.status='Devuelto' and psf.fechamvto>= %s and psf.fechamvto<= %s and h.idSucursal>=%s and h.idSucursal<=%s) as t2\
			 INNER JOIN pedidos_status_fechas as t3 on\
			 (t2.pedido=t3.pedido and t2.productono=t3.productono\
			 and t2.nolinea=t3.nolinea and t2.catalogo=t3.catalogo)\
	         INNER JOIN pedidoslines as l\
	         on (l.pedido=t3.pedido and l.productono=t3.productono\
	         and l.catalogo=t3.catalogo and l.nolinea=t3.nolinea)\
	         INNER JOIN articulo as art\
	         on (art.codigoarticulo=t3.productono and art.catalogo=t3.catalogo)\
	         WHERE t3.status='Facturado'\
	         GROUP BY art.idproveedor;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,))

			registros_devgral = dictfetchall(cursor)




			if not registros_venta:

				pass
				
			else:

				cursor.execute("SELECT COUNT(*) as totrec FROM vtas_pro_tmp")
				totrectmp=dictfetchall(cursor)

				
				for registro in registros_venta:

					cursor.execute("UPDATE vtas_pro_tmp SET\
						ventas= %s,\
						venta_FD=0,\
						ventabruta=0,\
						descuento=%s,\
						devoluciones=0,\
						ventaneta=0,nombreprov=%s where idproveedor=%s;",\
					 	(Decimal(registro['venta']),Decimal(registro['dscto']),\
					 		registro['razonsocial'],registro['idproveedor']))					 
                        										
					TotalVta   = TotalVta + float(registro['venta'])
					Totaldscto = Totaldscto + float(registro['dscto'])
					
					if (float(registro['venta']) != 0.0):
						TotalRegVentas = TotalRegVentas + 1


			if not registros_devgral:
				
				pass

			else:				

				for registro in registros_devgral:

					cursor.execute("UPDATE vtas_pro_tmp\
						SET devoluciones=%s WHERE idproveedor=%s;",\
					 			(registro['devgral'],registro['idproveedor']))
										
					
					TotalDevGral = TotalDevGral + float(registro['devgral'])
					
					if (float(registro['devgral']) != 0.0):
						TotalRegDev = TotalRegDev + 1



			""" 			
			if not registros_VtasDevMismodia:
				
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_vtasxproveedor.html',{'mensaje':mensaje,})


			else:			

				for registro in registros_VtasDevMismodia:

					cursor.execute("UPDATE vtas_pro_tmp\
						SET venta_FD=%s WHERE idproveedor=%s;",\
					 			(registro['VtasDevMD'],registro['idproveedor']))
										

									
					
					TotalVtaDevMD = TotalVtaDevMD + float(registro['VtasDevMD'])
					
					if (float(registro['VtasDevMD']) != 0.0):
						TotalRegVtaDevMD = TotalRegVtaDevMD + 1 """

			cursor.execute("UPDATE vtas_pro_tmp as t INNER JOIN proveedor as p on t.idproveedor=p.proveedorno SET t.nombreprov=p.razonsocial;")
			cursor.execute("DELETE FROM vtas_pro_tmp WHERE  ventas = 0 and  descuento =0 and devoluciones = 0 and ventaneta = 0;")
			cursor.execute("UPDATE vtas_pro_tmp SET ventabruta = ventas + venta_FD;")
			cursor.execute("UPDATE vtas_pro_tmp SET ventaneta = ventabruta - descuento - devoluciones;")
			
			mensaje =" "

			cursor.execute("SELECT * FROM vtas_pro_tmp;")
			vtasresult =  dictfetchall(cursor)


			cursor.execute("SELECT SUM(ventas) as tot_vtas,SUM(venta_FD) as tot_ventaFD,SUM(ventabruta) as tot_ventabruta, SUM(descuento) as tot_descuento,SUM(devoluciones) as tot_devoluciones,SUM(ventaneta) as tot_ventaneta FROM vtas_pro_tmp;")	
			totales = dictfetchall(cursor)
			for tot in totales:
				tot_vtas = tot['tot_vtas']
				tot_ventaFD = tot['tot_ventaFD']
				tot_ventabruta = tot['tot_ventabruta']
				tot_descuento = tot['tot_descuento']
				tot_devoluciones = tot['tot_devoluciones']
				tot_ventaneta = tot['tot_ventaneta']


			cursor.execute("SELECT d.Monto,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.Concepto FROM documentos d  WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,))
			
			

			registros_vtacomis_vtacatal = dictfetchall(cursor)


			for docto in registros_vtacomis_vtacatal:
										
					if (docto['Cancelado'] == '\x00'):  # pregunta si cancelado es '0' en hex o bien falso
						
						esvta =docto['Concepto'].strip()
						if esvta == 'Venta':
														
							TotalCargos = TotalCargos + float(docto['comisiones'])	
											
						if docto['VtaDeCatalogo'] == '\x01' :
							TotalVtaCatalogos = TotalVtaCatalogos + float(docto['Monto'])


			# SI TOTALES SON None, LES ASIGNA UN CERO YA QUE EN EL CONTEXT
			# HABRIA PROBLEMAS CON LA FUNCION FLOAT(), DADO QUE NO ACEPTA UN None COMO PARAMETRO.
			if tot_vtas is None:
				tot_vtas = 0
			if tot_ventabruta is None:
				tot_ventabruta = 0
			if tot_ventaFD is None:
				tot_ventaFD = 0
			if tot_ventaneta is None:
				tot_ventaneta = 0
			if tot_descuento is None:
				tot_descuento = 0
			if tot_devoluciones is None:
				tot_devoluciones =0
			

			

			context = {'form':form,'mensaje':mensaje,'vtasresult':vtasresult,'TotalRegistros':TotalRegistros,'tot_vtas':float(tot_vtas),'tot_ventaFD':float(tot_ventaFD),'tot_ventabruta':float(tot_ventabruta),'tot_descuento':float(tot_descuento),'tot_devoluciones':float(tot_devoluciones),'tot_ventaneta':float(tot_ventaneta),'TotalCargos':TotalCargos,'TotalVtaCatalogos':TotalVtaCatalogos,'fechainicial':fechainicial,'fechafinal':fechafinal,'sucursal_nombre':sucursal_nombre,'sucursalinicial':sucursalinicial,'sucursalfinal':sucursalfinal,}	
		
			return render(request,'pedidos/lista_vtasxproveedor.html',context)

		
	else:

		form = Consulta_ventasForm()
	return render(request,'pedidos/consultavtasxproveedor.html',{'form':form,})


# DETALLE DE LA VTA X PROVEEDOR.

def detallevtaxproveedor(request,idproveedor,fechainicial,fechafinal,sucursalinicial,sucursalfinal):

	#pdb.set_trace()
	cursor=connection.cursor()

	totalvta = 0

	cursor.execute("SELECT razonsocial from proveedor WHERE proveedorno=%s;",(idproveedor,))
	proveedor_nombre = cursor.fetchone()

	proveedor=proveedor_nombre[0]

	try:
		
		cursor.execute("SELECT h.pedidono,l.remisionno as remision_num,h.asociadono,h.fechapedido,h.horapedido,a.idmarca, a.idestilo,idcolor,a.talla,l.preciooriginal,l.observaciones from pedidoslines l inner join pedidosheader h on (h.empresano=1 and h.pedidono=l.pedido) inner join pedidos_status_fechas f on (f.empresano=1 and f.pedido=l.pedido and f.productono=l.productono and f.status='Facturado' and f.catalogo=l.catalogo and f.nolinea=l.nolinea) inner join articulo a on (a.empresano=1 and a.codigoarticulo=l.productono and a.catalogo=l.catalogo) inner join proveedor p on (p.empresano=1 and p.proveedorno=a.idproveedor) inner join pedidoslinestemporada plt on (plt.empresano=l.empresano and plt.pedido=l.pedido and plt.productono=l.productono and plt.catalogo=l.catalogo and plt.nolinea=l.nolinea) where f.fechamvto>=%s and f.fechamvto<=%s and h.idsucursal>=%s and h.idsucursal<=%s and a.idproveedor=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,idproveedor,))
		'''cursor.execute("SELECT l.preciooriginal from pedidoslines l inner join pedidosheader h on (h.empresano=1 and h.pedidono=l.pedido) inner join pedidos_status_fechas f on (f.empresano=1 and f.pedido=l.pedido and f.productono=l.productono and f.status='Facturado' and f.catalogo=l.catalogo and f.nolinea=l.nolinea) inner join articulo a on (a.empresano=1 and a.codigoarticulo=l.productono and a.catalogo=l.catalogo) inner join proveedor p on (p.empresano=1 and p.proveedorno=a.idproveedor) inner join pedidoslinestemporada plt on (plt.empresano=l.empresano and plt.pedido=l.pedido and plt.productono=l.productono and plt.catalogo=l.catalogo and plt.nolinea=l.nolinea)\
		inner join catalogostemporada ct on (ct.proveedorno=a.idproveedor and ct.periodo=CAST(SUBSTRING(l.catalogo,1,4) as UNSIGNED) and ct.Anio=plt.Temporada and ct.clasearticulo=l.catalogo)\
		where f.fechamvto>=%s and f.fechamvto<=%s and f.horamvto>='12:00:01' and f.horamvto<='13:59:59' and h.idsucursal>=%s and h.idsucursal<=%s and a.idproveedor=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,idproveedor,))'''





		"""cursor.execute("SELECT h.pedidono,\
			l.remisionno as remision_num,\
			h.asociadono,\
			h.fechapedido,\
			h.horapedido,\
			a.idmarca,\
			a.idestilo,\
			a.idcolor,\
			a.talla,\
			l.preciooriginal,\
			from pedidoslines l inner join pedidosheader h\
			on (h.empresano=1 and h.pedidono=l.pedido)\
			inner join pedidos_status_fechas f\
			on (f.empresano=1 and f.pedido=l.pedido\
			and f.productono=l.productono and f.status='Facturado'\
			and f.catalogo=l.catalogo)\
			inner join articulo a on (a.empresano=1 and a.codigoarticulo=l.productono\
			and a.catalogo=l.catalogo)\
			inner join proveedor p on (p.empresano=1 and p.proveedorno=a.idproveedor)\
			where f.fechamvto>=%s and f.fechamvto<=%s\
			and h.idsucursal>=%s and h.idsucursal<=%s and a.idproveedor=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,idproveedor,))"""
			
		vtasresult = dictfetchall(cursor)

		# DETERMINA EL TOTAL DE LA VENTA
		cursor.execute("SELECT l.preciooriginal from pedidoslines l inner join pedidosheader h on (h.empresano=1 and h.pedidono=l.pedido) inner join pedidos_status_fechas f on (f.empresano=1 and f.pedido=l.pedido and f.productono=l.productono and f.status='Facturado' and f.catalogo=l.catalogo and f.nolinea=l.nolinea) inner join articulo a on (a.empresano=1 and a.codigoarticulo=l.productono and a.catalogo=l.catalogo) inner join proveedor p on (p.empresano=1 and p.proveedorno=a.idproveedor) inner join pedidoslinestemporada plt on (plt.empresano=l.empresano and plt.pedido=l.pedido and plt.productono=l.productono and plt.catalogo=l.catalogo and plt.nolinea=l.nolinea) where f.fechamvto>=%s and f.fechamvto<=%s and h.idsucursal>=%s and h.idsucursal<=%s and a.idproveedor=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,idproveedor,))

		total_registros = dictfetchall(cursor)
		
		for reg in total_registros:
			totalvta = totalvta + float(reg['preciooriginal'])



	except DatabaseError as e:
		print (e)
		vtasresult =0

	context = {'vtasresult':vtasresult,'totalvta':totalvta,'proveedor':proveedor,'fechainicial':fechainicial,'fechafinal':fechafinal,}	


	return render(request,'pedidos/detalle_vtasxproveedor.html',context)









# VERICA LA EXISTENCIA DEL USUARIO EN 
# LA TABLA DE USUARIOS

def verifica_existencia_usr(psw_paso):
	#pdb.set_trace()

	cursor=connection.cursor()
	cursor.execute('SELECT usuariono FROM usr_extend where pass_paso=%s;',(psw_paso,))
	num = cursor.fetchone()

	cursor.close()

	if num is None:
		
		return 0 # Si no existe retorna un 0
	else:
		return num[0] # Si existe retorna el numero de empleado

# VERIFICA QUE EL USUARIO TENGA DERECHOS


def verifica_derechos_usr(num_usr_valido,usr_derecho):
	#pdb.set_trace()

	cursor=connection.cursor()
	cursor.execute('SELECT derechono FROM usuario_derechos where usuariono=%s and derechono=%s;',(num_usr_valido,usr_derecho))
	derechono = cursor.fetchone()


	cursor.close()
	if derechono is None:
		derecho = 0
	else:
		derecho = 1
	return(derecho)

def valida_usr(request):
	#pdb.set_trace()

	try:	
		socio_zapcat = request.session['socio_zapcat']	
	except KeyError as e:
		error_msg ="Error  1001: Error al validar el usuario en session, aparentemente su sesión se perdió, cierre completamente su navegador, reabralo y accese nuevamente al sistema !"
		return render(request,'pedidos/error.html',{'error_msg':error_msg,})



	tiene_derecho = 0 # asume que no tiene derecho
	psw_paso = request.GET.get('psw_paso')
	usr_derecho = int(request.GET.get('usr_derecho').encode('latin_1'))


	num_usr_valido = verifica_existencia_usr(psw_paso) # verifica si existe

	if num_usr_valido != 0:
		tiene_derecho = verifica_derechos_usr(num_usr_valido,usr_derecho) # Si existe verifica que tenga el derecho solicitado


	data = {'num_usr_valido':num_usr_valido,'tiene_derecho':tiene_derecho,}
	return HttpResponse(json.dumps(data),content_type='application/json',)




'''def modifica_cierre(request,id):
	#pdb.set_trace()

	id_cierre = id

	cursor=connection.cursor()

	cursor.execute("SELECT id,referencia,total_articulos,ColocadoVia,NumPedido,Paqueteria,NoGuia,TotArtRecibidos FROM prov_ped_cierre where id=%s;",(id,) )
	

	form = CierresForm(request.POST)
		
	if form.is_valid():

				# Agregue los siguientes dos if's por si entrega registros en cero, deben ir ???
		if cursor.fetchone():
			print "DATOS CIERRE:"

			datos_cierre = cursor.fetchone()
			for j  in range(0,len(datos_cierre)):
				
				form.id

				print datos_cierre[j]
		else:
			datos_cierre = ()
		
			data = json.dumps(l,cls=DjangoJSONEncoder)
			return HttpResponse(data,content_type='application/json')
		else:
			raise Http404'''

def modifica_cierre(request,id):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	msg = ''
	form = CierresForm(request.POST)
	if request.method == 'POST':
		
		if form.is_valid():
			#vtadecatalogo = request.POST.get('vtadecatalogo').encode('latin_1')
			id = request.POST.get('id')
			referencia = request.POST.get('referencia')
			pedidonum = request.POST.get('pedidonum')
			total_articulos = request.POST.get('total_articulos')
			total_art_recibidos = request.POST.get('total_art_recibidos')
			paqueteria = request.POST.get('paqueteria')
			noguia = request.POST.get('noguia')
			colocado_via = request.POST.get('colocado_via')
	
			
			cursor =  connection.cursor()
			try:

				cursor.execute('START TRANSACTION')
				cursor.execute('UPDATE prov_ped_cierre SET referencia=%s,NumPedido=%s,total_articulos=%s,TotArtRecibidos=%s,Paqueteria=%s,NoGuia=%s,ColocadoVia=%s WHERE id=%s;',(referencia,pedidonum,total_articulos,total_art_recibidos,paqueteria,noguia,colocado_via,id,))
				cursor.execute("COMMIT;")
				return HttpResponseRedirect(reverse('pedidos:seleccion_cierre_rpte_cotejo'))
			except ValueError as e:
				print e

			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				msg = 'Error en base de datos !'
				return HttpResponse('<h3>Ocurrio un error en la base de datos</h3><h2>{{e}}</h2>')

		
	print form.errors
				
	cursor =  connection.cursor()
	cursor.execute("SELECT id,referencia,NumPedido,total_articulos,ColocadoVia,Paqueteria,NoGuia,TotArtRecibidos FROM prov_ped_cierre where id=%s;",(id,) )

	datos_cierre =  cursor.fetchone()
	
		
	referencia = datos_cierre[1]
	pedidonum = datos_cierre[2]
	total_articulos = datos_cierre[3]
	total_art_recibidos = datos_cierre[7]
	paqueteria = datos_cierre[5]
	noguia = datos_cierre[6]
	colocado_via = datos_cierre[4]
	msg = "Existen campos vacios, por favor llene todo el formulario !"
	cursor.close()

	form =  CierresForm(initial= {'id':id,'referencia':referencia,'total_articulos':total_articulos,'colocado_via':colocado_via,'pedidonum':pedidonum,'paqueteria':paqueteria,'noguia':noguia,'total_art_recibidos':total_art_recibidos,})	
	return render(request,'pedidos/modifica_cierre.html',{'id':id,'form':form,'referencia':referencia,'total_articulos':total_articulos,'colocado_via':colocado_via,'pedidonum':pedidonum,'paqueteria':paqueteria,'noguia':noguia,'total_art_recibidos':total_art_recibidos,'msg':msg})




def imprime_venta(request):
	#pdb.set_trace()
	
	is_staff = request.session['is_staff']

	if request.method =='GET':
		p_num_venta = request.GET.get('p_num_venta') 
		p_num_credito = request.GET.get('p_num_credito')# p_num_pedido realmente almacena el numero  de documento (remision), solo que se dejo asi para no mover el codigo.
	else:
		
		p_num_venta = request.POST.get('p_num_venta')
		p_num_credito = request.POST.get('p_num_credito')

	# se encodifica como 'latin_1' ya que viene como unicode.

	#p_num_venta = p_num_venta.encode('latin_1')
	
	
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

	#Trae informacion del pedido.
	cursor =  connection.cursor()
	#pdb.set_trace()

	datos_documento,pedido_detalle,usuario,NotaCredito = None,None,None,0

	try:
		cursor.execute("SELECT asociado,venta,comisiones,saldo,descuentoaplicado,Lo_Recibido,idsucursal,UsuarioModifico,FechaCreacion,HoraCreacion,monto,tipodedocumento,concepto FROM documentos where nodocto=%s;",(p_num_venta,))
		datos_documento = cursor.fetchone()	

		cursor.execute("SELECT appaterno,apmaterno,nombre FROM asociado where asociadono=%s;",(datos_documento[0],))
		datos_socio =  cursor.fetchone()

		cursor.execute("SELECT l.precio,l.NoNotaCreditoPorPedido,l.Observaciones,l.Status,a.pagina,a.idmarca,a.idestilo,a.idcolor,a.talla,a.catalogo,so.nombre,so.appaterno,so.apmaterno,suc.nombre,l.PrecioOriginal FROM pedidoslines l INNER JOIN articulo a ON (l.empresano = a.empresano and l.productono = a.codigoarticulo and l.catalogo = a.catalogo) INNER JOIN asociado so ON (so.empresano=1 and so.asociadono = %s) INNER JOIN sucursal suc ON (suc.empresano=1 and suc.sucursalno = %s) WHERE l.RemisionNo = %s;",(datos_documento[0],datos_documento[6],p_num_venta))
		pedido_detalle = dictfetchall(cursor)

		cursor.execute("SELECT NoDocto,FechaCreacion,HoraCreacion,monto,concepto FROM documentos where PagoAplicadoARemisionNo=%s;",(p_num_venta,))
		creditos_aplicados = cursor.fetchall()	


		# la siguiente variable  se asigna para ser pasada a la rutina que 
		# imprimira la nota de credito ( en caso de que exista )
		if pedido_detalle is not(None):

			for elem in  pedido_detalle:
				NotaCredito = elem['NoNotaCreditoPorPedido']
				if elem['talla'] != 'NE':
					talla = elem['talla']
				else:
					talla = elem['Observaciones']
		
		cursor.execute("SELECT usuario from usuarios where usuariono=%s;",[datos_documento[7]])
		
		usuario = cursor.fetchone()

		mensaje=""
		
		if usuario is None:
			usuario=['ninguno']
		if (not datos_documento or not pedido_detalle):
			mensaje = "No se encontro informacion del pedido !"

	except DatabaseError as e:
		print "Ocurrio de base datos"
		print e
		
		mensaje = "Ocurrio un error de acceso a la bd. Inf. tecnica: "
	except Exception as e:
		mensaje = "Ocurrio un error desconocido. Inf. tecnica: "
		print "error desconocido: "
		print e
		
	cursor.close()

	linea = 2350

	
	
    # Create a file-like buffer to receive PDF data.
	buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
	#p = canvas.Canvas(buffer)
	pagesize = (8.5*inch, 33*inch)
	p = canvas.Canvas(buffer,pagesize=pagesize)
	#p.setPageSize("inch")

	#p.setFont("Helvetica",10)
	#p.drawString(1,linea,inicializa_imp)
	

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
	#p.drawString(20,810,mensaje)

	if ((datos_documento or pedido_detalle) and usuario):

		tipodedocumento = datos_documento[11]



		p.drawString(45,linea, request.session['cnf_razon_social'])
		linea -=20
		p.drawString(45,linea," SUC. "+request.session['sucursal_nombre'])
		linea -=20
		p.setFont("Helvetica",12)
		p.drawString(20,linea, "*** "+("VENTA" if tipodedocumento=='Remision' else "CARGO")+" NUM."+p_num_venta+" ***")
		linea -=20
		p.setFont("Helvetica",8)
		p.drawString(20,linea,request.session['sucursal_direccion'])
		linea -= 10
		p.drawString(20,linea,"COL. "+request.session['sucursal_colonia'])
		linea -= 10
		p.drawString(20,linea,request.session['sucursal_ciudad']+", "+request.session['sucursal_estado'])
		linea -= 10
		p.drawString(20,linea,datos_documento[8].strftime("%d-%m-%Y")+' '+datos_documento[9].strftime("%H:%M:%S")+' '+'Tel '+str(request.session['sucursal_telefono']))
		#p.drawString(100,linea,)
		linea -= 10
		p.drawString(20,linea,"CREADO POR: ")
		#p.drawString(100,linea,request.user.username)
		p.drawString(100,linea,usuario[0])
		linea -= 10
		p.drawString(20,linea,"SOCIO NUM: ")
		type(datos_documento[0])
		p.drawString(100,linea,str(datos_documento[0]))
		linea -= 10
		var_nombre = datos_socio[0]+' '+datos_socio[1]+' '+datos_socio[2]
		p.drawString(20,linea,var_nombre[0:26])
		linea -= 10
		p.drawString(20,linea,"--------------------------------------------------")

		linea -= 10
		
		p.drawString(20,linea,"Descrpcion")
		p.drawString(125,linea,"Precio")
		linea -= 10
		p.drawString(20,linea,"--------------------------------------------------")
		linea -= 10


		#p.setFont("Helvetica",8)
		i,paso=1,linea-10

		""" Ojo en la siguiente linea no cambiar el string 'Venta' en la comparacion
		ya que python es case sensitive """
	
		if tipodedocumento=='Cargo' or (tipodedocumento == 'Remision' and datos_documento[12] != 'Venta'):

			p.drawString(20,paso-10,datos_documento[12].upper()[0:25])
			p.drawString(125,paso-19,'$ '+str(datos_documento[10]))
		else:


			for elemento in pedido_detalle:

				if elemento['talla'] != 'NE':
					talla = elemento['talla']
				else:
					talla = elemento['Observaciones']
				
				p.drawString(20,paso,elemento['pagina']+' '+elemento['idmarca']+' '+elemento['idestilo']) 
				p.drawString(20,paso-10,elemento['idcolor'][0:7]+' '+talla)
				p.drawString(125,paso-12,'$ '+str(elemento['PrecioOriginal']))
				paso -= 20
			p.setFont("Helvetica-Bold",8)	
			p.drawString(20,paso-10,"Subtotal ==>")
			p.drawString(125,paso-10,'$ '+str(datos_documento[1]))
			p.setFont("Helvetica",8)
			p.drawString(20,paso-20,"+ Cargo ==>")
			p.drawString(125,paso-20,'$ '+str(datos_documento[2]))
			p.drawString(20,paso-30,"-  Descuento ==>")
			p.drawString(125,paso-30,'$ '+str(datos_documento[4]))

			p.drawString(125,paso-40,'-------------')
			p.setFont("Helvetica-Bold",8)
			p.drawString(20,paso-50,'Total ==>')
			p.drawString(125,paso-50,'$ '+str(datos_documento[1]+datos_documento[2]-datos_documento[4]))
			p.setFont("Helvetica",8)
			p.drawString(20,paso-60,"-  Credito ==>")
			p.drawString(125,paso-60,'$ '+str(datos_documento[3]))
			p.setFont("Helvetica-Bold",8)
			p.drawString(20,paso-70,"Importe a pagar ==>")
			
			importe_a_pagar = 0 if datos_documento[10]<0 else datos_documento[10]
			p.drawString(125,paso-70,'$ '+str(importe_a_pagar))
			p.setFont("Helvetica",8)

			p.drawString(20, paso-90,"Su pago ==>")
			p.drawString(125,paso -90, '$'+str(datos_documento[5]))
			p.drawString(20, paso-100,"Cambio ==>")
			p.drawString(125,paso -100,'$'+str(0 if datos_documento[5]-importe_a_pagar<=0 else datos_documento[5]-importe_a_pagar))


		compras = calcula_compras_socio_por_proveedor(datos_documento[0],datos_documento[8],1,0,'19010101','19010101')	
		#pdb.set_trace()

		print "RASTREANDO EN RUTINA DE IMPRESION VEENTA"
		#p.setFont("Helvetica",6)	


		
		p.drawString(20,paso-120,"SUS COMPRAS DE MES:")
		p.drawString(20,paso-130,"Catalogo")
		p.drawString(55,paso-130,"Compra")
		p.drawString(86,paso-130,"Dev.")
		p.drawString(117,paso-130,"Compra Neta")

		
		p.drawString(20,paso-140,"-"*50)
		
		linea=paso-150
		for compra in compras:
			if compra['ventabruta']-compra['descuento']-compra['devoluciones']>0:
			
				p.drawString(20,linea,str(compra['nombreprov'])[:7])
				p.drawString(55,linea,str(compra['ventabruta']-compra['descuento']))
				p.drawString(86,linea,str(compra['devoluciones'] if compra['ventabruta']-compra['descuento']>compra['devoluciones'] else 0))
				p.drawString(117,linea,str((compra['ventabruta']-compra['descuento']-compra['devoluciones']) if compra['ventabruta']-compra['descuento']>compra['devoluciones'] else 0))
				linea-=10

		paso = linea

		p.setFont("Helvetica",8)	

		p.drawString(20,paso-10,"Gracias por su compra !!!" if tipodedocumento=='Remision' else " ")
		p.drawString(20,paso-20,"Para sugerencias o quejas")
		p.drawString(20,paso-30,"llame al 867 132 9697")




		if creditos_aplicados:
			p.drawString(20,paso-50,"Notas de credito aplicadas:")
			p.drawString(20,paso-60,"--------------------------------------------------")
			linea -= 10
			p.drawString(20,paso-70,"Num.")
			p.drawString(55,paso-70,"Concepto")
			p.drawString(125,paso-70,"Monto")
			linea -= 10
			p.drawString(20,paso-80,"--------------------------------------------------")
			linea = paso-100

			for elemento in creditos_aplicados:
				p.drawString(20,linea,str(elemento[0]))
				p.drawString(55,linea,elemento[4][0:12])
				p.drawString(125,linea,'$ '+str(elemento[3]))
				linea -= 10 

		linea -= 20
		#linea -= 110

		




	#pdb.set_trace()	
	if p_num_credito != u'0':

		imprime_documento(p_num_credito,'Credito',False,request.session['cnf_razon_social'],request.session['cnf_direccion'],request.session['cnf_colonia'],request.session['cnf_ciudad'],request.session['cnf_estado'],p,buffer,response,True,linea,request)
	else:
		print "se vino por acaa.."
	# Close the PDF object cleanly, and we're done.

		p.showPage()
		p.save()


		pdf = buffer.getvalue()
		buffer.close()

		response.write(pdf)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    #return FileResponse(buffer, as_attachment=True,filename='hello.pdf')
	#return response
	return response



# SELECCION DEL CRITERIOS PARA DEVOLUCIONES QUE HACE CLIENTE
@login_required(login_url = "/pedidos/acceso/")
def devolucion_socio(request):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..

	
	mensaje = " "
	reg_encontrados = 0

	# elimina cualquier registro de la session.
	session_id = request.session.session_key
	# Asigna is_staff para validacines
	is_staff = request.session['is_staff']


	
	 
	if request.method == 'POST':

		form = Crea_devolucionForm(request.POST)

		if form.is_valid():

			socio = request.POST.get('Socio')
			tipoconsulta =  request.POST.get('tipoconsulta')
			fechainicial = request.POST.get('fechainicial')
			finicial =datetime.strptime(fechainicial, "%d/%m/%Y").date()
			fechafinal =request.POST.get('fechafinal')
			ffinal = datetime.strptime(fechafinal, "%d/%m/%Y").date()
			
			if tipoconsulta ==  u'1':
				tc = 'Facturado'
			else:
				tc = 'Aqui'
			
			cursor = connection.cursor()

			try:

				cursor.execute("SELECT appaterno,apmaterno,nombre FROM asociado WHERE asociadono=%s;",(socio,))
				nombre_socio =  cursor.fetchone()

				
				if nombre_socio is None:
					
					form = Crea_devolucionForm()
					print form
					return render(request,'pedidos/DevolucionSocio.html',{'form':form,'mensaje':"Socio Inexistente !",'is_staff':is_staff,})	

				else:

					cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,l.status,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,p.idSucursal,l.Observaciones,suc.nombre,psf.fechamvto FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) LEFT JOIN pedidos_status_fechas psf on (psf.empresano=l.empresano and psf.pedido=l.pedido and psf.productono=l.productono and psf.nolinea=l.nolinea and psf.status='Aqui') INNER JOIN pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN sucursal suc on (p.idSucursal=suc.SucursalNo) WHERE e.empresano=1 and p.asociadono=%s and psf.fechamvto>=%s and psf.fechamvto<=%s and  l.Status=%s order by a.idestilo;",(socio,finicial,ffinal,tc))
					#cursor.execute("SELECT e.Pedido,e.ProductoNo,e.Catalogo,e.NoLinea,l.status,p.FechaPedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,a.talla,l.precio,p.idSucursal,l.Observaciones,suc.nombre FROM pedidos_encontrados e  INNER JOIN  pedidoslines l on ( e.EmpresaNo=l.EmpresaNo and e.Pedido=l.Pedido and e.ProductoNo=l.ProductoNo and e.Catalogo=l.catalogo and e.NoLinea=l.nolinea ) INNER JOIN  pedidosheader p ON (e.EmpresaNo= p.EmpresaNo and e.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN sucursal suc on (p.idSucursal=suc.SucursalNo) WHERE e.empresano=1 and p.asociadono=%s and p.fechacreacion>=%s and p.fechacreacion<=%s and  l.Status=%s order by a.idestilo;",(socio,finicial,ffinal,tc))

			except DatabaseError as e:
				print "Error base de datos "+str(e)


			if cursor:

				registros = dictfetchall(cursor)
				cursor.close()
				mensaje = "Devolucion de articulos con status de " + tc		
				return render(request,'pedidos/muestra_registros_devolver.html', {'registros':registros,'mensaje':mensaje,'is_staff':is_staff,'socio':socio, 'nombre_socio':nombre_socio[0]+' '+nombre_socio[1]+' '+nombre_socio[2],'tipoconsulta':tipoconsulta})

				
			else:
				mensaje='No se encontraron registros con estos parametros !'
				cursor.close()
				
				return render(request,'pedidos/DevolucionSocio.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})



		else:

			print form.non_field_errors
			#form = SeleccionCierreRecepcionForm()
			return render(request,'pedidos/DevolucionSocio.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})
				
	form = Crea_devolucionForm()
	print form
	return render(request,'pedidos/DevolucionSocio.html',{'form':form,'mensaje':mensaje,'is_staff':is_staff,})	


# PROCESAR DEVOLUCIO DE SOCIO


def procesar_devolucion_socio(request):

	#pdb.set_trace()
	# rutina para grabar header y lines 
	def graba_header_lines():

		cursor.execute("UPDATE pedidosheader SET FechaUltimaModificacion=%s,horamodicacion=%s WHERE EmpresaNo=1 and pedidono=%s;",[fecha_hoy,hora_hoy,pedido])							
		cursor.execute("UPDATE pedidoslines SET status=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(nuevo_status_pedido,pedido,productono,catalogo,nolinea))
		return


	contador_productos_recibidos = 0
	nuevo_credito = 0




	if request.is_ajax()  and request.method == 'POST':
		# Pasa a una variable la tabla  recibida en json string
		TableData = request.POST.get('TableData')
		
		# carga la tabla ( la prepara con el formato de lista adecuado para leerla)
		datos = json.loads(TableData)

		capturista = request.session['socio_zapcat']
		sucursal = request.session['sucursal_activa']
		
		socio = request.POST.get('socio')

		psw_paso = request.POST.get('psw_paso')
		#almacen = request.POST.get('almacen')
		#almacen = almacen.encode('latin_1')
		tipoconsulta = request.POST.get('tipoconsulta')
		

		#marcartodo_nollego = request.POST.get('marcartodo_nollego')
		#cierre = request.POST.get('cierre').encode('latin_1')
		#nueva_fecha_llegada = request.POST.get('nueva_fecha_llegada').encode('latin_1')
		'''
		if nueva_fecha_llegada == u'None': 

 			f_convertida = '1901/01/01'
 		else:
 			f_convertida = datetime.strptime(nueva_fecha_llegada, "%d/%m/%Y").strftime("%Y%m%d")
			#f_convertida = datetime.strptime(nueva_fecha_llegada, "%d/%m/%Y").date()
		'''
		cursor = connection.cursor()

		''' INICIALIZACION DE VARIABLES '''

		pedidos_cambiados = 0 # inicializa contador de pedidos que sufrieron cambios entre la lectura inicial y el commit.
		
		nuevo_status_pedido = '' # variable que servira para  guardar el status de pedido segun se vayan cumpliendo condiciones,
							# posteriomente se utilizara par actualizar el status del pedido en pedidoslines y pedidos_status_confirmacion.

		error = False

		''' FIN DE INCIALIZACION DE VARIABLES '''


		# Se convierte la fecha de hoy a formatos manejables para insertarlos en el registro.
		hoy = datetime.now()
		fecha_hoy = hoy.strftime("%Y-%m-%d")
		hora_hoy = hoy.strftime("%H:%M:%S") 

		cursor.execute("SELECT usuariono FROM usr_extend WHERE pass_paso=%s;",(psw_paso,))
		usr_existente = cursor.fetchone()
		usr_existente = usr_existente[0]

		cursor.execute("START TRANSACTION;")



		"""cursor.execute("SELECT sucursalno from asociado WHERE EmpresaNo=1 and asociadono=%s;",(socio,) )
		registro = cursor.fetchone()
		sucursal = registro[0]"""


		# Se trae datos para revisar si procede el cobro de comision por no recoger calazado en tiempo.
		if tipoconsulta == u'2':		
			cursor.execute("SELECT maxdiasextemp,ComisionPorCalzadoNoRecogido from configuracion WHERE EmpresaNo=1 limit 1;")
			datos_extemporaniedad = cursor.fetchone()
			maxdiasextemp = datos_extemporaniedad[0]
			cuotadiasextemp = datos_extemporaniedad[1]
			total_comisiones_extemporaneas = Decimal(0.0)


        # Recupera cada diccionario y extrae los valores de la llave a buscar.
		
		try:
			total_devuelto_dinero = Decimal(0.0) # Inicializa acumulador de dinero a devolver
			
			for j in datos:
							
				pedido = j.get("Pedido").encode('latin_1')

				productono = j.get('ProductoNo').strip()
				catalogo =j.get('Catalogo').strip()
				nolinea = j.get('Nolinea').encode('latin_1')
				version_original_pedidos_lines = j.get('status').strip() # Traemos version anterior del registro pedidoslines, para esto usamos el campo 'status' con el que hacemos una comparacion con una nueva lectura al mismo para ver si cambio, no lo pasamos por encode (se queda en utf)
				incidencia = j.get('incidencia').encode('latin_1')
				
				# Comienza acceso a BD.

				# Se trae la fecha en que se recibio el pedido para utlizarla para
				# calcular si se aplica la cuota por extemporaneidad
				cursor.execute("SELECT fechamvto from pedidos_status_fechas WHERE EmpresaNo=1 and Pedido=%s and  ProductoNo=%s and Catalogo=%s and NoLinea=%s and status='Aqui';",(pedido,productono,catalogo,nolinea))
				registro = cursor.fetchone()
				f_fechamvto = registro[0]

		
				# verifica version actual pedidoslines y de una vez se trae el estatus actual para ser mostrado en caso de que la version actual difiera de la anterior
				cursor.execute("SELECT l.status,l.precio,a.idestilo,a.idcolor,a.talla from pedidoslines l inner join articulo a on (l.empresano=a.empresano and l.catalogo = a.catalogo and l.productono=a.CodigoArticulo) WHERE l.EmpresaNo=1 and l.Pedido=%s and  l.ProductoNo=%s and l.Catalogo=%s and l.NoLinea=%s;",(pedido,productono,catalogo,nolinea))
				registro = cursor.fetchone()

				# Crea variables de  version actual asi como el actual_estatus para pedidoslines
				
				version_actual_pedidos_lines =  registro[0].strip()
				
				# Si las versiones no concuerdan crea contador de pedidos_cambiados y sus lista respectiva para ser mostrados al usuario.
				if (version_actual_pedidos_lines != version_original_pedidos_lines):
					pedidos_cambiados += 1 # actualiza contador de pedidos cambiados durante el proceso
				else:

					# Si el pedido es correcto y llego.
					if incidencia != 'Seleccionar':
						nuevo_status_pedido = 'Devuelto'
						
						if tipoconsulta == u'1':
							total_devuelto_dinero += registro[1]
						else:

							# Para el caso de pedidos con status de Aqui.
							total_devuelto_dinero += 0

							# calcula cuota por extemporaneidad si es que le 
							# corresponde

							

							total_comisiones_extemporaneas += Decimal(cuotadiasextemp)
							nuevo_credito = 0
							nuevo_cargo = genera_documento(cursor,
							'Cargo',
							'Contado',
							socio,
							fecha_hoy,
							hora_hoy,
							usr_existente,
							fecha_hoy,
							hora_hoy,
							usr_existente,
							'Com. prod. no recogido '+registro[2]+' '+registro[3]+' '+registro[4],
							Decimal(cuotadiasextemp),
							Decimal(cuotadiasextemp),
							0,
							0,
							0,
							0,
							0,
							0,
							0,
							sucursal,
							0)






						graba_header_lines()

			

						cursor.execute("""INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,
										ProductoNo,Status,
										catalogo,NoLinea,
										FechaMvto,HoraMvto,Usuario)
										VALUES (%s,%s,%s,%s,
											%s,%s,%s,%s,%s);""",
										[1,pedido,productono,nuevo_status_pedido,
										catalogo,nolinea,fecha_hoy,hora_hoy,usr_existente])




						contador_productos_recibidos += 1

					else:
						pass	


			if tipoconsulta == u'1':		
				nuevo_credito = genera_documento(cursor,
				'Credito',
				'Contado',
				socio,
				fecha_hoy,
				hora_hoy,
				usr_existente,
				fecha_hoy,
				hora_hoy,
				usr_existente,
				'Credito generado por concepto de devolucion sobre venta',
				total_devuelto_dinero,
				total_devuelto_dinero,
				0,
				0,
				0,
				0,
				0,
				0,
				0,
				sucursal,
				0)

				''' Una vez generado el documento, asigna este a cada producto seleccionado
				para ser devuelto '''

				for j in datos:
								
					pedido = j.get("Pedido").encode('latin_1')

					productono = j.get('ProductoNo').strip()
					catalogo =j.get('Catalogo').strip()
					nolinea = j.get('Nolinea').encode('latin_1')
					incidencia = j.get('incidencia').encode('latin_1')

					if incidencia != 'Seleccionar':
						cursor.execute("UPDATE pedidoslines SET NoNotaCreditoPorDevolucion=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(nuevo_credito,pedido,productono,catalogo,nolinea))

			

			# crea log de pedido
			cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,8,fecha_hoy,hora_hoy,'Creó una devolución con nota de credito: '+str(nuevo_credito)))		



			cursor.execute("COMMIT;")

			data = {'status_operacion':'ok','error':"",'nuevo_credito':nuevo_credito,}

						
		except DatabaseError as error:
			
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error),}
			cursor.close()
		except:
			data = {'status_operacion':'fail','error':'Error no relativo a db.'}
			cursor.close()
		return HttpResponse(json.dumps(data),content_type='application/json',)


def imprime_credito(request):
	#pdb.set_trace()
	
	is_staff = request.session['is_staff']

	p_num_credito = request.GET.get('p_num_credito')# p_num_credito realmente almacena el numero  de documento (credito), solo que se dejo asi para no mover el codigo.


	# se encodifica como 'latin_1' ya que viene como unicode.

	#p_num_venta = p_num_venta.encode('latin_1')
	
	
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

	linea = 800
	
	
    # Create a file-like buffer to receive PDF data.
	buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
	p = canvas.Canvas(buffer)
	#p.setPageSize("inch")
	imprime_documento(p_num_credito,'Credito',True,request.session['cnf_razon_social'],request.session['cnf_direccion'],request.session['cnf_colonia'],request.session['cnf_ciudad'],request.session['cnf_estado'],p,buffer,response,True,linea,request)
		
	return response





def Cancela_credito(request):
	#pdb.set_trace()
	
	is_staff = request.session['is_staff']

	p_num_credito = request.GET.get('p_num_credito')# p_num_credito realmente almacena el numero  de documento (credito), solo que se dejo asi para no mover el codigo.

	cursor = connection.cursor()


	cursor.execute("UPDATE")	
	
		
	
    # Create a file-like buffer to receive PDF data.
	buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
	p = canvas.Canvas(buffer)
	#p.setPageSize("inch")
	imprime_documento(p_num_credito,'Credito',True,request.session['cnf_razon_social'],request.session['cnf_direccion'],request.session['cnf_colonia'],request.session['cnf_ciudad'],request.session['cnf_estado'],p,buffer,response,True,linea,request)
		
	return response

def calcula_bono(request):
	''' Inicializa Variables '''
	#pdb.set_trace()

	TotalRegVentas = 0
	TotalRegVtaDevMD = 0
	Totaldscto  = 0.0
	TotalVta = 0.0
	Totaldscto = 0.0
	TotalRegistros = 0
	TotalRegDev = 0
	TotalVtaDevMD = 0.0
	registros_devgral = 0.0
	registros_VtasDevMismodia = 0.0
	TotalDevGral = 0.0
	TotalCargos = 0.0
	TotalVtaCatalogos = 0.0

	""" **************************************"""

	tot_vtas = 0
	tot_ventaFD = 0
	tot_ventabruta = 0
	tot_descuento = 0
	tot_devoluciones = 0
	tot_ventaneta = 0
	sucursal_nombre = " NOMBRE SUCURSAL"
	sucursalinicial =1
	sucursalfinal = 1

	sucursal_activa = request.session['sucursal_activa']

	hoy = datetime.now()
	fecha_hoy = hoy.strftime("%Y-%m-%d")
	hora_hoy = hoy.strftime("%H:%M:%S")
	#fecha_hoy,hora_hoy =trae_fecha_hora_actual(,hora_hoy)


	mensaje =''
	if request.method == 'POST':

		form = Genera_BaseBonoForm(request.POST)

		if form.is_valid():

			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']
			porcentaje = form.cleaned_data['porcentaje']
			venta_minima = form.cleaned_data['venta_minima']
			generarcredito= form.cleaned_data['generarcredito']
			salida = form.cleaned_data['salida']

			cursor=connection.cursor()


			# CREA TABLA TEMPORAL
			cursor.execute("DROP TEMPORARY TABLE IF EXISTS vtas_socio_tmp;")
			cursor.execute("CREATE TEMPORARY TABLE vtas_socio_tmp SELECT * FROM ventas_socio_imagenbase;")

			
			
			# TRAE VENTA Y DESCUENTOS

			#cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones-d.descuentoaplicado <= d.Saldo,0,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado) as VtaComisionSaldo,if(d.venta + d.comisiones - d.descuentoaplicado <= d.Saldo,d.venta+d.comisiones-d.descuentoaplicado,d.Saldo) as cred_aplicado FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))

			"""cursor.execute("SELECT asociadono from asociado;")
			asociados=cursor.fetchall()

			for asociado in asociados:"""

			cursor.execute("SELECT h.asociadono,\
				TRUNCATE(sum(a.precio),2) as venta,\
				TRUNCATE(sum(if (a.precio>l.precio,a.precio-l.precio,0)),2) as dscto\
				from pedidoslines l inner join pedidosheader h\
				on (h.empresano=1 and h.pedidono=l.pedido)\
				inner join pedidos_status_fechas f\
				on (f.empresano=1 and f.pedido=l.pedido\
				and f.productono=l.productono\
				and f.status='Facturado'\
				and f.catalogo=l.catalogo and f.nolinea=l.nolinea)\
				inner join articulo a\
				on (a.empresano=1 and a.codigoarticulo=l.productono\
				and a.catalogo=l.catalogo)\
				inner join proveedor p\
				on (p.EmpresaNo=1 and p.proveedorno=a.idproveedor)\
				inner join ProvConfBono pcb on\
				(pcb.empresano=1 and p.proveedorno=pcb.proveedorno)\
				where f.fechamvto>=%s and f.fechamvto<=%s and pcb.BaseParaBono>0\
				group by h.asociadono;",\
				(fechainicial,fechafinal))

			
			registros_venta = dictfetchall(cursor)
			
			
			elementos = len(registros_venta)

			# TRAE DEVOLUCIONES EN GENERAL
			'''cursor.execute("SELECT a.idproveedor,'',\
				sum(l.precio) as devgral,\
				0 from pedidoslines l inner join pedidosheader h\
				on (h.empresano=1 and h.pedidono=l.pedido)\
				inner join pedidos_status_fechas f\
				on (f.empresano=1 and f.pedido=l.pedido\
				and f.productono=l.productono and f.status='Devuelto'\
				and f.catalogo=l.catalogo and f.nolinea =  l.nolinea) inner join articulo a\
				on (a.empresano=1 and a.codigoarticulo=l.productono\
				and a.catalogo=l.catalogo) inner join proveedor p\
				on (p.empresano=1 and p.proveedorno=a.idproveedor)\
				where f.fechamvto>=%s and f.fechamvto<=%s\
				and h.idsucursal>=%s and h.idsucursal<=%s\
				group by a.idproveedor; ",\
				(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			
			registros_devgral = dictfetchall(cursor)'''

			#TRAE DEVOLUCIONES GRAL
			''' esto este mal 
			cursor.execute("SELECT ph.asociadono,'',TRUNCATE(sum(l.precio),2) as devgral,0\
			 from (SELECT psf.pedido,\
			 psf.productono,\
			 psf.nolinea,\
			 psf.catalogo,\
			 psf.fechamvto from\
			 pedidos_status_fechas as psf USE INDEX (indice_2)\
			 INNER JOIN pedidosheader as h\
			 ON (h.empresano=1 and h.pedidono=psf.pedido) WHERE (psf.status='Devuelto' or psf.status='Dev a Prov' or psf.status='RecepEnDevol') and psf.fechamvto>= %s and psf.fechamvto<= %s) as t2\
			 left JOIN pedidos_status_fechas as t3 USE INDEX (indice_2) on\
			 (t3.empresano=1 and t2.pedido=t3.pedido and t2.productono=t3.productono\
			 and t2.nolinea=t3.nolinea and t2.catalogo=t3.catalogo)\
	         INNER JOIN pedidoslines as l\
	         on (l.empresano=1 and l.pedido=t3.pedido and l.productono=t3.productono\
	         and l.catalogo=t3.catalogo and l.nolinea=t3.nolinea)\
	         INNER JOIN articulo as art\
	         on (art.empresano=1 and art.codigoarticulo=t3.productono and art.catalogo=t3.catalogo)\
	         INNER JOIN pedidosheader ph on (l.empresano=ph.empresano and l.pedido=ph.pedidono)\
	         INNER JOIN ProvConfBono pcb on (pcb.empresano=1 and art.idproveedor=pcb.proveedorno)\
	         where (l.status='Devuelto' or l.status='Dev a Prov' or l.status='RecepEnDevol') and pcb.BaseParaBono>0\
	         GROUP BY ph.asociadono;",(fechainicial,fechafinal,)) '''
		
			''' malo 2

			cursor.execute("SELECT ph.asociadono,'',TRUNCATE(sum(l.precio),2) as devgral,0\
			 from (SELECT psf.pedido,\
			 psf.productono,\
			 psf.nolinea,\
			 psf.catalogo,\
			 psf.fechamvto from\
			 pedidos_status_fechas as psf USE INDEX (indice_2)\
			 INNER JOIN pedidosheader as h\
			 ON (h.empresano=1 and h.pedidono=psf.pedido) WHERE (psf.status='Devuelto' or psf.status='Dev a Prov' or psf.status='RecepEnDevol') and psf.fechamvto>= %s and psf.fechamvto<= %s) as t2\
			 INNER JOIN pedidoslines as l\
	         on (l.empresano=1 and l.pedido=t2.pedido and l.productono=t2.productono\
	         and l.catalogo=t2.catalogo and l.nolinea=t2.nolinea)\
	         INNER JOIN articulo as art\
	         on (art.empresano=1 and art.codigoarticulo=t2.productono and art.catalogo=t2.catalogo)\
	         INNER JOIN pedidosheader ph on (l.empresano=ph.empresano and l.pedido=ph.pedidono)\
	         INNER JOIN ProvConfBono pcb on (pcb.empresano=1 and art.idproveedor=pcb.proveedorno)\
	         where (l.status='Devuelto' or l.status='Dev a Prov' or l.status='RecepEnDevol') and pcb.BaseParaBono>0\
	         GROUP BY ph.asociadono;",(fechainicial,fechafinal,))'''

			cursor.execute("SELECT ph.asociadono,'',TRUNCATE(sum(l.precio),2) as devgral,0\
			 from (SELECT psf.pedido,\
			 psf.productono,\
			 psf.nolinea,\
			 psf.catalogo,\
			 psf.fechamvto from\
			 pedidos_status_fechas as psf USE INDEX (indice_2)\
			 INNER JOIN pedidosheader as h\
			 ON (h.empresano=1 and h.pedidono=psf.pedido) WHERE psf.status='Devuelto' and psf.fechamvto>= %s and psf.fechamvto<= %s) as t2\
			 INNER JOIN pedidoslines as l\
	         on (l.empresano=1 and l.pedido=t2.pedido and l.productono=t2.productono\
	         and l.catalogo=t2.catalogo and l.nolinea=t2.nolinea)\
	         INNER JOIN articulo as art\
	         on (art.empresano=1 and art.codigoarticulo=t2.productono and art.catalogo=t2.catalogo)\
	         INNER JOIN pedidosheader ph on (l.empresano=ph.empresano and l.pedido=ph.pedidono)\
	         INNER JOIN ProvConfBono pcb on (pcb.empresano=1 and art.idproveedor=pcb.proveedorno)\
	         where pcb.BaseParaBono>0\
	         GROUP BY ph.asociadono;",(fechainicial,fechafinal,))

			registros_devgral = dictfetchall(cursor)


			if not registros_venta:

				pass

				
			else:

				cursor.execute("SELECT COUNT(*) as totrec FROM vtas_socio_tmp")
				totrectmp=dictfetchall(cursor)

				j=1
				for registro in registros_venta:


					cursor.execute("UPDATE vtas_socio_tmp vst inner join asociado s on (s.empresano=1 and s.asociadono=vst.asociadono) SET\
						vst.ventas= %s,\
						vst.venta_FD=0,\
						vst.venta_bruta=0,\
						vst.descuento=%s,\
						vst.devoluciones=0,\
						vst.venta_neta=0,\
						vst.bono=0\
						where vst.asociadono=%s and s.EsSocio=1;",\
					 	(Decimal(registro['venta']),Decimal(registro['dscto']),\
					 		registro['asociadono']))					 
                        										
					TotalVta   = TotalVta + float(registro['venta'])
					Totaldscto = Totaldscto + float(registro['dscto'])
					
					if (float(registro['venta']) != 0.0):
						TotalRegVentas = TotalRegVentas + 1


			if not registros_devgral:
				
				pass

			else:				

				for registro in registros_devgral:

					cursor.execute("UPDATE vtas_socio_tmp\
						SET devoluciones=%s WHERE asociadono=%s;",\
					 			(registro['devgral'],registro['asociadono']))
										
					
					TotalDevGral = TotalDevGral + float(registro['devgral'])
					
					if (float(registro['devgral']) != 0.0):
						TotalRegDev = TotalRegDev + 1



			""" 			
			if not registros_VtasDevMismodia:
				
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_vtasxproveedor.html',{'mensaje':mensaje,})


			else:			cursorcursor

				for registro in registros_VtasDevMismodia:

					cursor.execute("UPDATE vtas_pro_tmp\
						SET venta_FD=%s WHERE idproveedor=%s;",\
					 			(registro['VtasDevMD'],registro['idproveedor']))
										

									
					
					TotalVtaDevMD = TotalVtaDevMD + float(registro['VtasDevMD'])
					
					if (float(registro['VtasDevMD']) != 0.0):
						TotalRegVtaDevMD = TotalRegVtaDevMD + 1 """
			#pdb.set_trace()
			#cursor.execute("UPDATE vtas_socio_tmp as t INNER JOIN asociado as p on t.asociadono=p.asociadono SET t.nombreprov=p.razonsocial;")
			cursor.execute("DELETE FROM vtas_socio_tmp WHERE  (ventas = 0 and  descuento =0 and devoluciones = 0 and venta_neta = 0);")
			cursor.execute("UPDATE vtas_socio_tmp SET venta_bruta = ventas + venta_FD;")
			cursor.execute("UPDATE vtas_socio_tmp SET venta_neta = venta_bruta - descuento - devoluciones,bono = if(venta_neta>=%s,venta_neta*%s/100,0);",(venta_minima,porcentaje))
			cursor.execute("DELETE FROM vtas_socio_tmp WHERE  venta_neta <= 0;")






			mensaje =" "

			cursor.execute("SELECT vst.*,CONCAT(s.nombre,' ',s.appaterno,' ',s.apmaterno) as nombre FROM vtas_socio_tmp vst INNER JOIN asociado s on (s.empresano=1 and s.asociadono = vst.asociadono) WHERE vst.bono>0;")
			vtasresult =  dictfetchall(cursor)


			if generarcredito==True:

				cursor.execute("START TRANSACTION ")

				for venta in vtasresult:

							# Trae el ultimo documento
					cursor.execute("SELECT nodocto from documentos WHERE empresano=1 ORDER BY nodocto DESC LIMIT 1 FOR UPDATE;")
					ultimo_docto = cursor.fetchone()
					nuevo_docto = ultimo_docto[0]+1
					nuevo_credito = nuevo_docto # se usa nueva_remision para retornala via ajax en diccionario.

					# Trae el ultimo documento
					cursor.execute("SELECT consecutivo from documentos WHERE empresano=1 and tipodedocumento=%s  ORDER BY consecutivo DESC LIMIT 1 FOR UPDATE;",('Credito',))
					ultimo_consec = cursor.fetchone()
					Nuevo_consec = ultimo_consec[0]+1	

					# Genera el documento.
					# Ojo: observar que el campo `UsuarioQueCreoDcto.` se coloco entre apostrofes inversos y el nombre del campo tal y como esta definido en la tabla (casesensitive) dado que si
							# se pone sin apostrofes marca error!
					cursor.execute("INSERT INTO documentos (`EmpresaNo`,`NoDocto`,\
												`Consecutivo`,`TipoDeDocumento`,\
												`TipoDeVenta`,`Asociado`,\
												`FechaCreacion`,`HoraCreacion`,\
												`UsuarioQueCreoDcto.`,`FechaUltimaModificacion`,\
												`HoraUltimaModificacion`,`UsuarioModifico`,\
												`Concepto`,`monto`,`saldo`,\
												`DescuentoAplicado`,`VtaDeCatalogo`,\
												`Cancelado`,`comisiones`,\
												`PagoAplicadoARemisionNo`,`Lo_recibido`\
												,`venta`,`idsucursal`,\
												`BloquearNotaCredito`) VALUES(%s,%s,%s,%s,%s,%s\
												,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
												%s,%s,%s,%s,%s);",(1,nuevo_docto,Nuevo_consec,\
													'Credito','Contado',venta['asociadono'],\
													fecha_hoy,hora_hoy,99,\
													fecha_hoy,hora_hoy,99,\
													"Bono de constancia",Decimal(venta['bono'],2),Decimal(venta['bono'],2),\
													0,False,False,\
													0,0,0,0,\
													sucursal_activa,False))
				cursor.execute("COMMIT;")	




			
			cursor.execute("SELECT SUM(ventas) as tot_vtas,SUM(venta_FD) as tot_ventaFD,SUM(venta_bruta) as tot_ventabruta, SUM(descuento) as tot_descuento,SUM(devoluciones) as tot_devoluciones,SUM(venta_neta) as tot_ventaneta,SUM(bono) as tot_bono FROM vtas_socio_tmp WHERE bono>0;")	
			totales = dictfetchall(cursor)
			for tot in totales:
				tot_vtas = tot['tot_vtas']
				tot_ventaFD = tot['tot_ventaFD']
				tot_ventabruta = tot['tot_ventabruta']
				tot_descuento = tot['tot_descuento']
				tot_devoluciones = tot['tot_devoluciones']
				tot_ventaneta = tot['tot_ventaneta']
			tot_bono = tot_ventaneta*porcentaje/100
			'''
			cursor.execute("SELECT d.Monto,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.Concepto FROM documentos d  WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,))
			
			

			registros_vtacomis_vtacatal = dictfetchall(cursor)


			for docto in registros_vtacomis_vtacatal:
										
					if (docto['Cancelado'] == '\x00'):  # pregunta si cancelado es '0' en hex o bien falso
						
						esvta =docto['Concepto'].strip()
						if esvta == 'Venta':
														
							TotalCargos = TotalCargos + float(docto['comisiones'])	
											
						if docto['VtaDeCatalogo'] == '\x01' :
							TotalVtaCatalogos = TotalVtaCatalogos + float(docto['Monto'])


			# SI TOTALES SON None, LES ASIGNA UN CERO YA QUE EN EL CONTEXT
			# HABRIA PROBLEMAS CON LA FUNCION FLOAT(), DADO QUE NO ACEPTA UN None COMO PARAMETRO.
			if tot_vtas is None:
				tot_vtas = 0
			if tot_ventabruta is None:
				tot_ventabruta = 0
			if tot_ventaFD is None:
				tot_ventaFD = 0
			if tot_ventaneta is None:
				tot_ventaneta = 0
			if tot_descuento is None:
				tot_descuento = 0
			if tot_devoluciones is None:
				tot_devoluciones =0'''
			

			
			if salida=='Pantalla':	
				context = {'form':form,'mensaje':mensaje,'vtasresult':vtasresult,'TotalRegistros':TotalRegistros,'tot_vtas':float(tot_vtas),'tot_ventaFD':float(tot_ventaFD),'tot_ventabruta':float(tot_ventabruta),'tot_descuento':float(tot_descuento),'tot_devoluciones':float(tot_devoluciones),'tot_bono':float(tot_bono),'tot_ventaneta':float(tot_ventaneta),'TotalCargos':TotalCargos,'TotalVtaCatalogos':TotalVtaCatalogos,'fechainicial':fechainicial,'fechafinal':fechafinal,'sucursal_nombre':sucursal_nombre,'sucursalinicial':sucursalinicial,'sucursalfinal':sucursalfinal,}	
			
				return render(request,'pedidos/lista_bono_socio.html',context)
			else:

				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="BONO_CONSTANCIA.csv"'

				writer = csv.writer(response)
				writer.writerow(['NUM_SOCIO','NOMBRE_SOCIO','VENTA_BRUTA','DESCUENTOS','DEVOLUCIONES','VENTA_NETA','BONO'])
			
				for vta in vtasresult:
			
					if  vta['ventas'] != 0 or vta['venta_FD'] != 0   or vta['venta_bruta'] != 0 or vta['descuento'] != 0 or vta['devoluciones'] != 0 or vta['venta_neta'] != 0:
						# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
						llaves_a_mostrar = ['asociadono','nombre','ventas','descuento','devoluciones','venta_neta','bono',] 
						# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
						lista = [vta[x] for x in llaves_a_mostrar]
						writer.writerow(lista)
		
				cursor.close()
				return response			
		
	else:

		form = Genera_BaseBonoForm()
	return render(request,'pedidos/generabonoforma.html',{'form':form,})

# DETALLE DE LA VENTA BASE PARA CALCULO DE BONO DEL SOCIO

def detallebonosocio(request,idsocio,fechainicial,fechafinal):

	#pdb.set_trace()
	cursor=connection.cursor()

	totalvta = 0

	cursor.execute("SELECT CONCAT(nombre,' ',appaterno,' ',apmaterno) as socio_nombre from asociado WHERE asociadono=%s;",(idsocio,))
	socio_nombre = cursor.fetchone()

	asociado=socio_nombre[0]

	try:
		
		cursor.execute("SELECT h.pedidono,l.remisionno as remision_num,h.asociadono,h.fechapedido,h.horapedido,a.idmarca, a.idestilo,idcolor,a.talla,l.preciooriginal,l.observaciones from pedidoslines l inner join pedidosheader h on (h.empresano=1 and h.pedidono=l.pedido) inner join pedidos_status_fechas f on (f.empresano=1 and f.pedido=l.pedido and f.productono=l.productono and f.status='Facturado' and f.catalogo=l.catalogo and f.nolinea=l.nolinea) inner join articulo a on (a.empresano=1 and a.codigoarticulo=l.productono and a.catalogo=l.catalogo) inner join proveedor p on (p.empresano=1 and p.proveedorno=a.idproveedor) inner join ProvConfBono pcb on (pcb.EmpresaNo=h.empresano and pcb.ProveedorNo=a.idproveedor) where pcb.BaseParaBono and f.fechamvto>=%s and f.fechamvto<=%s and h.asociadono=%s;",(fechainicial,fechafinal,idsocio,))
		"""cursor.execute("SELECT h.pedidono,\
			l.remisionno as remision_num,\
			h.asociadono,\
			h.fechapedido,\
			h.horapedido,\
			a.idmarca,\
			a.idestilo,\
			a.idcolor,\
			a.talla,\
			l.preciooriginal,\
			from pedidoslines l inner join pedidosheader h\
			on (h.empresano=1 and h.pedidono=l.pedido)\
			inner join pedidos_status_fechas f\
			on (f.empresano=1 and f.pedido=l.pedido\
			and f.productono=l.productono and f.status='Facturado'\
			and f.catalogo=l.catalogo)\
			inner join articulo a on (a.empresano=1 and a.codigoarticulo=l.productono\
			and a.catalogo=l.catalogo)\
			inner join proveedor p on (p.empresano=1 and p.proveedorno=a.idproveedor)\
			where f.fechamvto>=%s and f.fechamvto<=%s\
			and h.idsucursal>=%s and h.idsucursal<=%s and a.idproveedor=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,idproveedor,))"""
			
		vtasresult = dictfetchall(cursor)

		# DETERMINA EL TOTAL DE LA VENTA
		
		for reg in vtasresult:
			totalvta = totalvta + float(reg['preciooriginal'])



	except DatabaseError as e:
		print (e)


	context = {'vtasresult':vtasresult,'totalvta':totalvta,'asociado':asociado,'fechainicial':fechainicial,'fechafinal':fechafinal,}	


	return render(request,'pedidos/detalle_bono_socio.html',context)









def proveedores(request):
	cursor=connection.cursor()
	cursor.execute("SELECT proveedorno,razonsocial,telefono1,cel,email from proveedor")
	proveedores = dictfetchall(cursor)

	context = {'proveedores':proveedores,}	
		
	return render(request,'pedidos/proveedores.html',context)


def edita_proveedor(request,proveedorno):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	
	

	msg = ''

	if request.method == 'POST':

		form = DatosProveedorForm(request.POST)
		if form.is_valid():
			ProveedorNo = form.cleaned_data['ProveedorNo']
			RazonSocial = form.cleaned_data['RazonSocial']
			Direccion = form.cleaned_data['Direccion']
			Colonia = form.cleaned_data['Colonia']
			Ciudad = form.cleaned_data['Ciudad']
			Estado = form.cleaned_data['Estado']
			Pais = form.cleaned_data['Pais']
			CodigoPostal = form.cleaned_data['CodigoPostal']
			telefono1 = form.cleaned_data['telefono1']
			telefono2 = form.cleaned_data['telefono2']
			fax = form.cleaned_data['fax']
			cel = form.cleaned_data['celular']
			radio = form.cleaned_data['radio']
			email = form.cleaned_data['email']
			psw_paso = form.cleaned_data['psw_paso']
			maneja_desc = form.cleaned_data['maneja_desc']
			baseparabono = form.cleaned_data['baseparabono']


			fecha_hoy,hora_hoy = trae_fecha_hora_actual('','')


			usr_existente=0
			permiso_exitoso=0

			try:

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,14)

				if permiso_exitoso ==0:

					raise ValueError

				cursor =  connection.cursor()
			

				cursor.execute('START TRANSACTION')
				cursor.execute('UPDATE proveedor SET RazonSocial = %s,\
				Direccion = %s,\
				Colonia = %s,\
				Ciudad = %s,\
				Estado = %s,\
				Pais = %s,\
				CodigoPostal = %s,\
				telefono1 = %s,\
				telefono2 = %s,\
				fax = %s,\
				cel = %s,\
				radio = %s,\
				email = %s,\
				Usuaroi = %s,\
				manejar_desc = %s \
				WHERE proveedorno=%s;',(RazonSocial.upper(),Direccion.upper(),Colonia.upper(),Ciudad.upper(),Estado.upper(),Pais.upper(),CodigoPostal,telefono1,telefono2,fax,cel,radio,email.lower(),usr_existente,'\x01' if maneja_desc==u'1' else '\x00',proveedorno,))
			
				cursor.execute("UPDATE ProvConfBono SET BaseParaBono=%s WHERE proveedorno=%s;",(baseparabono,proveedorno,))

				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,14,fecha_hoy,hora_hoy,'Se modificó el proveedor: '+str(proveedorno)))		

				
				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:proveedores'))


			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				msg = 'Error en base de datos !'
				return HttpResponse('<h3>Ocurrio un error en la base de datos</h3><h2>{{e}}</h2>')
			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para editar información de proveedores !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)

		else:
			
			pass
	else:	

		form = DatosProveedorForm()
		
		cursor=connection.cursor()
		cursor.execute("SELECT 	p.proveedorno,\
								p.RazonSocial,\
								p.Direccion,\
								p.Colonia,\
								p.Ciudad,\
								p.Estado,\
								p.Pais,\
								p.CodigoPostal,\
								p.telefono1,\
								p.telefono2,\
								p.fax,\
								p.cel,\
								p.radio,\
								p.email,\
								p.FechaAta,\
								p.FechaBaja,\
								p.UsuarioQueDioAlta,\
								p.Usuaroi,\
								p.manejar_desc,\
								k.BaseParaBono\
								from proveedor p inner join ProvConfBono k on (k.empresano= 1 and p.proveedorno=k.proveedorno) where p.proveedorno=%s;",(proveedorno,))
		proveedor = cursor.fetchone()

		form = DatosProveedorForm(initial={'ProveedorNo':proveedor[0],'RazonSocial':proveedor[1],'Direccion':proveedor[2],'Colonia':proveedor[3],'Ciudad':proveedor[4],'Estado':proveedor[5],'Pais':proveedor[6],'CodigoPostal':proveedor[7],'telefono1':proveedor[8],'telefono2':proveedor[9],'fax':proveedor[10],'celular':proveedor[11],'radio':proveedor[12],'email':proveedor[13],'FechaAlta':proveedor[14],'maneja_desc':1 if proveedor[18]=='\x01' else 0,'baseparabono':True if proveedor[19] else False,})
					
	return render(request,'pedidos/edita_proveedor.html',{'form':form,'proveedorno':proveedorno,})
	
"""CREACION DE PROVEEDORES"""


def crea_proveedor(request):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	
	hoy = datetime.now()
	fecha_hoy = hoy.strftime("%Y-%m-%d")
	msg = ''

	if request.method == 'POST':

		form = CreaProveedorForm(request.POST)
		if form.is_valid():
			
			RazonSocial = form.cleaned_data['RazonSocial']
			Direccion = form.cleaned_data['Direccion']
			Colonia = form.cleaned_data['Colonia']
			Ciudad = form.cleaned_data['Ciudad']
			Estado = form.cleaned_data['Estado']
			Pais = form.cleaned_data['Pais']
			CodigoPostal = form.cleaned_data['CodigoPostal']
			telefono1 = form.cleaned_data['telefono1']
			telefono2 = form.cleaned_data['telefono2']
			fax = form.cleaned_data['fax']
			cel = form.cleaned_data['celular']
			radio = form.cleaned_data['radio']
			email = form.cleaned_data['email']
			psw_paso = form.cleaned_data['psw_paso']
			maneja_desc = form.cleaned_data['maneja_desc']
			baseparabono = form.cleaned_data['baseparabono']
			

			fecha_hoy,hora_hoy = trae_fecha_hora_actual('','')


			usr_existente=0
			permiso_exitoso=0

			try:

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,14)

				if permiso_exitoso ==0:

					raise ValueError

				cursor =  connection.cursor()
			
			





				cursor.execute("SELECT proveedorNo from proveedor order by proveedorno desc limit 1;")
				proveedorNo = cursor.fetchone()



				cursor.execute('START TRANSACTION')
				cursor.execute("INSERT INTO proveedor(EmpresaNo,ProveedorNo,RazonSocial,\
				Direccion,\
				Colonia,\
				Ciudad,\
				Estado,\
				Pais,\
				CodigoPostal,\
				telefono1,\
				telefono2,\
				fax,\
				cel,\
				radio,\
				email,\
				Usuaroi,\
				UsuarioQueDioAlta,\
				FechaAta,\
				FechaBaja,\
				manejar_desc) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",\
				(1,proveedorNo[0]+1,RazonSocial.upper(),\
				Direccion.upper(),\
				Colonia.upper(),\
				Ciudad.upper(),\
				Estado.upper(),\
				Pais.upper(),\
				CodigoPostal,\
				telefono1,\
				telefono2,\
				fax,\
				cel,\
				radio,\
				email.lower(),\
				usr_existente,\
				usr_existente,\
				fecha_hoy,\
				fecha_hoy,\
				'\x01' if maneja_desc==u'1' else '\x00'))

					
				cursor.execute("INSERT INTO ProvConfBono(EmpresaNo,ProveedorNo,BaseParaBono) VALUES(%s,%s,%s);",(1,proveedorNo[0]+1,baseparabono,))
				
				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,13,fecha_hoy,hora_hoy,'Se creó el proveedor: '+str(proveedorNo[0]+1)))		

				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:proveedores'))


			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				msg = 'Error en base de datos !'
				return HttpResponse('<h3>Ocurrio un error en la base de datos</h3><h2>{{e}}</h2>')

			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para crear proveedores !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)

		else:
			pass
	else:	

	

		form = CreaProveedorForm()
	
					
	return render(request,'pedidos/crea_proveedor.html',{'form':form,})

def lista_catalogos_proveedor(request,proveedorno):

	#pdb.set_trace() 	
	cursor=connection.cursor()
	cursor.execute("SELECT ProveedorNo,Periodo,anio,clasearticulo,if(activo=1,'SI','NO') AS activo,if(no_maneja_descuentos=1,'SI','NO') as no_maneja_descuentos,if(catalogo_promociones=1,'SI','NO') as catalogo_promociones from catalogostemporada where proveedorNo=%s order by Periodo desc;",(proveedorno,))
	catalogos = dictfetchall(cursor)
	cursor.execute("SELECT razonsocial FROM proveedor where proveedorno=%s;",(proveedorno,))
	nombre_proveedor=cursor.fetchone()

	context = {'catalogos':catalogos,'proveedorno':proveedorno,'nombre_proveedor':nombre_proveedor[0]}
	
		
	return render(request,'pedidos/lista_catalogos_proveedor.html',context)

def edita_catalogo(request,p_ProveedorNo,p_Anio,p_Periodo,p_ClaseArticulo):

	#pdb.set_trace()
	

	if request.method == 'POST':

		form = DatosCatalogoForm(request.POST)
		if form.is_valid():
			fProveedorNo = form.cleaned_data['ProveedorNo']
			fPeriodo = form.cleaned_data['Periodo']
			fAnio = form.cleaned_data['Anio']
			fClaseArticulo = form.cleaned_data['ClaseArticulo']
			fActivo = form.cleaned_data['Activo']
			fno_maneja_descuentos = form.cleaned_data['no_maneja_descuentos']
			fcatalogo_promociones = form.cleaned_data['catalogo_promociones']
			

			cursor =  connection.cursor()
			try:

				cursor.execute('START TRANSACTION')
				cursor.execute('UPDATE catalogostemporada SET Activo = %s,\
				no_maneja_descuentos = %s,\
				catalogo_promociones = %s \
				WHERE ProveedorNo=%s and Periodo=%s and Anio=%s and ClaseArticulo=%s ;',('\x01' if fActivo==u'1' else '\x00','\x01' if fno_maneja_descuentos==u'1' else '\x00','\x01' if fcatalogo_promociones==u'1' else '\x00',fProveedorNo,int(fPeriodo),int(fAnio),fClaseArticulo,))
			
				
				
				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:lista_catalogos_proveedor',args=(p_ProveedorNo,),))


			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				
				return HttpResponse('<h3>Ocurrio un error en la base de datos</h3><h2>{{e}}</h2>')

		else:
			pass

	else:	

		form = DatosCatalogoForm()		
		cursor=connection.cursor()
		cursor.execute("SELECT  ct.ProveedorNo,\
								ct.Anio,\
								ct.Periodo,\
								ct.ClaseArticulo,\
								ct.Activo,\
								ct.no_maneja_descuentos,\
								ct.catalogo_promociones \
								from catalogostemporada ct where ct.ProveedorNo=%s and ct.Periodo=%s and ct.Anio=%s and ct.ClaseArticulo=%s;",(p_ProveedorNo,p_Periodo,p_Anio,p_ClaseArticulo,))
		catalogostemporada = cursor.fetchone()
		type(catalogostemporada)
		form = DatosCatalogoForm(initial={'ProveedorNo':catalogostemporada[0],'Anio':catalogostemporada[1],'Periodo':catalogostemporada[2],'ClaseArticulo':catalogostemporada[3],'Activo':1 if catalogostemporada[4]=='\x01' else 0,'no_maneja_descuentos':1 if catalogostemporada[5]=='\x01' else 0,'catalogo_promociones':1 if catalogostemporada[6]=='\x01' else 0,})
	context = {'form':form,'ProveedorNo':p_ProveedorNo,'Anio':p_Anio,'Periodo':p_Periodo,'ClaseArticulo':p_ClaseArticulo,}			
	
	return render(request,'pedidos/edita_catalogo.html',context)




def crea_catalogo(request,id_proveedor):

	#pdb.set_trace()


	if request.method == 'POST':

		form = CreaCatalogoForm(request.POST)

		if form.is_valid():
			vProveedorNo = form.cleaned_data['ProveedorNo']
			vPeriodo = form.cleaned_data['Periodo']
			vAnio = form.cleaned_data['Anio']
			vClaseArticulo = form.cleaned_data['ClaseArticulo'].upper()
			vActivo = form.cleaned_data['Activo']
			vno_maneja_descuentos = form.cleaned_data['no_maneja_descuentos']
			vcatalogo_promociones = form.cleaned_data['catalogo_promociones']
			

			cursor =  connection.cursor()
			try:

				cursor.execute('START TRANSACTION')
				cursor.execute('INSERT INTO catalogostemporada(ProveedorNo,\
					Periodo,Anio,ClaseArticulo,Activo,no_maneja_descuentos,catalogo_promociones)\
					VALUES(%s,%s,%s,%s,%s,%s,%s);',\
					(id_proveedor,int(vPeriodo),int(vAnio),vClaseArticulo,\
					'\x01' if vActivo==u'1' else '\x00',\
					'\x01' if vno_maneja_descuentos==u'1' else '\x00',\
					'\x01' if vcatalogo_promociones==u'1' else '\x00',))

				
				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:lista_catalogos_proveedor',args=(id_proveedor,),))


			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				
				return HttpResponse('<h3>Ocurrio un error en la base de datos</h3><h2>{{e}}</h2>')

		else:
			context={'form':form,'ProveedorNo':id_proveedor,}

			

	else:	

		form = CreaCatalogoForm(initial={'ProveedorNo':id_proveedor,})
		context={'form':form,'ProveedorNo':id_proveedor,}
		
	return render(request,'pedidos/crea_catalogo.html',context)



'''REPORTE QUE CALCULA  LA VENTA NETA POR SOCIO Y POR PROVEEDOR '''

def vtaneta_socio(request):

	# EL REPORTE CONSIDERA TANTO SOCIOS COMO CLIENTES PARA DETERMINAR LAS VENTAS Y
	# QUE CUADRE CON EL REPORTE DE VENTA POR PROVEEDOR.
	
	''' Inicializa Variables '''
	#pdb.set_trace()

	TotalRegVentas = 0
	TotalRegVtaDevMD = 0
	Totaldscto  = 0.0
	TotalVta = 0.0
	Totaldscto = 0.0
	TotalRegistros = 0
	TotalRegDev = 0
	TotalVtaDevMD = 0.0
	registros_devgral = 0.0
	registros_VtasDevMismodia = 0.0
	TotalDevGral = 0.0
	TotalCargos = 0.0
	TotalVtaCatalogos = 0.0

	""" **************************************"""

	tot_vtas = 0
	tot_ventaFD = 0
	tot_ventabruta = 0
	tot_descuento = 0
	tot_devoluciones = 0
	tot_ventaneta = 0
	sucursal_nombre = " NOMBRE SUCURSAL"
	sucursalinicial =1
	sucursalfinal = 1

	sucursal_activa = request.session['sucursal_activa']

	hoy = datetime.now()
	fecha_hoy = hoy.strftime("%Y-%m-%d")
	hora_hoy = hoy.strftime("%H:%M:%S")
	#fecha_hoy,hora_hoy =trae_fecha_hora_actual(,hora_hoy)


	mensaje =''
	if request.method == 'POST':

		form = RpteVtaNetaSocioxMarcaForm(request.POST)

		if form.is_valid():

			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']
			proveedor = form.cleaned_data['proveedor']

			#pdb.set_trace()

			cursor=connection.cursor()


			# CREA TABLA TEMPORAL
			cursor.execute("DROP TEMPORARY TABLE IF EXISTS vtas_socio_tmp;")
			cursor.execute("CREATE TEMPORARY TABLE vtas_socio_tmp SELECT * FROM ventas_socio_imagenbase;")

			cursor.execute('SELECT RazonSocial FROM proveedor where proveedorno=%s',(proveedor,))
			nombre_proveedor = cursor.fetchone()



			

			
			# TRAE VENTA Y DESCUENTOS


			cursor.execute("SELECT h.asociadono,\
				TRUNCATE(sum(l.preciooriginal),2) as venta,\
				TRUNCATE(sum(if (l.preciooriginal>l.precio,l.preciooriginal-l.precio,0)),2) as dscto\
				from pedidoslines l inner join pedidosheader h\
				on (h.empresano=1 and h.pedidono=l.pedido)\
				inner join pedidos_status_fechas f\
				on (f.empresano=1 and f.pedido=l.pedido\
				and f.productono=l.productono\
				and f.status='Facturado'\
				and f.catalogo=l.catalogo and f.nolinea=l.nolinea)\
				inner join articulo a\
				on (a.empresano=1 and a.codigoarticulo=l.productono\
				and a.catalogo=l.catalogo)\
				inner join proveedor p\
				on (p.EmpresaNo=1 and p.proveedorno=a.idproveedor)\
				inner join pedidoslinestemporada plt on (plt.empresano=l.empresano and plt.pedido=l.pedido and plt.productono=l.productono and plt.catalogo=l.catalogo and plt.nolinea=l.nolinea)\
				left join catalogostemporada ct on (ct.proveedorno=a.idproveedor and ct.periodo=CAST(SUBSTRING(l.catalogo,1,4) as UNSIGNED) and ct.Anio=plt.Temporada and ct.clasearticulo=l.catalogo)\
				where f.fechamvto>=%s and f.fechamvto<=%s and p.proveedorno=%s\
				group by h.asociadono;",\
				(fechainicial,fechafinal,proveedor))

			
			registros_venta = dictfetchall(cursor)
			
			
			elementos = len(registros_venta)
			print " los Elementos son elementos", elementos

			# TRAE DEVOLUCIONES EN GENERAL
			
			cursor.execute("SELECT ph.asociadono,'',TRUNCATE(sum(l.precio),2) as devgral,0\
			 from (SELECT psf.pedido,\
			 psf.productono,\
			 psf.nolinea,\
			 psf.catalogo,\
			 psf.fechamvto from\
			 pedidos_status_fechas as psf USE INDEX (indice_2)\
			 INNER JOIN pedidosheader as h\
			 ON (h.empresano=1 and h.pedidono=psf.pedido) WHERE psf.status='Devuelto' and psf.fechamvto>= %s and psf.fechamvto<= %s) as t2\
			 INNER JOIN pedidos_status_fechas as t3 USE INDEX (indice_2) on\
			 (t3.empresano=1 and t2.pedido=t3.pedido and t2.productono=t3.productono\
			 and t2.nolinea=t3.nolinea and t2.catalogo=t3.catalogo)\
	         INNER JOIN pedidoslines as l\
	         on (l.empresano=1 and l.pedido=t3.pedido and l.productono=t3.productono\
	         and l.catalogo=t3.catalogo and l.nolinea=t3.nolinea)\
	         INNER JOIN articulo as art\
	         on (art.empresano=1 and art.codigoarticulo=t3.productono and art.catalogo=t3.catalogo)\
	         INNER JOIN pedidosheader ph on (l.empresano=ph.empresano and l.pedido=ph.pedidono)\
	         INNER JOIN ProvConfBono pcb on (pcb.empresano=1 and art.idproveedor=pcb.proveedorno)\
	         where t3.status='Facturado' and pcb.proveedorno=%s\
	         GROUP BY ph.asociadono;",(fechainicial,fechafinal,proveedor))

			registros_devgral = dictfetchall(cursor)


			if not registros_venta:

				pass

				
			else:

				cursor.execute("SELECT COUNT(*) as totrec FROM vtas_socio_tmp")
				totrectmp=dictfetchall(cursor)

				print "Total de regitron en tmporal", totrectmp
				j=1
				for registro in registros_venta:


					cursor.execute("UPDATE vtas_socio_tmp vst inner join asociado s on (s.empresano=1 and s.asociadono=vst.asociadono) SET\
						vst.ventas= %s,\
						vst.venta_FD=0,\
						vst.venta_bruta=0,\
						vst.descuento=%s,\
						vst.devoluciones=0,\
						vst.venta_neta=0,\
						vst.bono=0\
						where vst.asociadono=%s;",\
					 	(Decimal(registro['venta']),Decimal(registro['dscto']),\
					 		registro['asociadono']))					 
                        										
					TotalVta   = TotalVta + float(registro['venta'])
					Totaldscto = Totaldscto + float(registro['dscto'])
					
					if (float(registro['venta']) != 0.0):
						TotalRegVentas = TotalRegVentas + 1


			if not registros_devgral:
				
				pass

			else:				

				for registro in registros_devgral:

					cursor.execute("UPDATE vtas_socio_tmp\
						SET devoluciones=%s WHERE asociadono=%s;",\
					 			(registro['devgral'],registro['asociadono']))
										
					
					TotalDevGral = TotalDevGral + float(registro['devgral'])
					
					if (float(registro['devgral']) != 0.0):
						TotalRegDev = TotalRegDev + 1



			#pdb.set_trace()
			#cursor.execute("UPDATE vtas_socio_tmp as t INNER JOIN asociado as p on t.asociadono=p.asociadono SET t.nombreprov=p.razonsocial;")
			cursor.execute("DELETE FROM vtas_socio_tmp WHERE  (ventas = 0 and venta_FD=0 and  descuento =0 and devoluciones = 0 and venta_neta = 0);")
			cursor.execute("UPDATE vtas_socio_tmp SET venta_bruta = ventas + venta_FD;")
			cursor.execute("UPDATE vtas_socio_tmp SET venta_neta = venta_bruta - descuento - devoluciones,bono = 0;")
			cursor.execute("DELETE FROM vtas_socio_tmp WHERE  venta_bruta <= 0;")






			mensaje =" "

			cursor.execute("SELECT vst.*,CONCAT(s.nombre,' ',s.appaterno,' ',s.apmaterno) as nombre FROM vtas_socio_tmp vst INNER JOIN asociado s on (s.empresano=1 and s.asociadono = vst.asociadono) ORDER BY vst.venta_neta desc;")
			vtasresult =  dictfetchall(cursor)

			if not vtasresult:
				return HttpResponse("<h2>No existe movimientos para esta consulta !</h2>")
												

			"""
			if generarcredito==True:

				cursor.execute("START TRANSACTION ")

				for venta in vtasresult:

							# Trae el ultimo documento
					cursor.execute("SELECT nodocto from documentos WHERE empresano=1 ORDER BY nodocto DESC LIMIT 1 FOR UPDATE;")
					ultimo_docto = cursor.fetchone()
					nuevo_docto = ultimo_docto[0]+1
					nuevo_credito = nuevo_docto # se usa nueva_remision para retornala via ajax en diccionario.

					# Trae el ultimo documento
					cursor.execute("SELECT consecutivo from documentos WHERE empresano=1 and tipodedocumento=%s  ORDER BY consecutivo DESC LIMIT 1 FOR UPDATE;",('Credito',))
					ultimo_consec = cursor.fetchone()
					Nuevo_consec = ultimo_consec[0]+1	

					# Genera el documento.
					# Ojo: observar que el campo `UsuarioQueCreoDcto.` se coloco entre apostrofes inversos y el nombre del campo tal y como esta definido en la tabla (casesensitive) dado que si
							# se pone sin apostrofes marca error!
					cursor.execute("INSERT INTO documentos (`EmpresaNo`,`NoDocto`,\
												`Consecutivo`,`TipoDeDocumento`,\
												`TipoDeVenta`,`Asociado`,\
												`FechaCreacion`,`HoraCreacion`,\
												`UsuarioQueCreoDcto.`,`FechaUltimaModificacion`,\
												`HoraUltimaModificacion`,`UsuarioModifico`,\
												`Concepto`,`monto`,`saldo`,\
												`DescuentoAplicado`,`VtaDeCatalogo`,\
												`Cancelado`,`comisiones`,\
												`PagoAplicadoARemisionNo`,`Lo_recibido`\
												,`venta`,`idsucursal`,\
												`BloquearNotaCredito`) VALUES(%s,%s,%s,%s,%s,%s\
												,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
												%s,%s,%s,%s,%s);",(1,nuevo_docto,Nuevo_consec,\
													'Credito','Contado',venta['asociadono'],\
													fecha_hoy,hora_hoy,99,\
													fecha_hoy,hora_hoy,99,\
													"Bono de constancia",Decimal(venta['bono'],2),Decimal(venta['bono'],2),\
													0,False,False,\
													0,0,0,0,\
													sucursal_activa,False))
				cursor.execute("COMMIT;")	


				"""

			
			cursor.execute("SELECT SUM(ventas) as tot_vtas,SUM(venta_FD) as tot_ventaFD,SUM(venta_bruta) as tot_ventabruta, SUM(descuento) as tot_descuento,SUM(devoluciones) as tot_devoluciones,SUM(venta_neta) as tot_ventaneta,SUM(bono) as tot_bono FROM vtas_socio_tmp;")	
			totales = dictfetchall(cursor)
			for tot in totales:
				tot_vtas = tot['tot_vtas']
				tot_ventaFD = tot['tot_ventaFD']
				tot_ventabruta = tot['tot_ventabruta']
				tot_descuento = tot['tot_descuento']
				tot_devoluciones = tot['tot_devoluciones']
				tot_ventaneta = tot['tot_ventaneta']


			#pdb.set_trace()
			
			'''
			cursor.execute("SELECT d.Monto,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.Concepto FROM documentos d  WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,))
			
			

			registros_vtacomis_vtacatal = dictfetchall(cursor)


			for docto in registros_vtacomis_vtacatal:
										
					if (docto['Cancelado'] == '\x00'):  # pregunta si cancelado es '0' en hex o bien falso
						
						esvta =docto['Concepto'].strip()
						if esvta == 'Venta':
														
							TotalCargos = TotalCargos + float(docto['comisiones'])	
											
						if docto['VtaDeCatalogo'] == '\x01' :
							TotalVtaCatalogos = TotalVtaCatalogos + float(docto['Monto'])


			# SI TOTALES SON None, LES ASIGNA UN CERO YA QUE EN EL CONTEXT
			# HABRIA PROBLEMAS CON LA FUNCION FLOAT(), DADO QUE NO ACEPTA UN None COMO PARAMETRO.
			if tot_vtas is None:
				tot_vtas = 0
			if tot_ventabruta is None:
				tot_ventabruta = 0
			if tot_ventaFD is None:
				tot_ventaFD = 0
			if tot_ventaneta is None:
				tot_ventaneta = 0
			if tot_descuento is None:
				tot_descuento = 0
			if tot_devoluciones is None:
				tot_devoluciones =0'''
			

			

			context = {'form':form,'mensaje':mensaje,'vtasresult':vtasresult,'TotalRegistros':TotalRegistros,'tot_vtas':float(tot_vtas),'tot_ventaFD':float(tot_ventaFD),'tot_ventabruta':float(tot_ventabruta),'tot_descuento':float(tot_descuento),'tot_devoluciones':float(tot_devoluciones),'tot_ventaneta':float(tot_ventaneta),'TotalCargos':TotalCargos,'TotalVtaCatalogos':TotalVtaCatalogos,'fechainicial':fechainicial,'fechafinal':fechafinal,'sucursal_nombre':sucursal_nombre,'sucursalinicial':sucursalinicial,'sucursalfinal':sucursalfinal,'nombre_proveedor':nombre_proveedor[0]}	
		
			return render(request,'pedidos/lista_vtaneta_socio_xmarca.html',context)

		
	else:

		form = RpteVtaNetaSocioxMarcaForm()
	return render(request,'pedidos/vtaneta_socio_xproveedorform.html',{'form':form,})




""" CANCELA DOCUMENTO """




#@permission_required('auth.add_user',login_url=None,raise_exception=True)
def cancelardocumentoadvertencia(request,NoDocto):
	#no esta en 
	#pdb.set_trace()
	nodocto=NoDocto

	fecha_hoy,hora_hoy =trae_fecha_hora_actual('','')

	status_operation='fail'

	form=CanceladocumentoForm()
	context={}
	
	print request.is_ajax()
	if request.method == 'POST'  and not (request.is_ajax()):

		form = CanceladocumentoForm(request.POST)
		
		if form.is_valid():
			print " pasa por aqui"
			cursor = connection.cursor()
			# limpia datos 
			motivo_cancelacion = form.cleaned_data['motivo_cancelacion']
			psw_paso = form.cleaned_data['psw_paso']

			num_usr_valido = verifica_existencia_usr(psw_paso) # verifica si existe

			if num_usr_valido != 0:
				tiene_derecho = verifica_derechos_usr(num_usr_valido,25)
				if tiene_derecho ==0:
					error_msg = "Usuario sin derechos para cancelar !"
					return render(request,'pedidos/error.html',{'error_msg':error_msg,})
			else:
				error_msg = "Usuario no registrado con el password proporcionado !"
				return render(request,'pedidos/error.html',{'error_msg':error_msg,})
			''' Se cancela documento'''	                                                                  
			status_operation,error = cancela_documento(request,nodocto,motivo_cancelacion)			
			'''Se actualiza el usuario que cancela'''
			cursor.execute("UPDATE documentos SET UsuarioModifico=%s WHERE nodocto=%s;",(num_usr_valido,nodocto,))

			cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(num_usr_valido,25,fecha_hoy,hora_hoy,'Canceló el documento: '+str(nodocto)))		


			cursor.close()
			

			return render(request,'pedidos/msj_cancelacion_resultado.html',{'status_operation':status_operation,})
				
			
	elif request.method == 'POST'  and (request.is_ajax()):

		status_operation = cancela_documento(request,nodocto,'CANCELACION')
				
				
	else:			
		
		pass	
	context={'nodocto':nodocto,'status_operation':status_operation,'form':form}
	return render(request,'pedidos/cancelardocumentoadvertencia.html',context,)


# RUTINA PARA CANCELAR UN DOCUMENTO

def cancela_documento(request,nodocto,motivo_cancelacion):

	#pdb.set_trace()
	
	cursor = connection.cursor()

	hoy = datetime.now()
	fecha_hoy = hoy.strftime("%Y-%m-%d")
	hora_hoy = hoy.strftime("%H:%M:%S") 
	error = ''
	 
	try:
		cursor.execute("START TRANSACTION;")
		cursor.execute("UPDATE documentos set cancelado=1 WHERE empresano=1 and  nodocto=%s;",(nodocto,))
		cursor.execute("INSERT INTO documentoscancelados(EmpresaNo,NoDocto,FechaCancelacion,HoraCancelacion,Usuario,motivo) VALUES(%s,%s,%s,%s,%s,%s);",(1,nodocto,fecha_hoy,hora_hoy,99,motivo_cancelacion,))
		status_operation='ok'
		cursor.execute("COMMIT;")

	except DatabaseError as err:
		cursor.execute("ROLLBACK;")
		status_operation='fail'
		error=str(err)
	cursor.close()
	return status_operation,error


"""ESTA RUTINA CANCELA UN PEDIDO, ES LLAMADA TANTO DE PEDIDOS GENERAL
COMO DE LA PANTALLA DE VENTAS."""
def cancelar_documento(request,NoDocto):
	
	#pdb.set_trace()
	
	nodocto = NoDocto
	
	#motivo = request.POST['motivo']
	motivo = 'por prueba'

	status_operation='fail'
	error = ''
	
	context={}
	
	status_operacion,error = cancelardocumentoadvertencia(request,nodocto)
				
	data = {'status_operacion':status_operacion,'error':error}
	return HttpResponse(json.dumps(data),content_type='application/json',)	


def rptedecreditos(request):


	#pdb.set_trace()
	if request.method == 'POST':
			
		form = RpteCreditosForm(request.POST)
		
		if form.is_valid():

			sucursal_inicial = form.cleaned_data['sucursal_inicial']
			sucursal_final = form.cleaned_data['sucursal_final']

			tipo_credito = form.cleaned_data['tipo_credito'].encode('latin_1')
			status_credito = form.cleaned_data['status_credito'].encode('latin_1')

			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']
			
			salida_a = form.cleaned_data['salida_a']			


			if tipo_credito == 'Todos' and status_credito=='Aplicado':
				
			
				
				consulta = """SELECT d.idsucursal,d.NoDocto,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.saldo FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s
									and d.saldo=0 and d.cancelado=0;"""
		
				
			elif tipo_credito == 'Todos' and status_credito=='Sin aplicar':

				consulta = """SELECT d.idsucursal,d.NoDocto,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.saldo FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s
									and d.saldo >0 and d.cancelado=0;"""

			elif tipo_credito == 'Ajuste' and status_credito == 'Aplicado':
				
				busca = 'credito sobrante%'	

				consulta = """SELECT d.idsucursal,d.NoDocto,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.saldo FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s
									and d.saldo=0 and d.cancelado=0
									and d.concepto like %s ;"""		
			
			elif tipo_credito == 'Ajuste' and status_credito == 'Sin aplicar': 


				busca = 'credito sobrante%'	


				consulta = """SELECT d.idsucursal,d.NoDocto,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.saldo FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s
									and d.saldo>0 and d.cancelado=0
									and d.concepto like %s;"""

			elif tipo_credito == 'Devolucion' and status_credito == 'Aplicado':	

				busca = 'credito generado%'	


				consulta = """SELECT d.idsucursal,d.NoDocto,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.saldo FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s
									and d.saldo=0 and d.cancelado=0
									and d.concepto like %s;"""
			

			elif tipo_credito == 'Devolucion' and status_credito == 'Sin aplicar':


				busca = 'credito generado%'	


				consulta = """SELECT d.idsucursal,d.NoDocto,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.saldo FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s
									and d.saldo>0 and d.cancelado=0
									and d.concepto like %s;"""
			


			elif tipo_credito == 'Anticipo' and status_credito == 'Aplicado':

			
				busca = 'anticipo%'	

				consulta = """SELECT d.idsucursal,d.NoDocto,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.saldo FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s
									and d.saldo=0 and d.cancelado=0
									and d.concepto like %s;"""
			


			elif tipo_credito == 'Anticipo' and status_credito == 'Sin aplicar':

				busca = 'anticipo%'

				consulta = '''SELECT d.idsucursal,d.NoDocto,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.saldo FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s
									and d.saldo>0 and d.cancelado=0
									and d.concepto like %s;'''
			



			elif tipo_credito == 'Capturado' and status_credito == 'Aplicado':

				busca = 'c:%'

				consulta = """SELECT d.idsucursal,d.NoDocto,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.saldo FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s
									and d.saldo=0 and d.cancelado=0
									and d.concepto like %s;"""
			


			elif tipo_credito == 'Capturado' and status_credito == 'Sin aplicar':


				busca = 'c:%'

				consulta = """SELECT d.idsucursal,d.NoDocto,
									d.FechaCreacion,
									d.asociado,
									CONCAT(trim(s.nombre),' ',
									trim(s.appaterno),' ',
									trim(s.apmaterno)) as nombre_socio,
									d.concepto,
									d.monto,
									d.saldo FROM documentos d
									INNER JOIN asociado s
									on d.empresano=s.empresano
									and d.asociado=s.asociadono
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s
									and d.saldo>0 and d.cancelado=0
									and d.concepto like %s;"""
			
			else:

				consulta = """SELECT d.idsucursal,d.NoDocto,\
									d.FechaCreacion,\
									d.asociado,\
									CONCAT(trim(s.nombre),' ',\
									trim(s.appaterno),' ',\
									trim(s.apmaterno)) as nombre_socio,\
									d.concepto,\
									d.monto,\
									d.saldo FROM documentos d\
									INNER JOIN asociado s\
									on d.empresano=s.empresano\
									and d.asociado=s.asociadono\
									WHERE d.empresano=1 and d.idsucursal>=%s and d.idsucursal<=%s and d.tipodedocumento='Credito'\
									and d.FechaCreacion>=%s and d.FechaCreacion<=%s\
									and d.saldo>0 and d.cancelado=0;"""
			
			if tipo_credito != 'Todos':
				parms = [sucursal_inicial,sucursal_final,fechainicial,fechafinal,busca]
			else:
				parms = [sucursal_inicial,sucursal_final,fechainicial,fechafinal]

			try:
				cursor = connection.cursor()
		
				cursor.execute(consulta,parms) # observar que se uso parms como parte de una lista en lugar de una tupla, si se usa una tupla marca error

				documentos = dictfetchall(cursor)

				tot_monto,tot_saldo = 0,0
				for docu in documentos:
					tot_monto += docu['monto']
					tot_saldo += docu['saldo']

				if salida_a == 'Pantalla':

				#   ***** MANDA A PANTALLA IMPRESION ***			
					if not documentos:
						e = "No se encontraron registros !"
					else:
						e = ''
					context = {'documentos':documentos,'mensaje':e,'tot_monto':tot_monto,'tot_saldo':tot_saldo,'tipo_credito':tipo_credito,'status_credito':status_credito,}
					return render (request,'pedidos/rpte_creditos.html',context)
			
				else:

				# *** ***  MANDA A ARCHIVO IMPRESION *****
					if not documentos:
						e = "No se encontraron registros !"
						context = {'documentos':documentos,'mensaje':e,'tot_monto':tot_monto,'tot_saldo':tot_saldo,'tipo_credito':tipo_credito,'status_credito':status_credito,}
						return render (request,'pedidos/rpte_creditos.html',context)
					else:

						response = HttpResponse(content_type='text/csv')
						response['Content-Disposition'] = 'attachment; filename="RPTE_CREDITOS.csv"'

						writer = csv.writer(response)
						writer.writerow(['SUCURSAL', 'NO_DOCTO', 'FECHA', 'NUM_SOCIO','NOMBRE_SOCIO','CONCEPTO','MONTO','SALDO',])
					
						for documento in documentos:
					
					
							# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
							llaves_a_mostrar = ['idsucursal','NoDocto','FechaCreacion','asociado','nombre_socio','concepto','monto','saldo',] 
							# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
							lista = [documento[x] for x in llaves_a_mostrar]
				
							writer.writerow(lista)
						cursor.close()
						return response			

			except DatabaseError as e:
				print e

			
			cursor.close()
		
	else:
		form = RpteCreditosForm()

	return render (request,'pedidos/rpte_creditos_filtro.html',{'form':form,})
			
#@permission_required('auth.add_viasolicitud',login_url=None,raise_exception=True)
def recepcion_dev_prov(request):

	#pdb.set_trace()

	error = ''
	if request.method == 'POST':

		form = Recepcion_dev_provForm(request.POST)

		if form.is_valid():

			sucursal = form.cleaned_data['sucursal']

			ordenarpor = form.cleaned_data['ordenarpor'].encode('latin_1')
			
			try:

				''' En las siguientes consultas se hacen dos inner join a pedidos_status_fechas,
				 uno con el status "Devuelto" y el otro con status "Aqui",
				 el primero para delimintar la consulta en base a la fecha de devolucion
				 y el segundo para delimitar la consulta en base a la fecha de llegada 
				 del producto a la sucursal, es decir cuando alcanzo el status de "Aqui". 
				 '''

				if sucursal != u'0':

					consulta = """SELECT l.Pedido,l.ProductoNo,
										l.Catalogo,l.NoLinea,l.precio,
										l.status,h.AsociadoNo,
										h.FechaPedido,h.fechaultimamodificacion,
										a.codigoarticulo,a.catalogo,a.idmarca,
										a.idestilo,a.idcolor,a.talla,l.Observaciones,h.idSucursal,psf1.fechamvto,al.razonsocial,
										psf.fechamvto as fechadevuelto
										from pedidoslines l
										 inner join pedidosheader h on (h.empresano=l.empresano and l.pedido=h.pedidono)
										 inner join articulo a on
										(a.empresano=1 and 
										 l.productono=a.codigoarticulo
										and l.catalogo=a.catalogo)
										left join pedidos_status_fechas psf
										on (l.empresano=psf.empresano and l.pedido=psf.pedido
										and l.productono=psf.productono
										and l.catalogo=psf.catalogo
										and l.nolinea=psf.nolinea and (psf.status='Devuelto' or psf.status='Por Devolver')) 
										left join pedidos_status_fechas psf1
										on (l.empresano=psf1.empresano and l.pedido=psf1.pedido
										and l.productono=psf1.productono
										and l.catalogo=psf1.catalogo
										and l.nolinea=psf1.nolinea and psf1.status='Aqui')
										inner join pedidos_encontrados pe
										on (l.empresano=pe.empresano
										and l.pedido=pe.pedido
										and l.productono=pe.productono
										and l.catalogo=pe.catalogo and l.nolinea=pe.nolinea)
										inner join almacen al on (l.empresano=al.empresano and a.idproveedor=al.proveedorno and al.almacen=pe.bodegaencontro)
										where h.idsucursal=%s and (l.status='Devuelto' or l.status='Por Devolver')
										and psf.fechamvto>'20191201' ORDER BY if(%s='Estilo',a.idestilo,concat(a.idmarca,a.idestilo));"""
					parms =(sucursal,ordenarpor)

				else:

					consulta = """SELECT l.Pedido,l.ProductoNo,
										l.Catalogo,l.NoLinea,l.precio,
										l.status,h.AsociadoNo,
										h.FechaPedido,h.fechaultimamodificacion,
										a.codigoarticulo,a.catalogo,a.idmarca,
										a.idestilo,a.idcolor,a.talla,l.Observaciones,h.idSucursal,psf1.fechamvto,al.razonsocial,
										psf.fechamvto as fechadevuelto
										from pedidoslines l
										 inner join pedidosheader h on (h.empresano=l.empresano and l.pedido=h.pedidono)
										 inner join articulo a on
										(a.empresano=1 and 
										 l.productono=a.codigoarticulo
										and l.catalogo=a.catalogo)
										left join pedidos_status_fechas psf
										on (l.empresano=psf.empresano and l.pedido=psf.pedido
										and l.productono=psf.productono
										and l.catalogo=psf.catalogo
										and l.nolinea=psf.nolinea and (psf.status='Devuelto' or psf.status='Por Devolver')) 
										left join pedidos_status_fechas psf1
										on (l.empresano=psf1.empresano and l.pedido=psf1.pedido
										and l.productono=psf1.productono
										and l.catalogo=psf1.catalogo
										and l.nolinea=psf1.nolinea and psf1.status='Aqui')
										inner join pedidos_encontrados pe
										on (l.empresano=pe.empresano
										and l.pedido=pe.pedido
										and l.productono=pe.productono
										and l.catalogo=pe.catalogo and l.nolinea=pe.nolinea)
										inner join almacen al on (l.empresano=al.empresano and a.idproveedor=al.proveedorno and al.almacen=pe.bodegaencontro)
										where (l.status='Devuelto' or l.status='Por Devolver') and h.idsucursal>=1 and h.idsucursal<=999
										and psf.fechaMvto>'20191201' ORDER BY if(%s='Estilo',a.idestilo,concat(a.idmarca,a.idestilo));"""
					parms =(ordenarpor,)


				cursor = connection.cursor()
		
				cursor.execute(consulta,parms) # observar que se uso parms como parte de una lista en lugar de una tupla, si se usa una tupla marca error

				registros = dictfetchall(cursor)
				
				reg_encontrados = len(registros)

				return render(request,'pedidos/muestra_devueltos_aRecepcionar.html',{'registros':registros,'reg_encontrados':reg_encontrados})



			except DatabaseError as e:

				error = str(e)

	form = Recepcion_dev_provForm()
	return render(request,'pedidos/recepcion_devoluciones_proveedor.html',{'form':form,'error':error})
	


# PROCESAMIENTO DE RECEPCION DE DEVOLUCIONES A PROVEEDOR




def procesar_recepcion_devolucion_proveedor(request):
	
	#pdb.set_trace()
	if request.is_ajax()  and request.method == 'POST':
		# Pasa a una variable la tabla  recibida en json string
		TableData = request.POST.get('TableData')
		
		# carga la tabla ( la prepara con el formato de lista adecuado para leerla)
		datos = json.loads(TableData)

		cursor = connection.cursor()


		if request.POST.get('psw_paso') is not None:
		
			psw_paso = request.POST.get('psw_paso')
		
			cursor.execute("SELECT usuariono FROM usr_extend where pass_paso=%s;",(psw_paso,))
			usr_existente = cursor.fetchone()
			usr_existente = usr_existente[0]
			capturista = usr_existente

		else:
			capturista = 99
			usr_existente = 0




		''' INICIALIZACION DE VARIABLES '''

		error = False
		nuevo_status_pedido = 'RecepEnDevol'

		''' FIN DE INCIALIZACION DE VARIABLES '''


		# Se convierte la fecha de hoy a formatos manejables para insertarlos en el registro.
		hoy = datetime.now()
		fecha_hoy = hoy.strftime("%Y-%m-%d")
		hora_hoy = hoy.strftime("%H:%M:%S") 


		try:

			cursor.execute("START TRANSACTION")
			


	        # Recupera cada diccionario y extrae los valores de la llave a buscar.
			for j in datos:
				
				if j is not None: # Procesa solo los registros con contenido
			
				
					print "elegido:", j.get('elegido')
					pedido = j.get("Pedido").encode('latin_1')

					productono = j.get('ProductoNo').strip()
					catalogo =j.get('Catalogo').strip()
					nolinea = j.get('Nolinea').encode('latin_1')
					elegido = j.get('elegido')
				# Comienza acceso a BD.


					cursor.execute("UPDATE pedidosheader SET FechaUltimaModificacion=%s,horamodicacion=%s WHERE EmpresaNo=1 and pedidono=%s;",[fecha_hoy,hora_hoy,pedido])							
					cursor.execute("UPDATE pedidoslines SET status=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(nuevo_status_pedido,pedido,productono,catalogo,nolinea))


					# Crea o bien actualiza pedidos_status_fechas

					cursor.execute("INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,ProductoNo,Status,catalogo,NoLinea,FechaMvto,HoraMvto,Usuario) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",[1,pedido,productono,nuevo_status_pedido,catalogo,nolinea,fecha_hoy,hora_hoy,capturista])

					# crea log de pedido
					cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,32,fecha_hoy,hora_hoy,'Recepcionó una devolución de proveedor del pedido: '+str(pedido)))		



			cursor.execute("COMMIT;")
			data = {'status_operacion':'ok','error':'',}


		except DatabaseError as error_msg:
		
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			
			error = True
		except IntegrityError as error_msg:
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except OperationalError as error_msg:
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except NotSupportedError as error_msg:
	
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except ProgrammingError as error_msg:

			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except (RuntimeError, TypeError, NameError) as error_msg:
			cursor.execute("ROLLBACK;")
			#error_msg = 'Error no relativo a base de datos'
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except:
			cursor.execute("ROLLBACK;")
			error_msg = "Error desconocido"
			data = {'status_operacion':'fail','error':error_msg,}
			error = True

		cursor.close()

		# Si no hay error, nos devolvera la lista de pedidos cambiados
		# o bien un 'ok' y si hay error nos devolvera el mensaje de error.
		
		return HttpResponse(json.dumps(data),content_type='application/json',)




# DEVOLUCIONES A PROVEEDOR



def devolucion_a_proveedor(request):

	#pdb.set_trace()

	error = ''
	if request.method == 'POST':

		form = Dev_proveedorForm(request.POST)

		if form.is_valid():

			proveedor = form.cleaned_data['proveedor']

			almacen = form.cleaned_data['almacen']

			ordenarpor = form.cleaned_data['ordenarpor'].encode('latin_1')
			
			num_socio = form.cleaned_data['num_socio']

			nombre_socio = form.cleaned_data['nombre_socio']

			dirigir_a = form.cleaned_data['dirigir_a']

			try:

				

				consulta = """SELECT l.Pedido,l.ProductoNo,
									l.Catalogo,l.NoLinea,l.precio,
									l.status,h.AsociadoNo,
									h.FechaPedido,h.fechaultimamodificacion,
									a.codigoarticulo,a.catalogo,a.idmarca,
									a.idestilo,a.idcolor,a.talla,l.Observaciones,h.idSucursal,psf1.fechamvto,psf.fechamvto as fechaRecepEnDevol,al.razonsocial
									from pedidoslines l
									 inner join pedidosheader h on (h.empresano=l.empresano and l.pedido=h.pedidono)
									 inner join articulo a on
									(a.empresano=1 and 
									 l.productono=a.codigoarticulo
									and l.catalogo=a.catalogo)
									inner join pedidos_status_fechas psf
									on (l.empresano=psf.empresano and l.pedido=psf.pedido
									and l.productono=psf.productono
									and l.catalogo=psf.catalogo
									and l.nolinea=psf.nolinea and psf.status='RecepEnDevol')
									left join pedidos_status_fechas psf1
									on (l.empresano=psf1.empresano and l.pedido=psf1.pedido
									and l.productono=psf1.productono
									and l.catalogo=psf1.catalogo
									and l.nolinea=psf1.nolinea and psf1.status='Aqui')
									inner join pedidos_encontrados pe
									on (l.empresano=pe.empresano
									and l.pedido=pe.pedido
									and l.productono=pe.productono
									and l.catalogo=pe.catalogo and l.nolinea=pe.nolinea)
									inner join almacen al on (l.empresano=al.empresano and a.idproveedor=al.proveedorno and al.almacen=pe.bodegaencontro)
									where al.proveedorno=%s and al.almacen=%s and l.status='RecepEnDevol'
									and psf.fechamvto>'20191201' ORDER BY if(%s='Estilo',a.idestilo,a.idmarca);"""
				parms =(proveedor,almacen,ordenarpor)

				

				cursor = connection.cursor()
		
				cursor.execute(consulta,parms) # observar que se uso parms como parte de una lista en lugar de una tupla, si se usa una tupla marca error

				registros = dictfetchall(cursor)
				
				reg_encontrados = len(registros)

				if dirigir_a == 'Archivo':
					response = HttpResponse(content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename="devoluciones_proveedor.csv"'

					writer = csv.writer(response)
					writer.writerow(['ID_SUC','SOCIO','FECHA_LLEGO','FECHA_DEVOLVIO','MARCA','ESTILO','COLOR','TALLA','PRECIO','BODEGA'])
						
					for registro in registros:
						print registro
						# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
						llaves_a_mostrar = ['idSucursal','AsociadoNo','fechamvto','fechaultimamodificacion','idmarca','idestilo','idcolor','talla','precio','razonsocial'] 
						# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
						lista = [registro[x] for x in llaves_a_mostrar]					
						writer.writerow(lista)
					cursor.close()
					return response	
				else:

					return render(request,'pedidos/muestra_devueltos_aEnviar.html',{'registros':registros,'reg_encontrados':reg_encontrados,'proveedor':proveedor,'almacen':almacen,'num_socio':num_socio,'nombre_socio':nombre_socio,})



			except DatabaseError as e:

				error = str(e)

	form = Dev_proveedorForm()
	return render(request,'pedidos/devoluciones_proveedor.html',{'form':form,'error':error})



def procesar_devolucion_proveedor(request):
	
	#pdb.set_trace()
	if request.is_ajax()  and request.method == 'POST':
		# Pasa a una variable la tabla  recibida en json string
		TableData = request.POST.get('TableData')
		
		# carga la tabla ( la prepara con el formato de lista adecuado para leerla)
		datos = json.loads(TableData)

		# Se inicializa la variable cursor 
		cursor = connection.cursor()


		if request.POST.get('psw_paso') is not None:
			
				psw_paso = request.POST.get('psw_paso')
			
				cursor.execute("SELECT usuariono FROM usr_extend where pass_paso=%s;",(psw_paso,))
				usr_existente = cursor.fetchone()
				usr_existente = usr_existente[0]
				capturista = usr_existente

		else:
			capturista = 99
			usr_existente = 0

		'''if request.POST.get('usr_id') is not None:
			capturista = request.POST.get('usr_id')
		else:
			capturista = 99'''
		
		guia = request.POST.get('guia')
		guia = guia.encode('latin_1')

		observaciones = request.POST.get('observaciones')
		observaciones = observaciones.encode('latin_1')

		proveedor = request.POST.get('proveedor')
		almacen = request.POST.get('almacen')

		num_socio = request.POST.get('num_socio')
		nombre_socio = request.POST.get('nombre_socio')
	
		

		''' INICIALIZACION DE VARIABLES '''

		error = False
		nuevo_status_pedido = 'Dev a Prov'

		''' FIN DE INCIALIZACION DE VARIABLES '''


		# Se convierte la fecha de hoy a formatos manejables para insertarlos en el registro.
		hoy = datetime.now()
		fecha_hoy = hoy.strftime("%Y-%m-%d")
		hora_hoy = hoy.strftime("%H:%M:%S") 


		try:

			cursor.execute("START TRANSACTION")

			# Crea el registro padre de devoluciones
			cursor.execute("INSERT INTO devprov (fecha,hora,guia,observaciones,id_proveedor,id_almacen,fecharecepcion,recibio,num_socio,nombre_socio) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(fecha_hoy,hora_hoy,guia,observaciones,proveedor,almacen,hoy,'',num_socio,nombre_socio))

			cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,32,fecha_hoy,hora_hoy,'Envió una devolución al proveedor: '+str(proveedor)))		

			cursor.execute("SELECT id from devprov ORDER BY id DESC LIMIT 1;")
			id_devprov = cursor.fetchone()



	        # Recupera cada diccionario y extrae los valores de la llave a buscar.
			for j in datos:
				
				if j is not None: # Procesa solo los registros con contenido
				
					print "elegido:", j.get('elegido')
					pedido = j.get("Pedido").encode('latin_1')

					productono = j.get('ProductoNo').strip()
					catalogo =j.get('Catalogo').strip()
					nolinea = j.get('Nolinea').encode('latin_1')
					elegido = j.get('elegido')
				# Comienza acceso a BD.


					cursor.execute("UPDATE pedidosheader SET FechaUltimaModificacion=%s,horamodicacion=%s WHERE EmpresaNo=1 and pedidono=%s;",[fecha_hoy,hora_hoy,pedido])							
					cursor.execute("UPDATE pedidoslines SET status=%s WHERE EmpresaNo=1 and Pedido=%s and ProductoNo=%s and Catalogo=%s and NoLinea=%s;",(nuevo_status_pedido,pedido,productono,catalogo,nolinea))


					# Crea o bien actualiza pedidos_status_fechas

					cursor.execute("INSERT INTO pedidos_status_fechas (EmpresaNo,Pedido,ProductoNo,Status,catalogo,NoLinea,FechaMvto,HoraMvto,Usuario) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",[1,pedido,productono,nuevo_status_pedido,catalogo,nolinea,fecha_hoy,hora_hoy,capturista])


					# Crea el registro hijo de devoluciones

					cursor.execute("INSERT INTO devprovlines (EmpresaNo,Pedido,ProductoNo,catalogo,NoLinea,id_devprov) VALUES(%s,%s,%s,%s,%s,%s);",(1,pedido,productono,catalogo,nolinea,id_devprov[0]))



			cursor.execute("COMMIT;")
			data = {'status_operacion':'ok','error':'',}


		except DatabaseError as error_msg:
		
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			
			error = True
		except IntegrityError as error_msg:
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except OperationalError as error_msg:
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except NotSupportedError as error_msg:
	
			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except ProgrammingError as error_msg:

			cursor.execute("ROLLBACK;")
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except (RuntimeError, TypeError, NameError,ValueError) as error_msg:
			cursor.execute("ROLLBACK;")
			#error_msg = 'Error no relativo a base de datos'
			data = {'status_operacion':'fail','error':str(error_msg),}
			error = True
		except:
			cursor.execute("ROLLBACK;")
			error_msg = "Error desconocido"
			data = {'status_operacion':'fail','error':error_msg,}
			error = True

		cursor.close()

		# Si no hay error, nos devolvera la lista de pedidos cambiados
		# o bien un 'ok' y si hay error nos devolvera el mensaje de error.
		
		return HttpResponse(json.dumps(data),content_type='application/json',)


def filtro_dev_prov(request):
	#pdb.set_trace()
	if  request.method =='POST':

		form = FiltroDevProvForm(request.POST)

		if form.is_valid():

			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']
			proveedor = form.cleaned_data['proveedor']
			almacen = form.cleaned_data['almacen']

			cursor = connection.cursor()
			cursor.execute('SELECT dp.id,dp.fecha,dp.hora,p.razonsocial as proveedor,al.razonsocial as almacen,dp.id_proveedor,dp.id_almacen,dp.guia,dp.observaciones,dp.fecharecepcion,dp.recibio from devprov dp inner join proveedor p on (p.empresano=1 and p.proveedorno=dp.id_proveedor) inner join almacen al on (al.empresano=1 and al.proveedorno=dp.id_proveedor and al.almacen=dp.id_almacen) where fecha>=%s and fecha<=%s  and dp.id_proveedor=%s and dp.id_almacen=%s order by id desc;',(fechainicial,fechafinal,proveedor,almacen))
			registros = dictfetchall(cursor)
			
			cursor.execute('SELECT razonsocial as nom_prov from proveedor WHERE empresano=1 and proveedorno=%s;',(proveedor,))
			nom_prov = cursor.fetchone()

			cursor.execute('SELECT razonsocial as nom_almacen from almacen where empresano=1 and proveedorno=%s and almacen=%s;',(proveedor,almacen))
			nom_almacen = cursor.fetchone()

			return render(request,'pedidos/lista_dev_prov.html',{'registros':registros,'nom_prov':nom_prov[0],'nom_almacen':nom_almacen[0],'id':id,})


	form = FiltroDevProvForm()
	return render (request,'pedidos/filtro_dev_prov.html',{'form':form,})		



 # IMPRESION DE HOJA DE DEVOLUCION A PROVEEDOR

def imprime_hoja_devolucion(request):
	#pdb.set_trace()
	
	is_staff = request.session['is_staff']

	id = request.GET.get('id')
	
	# se encodifica como 'latin_1' ya que viene como unicode.

	id = int(id.encode('latin_1'))
	
	
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

	#Trae informacion del pedido.
	cursor =  connection.cursor()
	#pdb.set_trace()

	

	try:
			
		cursor.execute("SELECT fecha,hora,guia,num_socio,nombre_socio FROM devprov where id=%s;",(id,))
		pedido_header = cursor.fetchone()
		
		'''cursor.execute("SELECT appaterno,apmaterno,nombre FROM asociado where asociadono=%s;",(pedido_header[5],))
		datos_socio = cursor.fetchone()'''

		
		cursor.execute("SELECT dpl.id_devprov,l.Observaciones,l.Status,a.pagina,a.idmarca,a.idestilo,a.idcolor,a.talla,a.catalogo FROM devprovlines dpl inner join pedidoslines l  on (dpl.empresano=l.empresano and dpl.pedido=l.pedido and dpl.productono=l.productono and dpl.catalogo=l.catalogo and dpl.nolinea=l.nolinea) INNER JOIN articulo a ON (l.empresano=a.empresano and l.productono=a.codigoarticulo and l.catalogo=a.catalogo) WHERE dpl.id_devprov=%s ORDER BY a.idestilo ASC;",(id,))
		pedido_detalle = dictfetchall(cursor)
		# la siguiente variable  se asigna para ser pasada a la rutina que 
		# imprimira la nota de credito ( en caso de que exista )
		if pedido_detalle is not(None):

			for elem in  pedido_detalle:
				
				if elem['talla'] != 'NE':
					talla = elem['talla']
				else:
					talla = elem['Observaciones']
		
		cursor.execute("SELECT usuario from usuarios where usuariono=%s;",[pedido_header[3]])
		
		usuario = cursor.fetchone()

		mensaje=""
		
		if usuario is None:
			usuario=['ninguno']
		if (not pedido_header or not pedido_detalle):
			mensaje = "No se encontro informacion del pedido !"

	except DatabaseError as e:
		print "Ocurrio de base datos"
		print e
		
		mensaje = "Ocurrio un error de acceso a la bd. Inf. tecnica: "
	except Exception as e:
		mensaje = "Ocurrio un error desconocido. Inf. tecnica: "
		print "error desconocido: "
		print e
		
	cursor.close()

	linea = 800
	
	
    # Create a file-like buffer to receive PDF data.
	buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
	p = canvas.Canvas(buffer)
	#p.setPageSize("inch")

	p.setFont("Helvetica",12)
	#p.drawString(1,linea,inicializa_imp)
	

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
	#p.drawString(20,810,mensaje)

	if (pedido_header and pedido_detalle and usuario):
		p.drawString(250,linea, request.session['cnf_razon_social'])
		linea -=20
		p.setFont("Helvetica",12)
		p.drawString(220,linea, " ----- Devolución número "+str(id)+" ------")
		linea -=20
		p.setFont("Helvetica",8)
		p.drawString(20,linea,request.session['sucursal_direccion'])
		p.drawString(470,linea,"FECHA: "+pedido_header[0].strftime("%d-%m-%Y"))
		linea -= 10
		p.drawString(20,linea,"COL. "+request.session['sucursal_colonia'])
		linea -= 10
		p.drawString(20,linea,request.session['sucursal_ciudad']+", "+request.session['sucursal_estado'])
		linea -= 20
		
		p.setFont("Helvetica",8)
		
		#p.drawString(100,linea,pedido_header[1].strftime("%H:%M:%S"))
		#linea -= 10
	#	p.drawString(20,linea,"CREADO POR: ")
		#p.drawString(100,linea,request.user.username)
		#p.drawString(100,linea,usuario[0])
		#linea -= 20
		p.drawString(20,linea,"SOCIO NUM: ")
		#type()
		p.drawString(80,linea,str(pedido_header[3])+' '+pedido_header[4])
		#linea -= 10
		
		var_socio = "Abel Espinoza Montoya"

		#p.drawString(140,linea,pedido_header[4])
		linea -= 10

				
		#linea -= 10
		
		p.drawString(220,linea,"Estilo      ")
		p.drawString(270,linea,"Color       ")
		p.drawString(345,linea,"Talla       ")
		linea -= 10
		p.drawString(220,linea,"-------------------------------------------------")
		linea -= 10
		#p.setFont("Helvetica",8)
		i,paso=0,linea-10
		
		for elemento in pedido_detalle:

			if elemento['talla'] != 'NE':
				talla = elemento['talla']
			else:
				talla = elemento['Observaciones']
			
			
			p.drawString(220,paso,(elemento['idestilo']+(12-len(elemento['idestilo']))*' ')[0:12])
			p.drawString(270,paso,(elemento['idcolor']+(12-len(elemento['idcolor']))*' ')[0:12])		
			p.drawString(345,paso,talla)		
			paso -= 10
			i+=1
		paso-=10
			
		p.drawString(220,paso,"TOTAL DE ARTICULOS: "+str(i))
		linea = paso-110
	#pdb.set_trace()	
	

	# Close the PDF object cleanly, and we're done.
		p.showPage()
		p.save()


		pdf = buffer.getvalue()
		buffer.close()

		response.write(pdf)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    #return FileResponse(buffer, as_attachment=True,filename='hello.pdf')
	return response


def edita_devprov(request,id_prov):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	msg = ''
	
	if request.method == 'POST':
		form = Edicion_devprovForm(request.POST)
		id = request.POST.get('id')
		if form.is_valid():
			id = request.POST.get('id')
			observaciones =request.POST.get('observaciones').encode('latin_1')[0:100]
			guia = request.POST.get('guia').encode('latin_1')[0:100]
			fecha_recepcion = request.POST.get('fecha_recepcion')
			recibio = request.POST.get('recibio').encode('latin_1')[0:20]
			num_socio = request.POST.get('num_socio')
			nombre_socio = request.POST.get('nombre_socio').encode('latin_1')[0:30]

			# convierte la fecha a formato adecuado para poder ser grabada en base de datos		
			if fecha_recepcion is not None:
				f_convertida = datetime.strptime(fecha_recepcion, "%d/%m/%Y").date()
	 		else:
	 			f_convertida = '1901/01/01'



			''' OJO, los siguientes if's sirven para verificar 
			los campos boleanos 'vtadecatalogo' y 'bloquearnotacredito' 
			dado que el templeate los regresa con valores 'None' y 'on'
			esto hay que investigar porque lo hace, mientras
			se actualizan con calores correctos dependiendo de lo que 
			traigan '''

			
			
			cursor =  connection.cursor()
			try:

				cursor.execute('START TRANSACTION')
				cursor.execute('UPDATE devprov SET guia=%s,observaciones=%s,fecharecepcion=%s,recibio=%s,num_socio=%s,nombre_socio=%s WHERE id=%s;',(guia,observaciones,f_convertida,recibio,num_socio,nombre_socio,id_prov,))
				cursor.execute("COMMIT;")
				return HttpResponseRedirect(reverse('pedidos:filtro_dev_prov'))
				

			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				msg = 'Error en base de datos !'
				return HttpResponse('<h3>Ocurrio un error en la base de datos</h3><h2>{{e}}</h2>')

		else:
			

			return render(request,'pedidos/detalle_devprov.html',{'form':form,'id_prov':id,})
	else:	
				
		cursor =  connection.cursor()
		cursor.execute("SELECT d.id,\
			                   d.guia,\
			                   d.observaciones,\
			                   d.fecharecepcion,\
			                   d.recibio,\
			                   d.num_socio,\
			                   d.nombre_socio\
			                   FROM devprov d WHERE d.id=%s;",(id_prov,))	
		datos_documento =  cursor.fetchone()
		
		id = datos_documento[0]
		guia = datos_documento[1] 
		
		observaciones = datos_documento[2]
		fecha_recepcion = datos_documento[3]
		recibio = datos_documento[4]
		num_socio = datos_documento[5]
		nombre_socio = datos_documento[6]
		
		cursor.close()

		form =  Edicion_devprovForm(initial= {'id':id,'guia':guia,'observaciones':observaciones,'fecha_recepcion':fecha_recepcion,'recibio':recibio,'num_socio':num_socio,'nombre_socio':nombre_socio,})	
		return render(request,'pedidos/detalle_devprov.html',{'form':form,'id_prov':id_prov,'msg':msg},)


# LISTA DE DEVOLUCIONES A PROVEEDOR



def lista_devoluciones_recepcionadas(request):

	#pdb.set_trace()

	error = ''
	if request.method == 'POST':

		form = Lista_dev_recepcionadasForm(request.POST)

		if form.is_valid():

			
			

			ordenarpor = form.cleaned_data['ordenarpor'].encode('latin_1')
			
			
			try:

				

				consulta = """SELECT l.Pedido,l.ProductoNo,
									l.Catalogo,l.NoLinea,l.precio,
									l.status,h.AsociadoNo,
									h.FechaPedido,h.fechaultimamodificacion,
									a.codigoarticulo,a.catalogo,a.idmarca,
									a.idestilo,a.idcolor,a.talla,l.Observaciones,h.idSucursal,psf1.fechamvto,al.razonsocial,
									pr.razonsocial as prov_nombre

									from pedidoslines l
									 inner join pedidosheader h on (h.empresano=l.empresano and l.pedido=h.pedidono)
									 inner join articulo a on
									(a.empresano=1 and 
									 l.productono=a.codigoarticulo
									and l.catalogo=a.catalogo)
									inner join pedidos_status_fechas psf
									on (l.empresano=psf.empresano and l.pedido=psf.pedido
									and l.productono=psf.productono
									and l.catalogo=psf.catalogo
									and l.nolinea=psf.nolinea and psf.status='RecepEnDevol')
									left join pedidos_status_fechas psf1
									on (l.empresano=psf1.empresano and l.pedido=psf1.pedido
									and l.productono=psf1.productono
									and l.catalogo=psf1.catalogo
									and l.nolinea=psf1.nolinea and psf1.status='Aqui')
									inner join pedidos_encontrados pe
									on (l.empresano=pe.empresano
									and l.pedido=pe.pedido
									and l.productono=pe.productono
									and l.catalogo=pe.catalogo and l.nolinea=pe.nolinea)
									inner join almacen al on (l.empresano=al.empresano and a.idproveedor=al.proveedorno and al.almacen=pe.bodegaencontro) 
									inner join proveedor pr on (l.empresano=pr.empresano and a.idproveedor=pr.proveedorno)
									where l.status='RecepEnDevol'
									and psf.fechamvto>'20191201' ORDER BY a.Idproveedor,al.almacen,if(%s='Estilo',a.idestilo,a.idmarca);"""
				#parms =(proveedor,almacen,ordenarpor)
				parms =(ordenarpor,)

				

				cursor = connection.cursor()
		
				cursor.execute(consulta,parms) # observar que se uso parms como parte de una lista en lugar de una tupla, si se usa una tupla marca error

				registros = dictfetchall(cursor)
				
				reg_encontrados = len(registros)

				return render(request,'pedidos/lista_devueltos_recepcionados.html',{'registros':registros,'reg_encontrados':reg_encontrados,})



			except DatabaseError as e:

				error = str(e)

	form = Lista_dev_recepcionadasForm
	return render(request,'pedidos/ListaDev_proveedor.html',{'form':form,'error':error})

'''
def imprime_venta(request):
#pdb.set_trace()

	is_staff = request.session['is_staff']

	if request.method =='GET':
		p_num_venta = request.GET.get('p_num_venta') 
		p_num_credito = request.GET.get('p_num_credito')# p_num_pedido realmente almacena el numero  de documento (remision), solo que se dejo asi para no mover el codigo.
	else:
		
		p_num_venta = request.POST.get('p_num_venta')
		p_num_credito = request.POST.get('p_num_credito')

	# se encodifica como 'latin_1' ya que viene como unicode.

	#p_num_venta = p_num_venta.encode('latin_1')
	
	
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

	#Trae informacion del pedido.
	cursor =  connection.cursor()
	#pdb.set_trace()

	datos_documento,pedido_detalle,usuario,NotaCredito = None,None,None,0

	try:
		cursor.execute("SELECT asociado,venta,comisiones,saldo,descuentoaplicado,Lo_Recibido,idsucursal,UsuarioModifico,FechaCreacion,HoraCreacion,monto,tipodedocumento,concepto FROM documentos where nodocto=%s;",(p_num_venta,))
		datos_documento = cursor.fetchone()	

		cursor.execute("SELECT appaterno,apmaterno,nombre FROM asociado where asociadono=%s;",(datos_documento[0],))
		datos_socio =  cursor.fetchone()

		cursor.execute("SELECT l.precio,l.NoNotaCreditoPorPedido,l.Observaciones,l.Status,a.pagina,a.idmarca,a.idestilo,a.idcolor,a.talla,a.catalogo,so.nombre,so.appaterno,so.apmaterno,suc.nombre,l.PrecioOriginal FROM pedidoslines l INNER JOIN articulo a ON (l.empresano = a.empresano and l.productono = a.codigoarticulo and l.catalogo = a.catalogo) INNER JOIN asociado so ON (so.empresano=1 and so.asociadono = %s) INNER JOIN sucursal suc ON (suc.empresano=1 and suc.sucursalno = %s) WHERE l.RemisionNo = %s;",(datos_documento[0],datos_documento[6],p_num_venta))
		pedido_detalle = dictfetchall(cursor)

		cursor.execute("SELECT NoDocto,FechaCreacion,HoraCreacion,monto,concepto FROM documentos where PagoAplicadoARemisionNo=%s;",(p_num_venta,))
		creditos_aplicados = cursor.fetchall()	


		# la siguiente variable  se asigna para ser pasada a la rutina que 
		# imprimira la nota de credito ( en caso de que exista )
		if pedido_detalle is not(None):

			for elem in  pedido_detalle:
				NotaCredito = elem['NoNotaCreditoPorPedido']
				if elem['talla'] != 'NE':
					talla = elem['talla']
				else:
					talla = elem['Observaciones']
		
		cursor.execute("SELECT usuario from usuarios where usuariono=%s;",[datos_documento[7]])
		
		usuario = cursor.fetchone()

		mensaje=""
		
		if usuario is None:
			usuario=['ninguno']
		if (not datos_documento or not pedido_detalle):
			mensaje = "No se encontro informacion del pedido !"

	except DatabaseError as e:
		print "Ocurrio de base datos"
		print e
		
		mensaje = "Ocurrio un error de acceso a la bd. Inf. tecnica: "
	except Exception as e:
		mensaje = "Ocurrio un error desconocido. Inf. tecnica: "
		print "error desconocido: "
		print e
		
	cursor.close()

	linea = 800
	
	
    # Create a file-like buffer to receive PDF data.
	buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
	p = canvas.Canvas(buffer)
	#p.setPageSize("inch")

	#p.setFont("Helvetica",10)
	#p.drawString(1,linea,inicializa_imp)
	

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
	#p.drawString(20,810,mensaje)

	if ((datos_documento or pedido_detalle) and usuario):

		tipodedocumento = datos_documento[11]



		p.drawString(45,linea, request.session['cnf_razon_social'])
		linea -=20
		p.drawString(45,linea," SUC. "+request.session['sucursal_nombre'])
		linea -=20
		p.setFont("Helvetica",12)
		p.drawString(20,linea, "*** "+("VENTA" if tipodedocumento=='Remision' else "CARGO")+" NUM."+p_num_venta+" ***")
		linea -=20
		p.setFont("Helvetica",8)
		p.drawString(20,linea,request.session['sucursal_direccion'])
		linea -= 10
		p.drawString(20,linea,"COL. "+request.session['sucursal_colonia'])
		linea -= 10
		p.drawString(20,linea,request.session['sucursal_ciudad']+", "+request.session['sucursal_estado'])
		linea -= 10
		p.drawString(20,linea,datos_documento[8].strftime("%d-%m-%Y"))
		p.drawString(100,linea,datos_documento[9].strftime("%H:%M:%S"))
		linea -= 10
		p.drawString(20,linea,"CREADO POR: ")
		#p.drawString(100,linea,request.user.username)
		p.drawString(100,linea,usuario[0])
		linea -= 10
		p.drawString(20,linea,"SOCIO NUM: ")
		type(datos_documento[0])
		p.drawString(100,linea,str(datos_documento[0]))
		linea -= 10
		var_nombre = datos_socio[0]+' '+datos_socio[1]+' '+datos_socio[2]
		p.drawString(20,linea,var_nombre[0:26])
		linea -= 10
		p.drawString(20,linea,"--------------------------------------------------")

		linea -= 10
		
		p.drawString(20,linea,"Descrpcion")
		p.drawString(130,linea,"Precio")
		linea -= 10
		p.drawString(20,linea,"--------------------------------------------------")
		linea -= 10


		#p.setFont("Helvetica",8)
		i,paso=1,linea-10

		""" Ojo en la siguiente linea no cambiar el string 'Venta' en la comparacion
		ya que python es case sensitive """
	
		if tipodedocumento=='Cargo' or (tipodedocumento == 'Remision' and datos_documento[12] != 'Venta'):

			p.drawString(20,paso-10,datos_documento[12].upper()[0:25])
			p.drawString(125,paso-19,'$ '+str(datos_documento[10]))
		else:


			for elemento in pedido_detalle:

				if elemento['talla'] != 'NE':
					talla = elemento['talla']
				else:
					talla = elemento['Observaciones']
				
				p.drawString(20,paso,elemento['pagina']+' '+elemento['idmarca']+' '+elemento['idestilo']) 
				p.drawString(20,paso-10,elemento['idcolor'][0:7]+' '+talla)
				p.drawString(130,paso-12,'$ '+str(elemento['PrecioOriginal']))
				paso -= 20
			p.drawString(20,paso-10,"+ Venta ==>")
			p.drawString(130,paso-10,'$ '+str(datos_documento[1]))
			p.drawString(20,paso-20,"+ Cargo ==>")
			p.drawString(130,paso-20,'$ '+str(datos_documento[2]))
			p.drawString(20,paso-30,"-  Credito ==>")
			p.drawString(130,paso-30,'$ '+str(datos_documento[3]))
			p.drawString(20,paso-40,"-  Descuento ==>")
			p.drawString(130,paso-40,'$ '+str(datos_documento[4]))
			p.drawString(20,paso-50,"   TOTAL ==>")
			p.drawString(130,paso-50,'$ '+str(0 if datos_documento[10]<0 else datos_documento[10]))


		
		p.drawString(20,paso-70,"Gracias por su compra !!!" if tipodedocumento=='Remision' else " ")
		p.drawString(20,paso-90,"Para sugerencias o quejas")
		p.drawString(20,paso-100,"llame al 867 132 9697")		

		if creditos_aplicados:
			p.drawString(20,paso-120,"Notas de credito aplicadas:")
			p.drawString(20,paso-1300,"--------------------------------------------------")
			linea -= 10
			p.drawString(20,paso-140,"Num.")
			p.drawString(55,paso-140,"Concepto")
			p.drawString(130,paso-140,"Monto")
			linea -= 10
			p.drawString(20,paso-150,"--------------------------------------------------")
			linea = paso-160	

			for elemento in creditos_aplicados:
				p.drawString(20,linea,str(elemento[0]))
				p.drawString(55,linea,elemento[4][0:12])
				p.drawString(130,linea,'$ '+str(elemento[3]))
				linea -= 10 

			linea -= 20
		linea -= 110

	#pdb.set_trace()	
	if p_num_credito != u'0':
		imprime_documento(p_num_credito,'Credito',False,request.session['cnf_razon_social'],request.session['cnf_direccion'],request.session['cnf_colonia'],request.session['cnf_ciudad'],request.session['cnf_estado'],p,buffer,response,True,linea,request)
	else:

	# Close the PDF object cleanly, and we're done.
		p.showPage()
		p.save()


		pdf = buffer.getvalue()
		buffer.close()

		response.write(pdf)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    #return FileResponse(buffer, as_attachment=True,filename='hello.pdf')
	#return response
	return response'''


def rpte_ventas(request):


	#pdb.set_trace()
	''' Inicializa Variables '''
	VentaCalzado = 0.0
	TotalVtaBruta = 0.0
	TotalCargos = 0.0
	TotalCreditos = 0.0
	TotalDescuentos = 0.0
	TotalRegistros = 0.0
	TotalVtaCatalogos = 0.0
	TotalVtaNeta = 0.0

	a=''
	b=''
	hoy,hora = trae_fecha_hora_actual(a,b)


	# INICIALIZA REPORTLAB PARA REPORTE
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

    # Create a file-like buffer to receive PDF data.
	buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
	p = canvas.Canvas(buffer,pagesize=letter)
	#p.setPageSize("inch")

	p.setFont("Helvetica",10)
	#p.drawString(1,linea,inicializa_imp)

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

			
			#cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones > d.Saldo,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado,0) as VtaComisionSaldo FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones-d.descuentoaplicado <= d.Saldo,0,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado) as VtaComisionSaldo,if(d.venta + d.comisiones - d.descuentoaplicado <= d.Saldo,d.venta+d.comisiones-d.descuentoaplicado,d.Saldo) as cred_aplicado FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			
			

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
						tipodedocumento = docto['TipoDeDocumento']
						TotalVtaBruta = TotalVtaBruta + float(docto['venta'])
						esvta =docto['Concepto'].strip()
						vtadecatalogo = docto['VtaDeCatalogo']

						# calcula para ventas normales y ventas de catalogo
						if esvta == 'Venta' or vtadecatalogo =='\x01':

						#if tipodedocumento == 'Remision':

							#Excluye las ventas de catalogo para totales de creditos cargos y descuento
							if vtadecatalogo =='\x00':
								TotalCreditos = TotalCreditos + float(docto['cred_aplicado'])															
								TotalCargos = TotalCargos + float(docto['comisiones'])	
								TotalDescuentos =  TotalDescuentos + float(docto['descuentoaplicado'])	
								VentaCalzado = VentaCalzado + float(docto['venta'])
							print float(docto['venta']),float(docto['comisiones']),float(docto['cred_aplicado'])
							print "acumulados:"
							print TotalVtaBruta,TotalCargos,TotalCreditos

						if (TotalVtaBruta + TotalCargos > TotalCreditos):
							print "entro por vtabruta+cargos > creditos"

							TotalVtaNeta = TotalVtaBruta-TotalCreditos+TotalCargos-TotalDescuentos
						else:
							print "entro por el otro lado"
							TotalVtaNeta = 0;

						if vtadecatalogo == '\x01' :
							TotalVtaCatalogos = TotalVtaCatalogos + float(docto['Monto'])
						TotalRegistros = TotalRegistros + 1
						TotalVtaProductos = TotalVtaBruta - TotalVtaCatalogos -TotalDescuentos
				
				mensaje ="Registros encontrados == > "

				#linea = 800
				
				
				
			    # Draw things on the PDF. Here's where the PDF generation happens.
			    # See the ReportLab documentation for the full list of functionality.
				#p.drawString(20,810,mensaje)
				li,ls=0,85
				contador_registros_impresos =0	
				for j in range(1,1000):
					
					#p.translate(0.0,0.0)    # define a large font							

					linea = 800
									 
					p.drawString(250,linea, request.session['cnf_razon_social'])
					linea -=20
					p.setFont("Helvetica",9)
					p.drawString(220,linea, " ----- REPORTE DE VENTAS ------")
					p.drawString(240,linea-10, "       "+sucursal_nombre+" ")

					p.setFont("Helvetica",6)
					p.drawString(240,linea-20, "Entre el "+fechainicial.strftime("%Y-%m-%d")+" y el " +fechafinal.strftime("%Y-%m-%d"))
						
					linea -=25
					
					p.drawString(80,linea,request.session['sucursal_direccion'])
					p.drawString(430,linea,"FECHA: "+hoy)
					

					linea -= 8
					p.drawString(80,linea,"COL. "+request.session['sucursal_colonia'])
					p.drawString(430,linea,"HORA:  "+hora)

					linea -= 8
					p.drawString(80,linea,request.session['sucursal_ciudad']+", "+request.session['sucursal_estado'])
					linea -= 20
					
					p.setFont("Helvetica",6)



					p.drawString(80,linea,"Documento")
					p.drawString(120,linea,"Remision")
					p.drawString(160,linea,"Fecha")
					p.drawString(200,linea,"Socio")
					p.drawString(220,linea,"Nombre")
					p.drawString(290,linea,"Vta Bruta")
					p.drawString(330,linea,"Creditos")
					p.drawString(370,linea,"Cargos")
					p.drawString(410,linea,"Desctos")
					p.drawString(450,linea,"Vta Neta")

					linea -= 10
					p.drawString(80,linea,"-"*200)
					linea -= 10
					#p.setFont("Helvetica",8)
					i,paso=0,linea-5
		
					
					for elemento in registros_venta[li:ls]:


						p.drawString(80,paso,str(elemento['NoDocto']))
						p.drawString(120,paso,str(elemento['Consecutivo']))
						p.drawString(160,paso,elemento['FechaCreacion'].strftime("%d-%m-%Y"))		
						p.drawString(200,paso,str(elemento['Asociado']))
						p.drawString(220,paso,(elemento['Nombre']+' '+elemento['ApPaterno']+' '+elemento['ApMaterno'])[0:15])
						p.drawString(290,paso,str(elemento['venta']))			
						p.drawString(330,paso,str(elemento['cred_aplicado']) if elemento['Concepto']=='Venta' else str(0))				
						p.drawString(370,paso,str(elemento['comisiones']) if elemento['Concepto']=='Venta' else str(0))				
						p.drawString(410,paso,str(elemento['descuentoaplicado']))
						p.drawString(450,paso,str(elemento['VtaComisionSaldo']) if elemento['Concepto']=='Venta' else (str(elemento['venta']) if elemento['VtaDeCatalogo'] else str(0)))				
						#p.drawString(200,paso,talla)'''		
						paso -= 8
						i+=1
						contador_registros_impresos+=1

					if registros_venta[li:ls]:
						p.showPage()						

					li=ls
					ls=85*j	
					
					if contador_registros_impresos==elementos:
					
						paso=780
						p.translate(0.0,0.0)

						

						p.setFont("Helvetica",8)

						p.drawString(10,paso,"RESUMEN: ")

						paso-=5

						p.drawString(10,paso,27*'_')

						paso-=10

						
						locale.setlocale( locale.LC_ALL, '' )
						p.drawString(10,paso,"Venta Bruta: ")
						p.drawString(90,paso,locale.currency(TotalVtaBruta,grouping=True))

						paso-=10
						p.drawString(10,paso,"- Creditos: ")
						p.drawString(90,paso,locale.currency(TotalCreditos,grouping=True))

						paso-=10
						p.drawString(10,paso,"+ Cargos: ")
						p.drawString(90,paso,locale.currency(TotalCargos,grouping=True))

						paso-=10
						p.drawString(10,paso,"- Descuentos: ")
						p.drawString(90,paso,locale.currency(TotalDescuentos,grouping=True))

						paso-=7
						p.drawString(90,paso,"-"*17)

						paso-=10
						p.drawString(10,paso,"Venta Neta: ")
						p.drawString(90,paso,locale.currency(TotalVtaNeta,grouping=True))

						paso-=30
						p.drawString(10,paso,"Vta Productos: ")
						p.drawString(90,paso,locale.currency(TotalVtaProductos,grouping=True))

						paso-=10
						p.drawString(10,paso,"Vta Catalogos: ")
						p.drawString(90,paso,locale.currency(TotalVtaCatalogos,grouping=True))


						p.showPage()
						p.save()


						pdf = buffer.getvalue()
						buffer.close()

						response.write(pdf)

						return response




				context = {'form':form,'mensaje':mensaje,'registros_venta':registros_venta,'TotalRegistros':TotalRegistros,'sucursal_nombre':sucursal_nombre,'TotalCreditos':TotalCreditos,'TotalCargos':TotalCargos,'TotalDescuentos':TotalDescuentos,'VentaCalzado':VentaCalzado,'TotalVtaCatalogos':TotalVtaCatalogos,'TotalVtaBruta':TotalVtaBruta,'TotalVtaNeta':TotalVtaNeta,'TotalVtaProductos':TotalVtaProductos}	
			
				#return render(request,'pedidos/lista_ventas.html',context)

		
	else:

		form = Consulta_ventasForm()
	return render(request,'pedidos/rpte_vtas_form.html',{'form':form,})


'''CONSULTA DE STATUS DE PEDIDOS CLASIFICADOS POR SOCIO '''



def rpteStatusPedidosPorSocio(request):

	'''try:
	
		g_numero_socio_zapcat = request.session['socio_zapcat']	
	except KeyError :

		return	HttpResponse("Ocurrió un error de conexión con el servidor, Por favor salgase completamente y vuelva a entrar a la página !")

	if request.user.is_authenticated():'''		

	#pdb.set_trace()		
	if request.method == 'POST':
		form = RpteStatusDePedidosForm(request.POST)
		'''
		Si la forma es valida se normalizan los campos numpedido, status y fecha,
		de otra manera se envia la forma con su contenido erroreo para que el validador
		de errores muestre los mansajes correspondientes '''

		if form.is_valid():
		
			# limpia datos 
			sucursal = form.cleaned_data['sucursal']
			
			status = form.cleaned_data['status']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']
			salida_a = form.cleaned_data['salida_a']
			
			# Convierte el string '1901-01-01' a una fecha valida en python
			# para ser comparada con la fecha ingresada 

			fecha_1901 =datetime.strptime('1901-01-01', '%Y-%m-%d').date()
			hoy = date.today()


			# Establece conexion con la base de datos
			cursor=connection.cursor()

		
			# Comienza a hacer selects en base a criterios 


			

			if  sucursal ==u'0':
				suc_ini,suc_fin=1,99
			else:
				suc_ini,suc_fin=sucursal,sucursal
				
									
			
			cursor.execute("SELECT p.pedido,p.precio,p.status,\
				p.catalogo,p.nolinea,\
				a.pagina,a.idmarca,a.idestilo,a.idcolor,\
				a.talla,h.idsucursal,aso.asociadoNo,aso.Nombre,\
				aso.appaterno,aso.apmaterno, psf.fechamvto,\
				p.Observaciones,CONCAT(CAST(aso.asociadono AS CHAR),\
				' ',aso.nombre,' ',aso.appaterno,' ',aso.apmaterno)\
				 as socio,suc.nombre as sucursal FROM pedidoslines p\
				inner join  pedidosheader h\
				on (p.EmpresaNo=h.EmpresaNo and p.pedido=h.pedidoNo)\
				inner join articulo a\
				on ( p.EmpresaNo=a.empresano and p.productono=a.codigoarticulo\
				and p.catalogo=a.catalogo)\
				inner join asociado aso\
				on (h.asociadoNo=aso.asociadoNo)\
				inner join  pedidos_status_fechas psf\
				on (p.empresano=psf.empresaNo\
				and p.pedido=psf.pedido and p.productono=psf.productono\
				and p.status=psf.status and p.catalogo=psf.catalogo\
				and p.nolinea=psf.nolinea) \
				inner join sucursal suc on (h.idsucursal=suc.sucursalNo)\
				 WHERE p.status>=%s and p.status<=%s\
				and psf.fechamvto>=%s and psf.fechamvto<=%s\
				and h.idsucursal>=%s and h.idsucursal<=%s\
				ORDER BY aso.asociadoNo,\
				h.PedidoNo ASC;", (status,status,fechainicial,fechafinal,suc_ini,suc_fin,))
							
			pedidos = dictfetchall(cursor)
			elementos = len(pedidos)

			total_gral=0
			
			for i in pedidos:
				total_gral+= i['precio']

			cursor.execute("SELECT aso.asociadoNo,SUM(p.precio) AS subtotal FROM pedidoslines p\
				inner join  pedidosheader h\
				on (p.EmpresaNo=h.EmpresaNo and p.pedido=h.pedidoNo)\
				inner join articulo a\
				on ( p.EmpresaNo=a.empresano and p.productono=a.codigoarticulo\
				and p.catalogo=a.catalogo)\
				inner join asociado aso\
				on (h.asociadoNo=aso.asociadoNo)\
				inner join  pedidos_status_fechas psf\
				on (p.empresano=psf.empresaNo\
				and p.pedido=psf.pedido and p.productono=psf.productono\
				and p.status=psf.status and p.catalogo=psf.catalogo\
				and p.nolinea=psf.nolinea) \
				inner join sucursal suc on (h.idsucursal=suc.sucursalNo)\
				 WHERE p.status>=%s and p.status<=%s\
				and psf.fechamvto>=%s and psf.fechamvto<=%s\
				and h.idsucursal>=%s and h.idsucursal<=%s\
				GROUP BY aso.asociadoNo ASC;", (status,status,fechainicial,fechafinal,suc_ini,suc_fin,))
							
			subxsocio = dictfetchall(cursor)
			

			cursor.execute("SELECT nombre as nombresuc from sucursal where sucursalNo=%s;",(sucursal,))
			suc_nom=cursor.fetchone()
			

			if not pedidos:# or not nombre_socio[0]:
				mensaje = 'No se encontraron registros !'
				
				return render(request,'pedidos/lista_pedidos_PorStatus_Socio.html',{'form':form,'mensaje':mensaje,})
			else:
				mensaje ='Registros encontrados:'
				context = {'pedidos':pedidos,'subxsocio':subxsocio,'mensaje':mensaje,'elementos':elementos,'sucursal':suc_nom[0],'titulo':'Consulta de pedidos con status de '+status,'fechainicial':fechainicial,'fechafinal':fechafinal,'total_gral':total_gral,'elementos':elementos,}

				if salida_a == 'Pantalla':

					return render(request,'pedidos/lista_pedidos_PorStatus_Socio.html',context)
				else:

					response = HttpResponse(content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename="PedidosStatusSocios.csv"'

					writer = csv.writer(response)
					writer.writerow(['SUCURSAL','SOCIO_NUMERO','SOCIO_NOMBRE','SOCIO_APPATERNO','SOCIO_APMATERNO','PEDIDO','FECHA_MVTO','STATUS','CATALOGO','PAGINA','MARCA','ESTILO','COLOR','TALLA','PRECIO',])
					
					for registro in pedidos:
						print registro
						# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
						llaves_a_mostrar = ['sucursal','asociadoNo','Nombre','appaterno','apmaterno','pedido','fechamvto','status','catalogo','pagina','idmarca','idestilo','idcolor','talla','precio',] 
						# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
						lista = [registro[x] for x in llaves_a_mostrar]					
						writer.writerow(lista)
					cursor.close()
					return response			



			# Cierra la conexion a la base de datos
			cursor.close()
			
		
	else:
		form = RpteStatusDePedidosForm()
		#cursor.close()
		
	return render(request,'pedidos/pedidos_por_status_socio_form.html',{'form':form,})

def vtasporusuario_consulta(request):


	#pdb.set_trace()
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

		form = ventasporcajeroForm(request.POST)

		if form.is_valid():

			sucursal = form.cleaned_data['sucursal']
			usuario = form.cleaned_data['usuario']
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


			cursor.execute("SELECT usuario from usuarios WHERE EmpresaNo=1 and usuarioNo=%s;",(usuario,))
			usuario_nombre = cursor.fetchone()
			

			
			"""cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,psf.fechatentativallegada,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre)  left join  pedidoslines psf on (p.empresano=psf.empresaNo and p.pedido=psf.pedido and p.productono=psf.productono and p.catalogo=psf.catalogo and p.nolinea=psf.nolinea) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by c.id,psf.fechatentativallegada;",(fechainicial,fechafinal))"""

			
			#cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones > d.Saldo,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado,0) as VtaComisionSaldo FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones-d.descuentoaplicado <= d.Saldo,0,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado) as VtaComisionSaldo,if(d.venta + d.comisiones - d.descuentoaplicado <= d.Saldo,d.venta+d.comisiones-d.descuentoaplicado,d.Saldo) as cred_aplicado FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s and d.`UsuarioQueCreoDcto.`=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,usuario))
			
			

			registros_venta = dictfetchall(cursor)

			elementos = len(registros_venta)

			


			"""cursor.execute("SELECT p.razonsocial,a.razonsocial from proveedor p inner join almacen a on (p.empresano=a.empresano and p.proveedorno=a.proveedorno) where p.proveedorno=%s;",(ped['prov_id'],))
			
			prov_alm = cursor.fetchone()"""

			if not registros_venta:
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/lista_ventas_por_usuario.html',{'mensaje':mensaje,})

			else:

				
				for docto in registros_venta:
										
					if (docto['Cancelado'] == '\x00'):  # pregunta si cancelado es '0' en hex o bien falso
						tipodedocumento = docto['TipoDeDocumento']
						TotalVtaBruta = TotalVtaBruta + float(docto['venta'])
						esvta =docto['Concepto'].strip()
						vtadecatalogo = docto['VtaDeCatalogo']

						# calcula para ventas normales y ventas de catalogo
						if esvta == 'Venta' or vtadecatalogo =='\x01':

						#if tipodedocumento == 'Remision':

							#Excluye las ventas de catalogo para totales de creditos cargos y descuento
							if vtadecatalogo =='\x00':
								TotalCreditos = TotalCreditos + float(docto['cred_aplicado'])															
								TotalCargos = TotalCargos + float(docto['comisiones'])	
								TotalDescuentos =  TotalDescuentos + float(docto['descuentoaplicado'])	
								VentaCalzado = VentaCalzado + float(docto['venta'])
							print float(docto['venta']),float(docto['comisiones']),float(docto['cred_aplicado'])
							print "acumulados:"
							print TotalVtaBruta,TotalCargos,TotalCreditos

						if (TotalVtaBruta + TotalCargos > TotalCreditos):
							print "entro por vtabruta+cargos > creditos"

							TotalVtaNeta = TotalVtaBruta-TotalCreditos+TotalCargos-TotalDescuentos
						else:
							print "entro por el otro lado"
							TotalVtaNeta = 0;

						if vtadecatalogo == '\x01' :
							TotalVtaCatalogos = TotalVtaCatalogos + float(docto['Monto'])
						TotalRegistros = TotalRegistros + 1
						TotalVtaProductos = TotalVtaBruta - TotalVtaCatalogos -TotalDescuentos
				
				mensaje ="Registros encontrados == > "



				context = {'form':form,'mensaje':mensaje,'registros_venta':registros_venta,'TotalRegistros':TotalRegistros,'sucursal_nombre':sucursal_nombre,'TotalCreditos':TotalCreditos,'TotalCargos':TotalCargos,'TotalDescuentos':TotalDescuentos,'VentaCalzado':VentaCalzado,'TotalVtaCatalogos':TotalVtaCatalogos,'TotalVtaBruta':TotalVtaBruta,'TotalVtaNeta':TotalVtaNeta,'TotalVtaProductos':TotalVtaProductos,'usuario':usuario_nombre[0],}	
			
				return render(request,'pedidos/lista_ventas_por_usuario.html',context)

		
	else:

		form = ventasporcajeroForm()
	return render(request,'pedidos/consultaventas_por_usuario.html',{'form':form,})


def vtasporusuario(request):


	#pdb.set_trace()
	''' Inicializa Variables '''
	VentaCalzado = 0.0
	TotalVtaBruta = 0.0
	TotalCargos = 0.0
	TotalCreditos = 0.0
	TotalDescuentos = 0.0
	TotalRegistros = 0.0
	TotalVtaCatalogos = 0.0
	TotalVtaNeta = 0.0

	a=''
	b=''
	hoy,hora = trae_fecha_hora_actual(a,b)


	# INICIALIZA REPORTLAB PARA REPORTE
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

    # Create a file-like buffer to receive PDF data.
	buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
	p = canvas.Canvas(buffer,pagesize=letter)
	#p.setPageSize("inch")

	p.setFont("Helvetica",10)
	#p.drawString(1,linea,inicializa_imp)

	mensaje =''
	if request.method == 'POST':

		form = ventasporcajeroForm(request.POST)

		if form.is_valid():

			sucursal = form.cleaned_data['sucursal']
			usuario = form.cleaned_data['usuario']
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

			cursor.execute("SELECT usuario from usuarios WHERE EmpresaNo=1 and usuarioNo=%s;",(usuario,))
			usuario_nombre = cursor.fetchone()
	
			

			
			"""cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,psf.fechatentativallegada,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre)  left join  pedidoslines psf on (p.empresano=psf.empresaNo and p.pedido=psf.pedido and p.productono=psf.productono and p.catalogo=psf.catalogo and p.nolinea=psf.nolinea) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by c.id,psf.fechatentativallegada;",(fechainicial,fechafinal))"""

			
			#cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones > d.Saldo,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado,0) as VtaComisionSaldo FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones-d.descuentoaplicado <= d.Saldo,0,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado) as VtaComisionSaldo,if(d.venta + d.comisiones - d.descuentoaplicado <= d.Saldo,d.venta+d.comisiones-d.descuentoaplicado,d.Saldo) as cred_aplicado FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s and d.`UsuarioQueCreoDcto.`=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,usuario,))
			
			

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
						tipodedocumento = docto['TipoDeDocumento']
						TotalVtaBruta = TotalVtaBruta + float(docto['venta'])
						esvta =docto['Concepto'].strip()
						vtadecatalogo = docto['VtaDeCatalogo']

						# calcula para ventas normales y ventas de catalogo
						if esvta == 'Venta' or vtadecatalogo =='\x01':

						#if tipodedocumento == 'Remision':

							#Excluye las ventas de catalogo para totales de creditos cargos y descuento
							if vtadecatalogo =='\x00':
								TotalCreditos = TotalCreditos + float(docto['cred_aplicado'])															
								TotalCargos = TotalCargos + float(docto['comisiones'])	
								TotalDescuentos =  TotalDescuentos + float(docto['descuentoaplicado'])	
								VentaCalzado = VentaCalzado + float(docto['venta'])
							print float(docto['venta']),float(docto['comisiones']),float(docto['cred_aplicado'])
							print "acumulados:"
							print TotalVtaBruta,TotalCargos,TotalCreditos

						if (TotalVtaBruta + TotalCargos > TotalCreditos):
							print "entro por vtabruta+cargos > creditos"

							TotalVtaNeta = TotalVtaBruta-TotalCreditos+TotalCargos-TotalDescuentos
						else:
							print "entro por el otro lado"
							TotalVtaNeta = 0;

						if vtadecatalogo == '\x01' :
							TotalVtaCatalogos = TotalVtaCatalogos + float(docto['Monto'])
						TotalRegistros = TotalRegistros + 1
						TotalVtaProductos = TotalVtaBruta - TotalVtaCatalogos -TotalDescuentos
				
				mensaje ="Registros encontrados == > "

				#linea = 800
				
				
				
			    # Draw things on the PDF. Here's where the PDF generation happens.
			    # See the ReportLab documentation for the full list of functionality.
				#p.drawString(20,810,mensaje)
				li,ls=0,85
				contador_registros_impresos =0	
				for j in range(1,1000):
					
					#p.translate(0.0,0.0)    # define a large font							

					linea = 800
									 
					p.drawString(250,linea, request.session['cnf_razon_social'])
					linea -=20
					p.setFont("Helvetica",9)
					p.drawString(200,linea, " ---- REPORTE DE VENTAS ("+usuario_nombre[0]+")------")
					p.drawString(250,linea-10, "       "+sucursal_nombre+" ")

					p.setFont("Helvetica",6)
					p.drawString(240,linea-20, "Entre el "+fechainicial.strftime("%Y-%m-%d")+" y el " +fechafinal.strftime("%Y-%m-%d"))
						
					linea -=25
					
					p.drawString(80,linea,request.session['sucursal_direccion'])
					p.drawString(430,linea,"FECHA: "+hoy)
					

					linea -= 8
					p.drawString(80,linea,"COL. "+request.session['sucursal_colonia'])
					p.drawString(430,linea,"HORA:  "+hora)

					linea -= 8
					p.drawString(80,linea,request.session['sucursal_ciudad']+", "+request.session['sucursal_estado'])
					linea -= 20
					
					p.setFont("Helvetica",6)



					p.drawString(80,linea,"Documento")
					p.drawString(120,linea,"Remision")
					p.drawString(160,linea,"Fecha")
					p.drawString(200,linea,"Socio")
					p.drawString(220,linea,"Nombre")
					p.drawString(290,linea,"Vta Bruta")
					p.drawString(330,linea,"Creditos")
					p.drawString(370,linea,"Cargos")
					p.drawString(410,linea,"Desctos")
					p.drawString(450,linea,"Vta Neta")

					linea -= 10
					p.drawString(80,linea,"-"*200)
					linea -= 10
					#p.setFont("Helvetica",8)
					i,paso=0,linea-5
		
					
					for elemento in registros_venta[li:ls]:


						p.drawString(80,paso,str(elemento['NoDocto']))
						p.drawString(120,paso,str(elemento['Consecutivo']))
						p.drawString(160,paso,elemento['FechaCreacion'].strftime("%d-%m-%Y"))		
						p.drawString(200,paso,str(elemento['Asociado']))
						p.drawString(220,paso,(elemento['Nombre']+' '+elemento['ApPaterno']+' '+elemento['ApMaterno'])[0:15])
						p.drawString(290,paso,str(elemento['venta']))			
						p.drawString(330,paso,str(elemento['cred_aplicado']) if elemento['Concepto']=='Venta' else str(0))				
						p.drawString(370,paso,str(elemento['comisiones']) if elemento['Concepto']=='Venta' else str(0))				
						p.drawString(410,paso,str(elemento['descuentoaplicado']))
						p.drawString(450,paso,str(elemento['VtaComisionSaldo']) if elemento['Concepto']=='Venta' else (str(elemento['venta']) if elemento['VtaDeCatalogo'] else str(0)))				
						#p.drawString(200,paso,talla)'''		
						paso -= 8
						i+=1
						contador_registros_impresos+=1

					if registros_venta[li:ls]:
						p.showPage()						

					li=ls
					ls=85*j	
					
					if contador_registros_impresos==elementos:
					
						paso=780
						p.translate(0.0,0.0)

						

						p.setFont("Helvetica",8)

						p.drawString(10,paso,"RESUMEN: ")

						paso-=5

						p.drawString(10,paso,27*'_')

						paso-=10

						
						locale.setlocale( locale.LC_ALL, '' )
						p.drawString(10,paso,"Venta Bruta: ")
						p.drawString(90,paso,locale.currency(TotalVtaBruta,grouping=True))

						paso-=10
						p.drawString(10,paso,"- Creditos: ")
						p.drawString(90,paso,locale.currency(TotalCreditos,grouping=True))

						paso-=10
						p.drawString(10,paso,"+ Cargos: ")
						p.drawString(90,paso,locale.currency(TotalCargos,grouping=True))

						paso-=10
						p.drawString(10,paso,"- Descuentos: ")
						p.drawString(90,paso,locale.currency(TotalDescuentos,grouping=True))

						paso-=7
						p.drawString(90,paso,"-"*17)

						paso-=10
						p.drawString(10,paso,"Venta Neta: ")
						p.drawString(90,paso,locale.currency(TotalVtaNeta,grouping=True))

						paso-=30
						p.drawString(10,paso,"Vta Productos: ")
						p.drawString(90,paso,locale.currency(TotalVtaProductos,grouping=True))

						paso-=10
						p.drawString(10,paso,"Vta Catalogos: ")
						p.drawString(90,paso,locale.currency(TotalVtaCatalogos,grouping=True))


						p.showPage()
						p.save()


						pdf = buffer.getvalue()
						buffer.close()

						response.write(pdf)

						return response




				context = {'form':form,'mensaje':mensaje,'registros_venta':registros_venta,'TotalRegistros':TotalRegistros,'sucursal_nombre':sucursal_nombre,'TotalCreditos':TotalCreditos,'TotalCargos':TotalCargos,'TotalDescuentos':TotalDescuentos,'VentaCalzado':VentaCalzado,'TotalVtaCatalogos':TotalVtaCatalogos,'TotalVtaBruta':TotalVtaBruta,'TotalVtaNeta':TotalVtaNeta,'TotalVtaProductos':TotalVtaProductos}	
			
				#return render(request,'pedidos/lista_ventas.html',context)

		
	else:

		form = ventasporcajeroForm()
	return render(request,'pedidos/consultaventas_por_usuario.html',{'form':form,})


def busca_estilo(request):

	#pdb.set_trace()

	if request.method=='POST':
		
		form = BuscaEstiloForm(request.POST)
		
		if form.is_valid():

			vestilo = form.cleaned_data['var_estilo']
			vfechainicial =form.cleaned_data['fechainicial']
			vfechafinal = form.cleaned_data['fechafinal']

			string_buscar ="%"+(vestilo).strip()+"%"

			cursor = connection.cursor()

			cursor.execute("SELECT l.pedido,h.fechacreacion,\
				h.asociadono,CONCAT(trim(aso.nombre),' ',trim(aso.appaterno),\
				' ',trim(aso.apmaterno)) as nombre,l.status,\
				a.idmarca,a.idestilo,a.idcolor,a.talla,\
				l.precio,l.Observaciones,suc.nombre as nom_suc,alm.RazonSocial as nom_alm,psf.fechamvto FROM pedidoslines l \
				 inner join pedidosheader h on (h.empresano=l.empresano and h.pedidono=l.pedido)\
				 inner join asociado aso on (h.empresano=aso.empresano and h.asociadono=aso.asociadono)\
				 inner join articulo a on (l.empresano=a.empresano and l.productono=a.codigoarticulo\
				 and l.catalogo=a.catalogo) inner join sucursal suc\
				 on (suc.EmpresaNo=l.Empresano and suc.SucursalNo=h.idsucursal)\
				 inner join pedidos_encontrados pe\
				 on (pe.EmpresaNo=l.Empresano and pe.pedido=l.pedido\
				 and pe.productono=l.productono\
				 and l.catalogo=pe.catalogo and l.nolinea=pe.nolinea)\
                 left join almacen alm on (alm.EmpresaNo=h.Empresano\
                 and alm.ProveedorNo=a.idproveedor and alm.Almacen=pe.BodegaEncontro)\
                 inner join pedidos_status_fechas psf on (psf.empresano=l.empresano and psf.pedido=l.pedido and psf.productono=l.productono and psf.catalogo=l.catalogo and psf.nolinea=l.nolinea and psf.status=l.status)\
                 WHERE h.fechacreacion>=%s and h.fechacreacion<=%s and a.idestilo like %s;",(vfechainicial,vfechafinal,string_buscar,) )
			
			reg_encontrados = dictfetchall(cursor)

			return render(request,'pedidos/muestra_estilos_encontrados.html',{'registros':reg_encontrados,})	
	else:
		
		form =BuscaEstiloForm()
	
	return render(request,'pedidos/busca_estilo_forma.html',{'form':form,})	
			


def calcula_compras_socio_por_proveedor(sociono,fechavta,p_opt,p_idprov=0,p_fechainicial='19010101',p_fechafinal='19010101'):

	#pdb.set_trace()

	'''   DEFINICION DE PARAMETROS

	sociono:  Numero de socio al que se le calcularan las compras

	fechavta: Fecha en la que se hace la venta,

	p_opt:  Opcion para calculo:

	1. El calculo se hara para el historial de compras netas del mes del socio

	2.- El calculo se hara para el historial de compras netas del mes anterior a la venta.

	 
	p_idprov: El numero de proveedor con el cual se hara el calculo, si este trae un valor
	          tiene efecto solo para llamados de la rutina de calcular_descuento (en registro de la venta)    
			  de lo contrario se asume que el calculo es para el desglose de compras en el ticket. 
	 '''





	''' Inicializa Variables '''
	#pdb.set_trace()

	sucursal = '0'

	if p_opt == 1:    # Para calculo de desglose de historial de compras en ticket

		fechainicial = fechavta.replace(day=1)

		fechafinal = fechavta

		prov_ini=1
		prov_fin=999


	else:             # Para calculo de base para descuento al momento de la venta

		fechainicial = p_fechainicial
		fechafinal = p_fechafinal
		prov_ini =	p_idprov
		prov_fin = p_idprov


	cursor=connection.cursor()


	# CREA TABLA TEMPORAL
	cursor.execute("DROP TEMPORARY TABLE IF EXISTS vtas_pro_tmp;")
	cursor.execute("CREATE TEMPORARY TABLE vtas_pro_tmp SELECT * FROM vtas_proveedor_imagenbase;")

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


	
	# TRAE VENTA Y DESCUENTOS

	#cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones-d.descuentoaplicado <= d.Saldo,0,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado) as VtaComisionSaldo,if(d.venta + d.comisiones - d.descuentoaplicado <= d.Saldo,d.venta+d.comisiones-d.descuentoaplicado,d.Saldo) as cred_aplicado FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))


	cursor.execute("SELECT a.idproveedor,\
		p.razonsocial,\
		sum(a.precio) as venta,\
		sum(if (a.precio>l.precio and ct.no_maneja_descuentos=0,a.precio-l.precio,0 )) as dscto\
		from pedidoslines l inner join pedidosheader h\
		on (h.empresano=1 and h.pedidono=l.pedido)\
		inner join pedidos_status_fechas f\
		on (f.empresano=1 and f.pedido=l.pedido\
		and f.productono=l.productono\
		and f.status='Facturado'\
		and f.catalogo=l.catalogo and f.nolinea=l.nolinea)\
		inner join articulo a\
		on (a.empresano=1 and a.codigoarticulo=l.productono\
		and a.catalogo=l.catalogo)\
		inner join proveedor p\
		on (p.empresano=1 and p.proveedorno=a.idproveedor)\
		inner join pedidoslinestemporada plt on (plt.empresano=l.empresano and plt.pedido=l.pedido and plt.productono=l.productono and plt.catalogo=l.catalogo and plt.nolinea=l.nolinea)\
		left join catalogostemporada ct on (ct.proveedorno=a.idproveedor and ct.periodo=CAST(SUBSTRING(l.catalogo,1,4) as UNSIGNED) and ct.Anio=plt.Temporada and ct.clasearticulo=l.catalogo)\
		where f.fechamvto>=%s and f.fechamvto<=%s\
		and h.asociadono=%s and a.idproveedor>=%s and a.idproveedor<=%s\
		group by a.idproveedor ; ",\
		(fechainicial,fechafinal,sociono,prov_ini,prov_fin,))

	
	registros_venta = dictfetchall(cursor)
	#print "descuentos:",registros_venta[3]
	
	elementos = len(registros_venta)
	#TRAE DEVOLUCIONES GRAL
	'''cursor.execute("SELECT art.idproveedor,'',sum(l.precio) as devgral,0\
	 from (SELECT psf.empresano,psf.pedido,\
	 psf.productono,\
	 psf.nolinea,\
	 psf.catalogo,\
	 psf.fechamvto from\
	 pedidos_status_fechas as psf \
	 INNER JOIN pedidosheader as h \
	 ON h.empresano=psf.empresano and h.pedidono=psf.pedido WHERE (psf.status='Devuelto' or psf.status='Dev a Prov' or psf.status='RecepEnDevol') and psf.fechamvto>= %s and psf.fechamvto<= %s and h.asociadono=%s) as t2\
	 INNER JOIN pedidos_status_fechas as t3 on\
	 (t2.pedido=t3.pedido and t2.productono=t3.productono\
	 and t2.nolinea=t3.nolinea and t2.catalogo=t3.catalogo)\
     INNER JOIN pedidoslines as l\
     on (t2.empresano=t3.empresano and l.pedido=t3.pedido and l.productono=t3.productono\
     and l.catalogo=t3.catalogo and l.nolinea=t3.nolinea)\
     INNER JOIN articulo as art\
     on (art.empresano= t3.empresano and art.codigoarticulo=t3.productono and art.catalogo=t3.catalogo)\
     WHERE t3.status='Facturado'\
     GROUP BY art.idproveedor;",(fechainicial,fechafinal,sociono))'''
	cursor.execute("SELECT art.idproveedor,'',sum(l.precio) as devgral,0\
	from (SELECT psf.empresano,psf.pedido,\
	psf.productono,\
	psf.nolinea,\
	psf.catalogo,\
	psf.fechamvto from\
	pedidos_status_fechas as psf \
	INNER JOIN pedidosheader as h \
	ON h.empresano=psf.empresano and h.pedidono=psf.pedido WHERE (psf.status='Devuelto') and psf.fechamvto>= %s and psf.fechamvto<= %s and h.asociadono=%s) as t2\
	INNER JOIN pedidoslines as l\
	on (t2.empresano=l.empresano and l.pedido=t2.pedido and l.productono=t2.productono\
	and l.catalogo=t2.catalogo and l.nolinea=t2.nolinea)\
	INNER JOIN articulo as art\
	on (art.empresano= t2.empresano and art.codigoarticulo=t2.productono and art.catalogo=t2.catalogo)\
	WHERE art.idproveedor>=%s and art.idproveedor<=%s\
	GROUP BY art.idproveedor;",(fechainicial,fechafinal,sociono,prov_ini,prov_fin,))

	registros_devgral = dictfetchall(cursor)

	if not registros_venta:

		pass
		
	else:

		cursor.execute("SELECT COUNT(*) as totrec FROM vtas_pro_tmp")
		totrectmp=dictfetchall(cursor)

		
		for registro in registros_venta:

			cursor.execute("UPDATE vtas_pro_tmp SET\
				ventas= %s,\
				venta_FD=0,\
				ventabruta=0,\
				descuento=%s,\
				devoluciones=0,\
				ventaneta=0,nombreprov=%s where idproveedor=%s;",\
			 	(Decimal(registro['venta']),Decimal(registro['dscto']),\
			 		registro['razonsocial'],registro['idproveedor']))					 
                										
			'''TotalVta   = TotalVta + float(registro['venta'])
			Totaldscto = Totaldscto + float(registro['dscto'])
			
			if (float(registro['venta']) != 0.0):
				TotalRegVentas = TotalRegVentas + 1'''


	if not registros_devgral:
		
		pass

	else:				

		for registro in registros_devgral:

			cursor.execute("UPDATE vtas_pro_tmp\
				SET devoluciones=%s WHERE idproveedor=%s;",\
			 			(registro['devgral'],registro['idproveedor']))
								
			
			'''TotalDevGral = TotalDevGral + float(registro['devgral'])
			
			if (float(registro['devgral']) != 0.0):
				TotalRegDev = TotalRegDev + 1'''

	cursor.execute("UPDATE vtas_pro_tmp as t INNER JOIN proveedor as p on t.idproveedor=p.proveedorno SET t.nombreprov=p.razonsocial;")
	cursor.execute("DELETE FROM vtas_pro_tmp WHERE  ventas = 0 and  descuento =0 and devoluciones = 0 and ventaneta = 0;")
	cursor.execute("UPDATE vtas_pro_tmp SET ventabruta = ventas + venta_FD;")
	cursor.execute("UPDATE vtas_pro_tmp SET ventaneta = ventabruta - descuento - devoluciones;")
	
	mensaje =" "

	cursor.execute("SELECT * FROM vtas_pro_tmp;")
	vtasresult =  dictfetchall(cursor)
	print vtasresult
	'''
	cursor.execute("SELECT SUM(ventas) as tot_vtas,SUM(venta_FD) as tot_ventaFD,SUM(ventabruta) as tot_ventabruta, SUM(descuento) as tot_descuento,SUM(devoluciones) as tot_devoluciones,SUM(ventaneta) as tot_ventaneta FROM vtas_pro_tmp;")	
	totales = dictfetchall(cursor)
	for tot in totales:
		tot_vtas = tot['tot_vtas']
		tot_ventaFD = tot['tot_ventaFD']
		tot_ventabruta = tot['tot_ventabruta']
		tot_descuento = tot['tot_descuento']
		tot_devoluciones = tot['tot_devoluciones']
		tot_ventaneta = tot['tot_ventaneta']


	cursor.execute("SELECT d.Monto,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.Concepto FROM documentos d  WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,))
	
	

	registros_vtacomis_vtacatal = dictfetchall(cursor)


	for docto in registros_vtacomis_vtacatal:
								
			if (docto['Cancelado'] == '\x00'):  # pregunta si cancelado es '0' en hex o bien falso
				
				esvta =docto['Concepto'].strip()
				if esvta == 'Venta':
												
					TotalCargos = TotalCargos + float(docto['comisiones'])	
									
				if docto['VtaDeCatalogo'] == '\x01' :
					TotalVtaCatalogos = TotalVtaCatalogos + float(docto['Monto'])


	# SI TOTALES SON None, LES ASIGNA UN CERO YA QUE EN EL CONTEXT
	# HABRIA PROBLEMAS CON LA FUNCION FLOAT(), DADO QUE NO ACEPTA UN None COMO PARAMETRO.
	if tot_vtas is None:
		tot_vtas = 0
	if tot_ventabruta is None:
		tot_ventabruta = 0
	if tot_ventaFD is None:
		tot_ventaFD = 0
	if tot_ventaneta is None:
		tot_ventaneta = 0
	if tot_descuento is None:
		tot_descuento = 0
	if tot_devoluciones is None:
		tot_devoluciones =0
	

	

	context = {'form':form,'mensaje':mensaje,'vtasresult':vtasresult,'TotalRegistros':TotalRegistros,'tot_vtas':float(tot_vtas),'tot_ventaFD':float(tot_ventaFD),'tot_ventabruta':float(tot_ventabruta),'tot_descuento':float(tot_descuento),'tot_devoluciones':float(tot_devoluciones),'tot_ventaneta':float(tot_ventaneta),'TotalCargos':TotalCargos,'TotalVtaCatalogos':TotalVtaCatalogos,'fechainicial':fechainicial,'fechafinal':fechafinal,'sucursal_nombre':sucursal_nombre,'sucursalinicial':sucursalinicial,'sucursalfinal':sucursalfinal,}	
	'''
	return vtasresult	



def piezas_no_solicitadas(request): # el parametro 'tipo' toma los valores 'P' de pedido o 'D' de documento y se pasa a los templates 
	#pdb.set_trace()

	context ={}	
	asociado_data =()

	tipo='P'

	try:

		existe_socio = True
		is_staff =  request.session['is_staff']
		id_sucursal = 0
		session_id = request.session.session_key
		
	except KeyError:
		
		context={'error_msg':"Se perdio su sesion, por favor cierre su navegador completamente e ingrese nuevamente al sistema !",}
		return render(request, 'pedidos/error.html',context)

	form = PiezasNoSolicitadasForm(request)

	socio = 3
	
	cursor = connection.cursor()
	
	cursor.execute("SELECT asociadono,nombre,appaterno,apmaterno,EsSocio,telefono1 from asociado where asociadono=%s;",(socio,))
	
	asociado_data = cursor.fetchone()
				
	print asociado_data	
	print asociado_data		


	request.session['socio_pidiendo'] = asociado_data[0]
	request.session['EsSocio'] = asociado_data[4]
	num_socio = asociado_data[0]
	telefono_socio = asociado_data[5]
	nombre_socio = str(asociado_data[0])+' '+asociado_data[1]+ ' '+asociado_data[2]+' '+(asociado_data[3] if (asociado_data[3] is not None) else 'sin apellido')+'          TELEFONO: '+asociado_data[5]
	

	# trae catalogo de viasolicitud

	cursor.execute("SELECT id,descripcion FROM viasolicitud;")
	vias_solicitud = dictfetchall(cursor)

	# trae catalogo de tipos de servicio

	cursor.execute("SELECT tiposervicio from tiposervicio;")
	tipo_servicio = dictfetchall(cursor)


	cursor.execute("DELETE FROM pedidos_pedidos_tmp where session_key= %s;",[session_id])	


	cursor.close()

	
	cursor = connection.cursor()
	cursor.close()


	context = {'form':form,'nombre_socio':nombre_socio,'num_socio':3,'tipo_servicio':tipo_servicio,'vias_solicitud':vias_solicitud,'id_sucursal':3,'is_staff':is_staff,'tipo':tipo,}
	return render(request,'pedidos/articulos_no_solicitados.html',context,)
	


# REPORTE DE ARTICULOS NO SOLICITADOS ORDENADO POR MARCA 



def rpte_piezas_no_solicitadas(request):
	#pdb.set_trace()
	mensaje =''
	if request.method == 'GET':

		

		form = RpteArtNoSolicitadosForm(request.GET)

		if form.is_valid():

			proveedor = form.cleaned_data['proveedor']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']
			op = form.cleaned_data['op']
			#op='Pantalla'
			cursor=connection.cursor()

			
			"""cursor.execute("SELECT c.id,c.fechacolocacion,c.fechacierre,psf.fechatentativallegada,c.prov_id,c.almacen,c.total_articulos,c.numpedido,c.paqueteria,c.NoGuia FROM prov_ped_cierre c  left  join  pedidos_encontrados p on (c.id=p.id_cierre)  left join  pedidoslines psf on (p.empresano=psf.empresaNo and p.pedido=psf.pedido and p.productono=psf.productono and p.catalogo=psf.catalogo and p.nolinea=psf.nolinea) WHERE psf.fechatentativallegada>=%s and psf.fechatentativallegada<=%s and c.id<>0 group by c.id,psf.fechatentativallegada;",(fechainicial,fechafinal))"""

			if proveedor != u'0':
				
				cursor.execute("SELECT l.Pedido,l.ProductoNo,l.Catalogo,l.Nolinea,p.fechapedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,if(a.talla='NE',l.observaciones,a.talla) as talla,l.precio,a.idProveedor,p.idSucursal,e.BodegaEncontro,alm.RazonSocial FROM pedidoslines l INNER JOIN   pedidosheader p ON (l.EmpresaNo= p.EmpresaNo and l.Pedido=p.PedidoNo) INNER JOIN articulo a ON (l.EmpresaNo=a.EmpresaNo and l.ProductoNo=a.codigoarticulo and l.Catalogo=a.catalogo) INNER JOIN pedidos_encontrados e ON (l.empresano=e.empresano and l.pedido=e.pedido and l.productono=e.productono and l.catalogo=e.catalogo and l.nolinea=e.nolinea) INNER JOIN almacen alm on (alm.empresano=a.empresano and alm.proveedorno=a.idproveedor and alm.almacen=e.bodegaencontro) WHERE l.empresano=1 and l.status='RecepEnDevol' and  p.fechapedido>=%s and p.fechapedido<=%s and a.idproveedor=%s;",(fechainicial,fechafinal,proveedor,))
			else:
				
				cursor.execute("SELECT l.Pedido,l.ProductoNo,l.Catalogo,l.Nolinea,p.fechapedido,p.AsociadoNo,a.idmarca,a.idestilo,a.idcolor,if(a.talla='NE',l.observaciones,a.talla) as talla,l.precio,a.idProveedor,p.idSucursal,e.BodegaEncontro,alm.RazonSocial FROM pedidoslines l INNER JOIN pedidos_encontrados e ON (l.EmpresaNo=e.EmpresaNo and l.Pedido=e.Pedido and l.ProductoNo=e.ProductoNo and l.Catalogo=e.Catalogo and l.NoLinea=e.NoLinea) INNER JOIN pedidosheader p ON (l.EmpresaNo= p.EmpresaNo and l.Pedido=p.PedidoNo) INNER JOIN articulo a ON (e.EmpresaNo=a.EmpresaNo and e.ProductoNo=a.codigoarticulo and e.Catalogo=a.catalogo) INNER JOIN almacen alm on (alm.empresano=a.empresano and alm.proveedorno=a.idproveedor and alm.almacen=e.bodegaencontro) WHERE l.empresano=1 and l.status='RecepEnDevol' and  p.fechapedido>=%s and p.fechapedido<=%s order by a.idmarca,p.fechapedido;",(fechainicial,fechafinal,))

			 
			lista_pedidos = dictfetchall(cursor)

			

			elementos = len(lista_pedidos)

			


			"""cursor.execute("SELECT p.razonsocial,a.razonsocial from proveedor p inner join almacen a on (p.empresano=a.empresano and p.proveedorno=a.proveedorno) where p.proveedorno=%s;",(ped['prov_id'],))
			
			prov_alm = cursor.fetchone()"""

			if not lista_pedidos:
				mensaje = 'No se encontraron registros !'
				return render(request,'pedidos/rpte_piezas_no_solicitadas.html',{'mensaje':mensaje,})

			else:

				if op == 'Pantalla':

					print "lo que hay en pedidos"
					for ped in lista_pedidos:
						print ped

					
					mensaje ="Registros encontrados == > "

					context = {'form':form,'mensaje':mensaje,'elementos':elementos,'lista_pedidos':lista_pedidos,}	
				
					return render(request,'pedidos/rpte_piezas_no_solicitadas.html',context)
				else:

					response = HttpResponse(content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename="piezas_no_solicitadas.csv"'

					writer = csv.writer(response)
					writer.writerow(['PEDIDO','FECHA_PEDIDO','MARCA','ESTILO','COLOR','TALLA','PRECIO','BODEGA'])
					
					for registro in lista_pedidos:
						print registro
						# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
						llaves_a_mostrar = ['Pedido','fechapedido','idmarca','idestilo','idcolor','talla','precio','RazonSocial'] 
						# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
						lista = [registro[x] for x in llaves_a_mostrar]					
						writer.writerow(lista)
					cursor.close()
					return response			

		
	else:

		form = RpteArtNoSolicitadosForm()
	return render(request,'pedidos/rpte_piezas_no_solicitadas_form.html',{'form':form,})
	
 


def edita_asociado(request,asociadono):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	
	

	msg = ''

	if request.method == 'POST':

		form = DatosAsociadoForm(request.POST)
		if form.is_valid():
			asociado = form.cleaned_data['asociadono']
			numcontrol=form.cleaned_data['numcontrol']
			nombre = form.cleaned_data['nombre']
			appaterno = form.cleaned_data['appaterno']
			apmaterno = form.cleaned_data['apmaterno']
			direccion = form.cleaned_data['direccion']
			colonia = form.cleaned_data['colonia']
			ciudad = form.cleaned_data['ciudad']
			estado = form.cleaned_data['estado']
			pais = form.cleaned_data['pais']
			#codigopostal = form.cleaned_data['codigopostal']
			telefono1 = form.cleaned_data['telefono1']
			telefono2 = form.cleaned_data['telefono2']
			fax = form.cleaned_data['fax']
			cel = form.cleaned_data['celular']
			radio = form.cleaned_data['radio']
			direccionelectronica = form.cleaned_data['direccionelectronica']
			psw_paso = form.cleaned_data['psw_paso']
			essocio = form.cleaned_data['essocio']
			forzarcobroanticipo = form.cleaned_data['forzarcobroanticipo']
			numeroweb = form.cleaned_data['numeroweb']
			
			if numeroweb is None:
				numeroweb =0


			'''VALIDA USUARIO Y DERECHOS '''


			hoy = datetime.now()
			fecha_hoy = hoy.strftime("%Y-%m-%d")
			hora_hoy = hoy.strftime("%H:%M:%S") 

	

			usr_existente=0
			permiso_exitoso=0

			try:

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,3)

				if permiso_exitoso ==0:

					raise ValueError

			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para editar información de socios !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)		




			cursor =  connection.cursor()
			try:

				cursor.execute('START TRANSACTION')
				cursor.execute('UPDATE asociado SET nombre = %s,\
				appaterno = %s,\
				apmaterno = %s,\
				Direccion = %s,\
				Colonia = %s,\
				Ciudad = %s,\
				Estado = %s,\
				Pais = %s,\
				telefono1 = %s,\
				telefono2 = %s,\
				fax = %s,\
				celular = %s,\
				radio = %s,\
				direccionelectronica= %s,\
				essocio = %s,\
				forzarcobroanticipo = %s,\
				num_web = %s,\
				nocontrol=%s\
				WHERE asociadono=%s;',(nombre.upper().lstrip(),appaterno.upper().lstrip(),apmaterno.upper().lstrip(),direccion.upper().lstrip(),colonia.upper().lstrip(),ciudad.upper().lstrip(),estado.upper().lstrip(),pais.upper().lstrip(),telefono1,telefono2,fax,cel,radio.lstrip(),direccionelectronica.lower().lstrip(),essocio,forzarcobroanticipo,numeroweb,numcontrol.upper().lstrip(),asociadono,))

				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,3,fecha_hoy,hora_hoy,'Se modifico el socio: '+str(asociado)))		
							
				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:asociados'))


			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				msg = 'Error en base de datos !'
				return HttpResponse('<h3>Ocurrio un error en la base de datos</h3><h2>{{e}}</h2>')

		else:
			
			pass
	else:	

		form = DatosAsociadoForm()
		
		cursor=connection.cursor()
		cursor.execute("SELECT 	p.asociadono,\
								p.nombre,\
								p.appaterno,\
								p.apmaterno,\
								p.Direccion,\
								p.Colonia,\
								p.Ciudad,\
								p.Estado,\
								p.Pais,\
								p.telefono1,\
								p.telefono2,\
								p.fax,\
								p.celular,\
								p.radio,\
								p.direccionelectronica,\
								p.NoControl,\
								p.EsSocio,\
								p.ForzarCobroAnticipo,\
								p.num_web\
								from asociado p where p.asociadono=%s;",(asociadono,))
		asociado = cursor.fetchone()
		
		form = DatosAsociadoForm(initial={'asociadono':asociado[0],'nombre':asociado[1],'appaterno':asociado[2],'apmaterno':asociado[3],'direccion':asociado[4],'colonia':asociado[5],'ciudad':asociado[6],'estado':asociado[7],'pais':asociado[8],'telefono1':asociado[9],'telefono2':asociado[10],'fax':asociado[11],'celular':asociado[12],'radio':asociado[13],'direccionelectronica':asociado[14],'numcontrol':asociado[15], 'essocio':asociado[16],'forzaranticipo':False if asociado[17] else True,'numeroweb':asociado[18],'forzarcobroanticipo':asociado[17],})
					
	return render(request,'pedidos/edita_asociado.html',{'form':form,'asociadono':asociadono,})


def crea_asociado(request):

	msg = ''

	hoy = date.today()

	if request.method == 'POST':

		form = DatosAsociadoForm(request.POST)
		if form.is_valid():
			asociadoo = form.cleaned_data['asociadono']
			numcontrol = form.cleaned_data['numcontrol']
			nombre = form.cleaned_data['nombre']
			appaterno = form.cleaned_data['appaterno']
			apmaterno = form.cleaned_data['apmaterno']
			direccion = form.cleaned_data['direccion']
			colonia = form.cleaned_data['colonia']
			ciudad = form.cleaned_data['ciudad']
			estado = form.cleaned_data['estado']
			pais = form.cleaned_data['pais']
			#codigopostal = form.cleaned_data['codigopostal']
			telefono1 = form.cleaned_data['telefono1']
			telefono2 = form.cleaned_data['telefono2']
			fax = form.cleaned_data['fax']
			cel = form.cleaned_data['celular']
			radio = form.cleaned_data['radio']
			direccionelectronica = form.cleaned_data['direccionelectronica']
			psw_paso = form.cleaned_data['psw_paso']
			essocio = form.cleaned_data['essocio']
			forzarcobroanticipo = form.cleaned_data['forzarcobroanticipo']
			numeroweb = form.cleaned_data['numeroweb']
			

			if numeroweb is None:
				numeroweb =0

			
			'''VALIDA USUARIO Y DERECHOS '''


			hoy = datetime.now()
			fecha_hoy = hoy.strftime("%Y-%m-%d")
			hora_hoy = hoy.strftime("%H:%M:%S") 

			usr_existente=0
			permiso_exitoso=0

			try:

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,1)

				if permiso_exitoso ==0:

					raise ValueError

			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para crear socios !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)		


			cursor =  connection.cursor()
			try:

				cursor.execute('START TRANSACTION')

				cursor.execute("SELECT asociadono FROM asociado ORDER BY asociadono desc limit 1;")
				ultimo_socio = cursor.fetchone()	



				cursor.execute('INSERT INTO asociado(empresano,asociadono,nombre,\
				appaterno,\
				apmaterno,\
				Direccion,\
				Colonia,\
				Ciudad,\
				Estado,\
				Pais,\
				telefono1,\
				telefono2,\
				fax,\
				celular,\
				radio,\
				direccionelectronica,\
				essocio,\
				forzarcobroanticipo,\
				num_web,\
				fechaalta,\
				fechabaja,\
				pathfoto,\
				sucursalno,\
				creditodisponible,\
				nocontrol) \
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);',(1,ultimo_socio[0]+1,nombre.upper().lstrip(),appaterno.upper().lstrip(),apmaterno.upper().lstrip(),direccion.upper().lstrip(),colonia.upper().lstrip(),ciudad.upper().lstrip(),estado.upper().lstrip(),pais.upper().lstrip(),telefono1,telefono2,fax,cel,radio.lstrip(),direccionelectronica.lower().lstrip(),essocio,forzarcobroanticipo,numeroweb,hoy,'19010101',' ',0,0,numcontrol))

				cursor.execute("INSERT INTO ventas_socio_imagenbase(asociadono,ventas,venta_fd,venta_bruta,descuento,devoluciones,venta_neta,bono) values(%s,%s,%s,%s,%s,%s,%s,%s);",(ultimo_socio[0]+1,0,0,0,0,0,0,0))				


				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,1,fecha_hoy,hora_hoy,'Se creó el socio: '+str(ultimo_socio[0]+1)))		




				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:asociados'))


			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				msg = 'Error en base de datos !'
				return HttpResponse('<h3>Ocurrio un error en la base de datos</h3><h2>{{e}}</h2>')

		else:
			
			pass
	else:	

		form = DatosAsociadoForm()
		
					
	return render(request,'pedidos/crea_asociado.html',{'form':form,})



def filtrocatalogosasociado(request,asociadono):
	#pdb.set_trace()
	if  request.method =='POST':

		form = FiltroSocioCatalogoForm(request.POST)

		if form.is_valid():

			#proveedor = form.cleaned_data['ProveedorNo']
			#catalogo = form.cleaned_data['ClaseArticulo']
			periodo = form.cleaned_data['Periodo']	
			anio = form.cleaned_data['Anio']

			cursor = connection.cursor()


			cursor.execute('SELECT p.razonsocial,c.clasearticulo,if(c.activo,"Si","No") as activo,c.nodocto from sociocatalogostemporada c INNER JOIN proveedor p on (p.empresano=1 and p.proveedorno=c.proveedorno) WHERE c.asociadono=%s and c.periodo=%s and c.anio=%s;',(asociadono,periodo,anio,))
			registros = dictfetchall(cursor)
				
				

			'''cursor.execute('SELECT razonsocial as nom_almacen from almacen where empresano=1 and proveedorno=%s and almacen=%s;',(proveedor,almacen))
			nom_almacen = cursor.fetchone()'''
			cursor.close()
			return render(request,'pedidos/lista_catalogos_socio.html',{'registros':registros,'anio':'Primavera/Verano' if anio==u'1' else 'Otoño/Invierno','periodo':periodo,})

	form = FiltroSocioCatalogoForm()
	return render (request,'pedidos/filtro_asociado_catalogos.html',{'form':form,'asociadono':asociadono,})		





def filtroproveedor_almacen(request):

	if request.method=='POST':

		form = FiltroProveedorForm(request.POST)
		
		if form.is_valid():
			
			proveedor = form.cleaned_data['proveedor']

			cursor = connection.cursor()

			cursor.execute('SELECT Almacen,RazonSocial,Direccion,Telefono1 FROM almacen WHERE EmpresaNO=1 and ProveedorNo=%s;',(proveedor,))
			registros = dictfetchall(cursor)	
			
			cursor.execute('SELECT razonsocial FROM proveedor WHERE empresano=1 and proveedorno=%s',(proveedor,))
			prov_nom = cursor.fetchone()

			return render(request,'pedidos/lista_almacenes.html',{'registros':registros,'prov_nom':prov_nom[0],'proveedorno':proveedor,})		

	form = FiltroProveedorForm()
	return render(request,'pedidos/filtro_proveedor_almacen.html',{'form':form,})





def crea_almacen(request,proveedorno):

	msg = ''

	hoy = date.today()

	if request.method == 'POST':

		form = CreaAlmacenForm(request.POST)
		if form.is_valid():
			razonsocial = form.cleaned_data['RazonSocial']
			direccion = form.cleaned_data['Direccion']
			colonia = form.cleaned_data['Colonia']
			ciudad = form.cleaned_data['Ciudad']
			estado = form.cleaned_data['Estado']
			pais = form.cleaned_data['Pais']
			#codigopostal = form.cleaned_data['codigopostal']
			telefono1 = form.cleaned_data['telefono1']
			telefono2 = form.cleaned_data['telefono2']
			fax = form.cleaned_data['fax']
			cel = form.cleaned_data['celular']
			radio = form.cleaned_data['radio']
			direccionelectronica = form.cleaned_data['direccionelectronica']
			usr_id = form.cleaned_data['usr_id']
			


			cursor =  connection.cursor()
			try:

				cursor.execute('START TRANSACTION')

				cursor.execute("SELECT almacen FROM almacen ORDER BY almacen desc limit 1;")
				ultimo_almacen = cursor.fetchone()	



				cursor.execute('INSERT INTO almacen(empresano,proveedorno,almacen,RazonSocial,\
				Direccion,\
				Colonia,\
				Ciudad,\
				Estado,\
				Pais,\
				telefono1,\
				telefono2,\
				fax,\
				celular,\
				radio,\
				direccionelectronica,\
				fechaalta,\
				fechabaja) \
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);',(1,proveedorno,ultimo_almacen[0]+1,razonsocial.upper().lstrip(),direccion.upper().lstrip(),colonia.upper().lstrip(),ciudad.upper().lstrip(),estado.upper().lstrip(),pais.upper().lstrip(),telefono1,telefono2,fax,cel,radio.lstrip(),direccionelectronica.lower().lstrip(),'19010101','19010101'))
				

				cursor.execute("COMMIT;")

				'''				
				cursor = connection.cursor()

				cursor.execute('SELECT Almacen,RazonSocial,Direccion,Telefono1 FROM almacen WHERE EmpresaNO=1 and ProveedorNo=%s;',(proveedorno,))
				registros = dictfetchall(cursor)	
				
				cursor.execute('SELECT razonsocial FROM proveedor WHERE empresano=1 and proveedorno=%s',(proveedorno,))
				prov_nom = cursor.fetchone()

				return render(request,'pedidos/lista_almacenes.html',{'registros':registros,'prov_nom':prov_nom[0],'proveedorno':proveedorno,})'''		


				return HttpResponseRedirect(reverse('pedidos:filtroproveedor_almacen'))


			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				msg = 'Error en base de datos !'
				return HttpResponse('<h3>Ocurrio un error en la base de datos</h3><h2>{{e}}</h2>')

		else:
			
			pass
	else:	

		form = CreaAlmacenForm()
		
					
	return render(request,'pedidos/crea_almacen.html',{'form':form,'proveedorno':proveedorno})


def edita_almacen(request,proveedorno,almacenno):
	#pdb.set_trace()
	msg = ''

	hoy = date.today()

	cursor =  connection.cursor()


	if request.method == 'POST':

		form = CreaAlmacenForm(request.POST)
		if form.is_valid():
			razonsocial = form.cleaned_data['RazonSocial']
			direccion = form.cleaned_data['Direccion']
			colonia = form.cleaned_data['Colonia']
			ciudad = form.cleaned_data['Ciudad']
			estado = form.cleaned_data['Estado']
			pais = form.cleaned_data['Pais']
			#codigopostal = form.cleaned_data['codigopostal']
			telefono1 = form.cleaned_data['telefono1']
			telefono2 = form.cleaned_data['telefono2']
			fax = form.cleaned_data['fax']
			cel = form.cleaned_data['celular']
			radio = form.cleaned_data['radio']
			direccionelectronica = form.cleaned_data['direccionelectronica']
			psw_paso = form.cleaned_data['psw_paso']
			


			

			fecha_hoy,hora_hoy = trae_fecha_hora_actual('','')



			usr_existente=0
			permiso_exitoso=0

			try:

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,14)

				if permiso_exitoso ==0:

					raise ValueError




				cursor.execute('START TRANSACTION')

			
				cursor.execute('UPDATE almacen SET RazonSocial=%s,\
				Direccion=%s,\
				Colonia=%s,\
				Ciudad=%s,\
				Estado=%s,\
				Pais=%s,\
				telefono1=%s,\
				telefono2=%s,\
				fax=%s,\
				celular=%s,\
				radio=%s,\
				direccionelectronica=%s,\
				fechaalta=%s,\
				fechabaja=%s\
				WHERE empresano=%s and proveedorno=%s and almacen=%s;',(razonsocial.upper().lstrip(),direccion.upper().lstrip(),colonia.upper().lstrip(),ciudad.upper().lstrip(),estado.upper().lstrip(),pais.upper().lstrip(),telefono1,telefono2,fax,cel,radio.lstrip(),direccionelectronica.lower().lstrip(),'19010101','19010101',1,proveedorno,almacenno))

				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,14,fecha_hoy,hora_hoy,'Se modificó el almacén: '+str(almacenno)+' del proveedor: '+str(proveedorno)))		

				cursor.execute("COMMIT;")
				cursor.close()

				'''	
				cursor.execute("COMMIT;")

				cursor = connection.cursor()

				cursor.execute('SELECT Almacen,RazonSocial,Direccion,Telefono1 FROM almacen WHERE EmpresaNO=1 and ProveedorNo=%s;',(proveedorno,))
				registros = dictfetchall(cursor)	
				
				cursor.execute('SELECT razonsocial FROM proveedor WHERE empresano=1 and proveedorno=%s',(proveedorno,))
				prov_nom = cursor.fetchone()

				return render(request,'pedidos/lista_almacenes.html',{'registros':registros,'prov_nom':prov_nom[0],'proveedorno':proveedorno,})'''		



				return HttpResponseRedirect(reverse('pedidos:filtroproveedor_almacen'))


			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				msg = 'Error en base de datos !'
				return HttpResponse('<h3>Ocurrio un error en la base de datos</h3><h2>{{e}}</h2>')
			
			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para editar información de almacenes !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)		

		else:
			
			pass
	else:	

		cursor.execute('SELECT * FROM almacen where proveedorno=%s and almacen=%s limit 1;',(proveedorno,almacenno))
		alm =cursor.fetchone()


		form = CreaAlmacenForm(initial={'RazonSocial':alm[3],'Direccion':alm[4],'Colonia':alm[5],'Ciudad':alm[6],'Estado':alm[7],'Pais':alm[8],'telefono1':alm[9],'telefono2':alm[10],'fax':alm[11],'celular':alm[12],'radio':alm[13],'direccionelectronica':alm[14],})
		
					
	return render(request,'pedidos/edita_almacen.html',{'form':form,'proveedorno':proveedorno,'almacenno':almacenno,})


def asociado_edita_descuento(request,proveedorno,asociadono):

	#pdb.set_trace()
	cursor =  connection.cursor()

	if request.method=='POST':

		form=EditaDescuentoAsociadoForm(request.POST)

		if form.is_valid():

			descuento =form.cleaned_data['descuento']	

			psw_paso =form.cleaned_data['psw_paso']

			usr_existente=0
			permiso_exitoso=0

			fecha_hoy,hora_hoy=trae_fecha_hora_actual('','')

			
			try:

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,30)

				if permiso_exitoso ==0:

					raise ValueError


				cursor.execute('START TRANSACTION')
				cursor.execute("UPDATE socio_descuento SET descuento_porc = %s\
				WHERE idsocio=%s and idproveedor=%s;",(descuento,asociadono,proveedorno,))
				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,30,fecha_hoy,hora_hoy,'Modificó el descuento a nuevo valor de '+str(descuento)+' para el socio '+str(asociadono)+' en el proveedor '+str(proveedorno)))		
			
							
				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:asociado_proveedor',args=(asociadono,)))
				

			except DatabaseError as e:
				print e
				
				cursor.execute('ROLLBACK;')
				error_msg = 'Ha ocurrido un error en base de datos !'
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)

			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para operar en descuentos al socios !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)	


	else:
	
		cursor.execute('SELECT descuento_porc FROM socio_descuento where idsocio=%s and idproveedor=%s limit 1;',(asociadono,proveedorno,))
		alm =cursor.fetchone()


		form = EditaDescuentoAsociadoForm(initial={'descuento':alm[0],})

	return render(request,'pedidos/edita_socio_descuento.html',{'form':form,'proveedorno':proveedorno,'asociadono':asociadono,})				





def asociado_nuevo_descuento(request,asociadono):

	#pdb.set_trace()
	cursor =  connection.cursor()

	if request.method=='POST':

		form=CreaDescuentoAsociadoForm(request.POST)

		if form.is_valid():

			proveedorno=form.cleaned_data['proveedor']
			descuento =form.cleaned_data['descuento']	
			psw_paso = form.cleaned_data['psw_paso']
			
			fecha_hoy,hora_hoy=trae_fecha_hora_actual('','')
			usr_existente=0
			permiso_exitoso=0

			try:

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,30)

				if permiso_exitoso ==0:

					raise ValueError

				cursor.execute('START TRANSACTION')
				cursor.execute("INSERT INTO socio_descuento(idproveedor,idsocio,descuento_porc) VALUES(%s,%s,%s);",(proveedorno,asociadono,descuento,))
				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,30,fecha_hoy,hora_hoy,'Agregó descuento del '+str(descuento)+' al socio '+str(asociadono)+' en el proveedor '+str(proveedorno)))		
							
							
				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:asociado_proveedor',args=(asociadono,)))
				

			except IntegrityError as error_msg:

				context={'error_msg':"Actualmente ya existe un descuento para este proveedor, si desea puede editarlo y modificarlo pero no crear otro !",}
				return render(request, 'pedidos/error.html',context)

			except DatabaseError as error_msg:
				context={'error_msg':error_msg,}
				cursor.execute('ROLLBACK;')
				return render(request, 'pedidos/error.html',context)
			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para operar en descuentos al socios !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)		
				
	else:
		

		form = CreaDescuentoAsociadoForm()

	return render(request,'pedidos/crea_socio_descuento.html',{'form':form,'asociadono':asociadono,})				




# REPORTE DE REMISIONES ESPECIALES

def rpte_remisiones_especiales(request):


	#pdb.set_trace()
	''' Inicializa Variables '''
	
	TotalVta = 0.0
	TotalVtaBruta= 0.0

	a=''
	b=''
	hoy,hora = trae_fecha_hora_actual(a,b)



	#p.drawString(1,linea,inicializa_imp)

	mensaje =''
	if request.method == 'POST':

		form = remisionesespecialesForm(request.POST)

		if form.is_valid():

			sucursal = form.cleaned_data['sucursal']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']
			op = form.cleaned_data['op']

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
			
			cursor.execute("SELECT d.nodocto,d.concepto,d.monto,d.Asociado,a.ApPaterno,a.ApMaterno,a.Nombre,d.Cancelado,d.vtadecatalogo,d.idsucursal,d.FechaCreacion, suc.nombre as nom_suc from documentos d inner join asociado a on (d.empresano=a.empresano and d.asociado=a.asociadono) inner join sucursal suc on (suc.empresano=d.empresano and suc.sucursalno=d.idsucursal) where d.tipodedocumento='Remision' and not(d.cancelado) and not(d.vtadecatalogo) and d.fechacreacion>=%s and d.fechacreacion<=%s and d.idsucursal>=%s and d.idsucursal<=%s and d.nodocto not in (select p.remisionno from pedidoslines p) order by d.idsucursal,d.nodocto;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal,))

			#cursor.execute("SELECT d.EmpresaNo,d.Consecutivo,d.NoDocto,d.TipoDeDocumento,d.TipoDeVenta,d.Asociado,d.FechaCreacion,d.Concepto,d.Monto,d.Saldo,d.VtaDeCatalogo,d.Cancelado,d.comisiones,d.idsucursal,d.venta,d.descuentoaplicado,a.AsociadoNo,a.Nombre,a.ApPaterno,a.ApMaterno,s.SucursalNo,s.nombre as suc_nom, if(d.venta + d.comisiones-d.descuentoaplicado <= d.Saldo,0,d.venta+d.comisiones-d.Saldo-d.descuentoaplicado) as VtaComisionSaldo,if(d.venta + d.comisiones - d.descuentoaplicado <= d.Saldo,d.venta+d.comisiones-d.descuentoaplicado,d.Saldo) as cred_aplicado FROM documentos d INNER  JOIN  asociado a on ( d.EmpresaNo=a.EmpresaNo and d.Asociado=a.AsociadoNo) INNER JOIN  sucursal s ON (d.EmpresaNo= s.EmpresaNo and d.idsucursal=s.SucursalNo) WHERE d.EmpresaNo=1 and  d.TipoDeDocumento='Remision' and not(d.Cancelado) and d.TipoDeVenta='Contado' and d.FechaCreacion>=%s and d.FechaCreacion<=%s and d.idsucursal>=%s  and d.idsucursal<=%s;",(fechainicial,fechafinal,sucursalinicial,sucursalfinal))
			
			

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
						
						TotalVtaBruta = TotalVtaBruta + float(docto['monto'])
						
						
				mensaje ="Registros encontrados == > "

				#linea = 800
				
				
				
			    # Draw things on the PDF. Here's where the PDF generation happens.
			    # See the ReportLab documentation for the full list of functionality.
				#p.drawString(20,810,mensaje)
			
				if op == 'Pantalla':

					# INICIALIZA REPORTLAB PARA REPORTE
					response = HttpResponse(content_type='application/pdf')
					response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

				    # Create a file-like buffer to receive PDF data.
					buffer = io.BytesIO()

				    # Create the PDF object, using the buffer as its "file."
					p = canvas.Canvas(buffer,pagesize=letter)
					#p.setPageSize("inch")

					p.setFont("Helvetica",10)
	
					li,ls=0,85
					contador_registros_impresos =0	
					for j in range(1,1000):
						
						#p.translate(0.0,0.0)    # define a large font							

						linea = 800
										 
						p.drawString(250,linea, request.session['cnf_razon_social'])
						linea -=20
						p.setFont("Helvetica",9)
						p.drawString(200,linea, " ----- REMISIONES ESPECIALES ------")
						p.drawString(240,linea-10, "       "+sucursal_nombre+" ")

						p.setFont("Helvetica",6)
						p.drawString(230,linea-20, "Entre el "+fechainicial.strftime("%Y-%m-%d")+" y el " +fechafinal.strftime("%Y-%m-%d"))
							
						linea -=25
						
						p.drawString(80,linea,request.session['sucursal_direccion'])
						p.drawString(430,linea,"FECHA: "+hoy)
						

						linea -= 8
						p.drawString(80,linea,"COL. "+request.session['sucursal_colonia'])
						p.drawString(430,linea,"HORA:  "+hora)

						linea -= 8
						p.drawString(80,linea,request.session['sucursal_ciudad']+", "+request.session['sucursal_estado'])
						linea -= 20
						
						p.setFont("Helvetica",6)



						p.drawString(80,linea,"Sucursal")
						p.drawString(120,linea,"")
						p.drawString(160,linea,"Fecha")
						p.drawString(200,linea,"Socio")
						p.drawString(220,linea,"Nombre")
						p.drawString(290,linea,"Remision")
						p.drawString(330,linea,"Monto")
						p.drawString(370,linea,"Concepto")
						p.drawString(410,linea,"")
						p.drawString(450,linea,"")

						linea -= 10
						p.drawString(80,linea,"-"*200)
						linea -= 10
						#p.setFont("Helvetica",8)
						i,paso=0,linea-5
			
						
						for elemento in registros_venta[li:ls]:


							p.drawString(80,paso,str(elemento['nom_suc']))
							#p.drawString(120,paso,str(elemento['nodocto']))
							p.drawString(160,paso,elemento['FechaCreacion'].strftime("%d-%m-%Y"))		
							p.drawString(200,paso,str(elemento['Asociado']))
							p.drawString(220,paso,(elemento['Nombre']+' '+elemento['ApPaterno']+' '+elemento['ApMaterno'])[0:15])
							p.drawString(290,paso,str(elemento['nodocto']))			
							p.drawString(330,paso,str(elemento['monto']))				
							p.drawString(370,paso,str(elemento['concepto']))				
							#p.drawString(200,paso,talla)'''		
							paso -= 8
							i+=1
							contador_registros_impresos+=1

						if registros_venta[li:ls]:
							p.showPage()						

						li=ls
						ls=85*j	
						
						if contador_registros_impresos==elementos:
						
							paso=780
							p.translate(0.0,0.0)

							

							p.setFont("Helvetica",8)

							p.drawString(10,paso,"")

							paso-=5

							#p.drawString(10,paso,27*'_')

							paso-=10

							p.setFont("Helvetica",12)
							locale.setlocale( locale.LC_ALL, '' )
							p.drawString(10,paso,"Total: ")
							p.drawString(90,paso,locale.currency(TotalVtaBruta,grouping=True))



							p.showPage()
							p.save()


							pdf = buffer.getvalue()
							buffer.close()

							response.write(pdf)

							return response

				else:

					response = HttpResponse(content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename="remisiones_especiales.csv"'

					writer = csv.writer(response)
					writer.writerow(['SUCURSAL','FECHA_CREACION','NUM_SOCIO','NOMBRE','AP_PATERNO','AP_MATERNO','NUM_REMISION','MONTO','CONCEPTO'])
					
					for registro in registros_venta:
						print registro
						# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
						llaves_a_mostrar = ['nom_suc','FechaCreacion','Asociado','Nombre','ApPaterno','ApMaterno','nodocto','monto','concepto'] 
						# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
						lista = [registro[x] for x in llaves_a_mostrar]					
						writer.writerow(lista)
					cursor.close()
					return response			

		







				context = {'form':form,'mensaje':mensaje,'registros_venta':registros_venta,'TotalRegistros':TotalRegistros,'sucursal_nombre':sucursal_nombre,'TotalCreditos':TotalCreditos,'TotalCargos':TotalCargos,'TotalDescuentos':TotalDescuentos,'VentaCalzado':VentaCalzado,'TotalVtaCatalogos':TotalVtaCatalogos,'TotalVtaBruta':TotalVtaBruta,'TotalVtaNeta':TotalVtaNeta,'TotalVtaProductos':TotalVtaProductos}	
			
				#return render(request,'pedidos/lista_ventas.html',context)
				''' OJO CON LO SIGUIENTE
				response = HttpResponse(content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename="piezas_no_solicitadas.csv"'

					writer = csv.writer(response)
					writer.writerow(['PEDIDO','FECHA_PEDIDO','MARCA','ESTILO','COLOR','TALLA','PRECIO','BODEGA'])
					
					for registro in lista_pedidos:
						print registro
						# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
						llaves_a_mostrar = ['Pedido','fechapedido','idmarca','idestilo','idcolor','talla','precio','RazonSocial'] 
						# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
						lista = [registro[x] for x in llaves_a_mostrar]					
						writer.writerow(lista)
					cursor.close()
					return response'''			

		
	else:

		form = remisionesespecialesForm()
	return render(request,'pedidos/rpte_remisiones_especiales_form.html',{'form':form,})





# LISTA DE USUARIOS


def lista_usuarios(request):
	cursor=connection.cursor()
	cursor.execute('SELECT usuariono,nombre,fechacreacion,if(activo,"SI","NO") as esta_activo,usuario from usuarios;')
	usuarios = dictfetchall(cursor)
	cursor.close()
	context = {'usuarios': usuarios}
	return render(request, 'pedidos/usuarios.html', context)


# EDITA USUARIO


def edita_usuario(request,usuariono):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	
	

	msg = ''

	if request.method == 'POST':

		form = DatosUsuarioForm(request.POST)
		if form.is_valid():
			usuariono = form.cleaned_data['usuariono']
			nombre = form.cleaned_data['nombre']
			psw_paso = form.cleaned_data['psw_paso']
			activo = form.cleaned_data['activo']
			email = form.cleaned_data['email']
			usuario = form.cleaned_data['usuario']
			
			activo = int(activo)


			hoy = datetime.now()
			fecha_hoy = hoy.strftime("%Y-%m-%d")
			hora_hoy = hoy.strftime("%H:%M:%S") 



			usr_existente=0
			permiso_exitoso=0

			try:

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,19)

				if permiso_exitoso ==0:

					raise ValueError

				cursor=connection.cursor()

				cursor.execute('START TRANSACTION')

				cursor.execute('UPDATE usuarios SET nombre = %s,\
				activo = %s,\
				usuario=%s\
				WHERE usuariono=%s;',(nombre.upper().lstrip(),activo,usuario,usuariono,))

				cursor.execute('UPDATE usr_extend SET email= %s \
				WHERE usuariono=%s;',(email,usuariono,))

				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,19,fecha_hoy,hora_hoy,'Se modificó el usuario: '+str(usuariono)))		


				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:lista_usuarios'))
				

			except IntegrityError as error_msg:

				#print error_msg

				context={'error_msg':"Error de integridad. Es posible que el valor que escogió para el campo 'Usuario' ya esté asignado a otro usuario registrado, este valor debe ser único, por favor elija otro valor distinto para este campo !",}
				return render(request, 'pedidos/error.html',context)

			except DatabaseError as error_msg:
				context={'error_msg':error_msg,}
				cursor.execute('ROLLBACK;')
				return render(request, 'pedidos/error.html',context)
			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para editar información de otro usuario !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)		


			
		else:
			
			pass
			#form = DatosUsuarioForm()
		
	else:	

		form = DatosUsuarioForm()
		
		cursor=connection.cursor()
		cursor.execute("SELECT 	p.usuariono,\
								p.nombre,\
								p.activo,\
								p.usuario,\
								u.email \
								from usuarios p inner join usr_extend u  on (p.empresano=1 and p.usuariono =u.usuariono) where p.usuariono=%s;",(usuariono,))
		usuario = cursor.fetchone()
		
		form = DatosUsuarioForm(initial={'usuariono':usuario[0],'nombre':usuario[1],'activo':1 if usuario[2]==1 else 0,'usuario':usuario[3],'email':usuario[4],})
					
	return render(request,'pedidos/edita_usuario.html',{'form':form,'usuariono':usuariono,})


def crea_usuario(request):

	msg = ''

	hoy = date.today()

	if request.method == 'POST':

		form = DatosUsuarioForm(request.POST)
		if form.is_valid():
			
			usuariono = form.cleaned_data['usuariono']
			nombre = form.cleaned_data['nombre']
			psw_paso = form.cleaned_data['psw_paso']
			activo = form.cleaned_data['activo']
			email = form.cleaned_data['email']
			usuario = form.cleaned_data['usuario']
			
			activo =int(activo)
			
			hoy = datetime.now()
			fecha_hoy = hoy.strftime("%Y-%m-%d")
			hora_hoy = hoy.strftime("%H:%M:%S") 
			


			usr_existente=0
			permiso_exitoso=0

			try:

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,18)

				if permiso_exitoso ==0:

					raise ValueError



				cursor=connection.cursor()


				'''  COMIENZA A GENERAR UN PASSWORD DE PASO '''


				cursor.execute('SELECT pass_paso FROM usr_extend;')
	
				pass_resultantes = cursor.fetchall()
		
				
				# Busca un psw_paso no registrado  en la base de datos y lo asigna al usuario.
				psw_paso_nuevo = genera_cadena_tres()
				while psw_paso_nuevo in pass_resultantes:
					psw_paso_nuevo = genera_cadena_tres()


				# Empieza a insertar registro

				cursor.execute('START TRANSACTION')

				cursor.execute("SELECT usuariono FROM usuarios ORDER BY usuariono desc limit 1;")
				ultimo_usuario = cursor.fetchone()	



				cursor.execute('INSERT INTO usuarios(empresano,usuariono,nombre,\
				fechacreacion,\
				fechamodificacion,\
				password,\
				activo,\
				nivel,\
				usuario) \
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);',(1,ultimo_usuario[0]+1,nombre.upper().lstrip(),hoy,hoy,' ',activo,0,usuario.upper().lstrip()))

				cursor.execute('INSERT INTO usr_extend(usuariono,pass_paso,\
				email) \
				VALUES(%s,%s,%s);',(ultimo_usuario[0]+1,psw_paso_nuevo,email))


				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,18,fecha_hoy,hora_hoy,'Se creó el usuario: '+str(ultimo_usuario[0]+1)))		

								
				cursor.execute("COMMIT;")

				'''MANDA CORREO CON NUEVO PASS_PASO '''

				v_asunto='Nueva constraseña de paso.'
				v_cuerpo=""" Estimado usuario,

				Se generó una nueva constraseña de paso para Ud. para ejecutar transacciones en el sistema.

				La nueva contraseña es: """+psw_paso_nuevo+""".

				Por seguridad se recomienda borrar de su buzón este mensaje una vez que haya memorizado su contraseña.

				Le recordamos que puede solicitar en administración una nueva constraseña cuando lo crea conveniente.

				Atenamente,
				Administración Multimarcas Laredo. """
				
				v_para=email

				envio_mail_exitoso = 0
				error_envio_msg =''
				# La rutina envia_mail retorna un codigo (0=Error,1= Exito) y un mensaje de error, el primero es recibido por envia_mail_exitoso y el segundo por error_envio_msg
				envio_mail_exitoso,error_envio_msg = envia_mail(v_para,v_asunto,v_cuerpo)
				#envio_mail_exitoso = envia_correo(v_asunto,v_cuerpo,v_para)
				'''
				if envio_mail_exitoso == 0:

					error_msg='Se presento un error en el envio de correo, solicite nuevamente la generación de contraseña !. '+error_envio_msg
					return render(request,'pedidos/error.html',{'error_msg':error_msg,})
				'''

				return HttpResponseRedirect(reverse('pedidos:lista_usuarios'))
				

			except IntegrityError as error_msg:

				#print error_msg

				context={'error_msg':"Error de integridad. Es posible que el valor que escogió para el campo 'Usuario' ya esté asignado a otro usuario registrado, este valor debe ser único, por favor elija otro valor distinto para este campo !",}
				return render(request, 'pedidos/error.html',context)

			except DatabaseError as error_msg:
				context={'error_msg':error_msg,}
				cursor.execute('ROLLBACK;')
				return render(request, 'pedidos/error.html',context)
			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para dar de alta usuarios !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)					


		else:
			
			pass
	else:	

		form = DatosUsuarioForm()
		
					
	return render(request,'pedidos/crea_usuario.html',{'form':form,})


def lista_usuario_derechos(request,usuariono):
	cursor=connection.cursor()

	cursor.execute('SELECT ud.derechono,d.DESCRIPCION,ud.usuariono,if(ud.`Activo?`,"SI","NO") as derecho_activo from usuario_derechos ud inner join derechos d on (ud.empresano=1 and ud.derechono=d.id) where ud.usuariono=%s;',(usuariono,))
	derechos = dictfetchall(cursor)
	
	cursor.execute('SELECT usuario from usuarios WHERE usuariono=%s;',(usuariono,))
	usr_nombre = cursor.fetchone()
	usr_nombre = usr_nombre[0]


	cursor.close()
	context = {'derechos': derechos,'usuariono':usuariono,'usr_nombre':usr_nombre,}
	return render(request, 'pedidos/usuario_derechos.html', context)


def agregar_usuario_derecho(request,usuariono):


	if request.method == 'POST':

		form = DerechosFaltantesUsuarioForm(request.POST,usuariono=usuariono)

		if form.is_valid():
			
			derecho = form.cleaned_data['derecho']
			psw_paso = form.cleaned_data['psw_paso']

			usr_existente=0
			permiso_exitoso=0

			fecha_hoy,hora_hoy = trae_fecha_hora_actual('','')
			cursor =  connection.cursor()

			try:

				usr_existente=0
				permiso_exitoso=0

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,33)

				if permiso_exitoso ==0:

					raise ValueError

			
				cursor=connection.cursor()

				cursor.execute('START TRANSACTION')

				cursor.execute("INSERT INTO usuario_derechos(empresaNo,UsuarioNo,DerechoNo,`Activo?`) VALUES(%s,%s,%s,%s);",(1,usuariono,derecho,1))
			

				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) VALUES(%s,%s,%s,%s,%s);",(usr_existente,33,fecha_hoy,hora_hoy,'Agregó el derecho '+str(derecho)+' al usuario '+str(usuariono)))

							
				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:lista_usuario_derechos',args=(usuariono,)))
				

			except IntegrityError as error_msg:

				context={'error_msg':"Error de integridad !",}
				return render(request, 'pedidos/error.html',context)

			except DatabaseError as error_msg:
				context={'error_msg':error_msg,}
				cursor.execute('ROLLBACK;')
				return render(request, 'pedidos/error.html',context)
			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para a su vez asignar derechos a otro usuario !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)		

	else:

		form=DerechosFaltantesUsuarioForm(usuariono=usuariono)

	return render(request,'pedidos/crea_usuario_derecho.html',{'form':form,'usuariono':usuariono,})







def eliminar_usuario_derecho(request,usuariono,derechono):


	if request.method == 'POST':

		form = EliminaUsuarioDerechoForm(request.POST)

		if form.is_valid():


			psw_paso = form.cleaned_data['psw_paso']

			
			usr_existente=0
			permiso_exitoso=0

			fecha_hoy,hora_hoy = trae_fecha_hora_actual('','')
			cursor =  connection.cursor()

			try:

				usr_existente=0
				permiso_exitoso=0

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,33)

				if permiso_exitoso ==0:

					raise ValueError
		

				cursor=connection.cursor()

				cursor.execute('START TRANSACTION')

				cursor.execute('DELETE FROM usuario_derechos WHERE usuariono=%s and derechono=%s;',(usuariono,derechono,))
				
				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) VALUES(%s,%s,%s,%s,%s);",(usr_existente,34,fecha_hoy,hora_hoy,'Eliminó el derecho '+str(derechono)+' al usuario '+str(usuariono)))
			
							
				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:lista_usuario_derechos',args=(usuariono,)))
				

			except IntegrityError as error_msg:

				context={'error_msg':"Error de integridad !",}
				return render(request, 'pedidos/error.html',context)

			except DatabaseError as error_msg:
				context={'error_msg':error_msg,}
				cursor.execute('ROLLBACK;')
				return render(request, 'pedidos/error.html',context)
			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para a su vez eliminar derechos a otro usuario !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)		
	
			
	else:		
		form = EliminaUsuarioDerechoForm()


	return render(request,'pedidos/elimina_usuario_derecho.html',{'form':form,'usuariono':usuariono,'derechono':derechono,})	



# LISTA DE USUARIOSWEB

def lista_usuarios_web(request):
	cursor=connection.cursor()
	cursor.execute('SELECT id,last_login,username,first_name,last_name,email,is_staff,is_active from auth_user;')
	usuarios = dictfetchall(cursor)
	cursor.close()
	context = {'usuarios': usuarios}
	return render(request, 'pedidos/usuarios_web.html', context)


# EDITA USUARIO


def edita_usuario_web(request,id):
	#pdb.set_trace() # DEBUG...QUITAR AL TERMINAR DE PROBAR..
	
	

	msg = ''

	if request.method == 'POST':

		form = DatosUsuarioWebForm(request.POST)
		if form.is_valid():
			id = form.cleaned_data['id']

			is_active = form.cleaned_data['is_active']
			is_staff = form.cleaned_data['is_staff']
			email = form.cleaned_data['email']
			psw_paso = form.cleaned_data['psw_paso']
			
			is_active = int(is_active)
			is_staff = int(is_staff)


			fecha_hoy,hora_hoy = trae_fecha_hora_actual('','')



			usr_existente=0
			permiso_exitoso=0

			try:

				usr_existente = verifica_existencia_usr(psw_paso)

				if usr_existente==0:

					raise ValueError


				permiso_exitoso = verifica_derechos_usr(usr_existente,29)

				if permiso_exitoso ==0:

					raise ValueError

				cursor=connection.cursor()

				cursor.execute('START TRANSACTION')

				cursor.execute('UPDATE auth_user SET email = %s,\
				is_active = %s,\
				is_staff=%s\
				WHERE id=%s;',(email.lower().lstrip(),is_active,is_staff,id,))

				cursor.execute("INSERT INTO log_eventos(usuariono,derechono,fecha,hora,descripcion) values(%s,%s,%s,%s,%s);",(usr_existente,29,fecha_hoy,hora_hoy,'Se modificó el staff del socio_web: '+str(id)))		
			
				
				cursor.execute("COMMIT;")

				return HttpResponseRedirect(reverse('pedidos:lista_usuarios_web'))
				

			except IntegrityError as error_msg:

				#print error_msg

				context={'error_msg':"Error de integridad. Es posible que el valor que escogió para el campo 'Usuario' ya esté asignado a otro usuario registrado, este valor debe ser único, por favor elija otro valor distinto para este campo !",}
				return render(request, 'pedidos/error.html',context)

			except DatabaseError as error_msg:
				context={'error_msg':error_msg,}
				cursor.execute('ROLLBACK;')
				return render(request, 'pedidos/error.html',context)
			except ValueError:		

				error_msg ="Usuario no registrado o bien sin los derechos para editar información web de otro usuario !"
				context={'error_msg':error_msg,}
				
				return render(request, 'pedidos/error.html',context)		

		
		else:
			
			pass
			#form = DatosUsuarioForm()
		
	else:	

		form = DatosUsuarioWebForm()
		
		cursor=connection.cursor()
		cursor.execute("SELECT 	p.id,\
								p.email,\
								p.is_active,\
								p.is_staff,\
								p.username\
								from auth_user p where p.id=%s;",(id,))
		usuario = cursor.fetchone()
		
		form = DatosUsuarioWebForm(initial={'id':usuario[0],'email':usuario[1],'is_active':usuario[2],'is_staff':usuario[3],'nombre':usuario[3]})
					
	return render(request,'pedidos/edita_usuario_web.html',{'form':form,'id':id,})


def rpteStatusxMarca(request):

	'''try:
	
		g_numero_socio_zapcat = request.session['socio_zapcat']	
	except KeyError :

		return	HttpResponse("Ocurrió un error de conexión con el servidor, Por favor salgase completamente y vuelva a entrar a la página !")

	if request.user.is_authenticated():'''		

	#pdb.set_trace()		
	if request.method == 'POST':
		form = RpteStatusxMarcaForm(request.POST)
		'''
		Si la forma es valida se normalizan los campos numpedido, status y fecha,
		de otra manera se envia la forma con su contenido erroreo para que el validador
		de errores muestre los mansajes correspondientes '''

		if form.is_valid():
		
			# limpia datos 
			sucursal = form.cleaned_data['sucursal']
			
			status = form.cleaned_data['status']
			marca = form.cleaned_data['xmarca']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']
			salida_a = form.cleaned_data['salida_a']
			
			# Convierte el string '1901-01-01' a una fecha valida en python
			# para ser comparada con la fecha ingresada 

			fecha_1901 =datetime.strptime('1901-01-01', '%Y-%m-%d').date()
			hoy = date.today()


			# Establece conexion con la base de datos
			cursor=connection.cursor()

		
			# Comienza a hacer selects en base a criterios 


			

			if  sucursal ==u'0':
				suc_ini,suc_fin=1,99
			else:
				suc_ini,suc_fin=sucursal,sucursal

			if  marca ==u'0':
				marca_ini,marca_fin=1,99
			else:
				marca_ini,marca_fin=marca,marca
				
									
			
			cursor.execute("SELECT p.pedido,p.precio,p.status,\
				p.catalogo,p.nolinea,\
				a.pagina,a.idmarca,a.idestilo,a.idcolor,\
				a.talla,h.idsucursal,aso.asociadoNo,aso.Nombre,\
				aso.appaterno,aso.apmaterno, psf.fechamvto,\
				p.Observaciones,CONCAT(CAST(aso.asociadono AS CHAR),\
				' ',aso.nombre,' ',aso.appaterno,' ',aso.apmaterno)\
				 as socio,suc.nombre as sucursal,a.idproveedor FROM pedidoslines p\
				inner join  pedidosheader h\
				on (p.EmpresaNo=h.EmpresaNo and p.pedido=h.pedidoNo)\
				inner join articulo a\
				on ( p.EmpresaNo=a.empresano and p.productono=a.codigoarticulo\
				and p.catalogo=a.catalogo)\
				inner join asociado aso\
				on (h.asociadoNo=aso.asociadoNo)\
				inner join  pedidos_status_fechas psf\
				on (p.empresano=psf.empresaNo\
				and p.pedido=psf.pedido and p.productono=psf.productono\
				and p.status=psf.status and p.catalogo=psf.catalogo\
				and p.nolinea=psf.nolinea) \
				inner join sucursal suc on (h.idsucursal=suc.sucursalNo)\
				 WHERE p.status>=%s and p.status<=%s\
				and psf.fechamvto>=%s and psf.fechamvto<=%s\
				and h.idsucursal>=%s and h.idsucursal<=%s\
				and a.idproveedor >= %s and a.idproveedor <= %s\
				ORDER BY a.idproveedor,\
				h.asociadono ASC;", (status,status,fechainicial,fechafinal,suc_ini,suc_fin,marca_ini,marca_fin,))
							
			pedidos = dictfetchall(cursor)
			elementos = len(pedidos)

			total_gral=0
			
			for i in pedidos:
				total_gral+= i['precio']

			cursor.execute("SELECT a.idproveedor,SUM(p.precio) AS subtotal FROM pedidoslines p\
				inner join  pedidosheader h\
				on (p.EmpresaNo=h.EmpresaNo and p.pedido=h.pedidoNo)\
				inner join articulo a\
				on ( p.EmpresaNo=a.empresano and p.productono=a.codigoarticulo\
				and p.catalogo=a.catalogo)\
				inner join asociado aso\
				on (h.asociadoNo=aso.asociadoNo)\
				inner join  pedidos_status_fechas psf\
				on (p.empresano=psf.empresaNo\
				and p.pedido=psf.pedido and p.productono=psf.productono\
				and p.status=psf.status and p.catalogo=psf.catalogo\
				and p.nolinea=psf.nolinea) \
				inner join sucursal suc on (h.idsucursal=suc.sucursalNo)\
				 WHERE p.status>=%s and p.status<=%s\
				and psf.fechamvto>=%s and psf.fechamvto<=%s\
				and h.idsucursal>=%s and h.idsucursal<=%s\
				and a.idproveedor>=%s and a.idproveedor<=%s\
				GROUP BY a.idproveedor ASC;", (status,status,fechainicial,fechafinal,suc_ini,suc_fin,marca_ini,marca_fin,))
							
			subxsocio = dictfetchall(cursor)
			

			cursor.execute("SELECT nombre as nombresuc from sucursal where sucursalNo=%s;",(sucursal,))
			suc_nom=cursor.fetchone()
			
			cursor.execute("SELECT razonsocial from proveedor where empresano=1 and proveedorno=%s;",(marca,))
			proveedor_nombre=cursor.fetchone()





			if not pedidos:# or not nombre_socio[0]:
				mensaje = 'No se encontraron registros !'
				
				return render(request,'pedidos/lista_pedidos_StatusxMarca.html',{'form':form,'mensaje':mensaje,})
			else:
				mensaje ='Registros encontrados:'
				context = {'pedidos':pedidos,'subxsocio':subxsocio,'mensaje':mensaje,'elementos':elementos,'sucursal':suc_nom[0],'titulo':'Consulta de pedidos con status de '+status,'fechainicial':fechainicial,'fechafinal':fechafinal,'total_gral':total_gral,'elementos':elementos,'proveedor_nombre':proveedor_nombre[0] if marca!=u'0' else 'General',}

				if salida_a == 'Pantalla':

					return render(request,'pedidos/lista_pedidos_StatusxMarca.html',context)
				else:

					response = HttpResponse(content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename="PedidosStatusxMarca.csv"'

					writer = csv.writer(response)
					writer.writerow(['SUCURSAL','SOCIO_NUMERO','SOCIO_NOMBRE','SOCIO_APPATERNO','SOCIO_APMATERNO','PEDIDO','FECHA_MVTO','STATUS','CATALOGO','PAGINA','MARCA','ESTILO','COLOR','TALLA','PRECIO',])
					
					for registro in pedidos:
						print registro
						# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
						llaves_a_mostrar = ['sucursal','asociadoNo','Nombre','appaterno','apmaterno','pedido','fechamvto','status','catalogo','pagina','idmarca','idestilo','idcolor','talla','precio',] 
						# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
						lista = [registro[x] for x in llaves_a_mostrar]					
						writer.writerow(lista)
					cursor.close()
					return response			



			# Cierra la conexion a la base de datos
			cursor.close()
			
		
	else:
		form = RpteStatusxMarcaForm()
		#cursor.close()
		
	return render(request,'pedidos/pedidos_por_status_xmarca_form.html',{'form':form,})




"""ESTA RUTINA REASIGNA LA SUCURSAL A UN PEDIDO ES LLAMADA VIA AJAX DE LA PANTALLA
DE VENTAS"""
def reasigna_sucursal_apedido(request):
	
	#pdb.set_trace()
	try:
		id_sucursal = request.session['sucursal_activa']
	except KeyError:
		error_msg='Session expirada...cierre navegador y vuelva e entrar !'
		HttpResponse(error_msg)
	
	pedido = request.POST['pedido']
	productono = request.POST['productono']
	catalogo = request.POST['catalogo']
	nolinea = request.POST['nolinea']
	trid = request.POST['trid']

	status_operacion='fail'
	error = ''





	# AQUI VA LA EL UPDATE PARA CAMBIAR SUCURAL.
	try:
		cursor=connection.cursor()

		cursor.execute('START TRANSACTION')

		cursor.execute('UPDATE pedidosheader set idsucursal=%s WHERE pedidono=%s;',(id_sucursal,pedido,))
				
								
		cursor.execute("COMMIT;")
		status_operacion='ok'
		cursor.close()
	except DatabaseError as error_msg:
		cursor.execute('ROLLBACK;')
		status_operacion='fail'
		error =str(error_msg)

		cursor.close()	
	
	
	context={}
	
		
	data = {'status_operacion':status_operacion,'error':error,'nueva_suc':id_sucursal,'trid':trid,}
	return HttpResponse(json.dumps(data),content_type='application/json',)	


#### RUTINA PARA GENERAR UNA CADENA DE 3 DIGITOS ALEATORIA 



def genera_cadena_tres():

	return(get_random_string(3).lower())


# rutina para checar password de paso

def checa_pass_paso(request,passw):

	# trae el usuario con el pass

	cursor=connection.cursor()
	cursor.execute('SELECT id FROM usr_extend WHERE pass_paso=%s ',(passw,))
	
	resultado = cursor.fetchone()

	

	if resultado[0] != request.user:

		error_msg ='Password incorrecto !'
		return render(request,'pedidos/error.html',{'error_msg':error_msg,})
	else:

		return(resultado[0])

# RUTINA PARA GENERAR EL PASSWORD

def genera_pass_paso(request,usuariono):
	#pdb.set_trace()

	# trae passwords de todos los usuarios para comparar 

	cursor=connection.cursor()
	cursor.execute('SELECT pass_paso FROM usr_extend;')
	
	pass_resultantes = cursor.fetchall()


	# trae email del usuario
	cursor.execute('SELECT email FROM usr_extend WHERE usuariono=%s;',(usuariono,))
	
	email_result = cursor.fetchone()

	
	# Busca un psw_paso no registrado  en la base de datos y lo asigna al usuario.
	psw_paso = genera_cadena_tres()
	while psw_paso in pass_resultantes:
		psw_paso =genera_cadena_tres()

	try:
		cursor.execute('UPDATE usr_extend set pass_paso=%s where usuariono=%s;',(psw_paso,usuariono,))	
	
	except DatabaseError as e:

		error_msg ='Error en base de datos: '+e
		return render(request,'pedidos/error.html',{'error_msg':error_msg,})

	# envia correo

	v_asunto='Nueva constraseña de paso.'
	v_cuerpo=""" Estimado usuario,

	Se generó una nueva constraseña de paso para Ud. para ejecutar transacciones en el sistema.

	La nueva contraseña es: """+psw_paso+""".

	Por seguridad se recomienda borrar de su buzón este mensaje una vez que haya memorizado su contraseña.

	Le recordamos que puede solicitar en administración una nueva constraseña cuando lo crea conveniente.

	Atenamente,
	Administración Multimarcas Laredo. """
	
	v_para=email_result[0]

	envio_mail_exitoso = 0
	error_envio_msg =''
	# La rutina envia_mail retorna un codigo (0=Error,1= Exito) y un mensaje de error, el primero es recibido por envia_mail_exitoso y el segundo por error_envio_msg
	envio_mail_exitoso,error_envio_msg = envia_mail(v_para,v_asunto,v_cuerpo)
	#envio_mail_exitoso = envia_correo(v_asunto,v_cuerpo,v_para)

	if envio_mail_exitoso == 0:

		error_msg='Se presento un error en el envio de correo, solicite nuevamente la generación de contraseña !. '+error_envio_msg
	else:
		error_msg='Contraseña generada con exito !. Se envió un mensaje de correo al buzón del usuario !'

	return render(request,'pedidos/error.html',{'error_msg':error_msg,})
'''

def envia_correo(v_asunto,v_cuerpo,v_para):
	# Observar que en la siguiente linea  el parametro auth_user='pedidos_multimarcas' es el mailbox en el servidor de webfaction, mas que el correo electronico.
	#r= send_mail('prueba','prueba de envio de  message','soporte@esshoesmultimarcas.com',['jggalvan@prodigy.net.mx'], fail_silently=False, auth_user='pedidos_multimarcas', auth_password='pedidos1', connection=None, html_message=None)

	email_host_user = getattr(settings, "EMAIL_HOST_USER", None)

	envio_mail_exitoso = envia_mail(v_para,email_host_user,v_asunto,v_cuerpo)			  


	#envio_mail_exitoso= send_mail(v_asunto,v_cuerpo,'soporte@esshoesmultimarcas.com',[v_para], fail_silently=False, auth_user='pedidos_multimarcas', auth_password='pedidos1', connection=None, html_message=None)

	return(envio_mail_exitoso)

'''

def prueba_mail(request):

	r=0	
	try:
		send_mail('prueba','prueba de envio de  message por segunda vez','soporte@esshoesmultimarcas.com',['jggalvandlr2772@gmail.com'], fail_silently=False, auth_user='pedidos_multimarcas', auth_password='pedidos1', connection=None, html_message=None)
		
	except Error as e:
		print str(e)
		return HttpResponse(str(e))
	
	if r==0:
		return HttpResponse('Error en envio')
	else:
		return HttpResponse('Envio Ok')



			
def log_eventos_forma(request):

	#pdb.set_trace()

	if request.method == 'POST':

		form = UsuarioLogForm(request.POST)

		if form.is_valid():
			
			usuario = form.cleaned_data['usuario']
			derecho = form.cleaned_data['derecho']
			fechainicial = form.cleaned_data['fechainicial']
			fechafinal = form.cleaned_data['fechafinal']
			salida_a = form.cleaned_data['salida_a']

			cursor = connection.cursor()

			if usuario==u'0' and derecho ==u'0':

				cursor.execute("SELECT u.nombre as nombre_usuario, d.descripcion as nombre_derecho,le.descripcion as accion,le.fecha,le.hora FROM log_eventos le  INNER JOIN usuarios u  on (le.usuariono=u.usuariono) INNER JOIN derechos d on (le.derechono=d.id) where le.fecha>= %s and le.fecha <= %s ORDER BY le.usuariono,le.fecha,le.hora;",(fechainicial,fechafinal,))


			elif usuario != u'0'  and derecho == u'0':

				cursor.execute("SELECT u.nombre as nombre_usuario, d.descripcion as nombre_derecho,le.descripcion as accion,le.fecha,le.hora FROM log_eventos le  INNER JOIN usuarios u  on (le.usuariono=u.usuariono) INNER JOIN derechos d on (le.derechono=d.id) where le.fecha>= %s and le.fecha <= %s and le.usuariono=%s ORDER BY le.fecha,le.hora;",(fechainicial,fechafinal,usuario,))

			elif usuario ==u'0' and derecho !=u'0':

				cursor.execute("SELECT u.nombre as nombre_usuario, d.descripcion as nombre_derecho,le.descripcion as accion,le.fecha,le.hora FROM log_eventos le  INNER JOIN usuarios u  on (le.usuariono=u.usuariono) INNER JOIN derechos d on (le.derechono=d.id) where le.fecha>= %s and le.fecha <= %s and le.derechono=%s ORDER BY le.fecha,le.hora;",(fechainicial,fechafinal,derecho,))

			else:
				cursor.execute("SELECT u.nombre as nombre_usuario, d.descripcion as nombre_derecho,le.descripcion as accion,le.fecha,le.hora FROM log_eventos le  INNER JOIN usuarios u  on (le.usuariono=u.usuariono) INNER JOIN derechos d on (le.derechono=d.id) where le.fecha>= %s and le.fecha <= %s and le.derechono=%s and le.usuariono=%s ORDER BY le.fecha,le.hora;",(fechainicial,fechafinal,derecho,usuario,))

			
			registros = dictfetchall(cursor)

			tot_registros = len(registros)
	
			if salida_a == 'Pantalla':	
				
				return render(request,'pedidos/despliega_log_eventos.html',{'registros':registros,'tot_registros':tot_registros,})

			else:

				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="log_eventos.csv"'

				writer = csv.writer(response)
				writer.writerow(['USUARIO','DERECHO','FECHA','HORA','ACTIVIDAD'])
				
				for registro in registros:
					print registro
					# El registro contiene los elementos a exportar pero no en el orden que se necesita para eso se define la siguiente lista con las llaves en el orden que se desea se exporten	
					llaves_a_mostrar = ['nombre_usuario','nombre_derecho','fecha','hora','accion'] 
					# Con la siguiente linea se pasan los elementos del diccionario 'registro' a 'lista' de acuerdo al orden mostrado en 'llaves_a_mostrar'
					lista = [registro[x] for x in llaves_a_mostrar]					
					writer.writerow(lista)
				cursor.close()
				return response			


			cursor.close()

	form = UsuarioLogForm()
	return render(request,'pedidos/log_eventos_forma.html',{'form':form,})
'''	
def upload_file_catalogo(request):
	pdb.set_trace()
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			uploaded_file = request.FILES['file'].name

			print request.FILES['file'].name
			#handle_uploaded_file(request.FILES['file'])
			with open(uploaded_file,'r') as f:
				csv_file = csv.reader(f)	
				for row in csv_file:
					print row 
					
			return HttpResponse("ok")
	else:
		form = UploadFileForm()
	return render(request, 'pedidos/upload_catalogo.html', {'form': form})'''

		

def upload_file_catalogo(request):
	#pdb.set_trace()

	# prompt is a context variable that can have different values      depending on their context
	context = {
        'orden': 'El Orden del  CSV debe ser codigo,, address,    phone, profile',
        
              }


	fecha_hoy,hora_hoy=trae_fecha_hora_actual('','')



	template='pedidos/upload_catalogo.html'

	    # GET request returns the value of the data with the specified key.
	if request.method == "POST":
		
		form = UploadFileForm(request.POST, request.FILES)
		print form.is_valid()
		if form.is_valid():
			csv_file = request.FILES['file']
			idproveedor = form.cleaned_data['proveedor']
			catalogo = form.cleaned_data['catalogo']
			temporada = form.cleaned_data['temporada']



			# let's check if it is a csv file
			if not csv_file.name.endswith('.csv'):
				messages.error(request, 'Este no es un archivo en formato  CSV !')

			else:

				data_set = csv_file.read().decode('latin-1')   # setup a stream which is when we loop through each line we are able to handle a data in a strea
				
				io_string = io.StringIO(data_set)

				#next(io_string) #permite empezar a leer desde la segunda linea del psv ( omite leer 1er linea o encabezado )

				i=1
				lista_error=[]
				lista_elementos=[]
				for columna in csv.reader(io_string, delimiter=',', quotechar='"'):

					if '/' in columna[1]:
						lista_error.append(i)

					
					else:
						lista_elementos.append(columna)

					i+=1	

					# SE QUITAN COMAS (EN CASO DE QUE TRAIGAN) DE PRECIO Y PRECIO OPCIONAL 
					# PARA QUE LOS PUEDA CONVERTIR A DECIMAL SIN PROBLEMAS ANTES DE GRABAR A BASE DE DATOS.
					columna[7]=columna[7].replace(',','')
					columna[9]=columna[9].replace(',','')



				str1=",".join(str(j) for j in lista_error)	
				messages.error(request, 'Existen registros con una diagonal en el campo codigo_articulo, lineas: '+str1)
				
				""" Empieza actualizando Bd"""
				if not lista_error:
					try:
						cursor=connection.cursor()

						cursor.execute("START TRANSACTION;")
						print "el condenado string:"

						
						
						for columna in lista_elementos:
							print columna
							cursor.execute("INSERT INTO articulo (Empresano,\
											codigoarticulo,\
											fechaalta,\
											fechabaja,\
											pagina,\
											pathfoto,\
											idproveedor,\
											idmarca,\
											idestilo,\
											idcolor,\
											idacabado,\
											idmodelo,\
											talla,\
											precio,\
											catalogo,\
											costo,\
											descontinuado) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE descontinuado=%s;",(1,columna[1],fecha_hoy,fecha_hoy,columna[0],'',idproveedor,columna[4],columna[3],columna[5],columna[6],'',columna[8],Decimal(columna[7]),catalogo,0,0,0))
							
							cursor.execute("INSERT INTO preciobase (Empresano,\
																proveedorid,\
																temporada,\
																codigoarticulo,\
																costo,\
																precio,\
																fechacreacion,\
																horacreacion,\
																fechamodificacion,\
																horamodificacion,\
																usuariocreo,\
																UsuarioModifico,\
																pagina,\
																catalogo,\
																estilo,\
																idmarca,\
																idcolor,\
																talla\
																) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE horamodificacion=%s;",(1,idproveedor,temporada,columna[1],0,Decimal(columna[7]),fecha_hoy,hora_hoy,fecha_hoy,hora_hoy,0,0,columna[0],catalogo,columna[3],columna[4],columna[5],columna[8],hora_hoy))
												
							cursor.execute("INSERT INTO preciosopcionales (Empresano,\
																proveedor,\
																temporada,\
																articuloid,\
																tipoprecio,\
																precio,\
																fechacreacion,\
																horacreacion,\
																fechamodificacion,\
																horamodificacion,\
																catalogo\
																) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE horamodificacion=%s;",(1,idproveedor,temporada,columna[1],'Cliente',Decimal(columna[9]),fecha_hoy,hora_hoy,fecha_hoy,hora_hoy,catalogo,hora_hoy))


						cursor.execute("COMMIT;")
						cursor.close()
						messages.info(request, 'Catálgo subido exitosamente ! ')

						
					except DatabaseError as error_msg:
						cursor.execute('ROLLBACK;')
						status_operacion='fail'
						error =str(error_msg)
						messages.error(request, 'Error en base datos, inf. tecnica: '+error)


						cursor.close()	



		else:
			return render(request,template,{'form': form},)		
	form = UploadFileForm()		
	return render(request,template,{'form': form},)		



def combo_catalogos_importacion(request,*args,**kwargs):
	#pdb.set_trace()

	if request.is_ajax() and request.method == 'GET':
		id_prov = request.GET['id_prov_importar']
		id_temp = request.GET['id_temp_importar']
		

		cursor=connection.cursor()
		cursor.execute('SELECT clasearticulo FROM catalogostemporada WHERE proveedorno=%s and anio=%s',(id_prov,id_temp))
	
		resultado = cursor.fetchall()

		listacat=()
    	
		for row in resultado:
			elemento = tuple(row)
			listacat=listacat+elemento
		listacat=('Seleccione...',)+listacat
		
		h = {'listacat':listacat,}

		data = json.dumps(h)
		
		#data = {'Mensaje':"El id proveedor recibido fue %s" % request.GET['id_prov']}
				
		# En el siguiente return utilizo content_type. Intente usar 'mimetype'
		# en lugar de 'content_type' y no funciono.

	return HttpResponse(data,content_type='application/json')


