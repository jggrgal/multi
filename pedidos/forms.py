# -*- encoding: utf-8 -*-

from django import forms
from django.forms import ModelForm,modelform_factory,Textarea
from pedidos.models import Asociado,Pedidosheader,Pedidoslines,Proveedor,Catalogostemporada
from datetime import date,datetime,timedelta
from django.db import connection
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.contrib.auth.models import User
from functools import partial
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import connection,DatabaseError,Error,transaction,IntegrityError
from django.http import HttpResponse
import pdb 
import re

# FUNCION PARA GENERAR LISTA DE PROVEEDORES
# GENERALMENTE PARA EL LLENADO DE COMBOS

def lista_Catalogos(proveedor_parm,temporada_parm):
			#pdb.set_trace()
			cursor=connection.cursor()
			cursor.execute('SELECT Proveedorno,ClaseArticulo from catalogostemporada where proveedorno=%s and anio=%s;',(proveedor_parm,temporada_parm))
	
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

			
			
			return (lprov)

# FUNCION PARA GENERAR LISTA DE PROVEEDORES
# GENERALMENTE PARA EL LLENADO DE COMBOS

def lista_Proveedores():
			cursor=connection.cursor()
			cursor.execute('SELECT ProveedorNo,RazonSocial from proveedor;')
	
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

			
			
			return (lprov)


# FUNCION PARA GENERAR UNA LISTA DE SUCURSALES
# PARA LLENADO DE COMBO DE SUC.


def lista_Sucursales():
			cursor=connection.cursor()
			cursor.execute('SELECT SucursalNo,nombre from sucursal;')
	
			pr=() # Inicializa una tupla para llenar combo de Proveedores
			
			# Convierte el diccionario en tupla
			for row in cursor:
				elemento = tuple(row)
				pr=pr+elemento
			pr = (0L,u'GENERAL ') + pr
			

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

			
			
			return (lprov)

# FUNCION PARA TRAER LISTA DE STATUS


def lista_status():
			cursor=connection.cursor()
			cursor.execute('SELECT status from catalogostatuspedidos;')
	
			pr=() # Inicializa una tupla para llenar combo de Proveedores
			
			# Convierte el diccionario en tupla
			for row in cursor:
				elemento = tuple(row)
				pr=pr+elemento
			pr = (u'Todos') + pr
			

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

			
			
			return (lprov)





# FUNCION PARA TRAER LISTA DE ALMACENES DE PROVEEDOR


def lista_almacenes(proveedor):
			cursor=connection.cursor()
			cursor.execute('SELECT almacen,razonsocial from almacen where empresano=1 and proveedorno=%s;',(proveedor,))
	
			# Convierte el diccionario en tupla
			for row in cursor:
				elemento = tuple(row)
				pr=pr+elemento
			pr = (0L,u'TODOS ') + pr
			

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

			
			
			return (lprov)


'''   LISTA DE USUARIOS '''

def lista_usuarios():
			#pdb.set_trace()
			cursor=connection.cursor()
			cursor.execute('SELECT UsuarioNo,usuario from usuarios where activo;')
	
			pr=() # Inicializa una tupla para llenar combo de Proveedores
			
			# Convierte el diccionario en tupla
			for row in cursor:
				elemento = tuple(row)
				pr=pr+elemento
			pr = (0L,u'GENERAL ') + pr
			

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

			return (lprov)

# FUNCION PARA GENERAR UNA LISTA DE LOS DERECHOS AUN NO ASIGNADOS A UN USUARIO


def lista_derechos_no_asignados(usr):
			cursor=connection.cursor()
			#cursor.execute('SELECT id,descripcion from (SELECT d.id,d.descripcion FROM derechos d where d.id not in (SELECT us.id from usuario_derechos us where us.usuariono=%s));'(usr,))
			cursor.execute('SELECT r.id,r.descripcion from (SELECT d.id,d.descripcion FROM derechos d where d.id not in (SELECT ud.derechono from usuario_derechos ud where ud.usuariono=%s)) as r',(usr,))
			#cursor.execute('SELECT id,descripcion from derechos;')

			pr=() # Inicializa una tupla para llenar combo de Proveedores
			
			# Convierte el diccionario en tupla
			for row in cursor:
				elemento = tuple(row)
				pr=pr+elemento
			pr = (0L,u'GENERAL ') + pr
			

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

			return (lprov)

# FUNCION PARA GENERAR UNA LISTA DE LOS DERECHOS


def lista_derechos():
			#pdb.set_trace()
			cursor=connection.cursor()
			#cursor.execute('SELECT id,descripcion from (SELECT d.id,d.descripcion FROM derechos d where d.id not in (SELECT us.id from usuario_derechos us where us.usuariono=%s));'(usr,))
			cursor.execute('SELECT id,descripcion from derechos')
			#cursor.execute('SELECT id,descripcion from derechos;')

			pr=() # Inicializa una tupla para llenar combo de Proveedores
			
			# Convierte el diccionario en tupla
			for row in cursor:
				elemento = tuple(row)
				pr=pr+elemento
			pr = (0L,u'GENERAL ') + pr
			

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

			return (lprov)




f_inicial_init =  date.today()

f_final_init = f_inicial_init + timedelta(days=30)




class UserProfileConfig(forms.Form):

    def __init__(self,request,*args,**kwargs):
        super (UserProfileConfig,self).__init__(*args,**kwargs)
        self.fields['username'] = forms.CharField(label='Username',max_length=100,initial=request.session['some_var'])





class AccesoForm(forms.Form):
			
		username = forms.CharField(label='Usuario')
		password = forms.CharField(label='Contrase??a',widget=forms.PasswordInput)
		error_messages = {'usuario_vacio':'Ingrese su usuario  !',
							'password_vacio':'Ingrese su contrase??a (password) !'}

		def clean(self):
		
			cleaned_data = super(AccesoForm, self).clean()
			username = cleaned_data.get('username')
			password = cleaned_data.get('password')
		
			
			if not username:
			
				raise forms.ValidationError(self.error_messages['usuario_vacio'],code='usuario_vacio')

			if not password:

				raise forms.ValidationError(self.error_messages['password_vacio'],code='password_vacio')

			return self.cleaned_data

class AsociadoForm(ModelForm):
    class Meta:
        model = Asociado
        fields = ['asociadono', 'nombre', 'appaterno','apmaterno','telefono1']


class BuscapedidosForm(forms.Form):
	#hoy =  date.today()	
	t = datetime.now
	#t.strftime('%m/%d/%Y')



	DateInput = partial(forms.DateInput, {'class': 'datepicker'})
	numpedido = forms.IntegerField(label='N??mero',initial=0,validators=[MinValueValidator(0)])
	'''opciones_status = (('1','Pedido',),('2','Por Confirmar',),('3','Aqui',),('4','Cancelado',),('5','Todos',),)'''
	opciones_status = (('Encontrado','Encontrado',),('Por Confirmar','Por Confirmar',),('Confirmado','Confirmado',),('Aqui','Aqui',),('Cancelado','Cancelado',),('Devuelto','Devuelto',),('RecepEnDevol','RecepEnDevol',),('Dev a Prov','Dev a Prov',),('Facturado','Facturado',),('Descontinuado','Descontinuado'),('Todos','Todos',),)
	status = forms.ChoiceField(label='Status',initial='Confirmado',choices=opciones_status)
	#fecha = forms.DateField(label='Fecha en que hizo (dd/mm/yyyy)',initial= datetime.now,input_formats=['%d/%m/%Y',],)
	fecha = forms.DateField(label='Fecha en que hizo (dd/mm/yyyy)',widget=DateInput())
	error_messages = {
	'status_todos': 'Si el status es "Todos" forzosamente debe especificar una fecha distinta de 1901-01-01 !',
	'fecha_invalida': 'La fecha debe ser menor o igual a la fecha actual',
	'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
	'Error_en_mes': 'El mes de la fecha que esta ingresando es invalido !',
	}

	def clean(self):
		
		cleaned_data = super(BuscapedidosForm, self).clean()
		numpedido = cleaned_data.get('numpedido')
		'''fecha = cleaned_data.get('fecha')'''
		status = cleaned_data.get('status')

		'''if (fecha == datetime.strptime('01/01/1901' , '%d/%m/%Y').date()
			and status == 'Todos' and numpedido == 0 ):

			raise forms.ValidationError(self.error_messages['status_todos'],code='status_todos')

		if fecha > date.today():

			raise forms.ValidationError(self.error_messages['fecha_invalida'],code='fecha_invalida')'''

		
		return self.cleaned_data

	'''	
	def clean_fecha(self):
		hoy = date.today()
		self.fecha = self.cleaned_data.get('fecha')
		self.status = self.cleaned_data.get('status')
		self.numpedido = self.cleaned_data.get('numpedido')
			

		if (self.fecha == datetime.strptime('1901-01-01' , '''''').date()):
				
			raise forms.ValidationError( 
			self.error_messages['status_todos'],  #user my customized error message

			code='status_todos',   #set the error message key

			)	



		if self.fecha  > hoy:
			raise forms.ValidationError(self.error_messages['fecha_invalida'],code='fecha_invalida')
			

		return self.fecha 
	'''

		
class PedidosForm(forms.Form):

	proveedores = {}
	

	# La funcion siguiente "init" tambien  recibe el parametro
	# request, esto se hace para tener tambien disponibles las variables de entorno, en este caso
	# se requerira el request.session['is_staff'] para manejarlos en los campos
	# de fechaMaximaEntrega y el de periodo de entrega.
	# en el views.py los llamados deben inculir request como parametro tanto si la forma es valida como si no lo es.
	def __init__(self,request,*args,**kwargs):


		
		def lista_PeriodosEntrega():
			cursor=connection.cursor()
			cursor.execute('SELECT id,periodo from periodosentrega;')
	
			pr=() # Inicializa una tupla para llenar combo de Periodosentrega
			
			# Convierte el diccionario en tupla
			for row in cursor:
				elemento = tuple(row)
				pr=pr+elemento
			pr = (0L,u'SELECCIONE...') + pr
			

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
			lper_ent = tuple(tuple(x) for x in y)

			
			
			return (lper_ent)

		
		
		lprov = lista_Proveedores()
		lcat = (('0','Seleccione'),)
		lestilo = []
		lmarca = []
		lcolor = []
		ltalla = []
		lper_ent = lista_PeriodosEntrega()
		

		opcion_temporada = (('0','SELECCIONE...'),('1','Primavera/Verano'),('2','Oto??o/Invierno'))
		opcion_opt = (('1','1ra.'),('2','2da'),('3','3ra.'))

		
		#pr_dict = [['1','MODELI'],['2','IMPULS'],['3','OTRO']]
		#pr_dict = (('MODELI','MODELI'),('IMPULS','IMPULS'),('OTRO','OTRO'),)
		#pr_dict = lista_Proveedores()

		super(PedidosForm, self).__init__(*args,**kwargs)
		
		

		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
		label='Proveedor',choices = lprov,initial='0',required='True' )

		self.fields['temporada'] = forms.ChoiceField(widget=forms.Select(),
		label='Temporada',choices = opcion_temporada, initial='0',required ='True')
		
		self.fields['catalogo']  = forms.ChoiceField(widget=forms.Select(),
		label='Catalogo',initial = 'SELECCIONE...',required ='True' )
		
		self.fields['pagina'] = forms.CharField(label='Pagina')
		
		self.fields['estilo'] = forms.ChoiceField(widget=forms.Select(),
		label='Estilo',initial='Seleccione',required='True')
		
		self.fields['marca'] = forms.ChoiceField(widget = forms.Select(),
		label='Marca',initial='Seleccione',required='True')

		self.fields['color'] = forms.ChoiceField(widget = forms.Select(),
		label='Color', initial='Seleccione',required='True')
		
		self.fields['talla'] = forms.ChoiceField(widget = forms.Select(),
		label='Talla',initial='Seleccione',required='True')

		self.fields['tallaalt'] = forms.CharField(label='',help_text='Si talla es "NE", ingrese una aqui')



		try:# Si usuario no es del estaff no debe se mostrara ni periodo de entrega ni fechamaximaentrega.
			if not request.session['is_staff']:
		  		escondido = 'display: none;'
		  	else:
		  		escondido ='display: ;'
		except:
			return None

	  	self.fields['precio'] = forms.FloatField(label = 'Precio cliente:',initial=0.0,widget=forms.NumberInput(attrs={'style':'display: none;'}))

	  	self.fields['plazoentrega'] = forms.ChoiceField(label='Plazo de entrega:',initial=0,choices=lper_ent,required=True,widget=forms.Select(attrs={'style':escondido,}))
		self.fields['opcioncompra'] = forms.ChoiceField(label='Opcion de compra:',initial='1ra.',help_text='',widget=forms.Select(attrs={'style':escondido,}),choices=opcion_opt)
	  		
  		DateInput = partial(forms.DateInput, {'class': 'datepicker','style':escondido})

  		hoy=datetime.now()
  		f = hoy.strftime("%d/%m/%Y")
		self.fields['fechamaximaentrega'] = forms.DateField(label='Fecha max entrega (dd/mm/yyyy)',initial=f,widget=DateInput())			

class RegsocwebForm(forms.Form):
			
		numero = forms.IntegerField(label='N??mero',help_text='N??mero que le fue asignado en sucursal')



class Forma_RegistroForm(UserCreationForm):
	
	email = forms.EmailField(required = True)

	# El siguiente campo es solo para pasar el numero de socio de la vista al template
	# para posteriormente reutilizarlo en el registro de la forma.
	num_socio = forms.IntegerField(required=False,widget=forms.HiddenInput())
	
	error_messages = {
		'duplicate_username': 'Ya existe este usuario, intente con otro nombre !',
		'invalid_email': 'Direccion de correo invalida !',
		'password_mismatch': 'Los dos campos de password no coinciden entre si.',
		}

	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2')

	def clean_username(self):
		username = self.cleaned_data["username"]
		
       
		try:
			User._default_manager.get(username=username)
			#if the user exists, then let's raise an error message

			raise forms.ValidationError( 
				self.error_messages['duplicate_username'],  #user my customized error message

				code='duplicate_username',   #set the error message key

				)
		except User.DoesNotExist:
			return username # great, this user does not exist so we can continue the registration process


	def clean_email(self):
		email_vir = self.cleaned_data["email"]

		error_en_mail = False
       
		if not '@' in email_vir:

				raise forms.ValidationError( 
				self.error_messages['invalid_email'],  #email customized error message

				code='invalid_email',   #set the error message key

				)
		else:

			
			if User.objects.filter(email=email_vir).exists():
				raise forms.ValidationError('Esta direcci??n de correo ya existe en la base de datos')
    			


		return email_vir # great, the email is correct so we can continue the registration process




	def save(self,commit = True):   
		user = super(Forma_RegistroForm, self).save(commit = False)
		user.email = self.cleaned_data['email']
        
		if commit:
			user.save()

		return user


# Cambiar Password forms

class BuscapedidosporsocioForm(forms.Form):


	#hoy =  date.today()	
	t = datetime.now
	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	numpedido = forms.IntegerField(label='Pedido Numero',initial=0,validators=[MinValueValidator(0)],required=False)
	
	socio = forms.IntegerField(label='Socio Numero',initial=0,required=False)
	
	
	'''opciones_status = (('1','Pedido',),('2','Por Confirmar',),('3','Aqui',),('4','Cancelado',),('5','Todos',),)'''
	opciones_status = (('Encontrado','Encontrado',),('Por Confirmar','Por Confirmar',),('Confirmado','Confirmado',),('Aqui','Aqui',),('Cancelado','Cancelado',),('Devuelto','Devuelto',),('RecepEnDevol','RecepEnDevol',),('Dev a Prov','Dev a Prov',),('Facturado','Facturado',),('Descontinuado','Descontinuado'),('Todos','Todos',),)
	status = forms.ChoiceField(label='Status',initial='Confirmado',choices=opciones_status,required=False)
	#fecha = forms.DateField(label='Fecha en que hizo (dd/mm/yyyy)',initial= datetime.now,input_formats=['%d/%m/%Y',],)
	fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),required=False)
	fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),required=False)
	error_messages = {
	'status_todos': 'Si el status es "Todos" forzosamente debe especificar una fecha distinta de 1901-01-01 !',
	'fecha_invalida': 'La fecha debe ser menor o igual a la fecha actual',
	'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
	'Error_en_mes': 'El mes de la fecha que esta ingresando es invalido !',
	'No_existe_socio':'Numero de socio no registrado en la base de datos!'

	}

	def clean(self):
		
		cleaned_data = super(BuscapedidosporsocioForm,self).clean()
		numpedido = cleaned_data.get('numpedido')
		socio = cleaned_data.get('socio')
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')

		if numpedido == 0:

			if socio < 2:	
				raise forms.ValidationError('Ingrese un numero de socio mayor a 1 !')

			if fechainicial and fechafinal:

				if fechainicial > fechafinal:
					raise forms.ValidationError('La fecha final debe ser mayor o igual a la fecha inicial !')
			else:

				if not fechainicial:
					raise  forms.ValidationError('Ingrese una fecha inicial !')
				if not fechafinal:
					raise forms.ValidationError('Ingrese una fecha final !')

		return self.cleaned_data

class Calzadollego_gralForm(forms.Form):
	#hoy =  date.today()	
	t = datetime.now
	#t.strftime('%m/%d/%Y')

	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	
	fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
	fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'campo_vacio': 'Esta omitiendo ingresar un valor en algun campo fecha, por favor ingrese valores en todos los campos fecha!',
	}

	def clean(self):
		
		cleaned_data = super(Calzadollego_gralForm, self).clean()
		
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
	
		return self.cleaned_data


		

class Calzadollego_detalleForm(forms.Form):
	#hoy =  date.today()	
	t = datetime.now
	#t.strftime('%m/%d/%Y')

	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	
	fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
	fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	

	opciones_rpte = (('Pantalla','Pantalla',),('Archivo_Excel','Archivo_Excel',),)
	op = forms.ChoiceField(label='Dirigir a:',initial='Pantalla',choices=opciones_rpte,required=False)

	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
	'campo_vacio': 'Este omitiendo un valor de fecha, por favor ingrese un valor en todos los campos fecha !'
	}

	def clean(self):
		
		cleaned_data = super(Calzadollego_detalleForm, self).clean()
		
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		op = cleaned_data.get('op')

		print "fechas aqui:"
		print fechainicial
		print fechafinal

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
	
		

		return self.cleaned_data



class Consulta_colocacionesForm(forms.Form):

	proveedores = {}

	

	
	def __init__(self,*args,**kwargs):

		opcion_consulta = (('0','SELECCIONE...'),('1','Nuevos'),('2','Por Confirmar'))
		
		lprov = lista_Proveedores()

		super(Consulta_colocacionesForm, self).__init__(*args,**kwargs)
		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
			label='Proveedor',choices = lprov,initial='0',required='True' )



		self.fields['tipoconsulta']  = forms.ChoiceField(widget=forms.Select(),
			label='Tipo de Consulta',choices = opcion_consulta,initial='1',required='True' )

		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		self.fields['fechainicial'] = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	
		self.fields['fechafinal'] = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)

		'''error_messages = {
		
		'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
		'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
		}'''


		t = datetime.now
		#t.strftime('%m/%d/%Y')

		'''tipoconsulta  = forms.ChoiceField(widget=forms.Select(),
				label='Tipo de Consulta',choices = opcion_consulta,initial='1',required='True' )
		# Prepara el campo para utilizar datepicker
		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		
		fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)'''
		
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'campo_vacio': 'Esta omitiendo un valor en algun campo de fecha, por favor ingrese todas las fechas !',
	'error_proveedor': 'Seleccione un proveedor..!',
	'error_tipoconsulta': 'Seleccione el tipo de consulta que desea realizar',
	}

	def clean(self):

		
		cleaned_data = super(Consulta_colocacionesForm, self).clean()
		proveedor = cleaned_data.get('proveedor')
		tipoconsulta = cleaned_data.get('tipoconsulta')
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')

		print "fechas aqui:"
		print fechainicial
		print 

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
		
		
		if proveedor < '1':

			raise forms.ValidationError(self.error_messages['error_proveedor'],code='error_proveedor')

		if tipoconsulta < '1':

			raise forms.ValidationError(self.error_messages['error_tipoconsulta'],code='error_tipoconsulta')

		return self.cleaned_data

class Consulta_ventasForm(forms.Form):

	proveedores = {}

	

	
	def __init__(self,*args,**kwargs):

		opcion_consulta = (('0','SELECCIONE...'),('1','Nuevos'),('2','Por Confirmar'))
		
		lprov = lista_Sucursales()

		super(Consulta_ventasForm, self).__init__(*args,**kwargs)
		self.fields['sucursal'] = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal',choices = lprov,initial='0',required='True' )

		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		self.fields['fechainicial'] = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	
		self.fields['fechafinal'] = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)

		'''error_messages = {
		
		'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
		'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
		}'''








		t = datetime.now
		#t.strftime('%m/%d/%Y')

		'''tipoconsulta  = forms.ChoiceField(widget=forms.Select(),
				label='Tipo de Consulta',choices = opcion_consulta,initial='1',required='True' )
		# Prepara el campo para utilizar datepicker
		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		
		fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)'''
		
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'campo_vacio': 'Esta omitiendo ingresar el valor de fecha en algun campo de fecha, por favor ingrese ambas fechas !',
	'error_sucursal': 'Seleccione un proveedor..!',
	'error_tipoconsulta': 'Seleccione el tipo de consulta que desea realizar',
	}

	def clean(self):

		
		cleaned_data = super(Consulta_ventasForm, self).clean()
		sucursal = cleaned_data.get('sucursal')
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')

		print "fechas aqui:"
		print fechainicial
		print fechafinal

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
		'''if proveedor < '1':

			raise forms.ValidationError(self.error_messages['error_proveedor'],code='error_proveedor')'''

		return self.cleaned_data


class Consulta_comisionesForm(forms.Form):

	proveedores = {}

	

	
	def __init__(self,*args,**kwargs):

		opcion_consulta = (('0','SELECCIONE...'),('1','Nuevos'),('2','Por Confirmar'))
		
		lprov = lista_Sucursales()

		super(Consulta_comisionesForm, self).__init__(*args,**kwargs)
		self.fields['sucursal'] = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal',choices = lprov,initial='0',required='True' )

		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		self.fields['fechainicial'] = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	
		self.fields['fechafinal'] = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
		t = datetime.now
		#t.strftime('%m/%d/%Y')

		'''tipoconsulta  = forms.ChoiceField(widget=forms.Select(),
				label='Tipo de Consulta',choices = opcion_consulta,initial='1',required='True' )
		# Prepara el campo para utilizar datepicker
		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		
		fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)'''
		
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'campo_vacio': 'Esta omitiendo un valor de facha, ingrese valores en todos los campos de fecha !',
	'error_sucursal': 'Seleccione un proveedor..!',
	'error_tipoconsulta': 'Seleccione el tipo de consulta que desea realizar',
	}

	def clean(self):

		
		cleaned_data = super(Consulta_comisionesForm, self).clean()
		sucursal = cleaned_data.get('sucursal')
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')

		if fechainicial is not None and fechafinal is not None:
			2019
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
		
		return self.cleaned_data
	

class BuscapedidosposfechaForm(forms.Form):


	
	
	socio = forms.IntegerField(label='Socio Numero',initial=0,required=False)
	
		
	def clean(self):
		
		cleaned_data = super(BuscapedidosposfechaForm,self).clean()
		socio = cleaned_data.get('socio')

		if socio < 2:	

			raise forms.ValidationError('Ingrese un numero de socio mayor a 1 !')

		return self.cleaned_data


class PedidosgeneralForm(forms.Form):

	def __init__(self,*args,**kwargs):
		
		super(PedidosgeneralForm, self).__init__(*args,**kwargs)
		DateInput = partial(forms.DateInput, {'class': 'datepicker',})
		hoy=datetime.now()
  		f = hoy.strftime("%d/%m/%Y")

		self.fields['fechainicial'] = forms.DateField(label='Fecha de mvto inicial (dd/mm/yyyy)',initial=f,widget=DateInput())			
		self.fields['fechafinal'] = forms.DateField(label='Fecha de mvto final (dd/mm/yyyy)',initial=f,widget=DateInput())			
		self.fields['socionum'] = forms.IntegerField(initial=0,validators=[MinValueValidator(0)])			



	#hoy =  date.today()	
	#t = datetime.now
	# Prepara el campo para utilizar datepicker
	#DateInput = partial(forms.DateInput, {'class': 'datepicker',})

	#		hoy=datetime.now()
  	#	f = hoy.strftime("%d/%m/%Y")
	#	self.fields['fechamaximaentrega'] = forms.DateField(label='Fecha max entrega (dd/mm/yyyy)',initial=f,widget=DateInput())			


	DateInput = partial(forms.DateInput, {'class': 'datepicker','format':'%d/%m/%Y',})
	numpedido = forms.IntegerField(label='Pedido Numero',initial=0,validators=[MinValueValidator(0)],required=False)
	
	socionum = forms.IntegerField(label='Socio Numero',initial=0,required=False,validators=[MinValueValidator(0)])
	
	
	'''opciones_status = (('1','Pedido',),('2','Por Confirmar',),('3','Aqui',),('4','Cancelado',),('5','Todos',),)'''
	opciones_status = (('Encontrado','Encontrado',),('Por Confirmar','Por Confirmar',),('Confirmado','Confirmado',),('Aqui','Aqui',),('Cancelado','Cancelado',),('Devuelto','Devuelto',),('RecepEnDevol','RecepEnDevol',),('Dev a Prov','Dev a Prov',),('Facturado','Facturado',),('Descontinuado','Descontinuado'),('Todos','Todos',),)
	status = forms.ChoiceField(label='Status',initial='Confirmado',choices=opciones_status,required=False)
	#fecha = forms.DateField(label='Fecha en que hizo (dd/mm/yyyy)',initial= datetime.now,input_formats=['%d/%m/%Y',],)
	estiloalt =  forms.CharField(label='Estilo',required=False)
	fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),required=False)
	fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),required=False)
	error_messages = {
	'status_todos': 'Si el status es "Todos" forzosamente debe especificar una fecha distinta de 1901-01-01 !',
	'fecha_invalida': 'La fecha debe ser menor o igual a la fecha actual',
	'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
	'Error_en_mes': 'El mes de la fecha que esta ingresando es invalido !',
	'No_existe_socio':'Numero de socio no registrado en la base de datos!', 
	'Error_rango_fechas':'La fecha final debe ser mayor o igual a la fecha inicial !',

	}

	def clean(self):
		
		cleaned_data = super(PedidosgeneralForm,self).clean()
		numpedido = cleaned_data.get('numpedido')
		socionum = cleaned_data.get('socionum')
		status = cleaned_data.get('status')
		estiloalt =  cleaned_data.get('estiloalt')
		self.fechainicial = cleaned_data.get('fechainicial')
		self.fechafinal = cleaned_data.get('fechafinal')

		if numpedido == 0:

			if socionum < 2 and  socionum != 0:	
				raise forms.ValidationError('Ingrese un numero de socio mayor a 1 !')
			

			else:
				if socionum >= 2:
					cursor=connection.cursor()
					cursor.execute('SELECT asociadono from asociado where asociadono=%s;',(socionum,))
					
					if cursor.fetchone() == None:
						raise forms.ValidationError('N??mero de socio no registrado en la base de datos !')
				else:
					if estiloalt.strip() == '':
						if status == "Todos" :
							raise forms.ValidationError('No puede solicitar consulta de pedidos para todos los estatus en una sola exhibicion, elija un status en partiular !')
				

			if self.fechainicial and self.fechafinal:

				if self.fechainicial > self.fechafinal:
					raise forms.ValidationError('La fecha final debe ser mayor o igual a la fecha inicial !')
				if (self.fechafinal-self.fechainicial) > timedelta(days=90):
					raise forms.ValidationError('Solo se permite la consulta de hasta 90 dias !')
			else:

				if not self.fechainicial:
					raise  forms.ValidationError('Ingrese una fecha inicial !')
				if not self.fechafinal:
					raise forms.ValidationError('Ingrese una fecha final !')

		return self.cleaned_data




class Entrada_sistemaForm(forms.Form):

	proveedores = {}

	sucursal = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal',initial=0,required='True' )
		
	def __init__(self,*args,**kwargs):

		
		
		lprov = lista_Sucursales()

		super(Entrada_sistemaForm, self).__init__(*args,**kwargs)
		self.fields['sucursal'] = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal',choices = lprov,initial=0,required='True' )
		
	def clean_sucursal(self):

		cleaned_data = super(Entrada_sistemaForm, self).clean()
		sucursal = self.cleaned_data.get('sucursal')

		if sucursal=='0':
			raise forms.ValidationError("Seleccione una sucursal en particular !")
		
		return sucursal

class CancelaproductoForm(forms.Form):

	motivo_cancelacion = forms.CharField(label='Motivo de cancelacion:',initial=' ',required=True)

	def clean_motivo_cancelacion(self):
		
		cleaned_data = super(CancelaproductoForm,self).clean()
		motivo_cancelacion = self.cleaned_data.get('motivo_cancelacion')

		if not motivo_cancelacion: 	

			raise forms.ValidationError('Escriba un motivo por el cual esta cancelado el producto!')
		else:
			if len(motivo_cancelacion)<10:
				raise forms.ValidationError("La descripcion del motivo debe tener una longitud superior a 15 caracteres !")
		return motivo_cancelacion

class Ingresa_socioForm(forms.Form):

	
	socio = forms.IntegerField(label='Numero de socio:',initial=0,required=True)

	def clean_socio(self):
		cleaned_data = super(Ingresa_socioForm, self).clean()
		socio = self.cleaned_data.get('socio')
		
		if socio <= 0: 	

			raise forms.ValidationError('Ingrese un numero de socio !')
		
		elif socio == 3:

			raise forms.ValidationError('Este socio es para devoluciones a proveedor !')
		else:

			pass
		return socio	



class ColocacionesForm(forms.Form):
	#pdb.set_trace() 
	proveedores = {}

	lista_tipos_consulta = (('1','Nuevos'),('2','Por Confirmar'),('3','Encontrados'),('4','Colocados'),('5','Descontinuados'),('6','Cancelados'))
	lista_tipos_ordenamiento = (('1','Estilo'),('2','Socio'),('3','Fecha'),)

	lista_almacenes = ((0,'Seleccione'),(1,'Seleccione'),(2,'Seleccione'),(3,'Seleccione'),(4,'Seleccione'),(5,'Seleccione'),(6,'Seleccione'),(7,'Seleccione'),(8,'Seleccione'),(9,'Seleccione'))
	proveedor = forms.ChoiceField(widget=forms.Select(),label='Proveedor',initial=0,required=True)
	almacen = forms.ChoiceField(widget=forms.Select(),label='Almac??n',initial=0,choices=(),required=False)
	hoy =  date.today()	
	#t = datetime.now
	f_inicial_init =  date.today()

	f_final_init = f_inicial_init + timedelta(days=30)



	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	#fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),initial=f_inicial_init.strftime('%d/%m/%Y'),required=False)
	#fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),initial=f_final_init.strftime('%d/%m/%Y'),required=False)

	fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),required=False)
	fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),required=False)


	tipo_consulta = forms.ChoiceField(label="Consultar pedidos",widget=forms.Select(),choices=lista_tipos_consulta,required=True)
	
	ordenado_por = forms.ChoiceField(label="Ordenar por",widget=forms.Select(),initial='1',choices=lista_tipos_ordenamiento,required=True)

	def __init__(self,*args,**kwargs):

		
		lprov = lista_Proveedores()

		super(ColocacionesForm, self).__init__(*args,**kwargs)

		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
			label='Proveedor',choices = lprov,initial=0,required='True' )
		

	def clean(self):
		
		cleaned_data = super(ColocacionesForm, self).clean()
		
		proveedor = cleaned_data.get('proveedor')
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')

		if proveedor == '0':
			raise forms.ValidationError("Seleccione un proveedor !")

				
		else:
			if not(fechainicial and fechafinal):

				if not fechainicial:
					raise  forms.ValidationError('Ingrese una fecha inicial !')
				if not fechafinal:
					raise forms.ValidationError('Ingrese una fecha final x!')
				
			else:
				if fechainicial > fechafinal:
					raise forms.ValidationError('La fecha final debe ser mayor o igual a la fecha inicial !')
				if (fechafinal-fechainicial) > timedelta(days=90):
					raise forms.ValidationError('Solo se permite la consulta de hasta 90 dias !')
				

		return self.cleaned_data

class ElegirAlmacenaCerrarForm(forms.Form):

	proveedores = {}

	lista_almacenes = ((0,'Seleccione'),(1,'alm1'),(2,'alm2'),(3,'alm3'),(4,'alm4'),(5,'alm5'),(6,'alm6'),(7,'alm7',),(8,'alm8'),(9,'alm9'),(10,'alm10'),(11,'alm11'),(12,'alm12'),) # Estos valores que toma la lista, son solamente default; los valores reales de este campo son dinamicos y se crean via jquery
	proveedor = forms.ChoiceField(widget=forms.Select(),label='Proveedor',initial=0,required=True)
	almacen = forms.ChoiceField(widget=forms.Select(),label='Almac??n',initial='0',choices=lista_almacenes,required=True)
	#hoy =  date.today()

	error_messages ={'proveedor_erroneo':'Elija un proveedor !',}	
		
	def __init__(self,*args,**kwargs):

		
		lprov = lista_Proveedores()

		super(ElegirAlmacenaCerrarForm, self).__init__(*args,**kwargs)

		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
			label='Proveedor',choices = lprov,initial=0,required='True' )
		
	def clean(self):
		#import pdb; pdb.set_trace()

		cleaned_data = super(ElegirAlmacenaCerrarForm, self).clean()
		proveedor = cleaned_data.get('proveedor')

		if proveedor=='0':

			raise forms.ValidationError(self.error_messages['proveedor_erroneo'],code='proveedor_erroneo')
		
		return self.cleaned_data

# Seleccion de cierre para rpte cotejo


class SeleccionCierreRpteCotejoForm(forms.Form):

	proveedores = {}
	lista_cierres = (('Seleccione','Seleccione'),('cierre1','cierre1'),('cierre2','cierre2'),('cierre3','cierre3'),('cierre4','cierre4'),('cierre5','cierre5'),('cierre6','cierre6'),('cierre7','cierre7',),) # Estos valores que toma la lista, son solamente default; los valores reales de este campo son dinamicos y se crean via jquery

	proveedor_rpte_cotejo = forms.ChoiceField(widget=forms.Select(),label='Proveedor',initial=0,required=True)
	cierre_rpte_cotejo = forms.IntegerField(initial=0,label='Cierre',required=True)
	
	error_messages = {'proveedor_invalido':'Seleccione un proveedor !',
							'cierre_invalido':'Ingrese un numero de cierre mayor a cero !',
							'cierre_inexistente':'Numero de cierre no registrado en el sistema !'}	




	#hoy =  date.today()	
		
	def __init__(self,*args,**kwargs):

		
		lprov = lista_Proveedores()

		super(SeleccionCierreRpteCotejoForm, self).__init__(*args,**kwargs)

		self.fields['proveedor_rpte_cotejo'] = forms.ChoiceField(widget=forms.Select(),
			label='Proveedor',choices = lprov,initial=0,required='True' )
	

	def clean(self):
	
		cleaned_data = super( SeleccionCierreRpteCotejoForm, self).clean()
		proveedor_rpte_cotejo = cleaned_data.get('proveedor_rpte_cotejo')
		cierre_rpte_cotejo = cleaned_data.get('cierre_rpte_cotejo')


		cursor=connection.cursor()
		cursor.execute('SELECT id_cierre from pedidos_encontrados WHERE id_cierre=%s',(cierre_rpte_cotejo,))
		num_cierre = cursor.fetchone()
		cursor.close()




		
		if proveedor_rpte_cotejo == '0':
		
			raise forms.ValidationError(self.error_messages['proveedor_invalido'],code='proveedor_invalido')

		if cierre_rpte_cotejo <= 0:

			raise forms.ValidationError(self.error_messages['cierre_invalido'],code='cierre_invalido')
		else:
			if num_cierre is None:
				raise forms.ValidationError(self.error_messages['cierre_inexistente'],code='cierre_inexistente')

		return self.cleaned_data


# Seleccion de cierre paa recepion mercancia


class SeleccionCierreRecepcionForm(forms.Form):

	proveedores = {}
	lista_cierres = (('Seleccione','Seleccione'),('cierre1','cierre1'),('cierre2','cierre2'),('cierre3','cierre3'),('cierre4','cierre4'),('cierre5','cierre5'),('cierre6','cierre6'),('cierre7','cierre7',),) # Estos valores que toma la lista, son solamente default; los valores reales de este campo son dinamicos y se crean via jquery
	lista_tipos_ordenamiento = (('1','Estilo'),('2','Socio'),('3','Sucursal'))

	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})




	proveedor_rpte_cotejo = forms.ChoiceField(widget=forms.Select(),label='Proveedor',initial=0,required=True)
	cierre_rpte_cotejo = forms.IntegerField(initial=0,label='Cierre',required=True)
	marcartodo_nollego = forms.BooleanField(label="Marcar todo como No llego", initial=False,required=False)
	nueva_fecha_llegada =  forms.DateField(label='Nueva fecha llegada',widget=DateInput(),required=False)
	ordenado_por = forms.ChoiceField(label="Ordenar por",widget=forms.Select(),initial='1',choices=lista_tipos_ordenamiento,required=True)

	error_messages = {'proveedor_invalido':'Seleccione un proveedor !',
							'cierre_invalido':'Ingrese un numero de cierre mayor a cero !','fecha_invalida':'Ingrese una fecha nueva de llegada',
							'cierre_no_registrado':'Numero de cierre no registrado en el sistema con este proveedor !','cierre_recepcionado':'Este cierre ya fue recepcionado anteriormente !'}	

	#hoy =  date.today()	
		
	def __init__(self,*args,**kwargs):

		
		lprov = lista_Proveedores() # genera una lista de proveedores para ser asignada al combo.
		super(SeleccionCierreRecepcionForm, self).__init__(*args,**kwargs)

		self.fields['proveedor_rpte_cotejo'] = forms.ChoiceField(widget=forms.Select(),
			label='Proveedor',choices = lprov,initial=0,required='True' )


	

	def clean(self):
		#pdb.set_trace()
		cleaned_data = super( SeleccionCierreRecepcionForm, self).clean()
		proveedor_rpte_cotejo = cleaned_data.get('proveedor_rpte_cotejo')
		cierre_rpte_cotejo = cleaned_data.get('cierre_rpte_cotejo')
		marcartodo_nollego =  cleaned_data.get('marcartodo_nollego')
		nueva_fecha_llegada =  cleaned_data.get('nueva_fecha_llegada')
		#import pdb; pdb.set_trace()

		# Valida que existe el numero de cierre en la base de datos.
		cursor=connection.cursor()
		cursor.execute('SELECT id,recepcionado from prov_ped_cierre WHERE id=%s and prov_id=%s',(cierre_rpte_cotejo,proveedor_rpte_cotejo,))
		num_cierre = cursor.fetchone()
		cursor.close()

		
		if proveedor_rpte_cotejo == '0':
		
			raise forms.ValidationError(self.error_messages['proveedor_invalido'],code='proveedor_invalido')

		if cierre_rpte_cotejo <= 0:

			raise forms.ValidationError(self.error_messages['cierre_invalido'],code='cierre_invalido')
		else:
			if num_cierre is  None:
				raise forms.ValidationError(self.error_messages['cierre_no_registrado'],code='cierre_no_registrado')
		if num_cierre[1]=='\x01':
			raise forms.ValidationError(self.error_messages['cierre_recepcionado'],code='cierre_recepcionado')
		
		if nueva_fecha_llegada is None and marcartodo_nollego:

			raise forms.ValidationError(self.error_messages['fecha_invalida'],code='fecha_invalida')



		print "nueva_fecha_llegada"
		print nueva_fecha_llegada
		
		print marcartodo_nollego



		return self.cleaned_data


''' ***********   FORMA DOCUMENTOS   *************'''

class DocumentosForm(forms.Form):

	
	lista_tipos_movimiento = (('Todos','Todos'),('Cargo','Cargo'),('Credito','Credito'),('Remision','Remision'),('Abono','Abono'),)
	documento_num = forms.IntegerField(label='Documento',initial=0,required=False)
	tipo_movimiento = forms.ChoiceField(label="Tipo",widget=forms.Select(),choices=lista_tipos_movimiento,required=True)



	hoy =  date.today()	
	#t = datetime.now
	f_inicial_init =  date.today()

	f_final_init = f_inicial_init + timedelta(days=30)





	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	#fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),initial=f_inicial_init.strftime('%d/%m/%Y'),required=False)
	#fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),initial=f_final_init.strftime('%d/%m/%Y'),required=False)

	fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),required=False)
	fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),required=False)
	socio_num = forms.IntegerField(label='Socio',initial=0,required=True)

	error_messages = {'DctoSocio':'Ingrese un numero de documento o bien un numero de socio !',
					'FechaInicial':'Ingrese una fecha inicial !',
					'FechaFinal':'Ingrese una fecha final !',
					'FechIniMayor':'La fecha final debe ser mayor o igual a la fecha inicial !',
					'ConsultaFueraRango':'Solo se permite la consulta de hasta 90 dias !',
					'nohaysocio':'Socio no registrado !',
					'nohaydocto':'Documento no registrado !'}


	def clean(self):
		
		cleaned_data = super(DocumentosForm, self).clean()
		
		documento_num = cleaned_data.get('documento_num')
		tipo_movimiento = cleaned_data.get('tipo_movimiento')
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		socio_num =  cleaned_data.get('socio_num')
		#import pdb; pdb.set_trace()
		cursor = connection.cursor()

		try:

			x=int(socio_num)
 		except TypeError:
 			socio_num = u'0'





		# valida socio

		cursor.execute('SELECT count(*) as total_reg FROM asociado where empresano=1 and  asociadono=%s',(socio_num,))
		total_reg = cursor.fetchone()
		print total_reg[0]
		if total_reg[0] == 0:
			
			no_hay_socio = True
			
		else:
			no_hay_socio = False			
		
		# Valida documento

		cursor.execute('SELECT count(*) FROM documentos where empresano=1 and NoDocto=%s',(documento_num,))
		total_reg =  cursor.fetchone()
		cursor.close()
		print total_reg[0]
		if total_reg[0] == 0:

			no_hay_documento = True
			
		else:
			no_hay_documento = False


		'''if socio_num == 0 and documento_num == 0:
			#raise forms.ValidationError("Seleccione un proveedor !")
			raise forms.ValidationError(self.error_messages['DctoSocio'],code='DctoSocio')
			print "paso por ambos ceros"'''
		
		# Si el socio es diferente de cero valida la fecha:		
		if int(socio_num) != 0:

			if no_hay_socio:
				raise forms.ValidationError(self.error_messages['nohaysocio'],code='nohaysocio')

			if not(fechainicial and fechafinal):

				if not fechainicial:
					raise  forms.ValidationError(self.error_messages['FechaInicial'],code='FechaInicial')
				if not fechafinal:
					raise forms.ValidationError(self.error_messages['FechaFinal'],code='FechaFinal')
				
			else:
				if fechainicial > fechafinal:
					raise forms.ValidationError(self.error_messages['FechIniMayor'],code='FechIniMayor')
				if (fechafinal-fechainicial) > timedelta(days=90):
					raise forms.ValidationError(self.error_messages['ConsultaFueraRango'],code='ConsultaFueraRango')
		
		# De otra manera, quiere decir que el socio es cero y quien tiene un valor es
		# el numero de documento, siendo este el caso no hay ya validacion.
		elif documento_num !=0 :
			if no_hay_documento:
				raise forms.ValidationError(self.error_messages['nohaydocto'],code='nohaydocto')
		else:
			pass

		return self.cleaned_data

class DetalleDocumentoForm(forms.Form):
	#import pdb; pdb.set_trace()

	bloquear_opt =((1,'Si'),(0,'No'),)
	nodocto = forms.IntegerField(label='Num. documento',initial=0,required=False)
	tipodedocumento = forms.CharField(label="Tipo",required=False)
	#ventadecatalogo = forms.BooleanField(label="Venta de catalogo", initial=False,required=False)

	asociado= forms.IntegerField(label='Socio',initial=0,required=True)
	concepto = forms.CharField(label="Concepto",initial='',required=True)
	monto = forms.FloatField(label='Monto',initial=0,required=True)
	bloquearnotacredito = forms.ChoiceField(label='Bloquear ? (Con efecto solo para cr??ditos )',widget=forms.Select(),choices=bloquear_opt,required=False)

	error_messages = {'asociado_inv':'El numero de socio ingrasado debe ser mayor a 0 !',\
				'con_invalido':'Ingrese un concepto significativo,\
				 mayor a 4 caracteres !','err_monto':'Ingrese un monto mayor a cero !'}



	def __init__(self,*args,**kwargs):

		
		super(DetalleDocumentoForm, self).__init__(*args,**kwargs)

		self.fields['nodocto'].widget.attrs['readonly'] = True
		self.fields['tipodedocumento'].widget.attrs['readonly'] = True
		self.fields['asociado'].widget.attrs['readonly'] = True
		self.fields['concepto'].widget.attrs['readonly'] = True
		self.fields['monto'].widget.attrs['readonly'] = True
		
		if self.fields['tipodedocumento'] != 'Credito':
			self.fields['bloquearnotacredito'].widget.attrs['hidden'] = True

		return

	def clean(self):
		
		cleaned_data = super(DetalleDocumentoForm, self).clean()
		
		nodocto = cleaned_data.get('nodocto')
		tipodedocumento =  cleaned_data.get('tipodedocumento')
		#ventadecatalogo = cleaned_data.get('ventadecatalogo')
		asociado = cleaned_data.get('asociado')
		concepto =  cleaned_data.get('concepto')
		monto =  cleaned_data.get('monto')
		bloquearnotacredito = cleaned_data.get('bloquearnotacredito')


		if asociado < 1:

			raise forms.ValidationError(self.error_messages['asociado_inv'],code='asociado_inv')

		# Si el concepto viene con caracteres entonces validad que sean mas de 15


		elif not (concepto is None):

			if len(concepto.strip()) < 4:
			
				raise forms.ValidationError(self.error_messages['con_invalido'],code='con_invalido')
			else:
				pass
		# de otra manera si no trae caracteres solo manda el mensaje		
		elif concepto is None:
			raise forms.ValidationError(self.error_messages['con_invalido'],code='con_invalido')

		elif not (monto>0):
			
			raise forms.ValidationError(self.error_messages['err_monto'],code='err_monto')
		
		else:
			pass

		return self.cleaned_data


''' *************     CREA DOCUMENTOS FORM    ************** '''




class CreaDocumentoForm(forms.Form):

	lista_tipos_movimiento = (('Cargo','Cargo'),('Credito','Credito'),('Remision','Remision'),('Abono','Abono'),)
	
	bloquear_opt =((1,'Si'),(0,'No'),)


	lista_temporadas = ((0,'Seleccione'),(1,'Primavera/Verano'),(2,'Otono/Invierno')) # Estos valores que toma la lista, son solamente default; los valores reales de este campo son dinamicos y se crean via jquery

	doc_tipodedocumento = forms.ChoiceField(label="Tipo",widget=forms.Select(),choices=lista_tipos_movimiento,initial='Remision',required=True)
	doc_ventadecatalogo = forms.ChoiceField(label="Venta de catalogo",widget=forms.Select(),choices=bloquear_opt, initial='0',required=False)
	doc_proveedor = forms.ChoiceField(widget=forms.Select(),label='Proveedor',initial=0,required=False)
	doc_anio =  forms.IntegerField(label='A??o',initial=2018,required=False)
	doc_temporada = forms.ChoiceField(widget=forms.Select(),label='Temporada',choices = lista_temporadas,initial=0,required=False)


	doc_asociado= forms.IntegerField(label='Socio',initial=0,required=True)
	doc_concepto = forms.CharField(label="Concepto",initial=' ',required=True)
	doc_monto = forms.FloatField(label='Monto',initial=0,required=True)
	psw_paso = forms.CharField(widget=forms.PasswordInput,label='Password de paso',initial=0,max_length=3,required=True)


	error_messages = {'asociado_inv':'El numero de socio ingresado debe ser mayor a 0 !',\
				'con_invalido':'Ingrese un concepto significativo,\
				 mayor a 4 caracteres !','err_monto':'Ingrese un monto mayor a cero !'}




	def __init__(self,*args,**kwargs):

		#pdb.set_trace()
		hoy=datetime.now()
  		f = hoy.strftime("%d/%m/%Y")
  		anio_str=f[6:10]

		
		lprov = lista_Proveedores() # genera una lista de proveedores para ser asignada al combo.
		super(CreaDocumentoForm, self).__init__(*args,**kwargs)
		print 'argumetnosw:'
		for x in args:
			print x

		self.fields['doc_proveedor'] = forms.ChoiceField(widget=forms.Select(),
			label='Proveedor',choices = lprov,initial=0,required=False )
		self.fields['doc_asociado'] = forms.IntegerField(label='Socio',initial=0,required=True)
		self.fields['doc_anio'] =forms.IntegerField(label='A??o',initial=anio_str,required=False)
		return

	def clean(self):
		#pdb.set_trace()
		
		cleaned_data = super(CreaDocumentoForm, self).clean()

		
		self.tipodedocumento = cleaned_data.get('doc_tipodedocumento')
		self.ventadecatalogo = cleaned_data.get('doc_ventadecatalogo')
		self.asociado = cleaned_data.get('doc_asociado')
		self.concepto =  cleaned_data.get('doc_concepto')
		self.monto =  cleaned_data.get('doc_monto')
		self.psw_paso = cleaned_data.get('psw_paso')
		self.proveedor = cleaned_data.get('doc_proveedor')
		self.anio = cleaned_data.get('doc_anio')
		self.temporada = cleaned_data.get('doc_temporada')



		try:
			self.longitud_concepto = len(self.concepto.strip())
		except:
			self.longitud_concepto = 0

		if self.asociado < 1:
			raise forms.ValidationError(self.error_messages['asociado_inv'],code='asociado_inv')

		elif self.longitud_concepto <3:
			raise forms.ValidationError(self.error_messages['con_invalido'],code='con_invalido')

		elif not (self.monto>0):
			raise forms.ValidationError(self.error_messages['err_monto'],code='err_monto')
		elif self.ventadecatalogo==1 and int(self.anio)<2019:
			raise forms.ValidationError("Ingrese un anio")
		elif self.ventadecatalogo == u'1' and (self.proveedor==u'0' or self.anio<2019 or self.temporada=='0'):
			raise forms.ValidationError("Ingrese el proveedor, el a??o y la temporada !")


		return self.cleaned_data


class CierresForm(forms.Form):
	#pdb.set_trace() 
	

	lista_colocado_via = (('1','Pagina Web'),('2','Telefono'),('3','Correo Electronico'),)

	id = forms.IntegerField(label='id:')
	referencia = forms.CharField(label='Referencia:')
	pedidonum = forms.IntegerField(label='Pedido Numero:')
	total_articulos = forms.IntegerField(label='Total de articulos:')
	total_art_recibidos = forms.IntegerField(label='Tot. Articulos recibidos:')
	paqueteria = forms.CharField(label='Paqueteria:')
	noguia = forms.CharField(label='Numero de Guia:')
	colocado_via = forms.ChoiceField(widget=forms.Select(),label='Colocado Via:',choices=lista_colocado_via,initial=1,required=True)
	
	def clean(self):

		
		cleaned_data = super(CierresForm, self).clean()
			
		referencia = cleaned_data.get('referencia')
		pedidonum = cleaned_data.get('pedidonum')
		total_articulos = cleaned_data.get('total_articulos')
		total_art_recibidos = cleaned_data.get('total_art_recibidos')
		paqueteria = cleaned_data.get('paqueteria')
		noguia = cleaned_data.get('noguia')
		colocado_via =cleaned_data.get('colocado_via')
		
		return self.cleaned_data

	def __init__(self,*args,**kwargs):

		
		super(CierresForm, self).__init__(*args,**kwargs)

		self.fields['id'].widget.attrs['readonly'] = True
		return

class Crea_devolucionForm(forms.Form):

	proveedores = {}
	
	
	def __init__(self,*args,**kwargs):

		


		opcion_consulta = (('0','SELECCIONE...'),('1','Facturado'),('2','Aqui'))
		
		

		super(Crea_devolucionForm, self).__init__(*args,**kwargs)
		self.fields['Socio'] = forms.IntegerField(label='Socio',initial='0',required='True' )



		self.fields['tipoconsulta']  = forms.ChoiceField(widget=forms.Select(),
			label='Status',choices = opcion_consulta,initial='1',required='True' )

		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		self.fields['fechainicial'] = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),initial=date.today()-timedelta(days=15))
		#fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),initial=f_inicial_init)
	
		self.fields['fechafinal'] = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),initial=date.today())

		'''error_messages = {
		
		'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
		'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
		}'''


		t = datetime.now
		#t.strftime('%m/%d/%Y')

		'''tipoconsulta  = forms.ChoiceField(widget=forms.Select(),
				label='Tipo de Consulta',choices = opcion_consulta,initial='1',required='True' )
		# Prepara el campo para utilizar datepicker
		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		
		fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)'''
		
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'Error_rango_fechas': 'Solo se pueden hacer devoluciones de hasta 15 dias anteriores a la fecha actual !',
	'campo_vacio': 'Esta omitiendo un valor en algun campo de fecha, por favor ingrese todas las fechas !',
	'error_tipoconsulta': 'Seleccione el status de pedidos sobre los cuales hara devoluciones',
	}

	def clean(self):

		
		cleaned_data = super(Crea_devolucionForm, self).clean()
		
		tipoconsulta = cleaned_data.get('tipoconsulta')
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')

		print "fechas aqui:"
		print fechainicial
		print 

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
		
		if tipoconsulta < '1':

			raise forms.ValidationError(self.error_messages['error_tipoconsulta'],code='error_tipoconsulta')

		return self.cleaned_data


class Genera_BaseBonoForm(forms.Form):

	proveedores = {}

	

	
	def __init__(self,*args,**kwargs):

		
		super(Genera_BaseBonoForm, self).__init__(*args,**kwargs)
		

		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		self.fields['fechainicial'] = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		#	fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	
		self.fields['fechafinal'] = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)

		self.fields['porcentaje'] =forms.DecimalField(label='Porcentaje sobre Vta Bruta',required=True)
		self.fields['venta_minima'] = forms.DecimalField(label='Venta minima para bono')

		self.fields['generarcredito'] = forms.BooleanField(label='Generar el credito',required=False)

		self.fields['salida'] = forms.ChoiceField(widget=forms.Select(),label='Enviar a:',choices = (('Pantalla','Pantalla'),('Archivo','Archivo')),initial='Pantalla',required='True')


		'''error_messages = {
		
		'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
		'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
		}'''








		t = datetime.now
		#t.strftime('%m/%d/%Y')

		'''tipoconsulta  = forms.ChoiceField(widget=forms.Select(),
				label='Tipo de Consulta',choices = opcion_consulta,initial='1',required='True' )
		# Prepara el campo para utilizar datepicker
		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		
		fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)'''
		
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'campo_vacio': 'Esta omitiendo ingresar el valor de fecha en algun campo de fecha, por favor ingrese ambas fechas !',
	'error_sucursal': 'Seleccione un proveedor..!',
	'error_porcentaje': 'Seleccione el porcentaje sobre la venta neta que se otorgara como bono',
	}

	def clean(self):

		
		cleaned_data = super(Genera_BaseBonoForm, self).clean()
		
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		porcentaje = cleaned_data.get('porcentaje')
		venta_minima = cleaned_data.get('venta_minima')
		generarcredito =cleaned_data.get('generarcredito')
		salida = cleaned_data.get('salida')

		print "fechas aqui:"
		print fechainicial
		print fechafinal

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
		'''if proveedor < '1':

			raise forms.ValidationError(self.error_messages['error_proveedor'],code='error_proveedor')'''

		if porcentaje<=0:
				raise forms.ValidationError(self.error_messages['error_porcentaje'],code='error_porcentaje')

		return self.cleaned_data


''' FORMA PARA VETAS_NETAS_POR_SOCIO_POR MARCA '''



class RpteVtaNetaSocioxMarcaForm(forms.Form):

	proveedores = {}

	

	
	def __init__(self,*args,**kwargs):

		lprov =lista_Proveedores()

		super(RpteVtaNetaSocioxMarcaForm, self).__init__(*args,**kwargs)
		

		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		self.fields['fechainicial'] = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	
		self.fields['fechafinal'] = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)

		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
			label='Proveedor',choices = lprov,initial=0,required='True' )

		
		'''error_messages = {
		
		'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
		'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
		}'''








		t = datetime.now
		#t.strftime('%m/%d/%Y')

		'''tipoconsulta  = forms.ChoiceField(widget=forms.Select(),
				label='Tipo de Consulta',choices = opcion_consulta,initial='1',required='True' )
		# Prepara el campo para utilizar datepicker
		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		
		fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)'''
		
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'campo_vacio': 'Esta omitiendo ingresar el valor de fecha en algun campo de fecha, por favor ingrese ambas fechas !',
	'error_sucursal': 'Seleccione un proveedor..!',
	'error_porcentaje': 'Seleccione el porcentaje sobre la venta neta que se otorgara como bono',
	}

	def clean(self):

		
		cleaned_data = super(RpteVtaNetaSocioxMarcaForm, self).clean()
		
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		proveedor = cleaned_data.get('proveedor')
	

		print "fechas aqui:"
		print fechainicial
		print fechafinal

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
		'''if proveedor < '1':

			raise forms.ValidationError(self.error_messages['error_proveedor'],code='error_proveedor')'''

		

		return self.cleaned_data




class CanceladocumentoForm(forms.Form):

	motivo_cancelacion = forms.CharField(label='Motivo de cancelacion:',initial=' ',required=True)
	psw_paso = forms.CharField(widget=forms.PasswordInput,label='Password de paso',max_length=3,initial=0,required=True)

	def clean(self):
		
		cleaned_data = super(CanceladocumentoForm,self).clean()
		motivo_cancelacion = self.cleaned_data.get('motivo_cancelacion')
		psw_paso = self.cleaned_data.get('psw_paso')


		if not motivo_cancelacion: 	

			raise forms.ValidationError('Escriba un motivo por el cual esta cancelado el documento !')
		else:
			if len(motivo_cancelacion)<10:
				raise forms.ValidationError("La descripcion del motivo debe tener una longitud superior a 15 caracteres !")
		return cleaned_data



''' ***********   FORMA DOCUMENTOS   *************'''

class RpteCreditosForm(forms.Form):

	#pdb.set_trace()
	
	lista_status = (('Todos','Todos'),('Aplicado','Aplicado'),('Sin aplicar','Sin aplicar'),)
	lista_tipos_credito = (('Todos','Todos'),('Ajuste','Ajuste'),('Devolucion','Devolucion'),('Anticipo','Anticipo'),('Capturado','Capturado'),)
	lista_salida_imp =(('Pantalla','Pantalla'),('Archivo','Archivo'),)


	sucursales = {}

	sucursal_inicial = forms.ChoiceField(widget=forms.Select(),	label='Sucursal_inicial',initial=1,required='True')
	sucursal_final = forms.ChoiceField(widget=forms.Select(),label='Sucursal_final',initial=1,required='True')
 
	
	tipo_credito = forms.ChoiceField(label="Tipo",widget=forms.Select(),choices=lista_tipos_credito,required=True)
	status_credito = forms.ChoiceField(label="Status",widget=forms.Select(),choices=lista_status,required=True)



	hoy =  date.today()	
	#t = datetime.now
	f_inicial_init =  date.today()

	f_final_init = f_inicial_init + timedelta(days=30)





	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	#fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),initial=f_inicial_init.strftime('%d/%m/%Y'),required=False)
	#fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),initial=f_final_init.strftime('%d/%m/%Y'),required=False)

	fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),required=False)
	fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),required=False)

	salida_a = forms.ChoiceField(label="Enviar a",widget=forms.Select(),choices=lista_salida_imp,initial='Pantalla',required=True)
 

	error_messages = {'DctoSocio':'Ingrese un numero de documento o bien un numero de socio !',
					'FechaInicial':'Ingrese una fecha inicial !',
					'FechaFinal':'Ingrese una fecha final !',
					'FechIniMayor':'La fecha final debe ser mayor o igual a la fecha inicial !',
					'ConsultaFueraRango':'Solo se permite la consulta de hasta 90 dias !',
					'nohaysocio':'Socio no registrado !',
					'nohaydocto':'Documento no registrado !',
					'SucursalFinal':'La sucursal final debe ser mayor o igual a la sucursal inicial !',
					'CombinacionInvalida':'Combinacion de tipo de credito con status del mismo invalida !',
					'CombinacionSucursalInvalida': 'Sucursal inicial y final no pueden ser "General"'}


		
	def __init__(self,*args,**kwargs):

		
		
		lprov = lista_Sucursales()

		super(RpteCreditosForm, self).__init__(*args,**kwargs)
		self.fields['sucursal_inicial'] = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal_inicial',choices = lprov,initial=1,required='True' )
		
		self.fields['sucursal_final'] = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal_final',choices = lprov,initial=1,required='True' )
		



	"""def clean_sucursal(self):

		cleaned_data = super(Entrada_sistemaForm, self).clean()
		sucursal = self.cleaned_data.get('sucursal')

		if sucursal=='0':
			raise forms.ValidationError("Seleccione una sucursal en particular !")
		
		return sucursal"""



	def clean(self):
		
		cleaned_data = super(RpteCreditosForm, self).clean()

		sucursal_inicial = self.cleaned_data.get('sucursal_inicial')
		sucursal_final = self.cleaned_data.get('sucursal_final')
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		tipo_credito = cleaned_data.get('tipo_credito')
		status_credito = cleaned_data.get('status_credito')


		if sucursal_final<sucursal_inicial:
			raise forms.ValidationError(self.error_messages['SucursalFinal'],code='SucursalFinal')


		if sucursal_final=='0' and sucursal_inicial=='0':
			raise  forms.ValidationError(self.error_messages['CombinacionSucursalInvalida'],code='CombinacionSucursalInvalida')

		if tipo_credito != 'Todos' and status_credito == 'Todos':
			raise  forms.ValidationError(self.error_messages['CombinacionInvalida'],code='CombinacionInvalida')
	

		if not(fechainicial and fechafinal):

			if not fechainicial:
				raise  forms.ValidationError(self.error_messages['FechaInicial'],code='FechaInicial')
			if not fechafinal:
				raise forms.ValidationError(self.error_messages['FechaFinal'],code='FechaFinal')
			
		else:
			if fechainicial > fechafinal:
				raise forms.ValidationError(self.error_messages['FechIniMayor'],code='FechIniMayor')
			
		# De otra manera, quiere decir que el socio es cero y quien tiene un valor es
		# el numero de documento, siendo este el caso no hay ya validacion.

		return self.cleaned_data



class Recepcion_dev_provForm(forms.Form):

	

	def __init__(self,*args,**kwargs):

		opciones = (('Estilo','Estilo'),('Marca','Marca'))
		
		lprov = lista_Sucursales()

		super(Recepcion_dev_provForm, self).__init__(*args,**kwargs)
		self.fields['sucursal'] = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal',choices = lprov,initial=1,required='True' )
		
		self.fields['ordenarpor']= forms.ChoiceField(widget=forms.Select(),
			label= 'Ordenar por',choices = opciones,initial='Estilo')


class Dev_proveedorForm(forms.Form):

	

	def __init__(self,*args,**kwargs):

		lprov = lista_Proveedores()
		opciones = (('Estilo','Estilo'),('Marca','Marca'))
		lista_almacenes = ((0,'Seleccione'),(1,'Seleccione'),(2,'Seleccione'),(3,'Seleccione'),(4,'Seleccione'),(5,'Seleccione'),(6,'Seleccione'),(7,'Seleccione'),(8,'Seleccione'),(9,'Seleccione'))

		
		super(Dev_proveedorForm, self).__init__(*args,**kwargs)

		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
			label = 'Proveedor',choices =lprov, initial=0,required='True')

		self.fields['almacen'] = forms.ChoiceField(widget=forms.Select(),
			label='Almac??n',initial=0,choices=lista_almacenes,required=False)

		self.fields['ordenarpor']= forms.ChoiceField(widget=forms.Select(),
			label= 'Ordenar por',choices = opciones,initial='Estilo')

		self.fields['num_socio']= forms.IntegerField(label='Numero de Socio',required=True)
		self.fields['nombre_socio']= forms.CharField(label='Nombre del Socio',required=True,initial='Abel Espinoza Montoya')
		self.fields['dirigir_a']= forms.ChoiceField(widget=forms.Select(),label='Dirigir a',choices=(('Pantalla','Pantalla'),('Archivo','Archivo')),initial='Pantalla',required=True)



		

class FiltroDevProvForm(forms.Form):


	hoy =  date.today()	
	#t = datetime.now
	f_inicial_init =  date.today()

	f_final_init = f_inicial_init + timedelta(days=30)

	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	#fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),initial=f_inicial_init.strftime('%d/%m/%Y'),required=False)
	#fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),initial=f_final_init.strftime('%d/%m/%Y'),required=False)

	fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),required=False)
	fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),required=False)

	error_messages = {'FechaInicial':'Ingrese una fecha inicial !',
					'FechaFinal':'Ingrese una fecha final !',
					'FechIniMayor':'La fecha final debe ser mayor o igual a la fecha inicial !',}

	

	def __init__(self,*args,**kwargs):

		lprov = lista_Proveedores()
		opciones = (('Estilo','Estilo'),('Marca','Marca'))
		lista_almacenes = ((0,'Seleccione'),(1,'Seleccione'),(2,'Seleccione'),(3,'Seleccione'),(4,'Seleccione'),(5,'Seleccione'),(6,'Seleccione'),(7,'Seleccione'),(8,'Seleccione'),(9,'Seleccione'))

		
		super(FiltroDevProvForm, self).__init__(*args,**kwargs)

		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
			label = 'Proveedor',choices =lprov, initial=0,required='True')

		self.fields['almacen'] = forms.ChoiceField(widget=forms.Select(),
			label='Almac??n',initial=0,choices=lista_almacenes,required=False)


	def clean(self):

	
		cleaned_data = super(FiltroDevProvForm, self).clean()
		
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		

		print "fechas aqui:"
		print fechainicial
		print fechafinal

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')

		return self.cleaned_data


class Edicion_devprovForm(forms.Form):


	hoy =  date.today()	
	#t = datetime.now

	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	id = forms.IntegerField(label='id',required=False)

	guia = forms.CharField(label='Guia',required=True)

	observaciones = forms.CharField(label='Observaciones',required=True)

	fecha_recepcion = forms.DateField(label='Fecha recepcion',widget=DateInput(),required=False,initial=hoy)

	recibio = forms.CharField(label='Recibido por:',required=True)

	num_socio = forms.CharField(label='Numero Socio',required=True)
	nombre_socio = forms.CharField(label='Nombre del socio',required=True)


	def __init__(self,*args,**kwargs):

		
		super(Edicion_devprovForm, self).__init__(*args,**kwargs)

		self.fields['id'].widget.attrs['readonly'] = True
		return

	def clean(self):

		cleaned_data = super(Edicion_devprovForm,self).clean()
	
		id = cleaned_data.get('id')
		guia = cleaned_data.get('guia')
		observaciones = cleaned_data.get('observaciones')
		fecha_recepcion = cleaned_data.get('fecha_recepcion')
		recibio = cleaned_data.get('recibio')
		num_socio = cleaned_data.get('num_socio')
		nombre_socio = cleaned_data.get('nombre_socio')
		return self.cleaned_data

class DatosProveedorForm(forms.Form):

	def __init__(self,*args,**kwargs):

		
		super(DatosProveedorForm, self).__init__(*args,**kwargs)

		self.fields['ProveedorNo'].widget.attrs['readonly'] = True


	ProveedorNo = forms.IntegerField(label='Proveedor Num.',required=True)
	RazonSocial = forms.CharField(label='Nombre',required=True,max_length=45)	
	Direccion = forms.CharField(label='Direccion',required=True,max_length=45)
	Colonia = forms.CharField(label='Colonia',required=True,max_length=45)
	Ciudad = forms.CharField(label='Ciudad',required=True,max_length=45)
	Estado = forms.CharField(label='Estado',required=True,max_length=45)
	Pais = forms.CharField(label='Pais',required=True,max_length=11)
	CodigoPostal = forms.IntegerField(label='C.P.',required=True)
	telefono1 = forms.CharField(label='Telefono 1',required=True,max_length=15)
	telefono2 = forms.CharField(label='Telefono 2',required=True,max_length=15)
	fax = forms.CharField(label='Fax',required=True,max_length=15)
	celular = forms.CharField(label='Celular',required=True,max_length=15)
	radio = forms.CharField(label='radio',required=True,max_length=15)
	email = forms.EmailField(label='email',required=True,max_length=100)
	maneja_desc = forms.ChoiceField(widget=forms.Select(),
			label='Maneja descuento',choices =((1,'Si'),(0,'No')),required='True' )
	baseparabono = forms.BooleanField(label='Base para bono',required=False)
	psw_paso = forms.CharField(label='psw_paso',max_length=3,widget=forms.PasswordInput(),required=True)
	

	error_messages = {'telefono1':'Valor incorrecto para telefono1, ingrese unicamente numeros !',
					'telefono2':'Valor incorrecto para telefono2, ingrese unicamente numeros !',
					'fax':'Valor incorrecto para fax, ingrese unicamente numeros !',
					'celular':'Valor incorrecto para celular, ingrese unicamente numeros !'}




	def clean(self):

		cleaned_data = super(DatosProveedorForm,self).clean()
	
		ProveedorNo = cleaned_data.get('ProveedorNo')
		RazonSocial = cleaned_data.get('RazonSocial')
		Direccion = cleaned_data.get('Direccion')
		Colonia = cleaned_data.get('Colonia')
		Ciudad = cleaned_data.get('Ciudad')
		Estado = cleaned_data.get('num_socio')
		Pais = cleaned_data.get('Pais')
		CodigoPostal = cleaned_data.get('CodigoPostal')
		telefono1 = cleaned_data.get('telefono1')
		telefono2 = cleaned_data.get('telefono2')
		fax = cleaned_data.get('fax')
		celular = cleaned_data.get('celular')
		radio = cleaned_data.get('radio')
		email = cleaned_data.get('email')
		maneja_desc = cleaned_data.get('maneja_desc')
		baseparabono = cleaned_data.get('baseparabono')
		psw_paso = cleaned_data.get('psw_paso')
		if  not (telefono1 and telefono2 and fax and celular) is None:
			
			# elimina espacios al inicio

			telefono1=telefono1.strip()
			telefono2=telefono2.strip()
			fax=fax.strip()
			celular=celular.strip()

			if not(telefono1.isdigit()):
				raise forms.ValidationError(self.error_messages['telefono1'],code='telefono1')
			elif not(telefono2.isdigit()): 
				raise forms.ValidationError(self.error_messages['telefono2'],code='telefono2')
			elif not(fax.isdigit()): 
				raise forms.ValidationError(self.error_messages['fax'],code='fax')
			elif not(celular.isdigit()):
				raise forms.ValidationError(self.error_messages['celular'],code='celular')
			else:
				pass
		else:
			raise forms.ValidationError("Ingrese un valor en todos los campos telefonicos !")

				


		return self.cleaned_data

""" FORMA PARA CREAR PROVEEDOR """

class CreaProveedorForm(forms.Form):

	
	RazonSocial = forms.CharField(label='Nombre',required=True,max_length=45)	
	Direccion = forms.CharField(label='Direccion',required=True,max_length=45)
	Colonia = forms.CharField(label='Colonia',required=True,max_length=45)
	Ciudad = forms.CharField(label='Ciudad',required=True,max_length=45)
	Estado = forms.CharField(label='Estado',required=True,max_length=45)
	Pais = forms.CharField(label='Pais',required=True,max_length=45)
	CodigoPostal = forms.IntegerField(label='C.P.',required=True)
	telefono1 = forms.CharField(label='Telefono 1',required=True,max_length=15)
	telefono2 = forms.CharField(label='Telefono 2',required=True,max_length=15)
	fax = forms.CharField(label='Fax',required=True,max_length=15)
	celular = forms.CharField(label='Celular',required=True,max_length=15)
	radio = forms.CharField(label='radio',required=True,max_length=15)
	email = forms.EmailField(label='email',required=True,max_length=100)
	maneja_desc = forms.ChoiceField(widget=forms.Select(),
			label='Maneja descuento',choices =((1,'Si'),(0,'No')),required='True' )
	baseparabono = forms.BooleanField(label='Base para bono',required=False)
	psw_paso = forms.CharField(label='psw_paso',max_length=3,widget=forms.PasswordInput(),required=True)
	

	error_messages = {'telefono1':'Valor incorrecto para telefono1, ingrese unicamente numeros !',
					'telefono2':'Valor incorrecto para telefono2, ingrese unicamente numeros !',
					'fax':'Valor incorrecto para fax, ingrese unicamente numeros !',
					'celular':'Valor incorrecto para celular, ingrese unicamente numeros !'}




	def clean(self):

		cleaned_data = super(CreaProveedorForm,self).clean()
	
		
		RazonSocial = cleaned_data.get('RazonSocial')
		Direccion = cleaned_data.get('Direccion')
		Colonia = cleaned_data.get('Colonia')
		Ciudad = cleaned_data.get('Ciudad')
		Estado = cleaned_data.get('num_socio')
		Pais = cleaned_data.get('Pais')
		CodigoPostal = cleaned_data.get('CodigoPostal')
		telefono1 = cleaned_data.get('telefono1')
		telefono2 = cleaned_data.get('telefono2')
		fax = cleaned_data.get('fax')
		celular = cleaned_data.get('celular')
		radio = cleaned_data.get('radio')
		email = cleaned_data.get('email')
		maneja_desc = cleaned_data.get('maneja_desc')
		baseparabono = cleaned_data.get('baseparabono')
		psw_paso = cleaned_data.get('psw_paso')
		if  not (telefono1 and telefono2 and fax and celular) is None:
			if not(telefono1.isdigit()):
				raise forms.ValidationError(self.error_messages['telefono1'],code='telefono1')
			elif not(telefono2.isdigit()): 
				raise forms.ValidationError(self.error_messages['telefono2'],code='telefono2')
			elif not(fax.isdigit()): 
				raise forms.ValidationError(self.error_messages['fax'],code='fax')
			elif not(celular.isdigit()):
				raise forms.ValidationError(self.error_messages['celular'],code='celular')
			else:
				pass
		else:
			raise forms.ValidationError("Ingrese un valor en todos los campos telefonicos !")

		return self.cleaned_data		
		




class Lista_dev_recepcionadasForm(forms.Form):

	

	def __init__(self,*args,**kwargs):

		
		opciones = (('Estilo','Estilo'),('Marca','Marca'))

		
		super(Lista_dev_recepcionadasForm, self).__init__(*args,**kwargs)



		
		self.fields['ordenarpor']= forms.ChoiceField(widget=forms.Select(),
			label= 'Ordenar por',choices = opciones,initial='Estilo')

		






''' ***********   RPTE_STATUS_PEDIDOS   *************'''

class RpteStatusDePedidosForm(forms.Form):

	#pdb.set_trace()
	
	lista_salida_imp =(('Pantalla','Pantalla'),('Archivo','Archivo'),)

	sucursales = {}

	sucursal = forms.ChoiceField(widget=forms.Select(),	label='Sucursal',initial=1,required='True')

	opciones_status = (('Encontrado','Encontrado',),('Por Confirmar','Por Confirmar',),('Confirmado','Confirmado',),('Aqui','Aqui',),('Cancelado','Cancelado',),('Devuelto','Devuelto',),('RecepEnDevol','RecepEnDevol',),('Dev a Prov','Dev a Prov',),('Facturado','Facturado',),('Descontinuado','Descontinuado'),('Todos','Todos',),)
	status = forms.ChoiceField(label='Status',initial='Por Confirmar',choices=opciones_status)

	hoy =  date.today()	
	#t = datetime.now
	f_inicial_init =  date.today()

	f_final_init = f_inicial_init + timedelta(days=30)


	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	#fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),initial=f_inicial_init.strftime('%d/%m/%Y'),required=False)
	#fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),initial=f_final_init.strftime('%d/%m/%Y'),required=False)

	fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),required=False)
	fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),required=False)

	salida_a = forms.ChoiceField(label="Enviar a",widget=forms.Select(),choices=lista_salida_imp,initial='Pantalla',required=True)
 

	error_messages = {'FechaInicial':'Ingrese una fecha inicial !',
					'FechaFinal':'Ingrese una fecha final !',
					'FechIniMayor':'La fecha final debe ser mayor o igual a la fecha inicial !',
					}


		
	def __init__(self,*args,**kwargs):

		
		
		lprov = lista_Sucursales()

		super(RpteStatusDePedidosForm, self).__init__(*args,**kwargs)
		self.fields['sucursal'] = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal',choices = lprov,initial=1,required='True' )
		
		



	"""def clean_sucursal(self):

		cleaned_data = super(Entrada_sistemaForm, self).clean()
		sucursal = self.cleaned_data.get('sucursal')

		if sucursal=='0':
			raise forms.ValidationError("Seleccione una sucursal en particular !")
		
		return sucursal"""


	def clean(self):
		
		cleaned_data = super(RpteStatusDePedidosForm, self).clean()

		sucursal = self.cleaned_data.get('sucursal')
		status = self.cleaned_data.get('status')


		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		
		

		'''if sucursal =='0':
			raise  forms.ValidationError(self.error_messages['CombinacionSucursalInvalida'],code='CombinacionSucursalInvalida')'''

			
		if not(fechainicial and fechafinal):

			if not fechainicial:
				raise  forms.ValidationError(self.error_messages['FechaInicial'],code='FechaInicial')
			if not fechafinal:
				raise forms.ValidationError(self.error_messages['FechaFinal'],code='FechaFinal')
			
		else:
			if fechainicial > fechafinal:
				raise forms.ValidationError(self.error_messages['FechIniMayor'],code='FechIniMayor')
			
		# De otra manera, quiere decir que el socio es cero y quien tiene un valor es
		# el numero de documento, siendo este el caso no hay ya validacion.

		return self.cleaned_data




class ventasporcajeroForm(forms.Form):

	proveedores = {}

	

	
	def __init__(self,*args,**kwargs):

		opcion_consulta = (('0','SELECCIONE...'),('1','Nuevos'),('2','Por Confirmar'))
		
		lprov = lista_Sucursales()
		lusr = lista_usuarios()

		super(ventasporcajeroForm, self).__init__(*args,**kwargs)

		self.fields['sucursal'] = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal',choices = lprov,initial='0',required='True' )

		self.fields['usuario'] = forms.ChoiceField(widget=forms.Select(),
			label='Usuario',choices = lusr,initial='0',required='True' )


		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		self.fields['fechainicial'] = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	
		self.fields['fechafinal'] = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)

		'''error_messages = {
		
		'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
		'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
		}'''




		t = datetime.now
		#t.strftime('%m/%d/%Y')

		'''tipoconsulta  = forms.ChoiceField(widget=forms.Select(),
				label='Tipo de Consulta',choices = opcion_consulta,initial='1',required='True' )
		# Prepara el campo para utilizar datepicker
		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		
		fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)'''
		
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'campo_vacio': 'Esta omitiendo ingresar el valor de fecha en algun campo de fecha, por favor ingrese ambas fechas !',
	'error_sucursal': 'Seleccione un proveedor..!',
	'error_tipoconsulta': 'Seleccione el tipo de consulta que desea realizar',
	}

	def clean(self):

		
		cleaned_data = super(ventasporcajeroForm, self).clean()
		sucursal = cleaned_data.get('sucursal')
		usuario = cleaned_data.get('usuario')
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')

		print "fechas aqui:"
		print fechainicial
		print fechafinal

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
		'''if proveedor < '1':

			raise forms.ValidationError(self.error_messages['error_proveedor'],code='error_proveedor')'''

		return self.cleaned_data

"""  FORMA PARA EDITAR DATOS DE CATALOGO """

class DatosCatalogoForm(forms.Form):

	def __init__(self,*args,**kwargs):

		
		super(DatosCatalogoForm, self).__init__(*args,**kwargs)

		def genera_tupla_anios():
			li =[]
			le =[]
			for j in range(2010,2050):

				for z in range(1,2):
					li.append(j)
					li.append(j)
				li=tuple(li)
				le.append(li)
				li=[]
			le=tuple(le)
			return(le)	

		l = genera_tupla_anios()	

		self.fields['ProveedorNo'].widget.attrs['readonly'] = True
		
		self.fields['Anio'].widget.attrs['readonly'] = True
		self.fields['ClaseArticulo'].widget.attrs['readonly'] = True
		self.fields['Periodo'] = forms.ChoiceField(widget=forms.Select(),
		label='A??o',choices = l,required='True' )
		self.fields['Periodo'].widget.attrs['readonly'] = True
			

	ProveedorNo = forms.IntegerField(label='Proveedor Num.',required=True)
	Anio = forms.ChoiceField(label='Temporada',choices=((1,'Primavera/Verano'),(2,'Oto??o/Invierno')),initial=1,required=True)
	Periodo = forms.ChoiceField(widget=forms.Select(),
			label='A??o',required='True' )	
	ClaseArticulo = forms.CharField(label='Catalogo',required=True)
	Activo = forms.ChoiceField(widget=forms.Select(),
			label='Activo',choices =((1,'Si'),(0,'No')),required='True' )
	no_maneja_descuentos = forms.ChoiceField(widget=forms.Select(),
			label='Maneja descuento',choices =((0,'Si'),(1,'No')),required='True' )
	catalogo_promociones = forms.ChoiceField(widget=forms.Select(),
			label='Catalogo de promociones',choices =((1,'Si'),(0,'No')),required='True' )
	

	error_messages = {'error_clase':'Los primeros 4 digitos del catalogo son para el a??o y debe ser un valor mayor al 2020 !',}
					



	def clean(self):

		cleaned_data = super(DatosCatalogoForm,self).clean()
	
		ProveedorNo = cleaned_data.get('ProveedorNo')
		Anio = cleaned_data.get('Anio')
		Periodo = cleaned_data.get('Periodo')
		ClaseArticulo =cleaned_data.get('ClaseArticulo')
		Activo = cleaned_data.get('Activo')
		no_maneja_descuentos = cleaned_data.get('no_maneja_descuentos')
		catalogo_promociones = cleaned_data.get('catalogo_promociones')

		try:
			ClaseArticulo = int(ClaseArticulo[0:4])
		except TypeError as e:

			raise forms.ValidationError(self.error_messages['error_clase'],code='error_clase')


		if (not ClaseArticulo >=2000):
			raise forms.ValidationError(self.error_messages['error_clase'],code='error_clase')
		return self.cleaned_data


class CreaCatalogoForm(forms.Form):

	def __init__(self,*args,**kwargs):

		
		super(CreaCatalogoForm, self).__init__(*args,**kwargs)

		def genera_tupla_anios():
			li =[]
			le =[]
			for j in range(2010,2050):

				for z in range(1,2):
					li.append(j)
					li.append(j)
				li=tuple(li)
				le.append(li)
				li=[]
			le=tuple(le)
			return(le)	

		l = genera_tupla_anios()	

		self.fields['ProveedorNo'].widget.attrs['readonly'] = True
		
		self.fields['Anio'].widget.attrs['readonly'] = False
		self.fields['ClaseArticulo'].widget.attrs['readonly'] = False
		self.fields['Periodo'] = forms.ChoiceField(widget=forms.Select(),
		label='A??o',choices = l,required='True' )
		self.fields['Periodo'].widget.attrs['readonly'] = False	
			

	ProveedorNo = forms.IntegerField(label='Proveedor Num.',required=True)
	Anio = forms.ChoiceField(label='Temporada',choices=((1,'Primavera/Verano'),(2,'Oto??o/Invierno')),initial=1,required=True)
	Periodo = forms.ChoiceField(widget=forms.Select(),
			label='A??o',required='True' )	
	ClaseArticulo = forms.CharField(label='Catalogo',required=True)
	Activo = forms.ChoiceField(widget=forms.Select(),
			label='Activo',choices =((1,'Si'),(0,'No')),required='True' )
	no_maneja_descuentos = forms.ChoiceField(widget=forms.Select(),
			label='Maneja descuento',choices =((0,'Si'),(1,'No')),required='True' )
	catalogo_promociones = forms.ChoiceField(widget=forms.Select(),
			label='Catalogo de promociones',choices =((1,'Si'),(0,'No')),required='True' )
	

	error_messages = {'error_clase':'Error_Catalogo: Longitud max: 12. Ingrese primero 4 digitos del a??o,los subsecuentes deben contener solo letras sin dejar espacios,!',}
					



	def clean(self):

		cleaned_data = super(CreaCatalogoForm,self).clean()
	
		ProveedorNo = cleaned_data.get('ProveedorNo')
		Anio = cleaned_data.get('Anio')
		Periodo = cleaned_data.get('Periodo')
		ClaseArticulo =cleaned_data.get('ClaseArticulo')
		Activo = cleaned_data.get('Activo')
		no_maneja_descuentos = cleaned_data.get('no_maneja_descuentos')
		catalogo_promociones = cleaned_data.get('catalogo_promociones')

		try:
			result=re.match(r'^[2-3][0-9][0-9][0-9]\w{1,8}$',ClaseArticulo)
			if result is None:
				raise TypeError

		except TypeError:
			raise forms.ValidationError(self.error_messages['error_clase'],code='error_clase')

		return self.cleaned_data


'''BUSCA PRODUCTOS POR ESTILO'''


class BuscaEstiloForm(forms.Form):

	#hoy =  date.today()	
	t = datetime.now
	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class':'datepicker'})


	var_estilo = forms.CharField(label='Estilo a buscar:',required=True)
	
	#fecha = forms.DateField(label='Fecha en que hizo (dd/mm/yyyy)',initial= datetime.now,input_formats=['%d/%m/%Y',],)
	fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),required=False)
	fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),required=False)
	
	error_messages = {
	'fecha_invalida': 'La fecha debe ser menor o igual a la fecha actual',
	'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
	'Error_en_mes': 'El mes de la fecha que esta ingresando es invalido !',
	}

	def clean(self):
		
		cleaned_data = super(BuscaEstiloForm,self).clean()
		var_estilo = cleaned_data.get('var_estilo')
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')



		if fechainicial and fechafinal:

			if fechainicial > fechafinal:
				raise forms.ValidationError('La fecha final debe ser mayor o igual a la fecha inicial !')
		else:

			if not fechainicial:
				raise  forms.ValidationError('Ingrese una fecha inicial !')
			if not fechafinal:
				raise forms.ValidationError('Ingrese una fecha final !')
		if (var_estilo) is None:
			raise forms.ValidationError("Ingrese un valor para estilo !")

		return self.cleaned_data


class PiezasNoSolicitadasForm(forms.Form):

	proveedores = {}
	

	# La funcion siguiente "init" tambien  recibe el parametro
	# request, esto se hace para tener tambien disponibles las variables de entorno, en este caso
	# se requerira el request.session['is_staff'] para manejarlos en los campos
	# de fechaMaximaEntrega y el de periodo de entrega.
	# en el views.py los llamados deben inculir request como parametro tanto si la forma es valida como si no lo es.
	def __init__(self,request,*args,**kwargs):


		
		def lista_PeriodosEntrega():
			cursor=connection.cursor()
			cursor.execute('SELECT id,periodo from periodosentrega;')
	
			pr=() # Inicializa una tupla para llenar combo de Periodosentrega
			
			# Convierte el diccionario en tupla
			for row in cursor:
				elemento = tuple(row)
				pr=pr+elemento
			pr = (0L,u'SELECCIONE...') + pr
			

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
			lper_ent = tuple(tuple(x) for x in y)

			
			
			return (lper_ent)

		
		
		lprov = lista_Proveedores()
		lcat = (('0','Seleccione'),)
		lestilo = []
		lmarca = []
		lcolor = []
		ltalla = []
		lper_ent = lista_PeriodosEntrega()
		
		

		opcion_temporada = (('0','SELECCIONE...'),('1','Primavera/Verano'),('2','Oto??o/Invierno'))
		opcion_opt = (('1','1ra.'),('2','2da'),('3','3ra.'))
		lista_almacenes = ((0,'Seleccione'),(1,'Seleccione'),(2,'Seleccione'),(3,'Seleccione'),(4,'Seleccione'),(5,'Seleccione'),(6,'Seleccione'),(7,'Seleccione'),(8,'Seleccione'),(9,'Seleccione'))

		
		#pr_dict = [['1','MODELI'],['2','IMPULS'],['3','OTRO']]
		#pr_dict = (('MODELI','MODELI'),('IMPULS','IMPULS'),('OTRO','OTRO'),)
		#pr_dict = lista_Proveedores()

		super(PiezasNoSolicitadasForm, self).__init__(*args,**kwargs)
		
		

		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
		label='Proveedor',choices = lprov,initial='0',required='True' )

		self.fields['temporada'] = forms.ChoiceField(widget=forms.Select(),
		label='Temporada',choices = opcion_temporada, initial='0',required ='True')
		
		self.fields['catalogo']  = forms.ChoiceField(widget=forms.Select(),
		label='Catalogo',initial = 'SELECCIONE...',required ='True' )
		
		self.fields['pagina'] = forms.CharField(label='Pagina')
		
		self.fields['estilo'] = forms.ChoiceField(widget=forms.Select(),
		label='Estilo',initial='Seleccione',required='True')
		
		self.fields['marca'] = forms.ChoiceField(widget = forms.Select(),
		label='Marca',initial='Seleccione',required='True')

		self.fields['color'] = forms.ChoiceField(widget = forms.Select(),
		label='Color', initial='Seleccione',required='True')
		
		self.fields['talla'] = forms.ChoiceField(widget = forms.Select(),
		label='Talla',initial='Seleccione',required='True')

		self.fields['tallaalt'] = forms.CharField(label='',help_text='Si talla es "NE", ingrese una aqui')
		self.fields['almacen'] = forms.ChoiceField(widget = forms.Select(),label='Almacen',initial=0,choices=lista_almacenes)


		try:# ?? diferencia de pedido normal en art no solicitados siempre se esconderan algunos campos por eso se la siguiente variable
			
		  	escondido = 'display: none;'
		  	
		except:
			return None

	  	self.fields['precio'] = forms.FloatField(label = 'Precio cliente:',initial=0.0,widget=forms.NumberInput(attrs={'style':escondido}))

	  	self.fields['plazoentrega'] = forms.ChoiceField(label='Plazo de entrega:',initial=1,choices=lper_ent,required=True,widget=forms.Select(attrs={'style':escondido,}))
		self.fields['opcioncompra'] = forms.ChoiceField(label='Opcion de compra:',initial='1ra.',help_text='',widget=forms.Select(attrs={'style':escondido,}),choices=opcion_opt)
	  		
  		DateInput = partial(forms.DateInput, {'class': 'datepicker','style':escondido})

  		hoy=datetime.now()
  		f = hoy.strftime("%d/%m/%Y")
		self.fields['fechamaximaentrega'] = forms.DateField(label='Fecha max entrega (dd/mm/yyyy)',initial=f,widget=DateInput())			


class RpteArtNoSolicitadosForm(forms.Form):
	
	def __init__(self,*args,**kwargs):

		
		lprov = lista_Proveedores()

		super(RpteArtNoSolicitadosForm, self).__init__(*args,**kwargs)

		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
			label='Proveedor',choices = lprov,initial='0',required='True' )


	#hoy =  date.today()	
	t = datetime.now
	#t.strftime('%m/%d/%Y')

	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		
	fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
	fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
		

	opciones_rpte = (('Pantalla','Pantalla',),('Archivo_Excel','Archivo_Excel',),)
	op = forms.ChoiceField(label='Dirigir a:',initial='Pantalla',choices=opciones_rpte,required=False)


	error_messages = {
		
		'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
		'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
		'campo_vacio': 'Este omitiendo un valor de fecha, por favor ingrese un valor en todos los campos fecha !'
		}
		

	def clean(self):

		
		
		cleaned_data = super(RpteArtNoSolicitadosForm, self).clean()
		
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		#op = cleaned_data.get('op')

		print "fechas aqui:"
		print fechainicial
		print fechafinal

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
	
		

		return self.cleaned_data


class DatosAsociadoForm(forms.Form):

	def __init__(self,*args,**kwargs):

		
		super(DatosAsociadoForm, self).__init__(*args,**kwargs)

		self.fields['asociadono'].widget.attrs['readonly'] = True


	asociadono = forms.IntegerField(label='Socio Num.',required=False)
	numcontrol = forms.CharField(label='Numero de control',required=True,max_length=12)
	nombre = forms.CharField(label='Nombre',required=True,max_length=45)	
	appaterno = forms.CharField(label='Apellido Paterno',required=True,max_length=45)	
	apmaterno = forms.CharField(label='Apellido Materno',required=True,max_length=45)	
	direccion = forms.CharField(label='Direccion',required=True,max_length=45)
	colonia = forms.CharField(label='Colonia',required=True,max_length=45)
	ciudad = forms.CharField(label='Ciudad',required=True,max_length=45)
	estado = forms.CharField(label='Estado',required=True,max_length=45)
	pais = forms.CharField(label='Pais',required=True,max_length=11)
	#codigopostal = forms.IntegerField(label='C.P.',required=True)
	telefono1 = forms.CharField(label='Telefono 1',required=True,max_length=15)
	telefono2 = forms.CharField(label='Telefono 2',required=True,max_length=15)
	fax = forms.CharField(label='Fax',required=True,max_length=15)
	celular = forms.CharField(label='Celular',required=True,max_length=15)
	radio = forms.CharField(label='radio',required=True,max_length=15)
	direccionelectronica = forms.EmailField(label='email',required=True,max_length=100)
	essocio = forms.ChoiceField(widget=forms.Select(),
			label='Es socio',choices =((1,'Si'),(0,'No')),required='True' )
	forzarcobroanticipo = forms.ChoiceField(widget=forms.Select(),
			label='Forzar el cobro de anticipo',choices =((1,'Si'),(0,'No')),required='True' )
	numeroweb = forms.IntegerField(label='Numero Web',required=False)
	activo = forms.ChoiceField(widget=forms.Select(),
		label='Activo',choices=((1,'Si'),(0,'No')),required='True')
	psw_paso = forms.CharField(label='psw_paso',widget=forms.PasswordInput(),max_length=3,required=True)
	
	
	error_messages = {'telefono1':'Valor incorrecto para telefono1, ingrese unicamente numeros !',
					'telefono2':'Valor incorrecto para telefono2, ingrese unicamente numeros !',
					'fax':'Valor incorrecto para fax, ingrese unicamente numeros !',
					'celular':'Valor incorrecto para celular, ingrese unicamente numeros !',
					'activo':'No ha ingresado el numero web designado para que pueda trabajar en plataforma, mientras no lo asigne no puede cambiar el status de activo !'}




	def clean(self):

		cleaned_data = super(DatosAsociadoForm,self).clean()
	
		asociadono = cleaned_data.get('asociadono')
		nombre = cleaned_data.get('nombre')
		appaterno = cleaned_data.get('appaterno')
		apmaterno = cleaned_data.get('apmaterno')
		direccion = cleaned_data.get('direccion')
		colonia = cleaned_data.get('colonia')
		ciudad = cleaned_data.get('ciudad')
		estado = cleaned_data.get('estado')
		pais = cleaned_data.get('pais')
		codigopostal = cleaned_data.get('codigopostal')
		telefono1 = cleaned_data.get('telefono1')
		telefono2 = cleaned_data.get('telefono2')
		fax = cleaned_data.get('fax')
		celular = cleaned_data.get('celular')
		radio = cleaned_data.get('radio')
		direccionelectronica = cleaned_data.get('direccionelectronica')
		essocio = cleaned_data.get('essocio')
		forzarcobroanticipo = cleaned_data.get('forzarcobroanticipo')
		numeroweb = cleaned_data.get('numeroweb')
		activo=cleaned_data.get('activo')
		usr_id = cleaned_data.get('usr_id')
		if  not (telefono1 and telefono2 and fax and celular) is None:
			
			# elimina espacios al inicio

			telefono1=telefono1.strip()
			telefono2=telefono2.strip()
			fax=fax.strip()
			celular=celular.strip()

			if not(telefono1.isdigit()):
				raise forms.ValidationError(self.error_messages['telefono1'],code='telefono1')
			elif not(telefono2.isdigit()): 
				raise forms.ValidationError(self.error_messages['telefono2'],code='telefono2')
			elif not(fax.isdigit()): 
				raise forms.ValidationError(self.error_messages['fax'],code='fax')
			elif not(celular.isdigit()):
				raise forms.ValidationError(self.error_messages['celular'],code='celular')
			elif numeroweb > 32767:
				 raise forms.ValidationError("Numero web debe ser menor a 32767")	
			elif ',' in direccion:
				 raise forms.ValidationError("No se permite poner comas en el campo direccion, quitelas")
			elif ',' in ciudad:
				 raise forms.ValidationError("No se permite poner comas en el campo ciudad, quitelas")
			elif ',' in colonia:
				 raise forms.ValidationError("No se permite poner comas en el campo colonia, quitelas")
			elif ',' in estado:
				 raise forms.ValidationError("No se permite poner comas en el campo estado, quitelas")

			else:
				pass
		else:
			raise forms.ValidationError("Ingrese un valor en todos los campos telefonicos !")

		'''if activo == 1 and numeroweb==0:
			raise forms.ValidationError(self.error_messages['activo'],code='activo')'''	
				


		return self.cleaned_data

""" FORMA PARA CREAR SOCIO """

class CreaAsociadoForm(forms.Form):

	def __init__(self,*args,**kwargs):

		
		super(CreaAsociadoForm, self).__init__(*args,**kwargs)

		self.fields['asociadono'].widget.attrs['readonly'] = True
		

	asociadono = forms.IntegerField(label='Socio Num.',required=False)
	numcontrol = forms.CharField(label='Numero de control',required=True,max_length=12)
	nombre = forms.CharField(label='Nombre',required=True,max_length=45)	
	appaterno = forms.CharField(label='Apellido Paterno',required=True,max_length=45)	
	apmaterno = forms.CharField(label='Apellido Materno',required=True,max_length=45)	
	direccion = forms.CharField(label='Direccion',required=True,max_length=45)
	colonia = forms.CharField(label='Colonia',required=True,max_length=45)
	ciudad = forms.CharField(label='Ciudad',required=True,max_length=45,initial= 'NUEVO LAREDO')
	estado = forms.CharField(label='Estado',required=True,max_length=45,initial='TAMAULIPAS')
	pais = forms.CharField(label='Pais',required=True,max_length=11,initial='MEXICO')
	#codigopostal = forms.IntegerField(label='C.P.',required=True)
	telefono1 = forms.CharField(label='Telefono 1',required=True,max_length=15)
	telefono2 = forms.CharField(label='Telefono 2',required=True,max_length=15)
	fax = forms.CharField(label='Fax',required=True,max_length=15)
	celular = forms.CharField(label='Celular',required=True,max_length=15)
	radio = forms.CharField(label='radio',required=True,max_length=15)
	direccionelectronica = forms.EmailField(label='email',required=True,max_length=100)
	essocio = forms.ChoiceField(widget=forms.Select(),
			label='Es socio',choices =((1,'Si'),(0,'No')),required='True' )
	forzarcobroanticipo = forms.ChoiceField(widget=forms.Select(),
			label='Forzar el cobro de anticipo',choices =((1,'Si'),(0,'No')),required='True' )
	numeroweb = forms.IntegerField(label='Numero Web',required=False)
	psw_paso = forms.CharField(label='psw_paso',widget=forms.PasswordInput(),max_length=3,required=True)
	
	
	error_messages = {'telefono1':'Valor incorrecto para telefono1, ingrese unicamente numeros !',
					'telefono2':'Valor incorrecto para telefono2, ingrese unicamente numeros !',
					'fax':'Valor incorrecto para fax, ingrese unicamente numeros !',
					'celular':'Valor incorrecto para celular, ingrese unicamente numeros !'}




	def clean(self):

		cleaned_data = super(CreaAsociadoForm,self).clean()
	
		asociadono = cleaned_data.get('asociadono')
		nombre = cleaned_data.get('nombre')
		appaterno = cleaned_data.get('appaterno')
		apmaterno = cleaned_data.get('apmaterno')
		direccion = cleaned_data.get('direccion')
		colonia = cleaned_data.get('colonia')
		ciudad = cleaned_data.get('ciudad')
		estado = cleaned_data.get('estado')
		pais = cleaned_data.get('pais')
		codigopostal = cleaned_data.get('codigopostal')
		telefono1 = cleaned_data.get('telefono1')
		telefono2 = cleaned_data.get('telefono2')
		fax = cleaned_data.get('fax')
		celular = cleaned_data.get('celular')
		radio = cleaned_data.get('radio')
		direccionelectronica = cleaned_data.get('direccionelectronica')
		essocio = cleaned_data.get('essocio')
		forzarcobroanticipo = cleaned_data.get('forzarcobroanticipo')
		numeroweb = cleaned_data.get('numeroweb')
		usr_id = cleaned_data.get('usr_id')
		if  not (telefono1 and telefono2 and fax and celular) is None:
			
			# elimina espacios al inicio

			telefono1=telefono1.strip()
			telefono2=telefono2.strip()
			fax=fax.strip()
			celular=celular.strip()

			if not(telefono1.isdigit()):
				raise forms.ValidationError(self.error_messages['telefono1'],code='telefono1')
			elif not(telefono2.isdigit()): 
				raise forms.ValidationError(self.error_messages['telefono2'],code='telefono2')
			elif not(fax.isdigit()): 
				raise forms.ValidationError(self.error_messages['fax'],code='fax')
			elif not(celular.isdigit()):
				raise forms.ValidationError(self.error_messages['celular'],code='celular')
			elif numeroweb > 32767:
				 raise forms.ValidationError("Numero web debe ser menor a 32767")	
			elif ',' in direccion:
				 raise forms.ValidationError("No se permite poner comas en el campo direccion, quitelas")
			elif ',' in ciudad:
				 raise forms.ValidationError("No se permite poner comas en el campo ciudad, quitelas")
			elif ',' in colonia:
				 raise forms.ValidationError("No se permite poner comas en el campo colonia, quitelas")
			elif ',' in estado:
				 raise forms.ValidationError("No se permite poner comas en el campo Estado, quitelas")

	 		else:
	 			pass
	
		else:
			raise forms.ValidationError("Ingrese un valor en todos los campos telefonicos !")



		return self.cleaned_data




class FiltroSocioCatalogoForm(forms.Form):

	lprov = lista_Proveedores()

	def __init__(self,*args,**kwargs):

		
		super(FiltroSocioCatalogoForm, self).__init__(*args,**kwargs)


		

		def genera_tupla_anios():
			li =[]
			le =[]
			for j in range(2010,2050):

				for z in range(1,2):
					li.append(j)
					li.append(j)
				li=tuple(li)
				le.append(li)
				li=[]
			le=tuple(le)
			return(le)	

		l = genera_tupla_anios()	

		#self.fields['ProveedorNo'].widget.attrs['readonly'] = True
		
		#self.fields['Anio'].widget.attrs['readonly'] = True
		#self.fields['ClaseArticulo'].widget.attrs['readonly'] = True
		self.fields['Periodo'] = forms.ChoiceField(widget=forms.Select(),
		label='A??o',choices = l,required='True' )
		#self.fields['Periodo'].widget.attrs['readonly'] = True
			

	#ProveedorNo = forms.ChoiceField(label='Proveedor Num.',choices=lprov,required=True)
	Anio = forms.ChoiceField(label='Temporada',choices=((1,'Primavera/Verano'),(2,'Oto??o/Invierno')),initial=1,required=True)
	Periodo = forms.ChoiceField(widget=forms.Select(),
			label='A??o',required='True' )	
	#ClaseArticulo = forms.CharField(label='Catalogo',required=True)
	
	error_messages = {'error_clase':'Los primeros 4 digitos del catalogo son para el a??o y debe ser un valor mayor al 2020 !',}
					



	def clean(self):

		cleaned_data = super(FiltroSocioCatalogoForm,self).clean()
	
		ProveedorNo = cleaned_data.get('ProveedorNo')
		Anio = cleaned_data.get('Anio')
		Periodo = cleaned_data.get('Periodo')
		#ClaseArticulo =cleaned_data.get('ClaseArticulo')
		'''
		try:
			ClaseArticulo = int(ClaseArticulo[0:4])
		except TypeError as e:

			raise forms.ValidationError(self.error_messages['error_clase'],code='error_clase')


		if (not ClaseArticulo >=2000):
			raise forms.ValidationError(self.error_messages['error_clase'],code='error_clase')'''
		return self.cleaned_data


class AFiltroDatosCatalogoForm(forms.Form):

	def __init__(self,*args,**kwargs):

		
		super(DatosCatalogoForm, self).__init__(*args,**kwargs)

		def genera_tupla_anios():
			li =[]
			le =[]
			for j in range(2010,2050):

				for z in range(1,2):
					li.append(j)
					li.append(j)
				li=tuple(li)
				le.append(li)
				li=[]
			le=tuple(le)
			return(le)	

		l = genera_tupla_anios()	

		self.fields['ProveedorNo'].widget.attrs['readonly'] = True
		
		self.fields['Anio'].widget.attrs['readonly'] = True
		self.fields['ClaseArticulo'].widget.attrs['readonly'] = True
		self.fields['Periodo'] = forms.ChoiceField(widget=forms.Select(),
		label='A??o',choices = l,required='True' )
		self.fields['Periodo'].widget.attrs['readonly'] = True
			

	ProveedorNo = forms.IntegerField(label='Proveedor Num.',required=True)
	Anio = forms.ChoiceField(label='Temporada',choices=((1,'Primavera/Verano'),(2,'Oto??o/Invierno')),initial=1,required=True)
	Periodo = forms.ChoiceField(widget=forms.Select(),
			label='A??o',required='True' )	
	ClaseArticulo = forms.CharField(label='Catalogo',required=True)
	Activo = forms.ChoiceField(widget=forms.Select(),
			label='Activo',choices =((1,'Si'),(0,'No')),required='True' )
	no_maneja_descuentos = forms.ChoiceField(widget=forms.Select(),
			label='No maneja descuento',choices =((1,'Si'),(0,'No')),required='True' )
	catalogo_promociones = forms.ChoiceField(widget=forms.Select(),
			label='Catalogo de promociones',choices =((1,'Si'),(0,'No')),required='True' )
	

	error_messages = {'error_clase':'Los primeros 4 digitos del catalogo son para el a??o y debe ser un valor mayor al 2020 !',}
					



	def clean(self):

		cleaned_data = super(DatosCatalogoForm,self).clean()
	
		ProveedorNo = cleaned_data.get('ProveedorNo')
		Anio = cleaned_data.get('Anio')
		Periodo = cleaned_data.get('Periodo')
		ClaseArticulo =cleaned_data.get('ClaseArticulo')
		Activo = cleaned_data.get('Activo')
		no_maneja_descuentos = cleaned_data.get('no_maneja_descuentos')
		catalogo_promociones = cleaned_data.get('catalogo_promociones')

		try:
			ClaseArticulo = int(ClaseArticulo[0:4])
		except TypeError as e:

			raise forms.ValidationError(self.error_messages['error_clase'],code='error_clase')


		if (not ClaseArticulo >=2000):
			raise forms.ValidationError(self.error_messages['error_clase'],code='error_clase')
		return self.cleaned_data


class FiltroProveedorForm(forms.Form):

	def __init__(self,*args,**kwargs):

		super(FiltroProveedorForm, self).__init__(*args,**kwargs)


		lprov = lista_Proveedores()

		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
			label='Proveedor',choices = lprov,initial='0',required='True' )
	'''proveedor = forms.ChoiceField(label='Proveedor Num.',required=True)'''

	


	def clean(self):

		cleaned_data = super(FiltroProveedorForm,self).clean()

		proveedor = self.cleaned_data.get('proveedor')

		return(self.cleaned_data)




class CreaAlmacenForm(forms.Form):

	
	RazonSocial = forms.CharField(label='Nombre',required=True,max_length=45)	
	Direccion = forms.CharField(label='Direccion',required=True,max_length=45)
	Colonia = forms.CharField(label='Colonia',required=True,max_length=45)
	Ciudad = forms.CharField(label='Ciudad',required=True,max_length=45)
	Estado = forms.CharField(label='Estado',required=True,max_length=45)
	Pais = forms.CharField(label='Pais',required=True,max_length=45)
	#CodigoPostal = forms.IntegerField(label='C.P.',required=True)
	telefono1 = forms.CharField(label='Telefono 1',required=True,max_length=15)
	telefono2 = forms.CharField(label='Telefono 2',required=True,max_length=15)
	fax = forms.CharField(label='Fax',required=True,max_length=15)
	celular = forms.CharField(label='Celular',required=True,max_length=15)
	radio = forms.CharField(label='radio',required=True,max_length=15)
	direccionelectronica = forms.EmailField(label='email',required=True,max_length=100)
	psw_paso = forms.CharField(label='psw_paso',max_length=3,widget=forms.PasswordInput(),required=True)
			

	error_messages = {'telefono1':'Valor incorrecto para telefono1, ingrese unicamente numeros !',
					'telefono2':'Valor incorrecto para telefono2, ingrese unicamente numeros !',
					'fax':'Valor incorrecto para fax, ingrese unicamente numeros !',
					'celular':'Valor incorrecto para celular, ingrese unicamente numeros !'}




	def clean(self):

		cleaned_data = super(CreaAlmacenForm,self).clean()
	
		
		RazonSocial = cleaned_data.get('RazonSocial')
		Direccion = cleaned_data.get('Direccion')
		Colonia = cleaned_data.get('Colonia')
		Ciudad = cleaned_data.get('Ciudad')
		Estado = cleaned_data.get('num_socio')
		Pais = cleaned_data.get('Pais')
		#CodigoPostal = cleaned_data.get('CodigoPostal')
		telefono1 = cleaned_data.get('telefono1')
		telefono2 = cleaned_data.get('telefono2')
		fax = cleaned_data.get('fax')
		celular = cleaned_data.get('celular')
		radio = cleaned_data.get('radio')
		direccionelectronica = cleaned_data.get('direccionelectronica')
		
		usr_id = cleaned_data.get('usr_id')
		if  not (telefono1 and telefono2 and fax and celular) is None:
			if not(telefono1.isdigit()):
				raise forms.ValidationError(self.error_messages['telefono1'],code='telefono1')
			elif not(telefono2.isdigit()): 
				raise forms.ValidationError(self.error_messages['telefono2'],code='telefono2')
			elif not(fax.isdigit()): 
				raise forms.ValidationError(self.error_messages['fax'],code='fax')
			elif not(celular.isdigit()):
				raise forms.ValidationError(self.error_messages['celular'],code='celular')
			else:
				pass
		else:
			raise forms.ValidationError("Ingrese un valor en todos los campos telefonicos !")

		return self.cleaned_data		


class EditaDescuentoAsociadoForm(forms.Form):

	descuento = forms.DecimalField(label='Porcentaje de descuento',initial=0)
	psw_paso = forms.CharField(label='psw_paso',widget=forms.PasswordInput(),max_length=3,required=True)

	def clean(self):

		cleaned_data = super(EditaDescuentoAsociadoForm,self).clean()

		descuento = self.cleaned_data.get('descuento')

		psw_paso = self.cleaned_data.get('psw_paso')

		return(self.cleaned_data)


class CreaDescuentoAsociadoForm(forms.Form):

	lprov = lista_Proveedores()

	def __init__(self,*args,**kwargs):

		
		super(CreaDescuentoAsociadoForm, self).__init__(*args,**kwargs)

	#self.fields['ProveedorNo'].widget.attrs['readonly'] = True
	
	proveedor = forms.ChoiceField(label='Proveedor',choices=lprov,initial=0)
	descuento = forms.DecimalField(label='Porcentaje de descuento',initial=0)
	psw_paso = forms.CharField(label='psw_paso',max_length=3,widget=forms.PasswordInput(),required=True)

	def clean(self):

		cleaned_data = super(CreaDescuentoAsociadoForm,self).clean()

		descuento = self.cleaned_data.get('descuento')
		psw_paso = self.cleaned_data.get('psw_paso')

		return(self.cleaned_data)


# FORMA REMISIONES ESPECIALES


class remisionesespecialesForm(forms.Form):


	
	
	def __init__(self,*args,**kwargs):


		super(remisionesespecialesForm, self).__init__(*args,**kwargs)

		lprov = lista_Sucursales()

		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		self.fields['sucursal'] = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal',choices = lprov,initial='0',required='True' )


		self.fields['fechainicial'] = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	
		self.fields['fechafinal'] = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)

		self.opciones_rpte = (('Pantalla','Pantalla',),('Archivo_Excel','Archivo_Excel',),)
		self.fields['op'] = forms.ChoiceField(label='Dirigir a:',initial='Pantalla',choices=self.opciones_rpte,required=False)
		


		t = datetime.now
		
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'campo_vacio': 'Esta omitiendo ingresar el valor de fecha en algun campo de fecha, por favor ingrese ambas fechas !',
		}

	def clean(self):

		
		cleaned_data = super(remisionesespecialesForm, self).clean()
		
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')

		op = cleaned_data.get('op')
		
		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')


# FORMA PARA EDITAR/CREAR  USUARIO

class DatosUsuarioForm(forms.Form):

	def __init__(self,*args,**kwargs):

		
		super(DatosUsuarioForm, self).__init__(*args,**kwargs)

		self.fields['usuariono'].widget.attrs['readonly'] = True


	usuariono = forms.IntegerField(label='Num. Usuario',required=False)
	nombre = forms.CharField(label='Nombre',required=True,max_length=45)	
	activo = forms.ChoiceField(widget=forms.Select(),
			label='Activo',choices =((1,'Si'),(0,'No')),required='True' )
	email = forms.EmailField(label='Email',required=True,max_length=254)
	usuario = forms.CharField(label='Usuario',required=True,max_length=15)	
	psw_paso = forms.CharField(label='psw_paso',max_length=3,widget=forms.PasswordInput(),required=True)


	def clean(self):

		cleaned_data = super(DatosUsuarioForm,self).clean()
	
		usuariono = cleaned_data.get('usuariono')
		nombre = cleaned_data.get('nombre')
		activo = cleaned_data.get('activo')
		usuario = cleaned_data.get('usuario')
		email = cleaned_data.get('email')
		psw_paso = cleaned_data.get('psw_paso')
		
		return self.cleaned_data


class DerechosFaltantesUsuarioForm(forms.Form):
	#pdb.set_trace()

	#lista_derechos = ()
	#lprov=()

	def __init__(self,*args,**kwargs):
		#pdb.set_trace()
		usr = kwargs.pop('usuariono')

		
		super(DerechosFaltantesUsuarioForm, self).__init__(*args,**kwargs)

		

		lprov = lista_derechos_no_asignados(usr)	

		#derecho = forms.ChoiceField(widget=forms.Select(),
		#		label='Derecho',choices =lprov,required='True' )
		self.fields['derecho'] = forms.ChoiceField(widget=forms.Select(),
		label='Derecho',choices = lprov,required='True' )	
 
		#usr_id = forms.IntegerField(label='usr_id',widget=forms.PasswordInput(),required=True)

	derecho = forms.ChoiceField(widget=forms.Select(),
		label='Derecho',required='True' )

	psw_paso = forms.CharField(label='psw_paso',widget=forms.PasswordInput(),max_length=3,required=True)




	def clean(self):

		cleaned_data = super(DerechosFaltantesUsuarioForm,self).clean()
	
		derecho = cleaned_data.get('derecho')
		
		psw_paso = cleaned_data.get('psw_paso')
		
		return self.cleaned_data



class EliminaUsuarioDerechoForm(forms.Form):


	psw_paso = forms.CharField(label='psw_paso',widget=forms.PasswordInput(),max_length=3,required=True)


	def clean(self):
		
		cleaned_data = super(EliminaUsuarioDerechoForm,self).clean()

		psw_paso = cleaned_data.get('psw_paso')

		return self.cleaned_data



# Datos socioweb

class DatosUsuarioWebForm(forms.Form):

	def __init__(self,*args,**kwargs):

		
		super(DatosUsuarioWebForm, self).__init__(*args,**kwargs)

		self.fields['id'].widget.attrs['readonly'] = True


	id = forms.IntegerField(label='Num. Usuario',required=False)

	is_active = forms.ChoiceField(widget=forms.Select(),
			label='Activo',choices =((1,'Si'),(0,'No')),required='True' )
	is_staff = forms.ChoiceField(widget=forms.Select(),
			label='Staff',choices =((1,'Si'),(0,'No')),required='True' )
	email = forms.EmailField(label='Email',required=True,max_length=150)
	psw_paso = forms.CharField(label='psw_paso',max_length=3,widget=forms.PasswordInput(),required=True)


	def clean(self):

		cleaned_data = super(DatosUsuarioWebForm,self).clean()
	
		id = cleaned_data.get('id')

		is_active = cleaned_data.get('is_active')
		is_staff = cleaned_data.get('is_staff')
		email = cleaned_data.get('email')
		psw_paso = cleaned_data.get('psw_paso')
		
		return self.cleaned_data




''' ***********   RPTE_STATUSXMARCA   *************'''

class RpteStatusxMarcaForm(forms.Form):

	#pdb.set_trace()
	
	lista_salida_imp =(('Pantalla','Pantalla'),('Archivo','Archivo'),)

	sucursales = {}

	sucursal = forms.ChoiceField(widget=forms.Select(),	label='Sucursal',initial=1,required='True')

	opciones_status = (('Encontrado','Encontrado',),('Por Confirmar','Por Confirmar',),('Confirmado','Confirmado',),('Aqui','Aqui',),('Cancelado','Cancelado',),('Devuelto','Devuelto',),('RecepEnDevol','RecepEnDevol',),('Dev a Prov','Dev a Prov',),('Facturado','Facturado',),('Descontinuado','Descontinuado'),('Todos','Todos',),)

	xmarca = forms.ChoiceField(widget=forms.Select(),label='Marca',initial=0,required='True')


	status = forms.ChoiceField(label='Status',initial='Por Confirmar',choices=opciones_status)

	hoy =  date.today()	
	#t = datetime.now
	f_inicial_init =  date.today()

	f_final_init = f_inicial_init + timedelta(days=30)


	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	#fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),initial=f_inicial_init.strftime('%d/%m/%Y'),required=False)
	#fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),initial=f_final_init.strftime('%d/%m/%Y'),required=False)

	fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),required=False)
	fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),required=False)

	salida_a = forms.ChoiceField(label="Enviar a",widget=forms.Select(),choices=lista_salida_imp,initial='Pantalla',required=True)
 

	error_messages = {'FechaInicial':'Ingrese una fecha inicial !',
					'FechaFinal':'Ingrese una fecha final !',
					'FechIniMayor':'La fecha final debe ser mayor o igual a la fecha inicial !',
					}


		
	def __init__(self,*args,**kwargs):

		
		
		lprov = lista_Sucursales()
		lmar =lista_Proveedores()

		super(RpteStatusxMarcaForm, self).__init__(*args,**kwargs)
		self.fields['sucursal'] = forms.ChoiceField(widget=forms.Select(),
			label='Sucursal',choices = lprov,initial=1,required='True' )
		
		self.fields['xmarca'] = forms.ChoiceField(widget=forms.Select(),
			label='Marca',choices = lmar,initial=0,required='True' )
			



	"""def clean_sucursal(self):

		cleaned_data = super(Entrada_sistemaForm, self).clean()
		sucursal = self.cleaned_data.get('sucursal')

		if sucursal=='0':
			raise forms.ValidationError("Seleccione una sucursal en particular !")
		
		return sucursal"""


	def clean(self):
		
		cleaned_data = super(RpteStatusxMarcaForm, self).clean()

		sucursal = self.cleaned_data.get('sucursal')
		status = self.cleaned_data.get('status')
		xmarca = self.cleaned_data.get('xmarca')

		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		
		

		'''if sucursal =='0':
			raise  forms.ValidationError(self.error_messages['CombinacionSucursalInvalida'],code='CombinacionSucursalInvalida')'''

			
		if not(fechainicial and fechafinal):

			if not fechainicial:
				raise  forms.ValidationError(self.error_messages['FechaInicial'],code='FechaInicial')
			if not fechafinal:
				raise forms.ValidationError(self.error_messages['FechaFinal'],code='FechaFinal')
			
		else:
			if fechainicial > fechafinal:
				raise forms.ValidationError(self.error_messages['FechIniMayor'],code='FechIniMayor')
			
		# De otra manera, quiere decir que el socio es cero y quien tiene un valor es
		# el numero de documento, siendo este el caso no hay ya validacion.

		return self.cleaned_data




#  FORMA PARA SELECCIONAR USUARIO Y DERECHO PARA REPORTE DE ACTIVIDAD


class UsuarioLogForm(forms.Form):

	usuarios = {}

	derechos = {}

	
	def __init__(self,*args,**kwargs):

		lusuarios =lista_usuarios()
		lderechos =lista_derechos()
		lista_salida_imp =(('Pantalla','Pantalla'),('Archivo','Archivo'),)


		super(UsuarioLogForm, self).__init__(*args,**kwargs)
		

		DateInput = partial(forms.DateInput, {'class': 'datepicker'})


		self.fields['usuario'] = forms.ChoiceField(widget=forms.Select(),
			label='Usuario',choices = lusuarios,initial=0,required='True' )

		self.fields['derecho'] = forms.ChoiceField(widget=forms.Select(),
			label='Derecho',choices = lderechos,initial=0,required='True' )

		self.fields['fechainicial'] = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	
		self.fields['fechafinal'] = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
		
		self.fields['salida_a'] = forms.ChoiceField(label="Enviar a",widget=forms.Select(),choices=lista_salida_imp,initial='Pantalla',required=True)


		t = datetime.now
		
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'campo_vacio': 'Esta omitiendo ingresar el valor de fecha en algun campo de fecha, por favor ingrese ambas fechas !',
	'error_sucursal': 'Seleccione un proveedor..!',
	'error_porcentaje': 'Seleccione el porcentaje sobre la venta neta que se otorgara como bono',
	}

	def clean(self):

		
		cleaned_data = super(UsuarioLogForm, self).clean()
		
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		usuario = cleaned_data.get('usuario')
		derecho = cleaned_data.get('derecho')
		salida_a = cleaned_data.get('salida_a')

		print "fechas aqui:"
		print fechainicial
		print fechafinal

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
		'''if proveedor < '1':

			raise forms.ValidationError(self.error_messages['error_proveedor'],code='error_proveedor')'''

		

		return self.cleaned_data

class UploadFileForm(forms.Form):
	#pdb.set_trace()
	

	def __init__(self,*args,**kwargs):

		opcion_temporada = (('0','Seleccione...'),('1','Primavera/Verano'),('2','Oto??o/Invierno'))
		
		lprov = lista_Proveedores()

		super(UploadFileForm, self).__init__(*args,**kwargs)
		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(attrs={'id':'id_prov_importar'}),
			label='Proveedor',choices = lprov,required='True')
		self.fields['temporada'] = forms.ChoiceField(widget=forms.Select(attrs={'id':'id_temp_importar'}),label='Temporada',choices=opcion_temporada,required='True',initial='0')
		print "temporada:"
		print self.fields['temporada']


		#lcat = lista_Catalogos(self.proveedor,self.temporada)
		#self.fields['catalogo'] = forms.CharField(max_length=12,required='True',initial='2020ij')
		self.fields['catalogo'] = forms.CharField(max_length=12,label='Catalogo',required='True')

		'''widget=forms.TextInput(attrs={'placeholder':"AAAATTTTTTTT (Primeros 4 digitos para el a??o, 8 restantes para texto)"})''',
		self.fields['file']= forms.FileField()
		


	error_messages = {
	
	'error_cero_proveedor': 'Seleccione un proveedor !',
	'error_cero_temporada': 'Seleccione una temporada !',
	'error_diagonal_no_permitido': 'No se permiten diagonales (/) en el campo "catalogo", use gui??n bajo o gui??n medio en su lugar !',

	}

	def clean(self):
		#pdb.set_trace()
		cleaned_data = super(UploadFileForm, self).clean()
		
		proveedor = self.cleaned_data.get('proveedor')
		temporada = self.cleaned_data.get('temporada')
		catalogo = self.cleaned_data.get('catalogo')
		file = self.cleaned_data.get('file')

		'''
		if catalogo is not None:

			if '/' in catalogo:

				raise forms.ValidationError(self.error_messages['error_diagonal_no_permitido'],code='error_diagonal_no_permitido')
		'''	

		if proveedor == '0':

			raise forms.ValidationError(self.error_messages['error_cero_proveedor'],code='error_cero_proveedor')
		
		if temporada == '0':

			raise forms.ValidationError(self.error_messages['error_cero_temporada'],code='error_cero_temporada')


		return self.cleaned_data



''' ***********   RPTE_VTACATALOGO POR SOCIO   *************'''

class RpteVtaCatXSocioForm(forms.Form):

	#pdb.set_trace()
	

	hoy =  date.today()	
	#t = datetime.now
	f_inicial_init =  date.today()

	f_final_init = f_inicial_init + timedelta(days=30)


	socioinicial = forms.IntegerField(label='Socio inicial',initial=1,required=True)
	sociofinal = forms.IntegerField(label='Socion final',initial=999999,required=True)




	# Prepara el campo para utilizar datepicker
	DateInput = partial(forms.DateInput, {'class': 'datepicker'})

	#fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),initial=f_inicial_init.strftime('%d/%m/%Y'),required=False)
	#fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),initial=f_final_init.strftime('%d/%m/%Y'),required=False)

	fechainicial = forms.DateField(label='Fecha inicial(dd/mm/yyyy)',widget=DateInput(),required=False)
	fechafinal = forms.DateField(label='Fecha final (dd/mm/yyyy)',widget=DateInput(),required=False)

 

	error_messages = {'FechaInicial':'Ingrese una fecha inicial !',
					'FechaFinal':'Ingrese una fecha final !',
					'FechIniMayor':'La fecha final debe ser mayor o igual a la fecha inicial !',
					'SocioFinal':'Socio final no puede ser menor que el socio inicial !'
					}

	def __init__(self,*args,**kwargs):

		lista_salida_imp =(('Pantalla','Pantalla'),('Archivo','Archivo'),)

		lmar=lista_Proveedores()	
		super(RpteVtaCatXSocioForm, self).__init__(*args,**kwargs)	

		# Se define la marca pero se pone un id cualquiera para que no reaccione a jquery ya que el default es id_marca y se habilita en jquery.
		self.fields['marca'] = forms.ChoiceField(widget=forms.Select(attrs={'id':'id_cualquiera',}),
			label='Marca (seleccione una o se incluir??n todas)',choices = lmar,initial=0,required='True' )
	
		self.fields['salida_a'] = forms.ChoiceField(label="Enviar a",widget=forms.Select(),choices=lista_salida_imp,initial='Pantalla',required=True)
			

	def clean(self):
		
		cleaned_data = super(RpteVtaCatXSocioForm, self).clean()
		
		fechainicial = self.cleaned_data.get('fechainicial')
		fechafinal = self.cleaned_data.get('fechafinal')
		socioinicial= self.cleaned_data.get('socioinicial')
		sociofinal = self.cleaned_data.get('sociofinal')
		marca = self.cleaned_data.get('marca')		
		salida_a = self.cleaned_data.get('salida_a')

		'''if sucursal =='0':
			raise  forms.ValidationError(self.error_messages['CombinacionSucursalInvalida'],code='CombinacionSucursalInvalida')'''

		''' Se valida socioinicial vs socio final'''

		if socioinicial > sociofinal:
			raise  forms.ValidationError(self.error_messages['SocioFinal'],code='SocioFinal')

			
		if not(fechainicial and fechafinal):

			if not fechainicial:
				raise  forms.ValidationError(self.error_messages['FechaInicial'],code='FechaInicial')
			if not fechafinal:
				raise forms.ValidationError(self.error_messages['FechaFinal'],code='FechaFinal')
			
		else:
			if fechainicial > fechafinal:
				raise forms.ValidationError(self.error_messages['FechIniMayor'],code='FechIniMayor')
			
		# De otra manera, quiere decir que el socio es cero y quien tiene un valor es
		# el numero de documento, siendo este el caso no hay ya validacion.

		return self.cleaned_data



class RpteVtaNetaSocioGralForm(forms.Form):

	proveedores = {}

	

	
	def __init__(self,*args,**kwargs):

		lprov =lista_Proveedores()

		super(RpteVtaNetaSocioGralForm, self).__init__(*args,**kwargs)
		

		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		self.fields['fechainicial'] = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)
	
		self.fields['fechafinal'] = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)

		'''self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
			label='Proveedor',choices = lprov,initial=0,required='True' )'''

		
		'''error_messages = {
		
		'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
		'Error_en_Fecha': 'Existe un error en el valor de la fecha !',
		}'''


		t = datetime.now
		#t.strftime('%m/%d/%Y')

		'''tipoconsulta  = forms.ChoiceField(widget=forms.Select(),
				label='Tipo de Consulta',choices = opcion_consulta,initial='1',required='True' )
		# Prepara el campo para utilizar datepicker
		DateInput = partial(forms.DateInput, {'class': 'datepicker'})

		
		fechainicial = forms.DateField(label='Fecha inicial (dd/mm/yyyy)',widget=DateInput(),)
		fechafinal = forms.DateField(label = 'Fecha final (dd/mm/yyyy)',widget=DateInput(),)'''
		
	error_messages = {
	
	'error_fechafinal': 'La fecha final debe ser mayor o igual a la fecha inicial !',
	'campo_vacio': 'Esta omitiendo ingresar el valor de fecha en algun campo de fecha, por favor ingrese ambas fechas !',
	'error_porcentaje': 'Seleccione el porcentaje sobre la venta neta que se otorgara como bono',
	}

	def clean(self):

		
		cleaned_data = super(RpteVtaNetaSocioGralForm, self).clean()
		
		fechainicial = cleaned_data.get('fechainicial')
		fechafinal = cleaned_data.get('fechafinal')
		'''proveedor = cleaned_data.get('proveedor')'''
	

		print "fechas aqui:"
		print fechainicial
		print fechafinal

		if fechainicial is not None and fechafinal is not None:
			
			if (fechainicial > fechafinal):
				
				raise forms.ValidationError(self.error_messages['error_fechafinal'],code='error_fechafinal')
		else:
				raise forms.ValidationError(self.error_messages['campo_vacio'],code='campo_vacio')
		'''if proveedor < '1':

			raise forms.ValidationError(self.error_messages['error_proveedor'],code='error_proveedor')'''

		

		return self.cleaned_data

class TraeSocioForm(forms.Form):

	socio = forms.IntegerField(label='Numero de socio',initial=0)
	
	def clean(self):

		cleaned_data = super( TraeSocioForm,self).clean()

		socio = self.cleaned_data.get('socio')

	

		return(self.cleaned_data)


# DATOS EMPRESA FORM

class DatosEmpresaForm(forms.Form):

	def __init__(self,*args,**kwargs):

		
		super(DatosEmpresaForm, self).__init__(*args,**kwargs)

		def genera_tupla_anios():
			li =[]
			le =[]
			for j in range(2010,2050):

				for z in range(1,2):
					li.append(j)
					li.append(j)
				li=tuple(li)
				le.append(li)
				li=[]
			le=tuple(le)
			return(le)	

		l = genera_tupla_anios()	


		self.fields['EmpresaNo'].widget.attrs['readonly'] = True
		self.fields['EjercicioVigente'] = forms.ChoiceField(widget=forms.Select(),
		label='Ejercicio',choices = l,required='True' )
					

	EmpresaNo = forms.IntegerField(label='Empresa Num.',required=True,initial=1)
	EjercicioVigente = forms.ChoiceField(widget=forms.Select(),
			label='Ejercicio',required='True' )

	PeriodoVigente = forms.ChoiceField(label='Temporada',choices=((1,'Primavera/Verano'),(2,'Oto??o/Invierno')),initial=1,required=True)
		
	RazonSocial =forms.CharField(label='Raz??n Social',max_length=45,required=True)
	Direccion =forms.CharField(label='Direcci??n',max_length=45,required=True)
	Colonia=forms.CharField(label='Colonia',max_length=45,required=True)
	Ciudad =forms.CharField(label='Ciuidad',max_length=45,required=True)
	Estado =forms.CharField(label='Estado',max_length=45,required=True)
	CodigoPostal = forms.IntegerField(label='C??digo Postal',required=True)
	Telefono = forms.CharField(label='Tel??fono',max_length=15, required=True)
	rfc = forms.CharField(label='RFC',max_length=16,required=True)
	buzonelectronico = forms.EmailField(label='Direcci??n email',max_length=100, required=True)
	iva = forms.FloatField(label='IVA %',required=True)
	porcentajeanticipo =forms.FloatField(label='Anticipo %',required=True)
	diasextemporaniedad = forms.IntegerField(label='Dias de gracia para recoger el producto una vez que arrib?? a la tienda',required=True)
	cuotadiasextemp = forms.FloatField(label='Cuota a cobrar si no se recoje el producto durante los dias de gracia',required=True)
	diasvigenciacredito = forms.IntegerField(label='Dias de gracia que se la dar??n a los cr??ditos para poder ser aplicados',required=True)
	comisionxcalzadonorecogido = forms.FloatField(label='Comisi??n a cobrar por producto recepcionado "Aqu??" y que nunca fu?? recogido',required=True)
	diasPlazoVmtoAquiSocioConCred = forms.IntegerField(label='Dias de plazo de vencimiento para socios que tengan al menos un cr??dito pendiente',required=True)
	diasPlazoVmtoAquiSocioSinCred = forms.IntegerField(label='Dias de plazo de vencimiento para socios que no tienen creditos pendientes',required=True)
	psw_paso = forms.CharField(label='psw_paso',max_length=3,widget=forms.PasswordInput(),required=True)


	error_messages = {'error_clase':'Los primeros 4 digitos del catalogo son para el a??o y debe ser un valor mayor al 2020 !',}
					



	def clean(self):

		cleaned_data = super(DatosEmpresaForm,self).clean()
	
		EmpresaNo = cleaned_data.get('EmpresaNo')
		EjercicioVigente = cleaned_data.get('EjercicioVigente')
		PeriodoVigente = cleaned_data.get('PeriodoVigente')
		RazonSocial = cleaned_data.get('RazonSocial')
		Direccion = cleaned_data.get('Direccion')
		Colonia = cleaned_data.get('Colonia')
		Ciudad = cleaned_data.get('Ciudad')
		Estado = cleaned_data.get('Estado')
		CodigoPostal = cleaned_data.get('CodigoPostal')
		Telefono = cleaned_data.get('Telefono')
		rfc = cleaned_data.get('rfc')
		buzonelectronico = cleaned_data.get('buzonelectronico')
		iva = cleaned_data.get('iva')
		porcentajeanticipo = cleaned_data.get('porcentajeanticipo')
		diasextemporaniedad = cleaned_data.get('diasextemporaniedad')
		cuotadiasextemp = cleaned_data.get('cuotadiasextemp')
		diasvigenciacredito = cleaned_data.get('diasvigenciacredito')
		comisionxcalzadonorecogido = cleaned_data.get('Comisionxcalzadonorecogido')	
		diasPlazoVmtoAquiSocioConCred = cleaned_data.get('diasPlazoVmtoAquiSocioConCred')
		diasPlazoVmtoAquiSocioSinCred = cleaned_data.get('diasPlazoVmtoAquiSocioSinCred')
		psw_paso = cleaned_data.get('psw_paso')

		return self.cleaned_data


# FORMA PARA DAR DE ALTA UN ARTICULO


class ChoiceFieldNoValidation(forms.ChoiceField):
	def validate(self, value):
		pass



class ArticuloForm(forms.Form):

	proveedores = {}
	

	# La funcion siguiente "init" tambien  recibe el parametro
	# request, esto se hace para tener tambien disponibles las variables de entorno, en este caso
	# se requerira el request.session['is_staff'] para manejarlos en los campos
	# de fechaMaximaEntrega y el de periodo de entrega.
	# en el views.py los llamados deben inculir request como parametro tanto si la forma es valida como si no lo es.
	def __init__(self,*args,**kwargs):


		
		def lista_PeriodosEntrega():
			cursor=connection.cursor()
			cursor.execute('SELECT id,periodo from periodosentrega;')
	
			pr=() # Inicializa una tupla para llenar combo de Periodosentrega
			
			# Convierte el diccionario en tupla
			for row in cursor:
				elemento = tuple(row)
				pr=pr+elemento
			pr = (0L,u'SELECCIONE...') + pr
			

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
			lper_ent = tuple(tuple(x) for x in y)

			
			
			return (lper_ent)

		
		
		lprov = lista_Proveedores()
		lcat = (('0','Seleccione'),)
		lestilo = []
		lmarca = []
		lcolor = []
		ltalla = []
		lper_ent = lista_PeriodosEntrega()
		

		opcion_temporada = (('0','SELECCIONE...'),('1','Primavera/Verano'),('2','Oto??o/Invierno'))
		opcion_opt = (('1','1ra.'),('2','2da'),('3','3ra.'))


		super(ArticuloForm, self).__init__(*args,**kwargs)
		
			
		self.fields['proveedor'] = forms.ChoiceField(widget=forms.Select(),
		label='Proveedor',choices = lprov,initial='0',required='True' )

		self.fields['temporada'] = forms.ChoiceField(widget=forms.Select(),
		label='Temporada',choices = opcion_temporada, initial='0',required ='True')

		self.fields['catalogo']  = ChoiceFieldNoValidation(widget=forms.Select(),
		label='Catalogo',required ='True' )

				
		self.fields['pagina'] = forms.CharField(label='Pagina')
		
		self.fields['estilo'] = ChoiceFieldNoValidation(widget=forms.Select(),
		label='Estilo',initial='Seleccione',required='True')
		
		self.fields['marca'] = ChoiceFieldNoValidation(widget = forms.Select(),
		label='Marca',initial='Seleccione',required='True')

		self.fields['color'] = ChoiceFieldNoValidation(widget = forms.Select(),
		label='Color', initial='Seleccione',required='True')
		
		self.fields['talla'] = ChoiceFieldNoValidation(widget = forms.Select(),
		label='Talla',initial='Seleccione',required='True')

		#self.fields['precio'] = forms.FloatField(label = 'Precio cliente:',initial=0.0,widget=forms.NumberInput(attrs={'style':'display: none;'}))
		self.fields['precio'] = forms.FloatField(label = 'Precio',initial=0.0, required='True')
	  	
	productono = forms.CharField(label='Codigo articulo',initial='AUTOMATICO',required=False )
	proveedor = forms.ChoiceField(widget=forms.Select(),
		label='Proveedor',initial='0',required='True' )

	temporada = forms.ChoiceField(widget=forms.Select(),
		label='Temporada',initial='0',required ='True')
		
	catalogo  = ChoiceFieldNoValidation(widget=forms.Select(),
		label='Catalogo',initial='SELECCIONE...',required ='True' )

	pagina = forms.CharField(label='Pagina')
		
	estilo = ChoiceFieldNoValidation(widget=forms.Select(),
		label='Estilo',initial='Seleccione',required='True')
		
	marca = ChoiceFieldNoValidation(widget = forms.Select(),
		label='Marca',initial='Seleccione',required='True')

	color = ChoiceFieldNoValidation(widget = forms.Select(),
		label='Color', initial='Seleccione',required='True')
		
	talla = ChoiceFieldNoValidation(widget = forms.Select(),
		label='Talla',initial='Seleccione',required='True')


	
	precio = forms.FloatField(label='Precio',initial=0.0)

	error_messages = {'error_productono':'No se permiten caracteres especiales en el c??digo !',
	'error_precio':'Ingrese un precio !',
	'error_estilo':'Seleccione un estilo !',
	'error_pagina':'Ingrese un numero de pagina !',
	'error_catalogo':'Seleccione un cat??logo !',
	'error_talla':'Seleccione una talla !',
	'error_color':'Seleccione un color !',
	'error_marca':'Seleccione una marca !',
	'error_productono':'No se permiten caracteres especiales en el c??digo !'}


	def validate(self):

		catalogo= self.cleaned_data['catalogo',True]
		if "SELECCIONE..." in catalogo:
			raise ValidationError("Seleccione un catalogo !")
		else:
			pass

		# Always return a value to use as the new cleaned data, even if
		# this method didn't change it.
		return catalogo


  	def clean(self):

		cleaned_data = super(ArticuloForm, self).clean()

		productono = cleaned_data.get('productono')
		proveedor = cleaned_data.get('proveedor')
		temporada = cleaned_data.get('temporada')
		catalogo = cleaned_data.get('catalogo')
		pagina = cleaned_data.get('pagina')
		estilo = cleaned_data.get('estilo')
		marca = cleaned_data.get('marca')
		color = cleaned_data.get('color')
		talla = cleaned_data.get('talla')
		precio = cleaned_data.get('precio')	
		
		if precio ==0 or catalgo.strip()=="" or pagina.strip()=="" or estilo.strip()=="" or marca.strip()=="" or color.strip()=="" or talla.strip()=="":
			raise forms.ValidationError("Por favor llene todos los campos del formulario !")

		if not es_alfanumerica(productono):
			
			raise forms.ValidationError(self.error_messages['error_productono'],code='error_productono')
		if precio <= 0:
			raise forms.ValidationError(self.error_messages['error_precio'],code='error_precio')
		if catalogo.strip() == 'SELECCIONE...' or catalogo.strip()=="":
			raise forms.ValidationError(self.error_messages['error_catalogo'],code='error_catalogo')
		if pagina.strip() == '0' or pagina.strip()=="":
			raise forms.ValidationError(self.error_messages['error_pagina'],code='error_pagina')
		if estilo.strip() == 'SELECCIONE...' or estilo.strip()=="":
			raise forms.ValidationError(self.error_messages['error_estilo'],code='error_estilo')
		if marca.strip() == 'SELECCIONE...' or marca.strip()=="":
			raise forms.ValidationError(self.error_messages['error_marca'],code='error_marca')			
		if color.strip() == 'SELECCIONE...' or color.strip()=="":
			raise forms.ValidationError(self.error_messages['error_color'],code='error_color')
		if talla.strip() == 'SELECCIONE...' or talla.strip()=="":
			raise forms.ValidationError(self.error_messages['error_talla'],code='error_talla')

		return self.cleaned_data

	


def es_alfanumerica(p_entrada):

	'''valida que p_entrada sea alfanumerico,
	retorna Falso si no es y Verdadero si si es'''
	try:
		result=re.match(r'^[a-zA-Z0-9]{4,10}$',p_entrada)
		if result is None:
			raise TypeError
		else:
			return True

	except TypeError:
		return False