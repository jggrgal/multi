# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class AbonosRemisiones(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    nodocto = models.IntegerField(db_column='NoDocto')  # Field name made lowercase.
    noremision = models.IntegerField(db_column='NoRemision')  # Field name made lowercase.
    fecha = models.DateField(db_column='Fecha')  # Field name made lowercase.
    hora = models.TimeField(db_column='Hora')  # Field name made lowercase.
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'abonos_remisiones'
        unique_together = ['empresano', 'nodocto', 'noremision']


class Acabados(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    proveedorno = models.IntegerField(db_column='ProveedorNo')  # Field name made lowercase.
    idacabados = models.CharField(db_column='idAcabados', max_length=40)  # Field name made lowercase.
    fechaalta = models.DateField(db_column='FechaAlta', blank=True, null=True)  # Field name made lowercase.
    fechabaja = models.DateField(db_column='FechaBaja', blank=True, null=True)  # Field name made lowercase.
    horaalta = models.TimeField(db_column='HoraAlta', blank=True, null=True)  # Field name made lowercase.
    horabaja = models.TimeField(db_column='HoraBaja', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'acabados'
        unique_together = ['empresano', 'proveedorno', 'idacabados']


class Almacen(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    proveedorno = models.IntegerField(db_column='ProveedorNo')  # Field name made lowercase.
    almacen = models.SmallIntegerField(db_column='Almacen')  # Field name made lowercase.
    razonsocial = models.CharField(db_column='RazonSocial', max_length=45, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=45, blank=True, null=True)  # Field name made lowercase.
    colonia = models.CharField(db_column='Colonia', max_length=45, blank=True, null=True)  # Field name made lowercase.
    ciudad = models.CharField(db_column='Ciudad', max_length=45, blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(db_column='Estado', max_length=45, blank=True, null=True)  # Field name made lowercase.
    pais = models.CharField(db_column='Pais', max_length=45, blank=True, null=True)  # Field name made lowercase.
    telefono1 = models.CharField(db_column='Telefono1', max_length=15)  # Field name made lowercase.
    telefono2 = models.CharField(db_column='Telefono2', max_length=15)  # Field name made lowercase.
    fax = models.CharField(db_column='Fax', max_length=15, blank=True, null=True)  # Field name made lowercase.
    celular = models.CharField(db_column='Celular', max_length=15, blank=True, null=True)  # Field name made lowercase.
    radio = models.CharField(db_column='Radio', max_length=15, blank=True, null=True)  # Field name made lowercase.
    direccionelectronica = models.CharField(db_column='DireccionElectronica', max_length=100, blank=True, null=True)  # Field name made lowercase.
    fechaalta = models.DateField(db_column='FechaAlta')  # Field name made lowercase.
    fechabaja = models.DateField(db_column='FechaBaja')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'almacen'
        unique_together = ['empresano', 'proveedorno', 'almacen']


class Articulo(models.Model):
    empresano = models.ForeignKey('Proveedor',related_name="fk_pro_emp", db_column='EmpresaNo')  # Field name made lowercase.
    codigoarticulo = models.CharField(primary_key='True',db_column='CodigoArticulo', max_length=16)  # Field name made lowercase.
    fechaalta = models.DateField(db_column='FechaAlta')  # Field name made lowercase.
    fechabaja = models.DateField(db_column='FechaBaja')  # Field name made lowercase.
    pagina = models.CharField(max_length=6, blank=True, null=True)
    pathfoto = models.CharField(db_column='PathFoto', max_length=150, blank=True, null=True)  # Field name made lowercase.
    idproveedor = models.ForeignKey('Proveedor',related_name="fk_prov_idprov", db_column='idProveedor')  # Field name made lowercase.
    idmarca = models.CharField(db_column='idMarca', max_length=40)  # Field name made lowercase.
    idestilo = models.CharField(db_column='idEstilo', max_length=40)  # Field name made lowercase.
    idcolor = models.CharField(db_column='idColor', max_length=40)  # Field name made lowercase.
    idacabado = models.CharField(db_column='idAcabado', max_length=40)  # Field name made lowercase.
    idmodelo = models.CharField(db_column='idModelo', max_length=40)  # Field name made lowercase.
    talla = models.CharField(max_length=12, blank=True, null=True)
    precio = models.FloatField(blank=True, null=True)
    catalogo = models.CharField(db_column='Catalogo', max_length=12)  # Field name made lowercase.
    costo = models.FloatField(blank=True, null=True)

    def __str__(self):
        return(self.codigoarticulo)





    class Meta:
        managed = False
        db_table = 'articulo'
        unique_together = ['empresano', 'codigoarticulo', 'catalogo']
        

class Asociado(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    asociadono = models.IntegerField(db_column='AsociadoNo')  # Field name made lowercase.
    razonsocial = models.CharField(db_column='RazonSocial', max_length=45, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=30, blank=True, null=True)  # Field name made lowercase.
    appaterno = models.CharField(db_column='ApPaterno', max_length=30, blank=True, null=True)  # Field name made lowercase.
    apmaterno = models.CharField(db_column='ApMaterno', max_length=30, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=45, blank=True, null=True)  # Field name made lowercase.
    colonia = models.CharField(db_column='Colonia', max_length=45, blank=True, null=True)  # Field name made lowercase.
    ciudad = models.CharField(db_column='Ciudad', max_length=45, blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(db_column='Estado', max_length=45, blank=True, null=True)  # Field name made lowercase.
    pais = models.CharField(db_column='Pais', max_length=45, blank=True, null=True)  # Field name made lowercase.
    telefono1 = models.CharField(max_length=15, blank=True, null=True)
    telefono2 = models.CharField(max_length=15, blank=True, null=True)
    fax = models.CharField(max_length=15, blank=True, null=True)
    celular = models.CharField(max_length=15, blank=True, null=True)
    radio = models.CharField(db_column='Radio', max_length=15, blank=True, null=True)  # Field name made lowercase.
    direccionelectronica = models.CharField(db_column='DireccionElectronica', max_length=100, blank=True, null=True)  # Field name made lowercase.
    fechaalta = models.DateField(db_column='FechaAlta')  # Field name made lowercase.
    fechabaja = models.DateField(db_column='FechaBaja')  # Field name made lowercase.
    pathfoto = models.CharField(db_column='PathFoto', max_length=150, blank=True, null=True)  # Field name made lowercase.
    sucursalno = models.SmallIntegerField(db_column='SucursalNo')  # Field name made lowercase.
    creditodisponible = models.FloatField(db_column='CreditoDisponible', blank=True, null=True)  # Field name made lowercase.
    nocontrol = models.CharField(db_column='NoControl', max_length=12, blank=True, null=True)  # Field name made lowercase.
    essocio = models.IntegerField(db_column='EsSocio')  # Field name made lowercase.
    forzarcobroanticipo = models.IntegerField(db_column='ForzarCobroAnticipo')  # Field name made lowercase.
    num_web = models.SmallIntegerField(db_column='Num_Web')
    
    class Meta:
        managed = False
        db_table = 'asociado'
        unique_together = ['empresano', 'asociadono']

    def __str__(self):              # __unicode__ on Python 2
        return self.nombre


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = ['group', 'permission']


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = ['content_type', 'codename']


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = ['user', 'group']


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = ['user', 'permission']


class Catalogostatuspedidos(models.Model):
    status = models.CharField(db_column='Status', primary_key=True, max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'catalogostatuspedidos'


class Catalogostemporada(models.Model):
    proveedorno = models.IntegerField(db_column='ProveedorNo')  # Field name made lowercase.
    periodo = models.SmallIntegerField(db_column='Periodo')  # Field name made lowercase.
    anio = models.SmallIntegerField(db_column='Anio')  # Field name made lowercase.
    clasearticulo = models.CharField(db_column='ClaseArticulo', max_length=12)  # Field name made lowercase.
    activo = models.TextField(db_column='Activo')  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = False
        db_table = 'catalogostemporada'
        unique_together = ['proveedorno', 'periodo', 'anio', 'clasearticulo']


class Causasdevoluciones(models.Model):
    causa = models.CharField(db_column='Causa', primary_key=True, max_length=25)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'causasdevoluciones'

class Comprasdetalle(models.Model):
    empresano = models.ForeignKey('Comprasencab',related_name="fk_empresa", db_column='EmpresaNo')  # Field name made lowercase.
    proveedorno = models.ForeignKey('Comprasencab',related_name="fk_compencab_provee", db_column='ProveedorNo')  # Field name made lowercase.
    numalmacen = models.ForeignKey('Comprasencab',related_name="fk_almacen", db_column='NumAlmacen')  # Field name made lowercase.
    requisicionno = models.ForeignKey('Comprasencab',related_name="fk_compencab_requisicion", db_column='RequisicionNo')  # Field name made lowercase.
    codigoarticulo = models.CharField(db_column='CodigoArticulo', max_length=16)  # Field name made lowercase.
    cantidadsolicitada = models.IntegerField(db_column='CantidadSolicitada')  # Field name made lowercase.
    costo = models.DecimalField(db_column='Costo', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    pedidono = models.IntegerField(db_column='PedidoNo')  # Field name made lowercase.
    catalogo = models.CharField(max_length=12)
    nolinea = models.IntegerField(db_column='NoLinea')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'comprasdetalle'
        unique_together = ['empresano', 'proveedorno', 'numalmacen', 'requisicionno', 'pedidono', 'codigoarticulo', 'catalogo', 'nolinea']


class Comprasencab(models.Model):
    empresano = models.SmallIntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    proveedor = models.IntegerField(db_column='Proveedor')  # Field name made lowercase.
    almacen = models.SmallIntegerField(db_column='Almacen')  # Field name made lowercase.
    requisicionno = models.CharField(db_column='RequisicionNO', max_length=15)  # Field name made lowercase.
    fechacreacion = models.DateField(db_column='FechaCreacion', blank=True, null=True)  # Field name made lowercase.
    fechauitimamodificacion = models.DateField(db_column='FechaUItimaModificacion', blank=True, null=True)  # Field name made lowercase.
    horacraacion = models.TimeField(db_column='HoraCraacion')  # Field name made lowercase.
    horaultimamodificacion = models.TimeField(db_column='HoraUltimaModificacion')  # Field name made lowercase.
    usuariocreo = models.SmallIntegerField(db_column='UsuarioCreo')  # Field name made lowercase.
    usuariomodifico = models.SmallIntegerField(db_column='UsuarioModifico')  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'comprasencab'
        unique_together = ['empresano', 'proveedor', 'almacen', 'requisicionno']


class Configuracion(models.Model):
    empresano = models.SmallIntegerField(db_column='EmpresaNo', primary_key=True)  # Field name made lowercase.
    ejerciciovigente = models.SmallIntegerField(db_column='EjercicioVigente')  # Field name made lowercase.
    periodovigente = models.SmallIntegerField(db_column='PeriodoVigente')  # Field name made lowercase.
    razonsocial = models.CharField(db_column='RazonSocial', max_length=45)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=45)  # Field name made lowercase.
    colonia = models.CharField(db_column='Colonia', max_length=45)  # Field name made lowercase.
    ciudad = models.CharField(db_column='Ciudad', max_length=45)  # Field name made lowercase.
    estado = models.CharField(db_column='Estado', max_length=45)  # Field name made lowercase.
    pais = models.CharField(db_column='Pais', max_length=45)  # Field name made lowercase.
    codigopostal = models.IntegerField(db_column='CodigoPostal')  # Field name made lowercase.
    telefono = models.CharField(db_column='Telefono', max_length=15)  # Field name made lowercase.
    rfc = models.CharField(db_column='RFC', max_length=16)  # Field name made lowercase.
    buzonelectronico = models.CharField(db_column='BuzonElectronico', max_length=100)  # Field name made lowercase.
    iva = models.FloatField(db_column='Iva')  # Field name made lowercase.
    porcentajeanticipo = models.FloatField(db_column='PorcentajeAnticipo')  # Field name made lowercase.
    tiposervidor = models.CharField(db_column='TipoServidor', max_length=1)  # Field name made lowercase.
    servidor = models.CharField(max_length=50)
    usuario = models.CharField(max_length=50)
    contrasena = models.CharField(max_length=50)
    maxdiasextemp = models.SmallIntegerField(db_column='MaxDiasExtemp')  # Field name made lowercase.
    cuotadiasextemp = models.FloatField(db_column='CuotaDiasExtemp')  # Field name made lowercase.
    diasvigenciacredito = models.SmallIntegerField(db_column='DiasVigenciaCredito')  # Field name made lowercase.
    comisionporcalzadonorecogido = models.FloatField(db_column='ComisionPorCalzadoNoRecogido')  # Field name made lowercase.
    diasplazovmtoaquisocioconcred = models.SmallIntegerField(db_column='DiasPlazoVmtoAquiSocioConCred')  # Field name made lowercase.
    diasplazovmtoaquisociosincred = models.SmallIntegerField(db_column='DiasPlazoVmtoAquiSocioSinCred')  # Field name made lowercase.
    mostrarsocioenticket = models.TextField(db_column='MostrarSocioEnTicket', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
   
    class Meta:
        managed = False
        db_table = 'configuracion'


class Creditoaplicado(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    nodocto = models.IntegerField(db_column='NoDocto')  # Field name made lowercase.
    tipodedocumento = models.CharField(db_column='TipoDeDocumento', max_length=12, blank=True, null=True)  # Field name made lowercase.
    fechacreacion = models.DateField(db_column='FechaCreacion')  # Field name made lowercase.
    horacreacion = models.TimeField(db_column='HoraCreacion')  # Field name made lowercase.
    fechaultimamodificacion = models.DateField(db_column='FechaUltimaModificacion')  # Field name made lowercase.
    horaultimamodificacion = models.TimeField(db_column='HoraUltimaModificacion')  # Field name made lowercase.
    monto = models.DecimalField(db_column='Monto', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'creditoaplicado'
        unique_together = ['empresano', 'nodocto']


class Derechos(models.Model):
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=45)  # Field name made lowercase.
    fechaalta = models.DateField(db_column='FechaAlta')  # Field name made lowercase.
    fechabaja = models.DateField(db_column='FechaBaja')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'derechos'


class Devolucionesaprovheader(models.Model):
    empresano = models.SmallIntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    pedidono = models.IntegerField(db_column='PedidoNo')  # Field name made lowercase.
    almacen = models.IntegerField(db_column='Almacen')  # Field name made lowercase.
    fecha = models.DateField(db_column='Fecha')  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=10, decimal_places=2)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'devolucionesaprovheader'
        unique_together = ['empresano', 'pedidono']


class Devolucionesaprovlines(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    devolucionno = models.IntegerField(db_column='DevolucionNo')  # Field name made lowercase.
    pedido = models.IntegerField(db_column='Pedido')  # Field name made lowercase.
    fechadevolucion = models.DateField(db_column='FechaDevolucion')  # Field name made lowercase.
    horadevolucion = models.TimeField(db_column='HoraDevolucion')  # Field name made lowercase.
    usuariocrea = models.SmallIntegerField(db_column='UsuarioCrea')  # Field name made lowercase.
    fechacreacion = models.DateField(db_column='FechaCreacion')  # Field name made lowercase.
    usuarionmodifica = models.SmallIntegerField(db_column='UsuarionModifica')  # Field name made lowercase.
    fechamodificacion = models.DateField(db_column='FechaModificacion')  # Field name made lowercase.
    productono = models.CharField(db_column='ProductoNo', max_length=16)  # Field name made lowercase.
    cantidadsolicitada = models.IntegerField(db_column='CantidadSolicitada', blank=True, null=True)  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=8, decimal_places=2)  # Field name made lowercase.
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=10, decimal_places=2)  # Field name made lowercase.
    causadevolucion = models.CharField(db_column='CausaDevolucion', max_length=25)  # Field name made lowercase.
    catalogo = models.CharField(db_column='Catalogo', max_length=12)  # Field name made lowercase.
    nolinea = models.SmallIntegerField(db_column='NoLinea')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'devolucionesaprovlines'
        unique_together = ['empresano', 'devolucionno', 'productono', 'catalogo', 'nolinea']


class Devolucionesheader(models.Model):
    empresano = models.ForeignKey(Asociado,related_name="fk_asoc_empno", db_column='EmpresaNo')  # Field name made lowercase.
    pedidono = models.IntegerField(db_column='PedidoNo')  # Field name made lowercase.
    asociadono = models.ForeignKey(Asociado,related_name="fk_asoc_asoc", db_column='AsociadoNo')  # Field name made lowercase.
    fecha = models.DateField(db_column='Fecha')  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'devolucionesheader'
        unique_together = ['empresano', 'pedidono']


class Devolucioneslines(models.Model):
    empresano = models.ForeignKey(Devolucionesheader,related_name="fk_devhead_empno", db_column='EmpresaNo')  # Field name made lowercase.
    devolucionno = models.ForeignKey(Devolucionesheader,related_name="fk_devhead_dev", db_column='DevolucionNo')  # Field name made lowercase.
    pedidono = models.IntegerField(db_column='PedidoNo')  # Field name made lowercase.
    fechadevolucion = models.DateField(db_column='FechaDevolucion')  # Field name made lowercase.
    horadevolucion = models.TimeField(db_column='HoraDevolucion')  # Field name made lowercase.
    usuariocrea = models.SmallIntegerField(db_column='UsuarioCrea')  # Field name made lowercase.
    fechacreacion = models.DateField(db_column='FechaCreacion')  # Field name made lowercase.
    usuarionmodifica = models.SmallIntegerField(db_column='UsuarionModifica')  # Field name made lowercase.
    fechamodificacion = models.DateField(db_column='FechaModificacion')  # Field name made lowercase.
    productono = models.CharField(db_column='ProductoNo', max_length=16)  # Field name made lowercase.
    cantidadsolicitada = models.IntegerField(db_column='CantidadSolicitada', blank=True, null=True)  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=8, decimal_places=2)  # Field name made lowercase.
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=10, decimal_places=2)  # Field name made lowercase.
    causadevolucion = models.CharField(db_column='CausaDevolucion', max_length=25)  # Field name made lowercase.
    catalogo = models.CharField(db_column='Catalogo', max_length=12)  # Field name made lowercase.
    nolinea = models.SmallIntegerField(db_column='NoLinea')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'devolucioneslines'
        unique_together = ['empresano', 'devolucionno', 'productono', 'catalogo', 'nolinea']


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = ['app_label', 'model']


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Documentos(models.Model):
    empresano = models.ForeignKey(Asociado,related_name="fk_asociado_empno_2", db_column='EmpresaNo')  # Field name made lowercase.
    nodocto = models.IntegerField(db_column='NoDocto')  # Field name made lowercase.
    consecutivo = models.IntegerField(db_column='Consecutivo')  # Field name made lowercase.
    tipodedocumento = models.CharField(db_column='TipoDeDocumento', max_length=12, blank=True, null=True)  # Field name made lowercase.
    tipodeventa = models.CharField(db_column='TipoDeVenta', max_length=12)  # Field name made lowercase.
    asociado = models.ForeignKey(Asociado,related_name="fk_asociado_asociado_2", db_column='Asociado')  # Field name made lowercase.
    fechacreacion = models.DateField(db_column='FechaCreacion')  # Field name made lowercase.
    horacreacion = models.TimeField(db_column='HoraCreacion')  # Field name made lowercase.
    usuarioquecreodcto_field = models.IntegerField(db_column='UsuarioQueCreoDcto.', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    fechaultimamodificacion = models.DateField(db_column='FechaUltimaModificacion')  # Field name made lowercase.
    horaultimamodificacion = models.TimeField(db_column='HoraUltimaModificacion')  # Field name made lowercase.
    usuariomodifico = models.IntegerField(db_column='UsuarioModifico', blank=True, null=True)  # Field name made lowercase.
    concepto = models.CharField(db_column='Concepto', max_length=60, blank=True, null=True)  # Field name made lowercase.
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    porcentajededescuento = models.FloatField(db_column='PorcentajeDeDescuento')  # Field name made lowercase.
    vtadecatalogo = models.TextField(db_column='VtaDeCatalogo')  # Field name made lowercase. This field type is a guess.
    cancelado = models.TextField(db_column='Cancelado')  # Field name made lowercase. This field type is a guess.
    comisiones = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pagoaplicadoaremisionno = models.IntegerField(db_column='PagoAplicadoARemisionNo')  # Field name made lowercase.
    lo_recibido = models.DecimalField(db_column='Lo_Recibido', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    idsucursal = models.SmallIntegerField(db_column='idsucursal',null=False)
    
    class Meta:
        managed = False
        db_table = 'documentos'
        unique_together = ['empresano', 'nodocto']


class Documentoscancelados(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    nodocto = models.IntegerField(db_column='NoDocto')  # Field name made lowercase.
    fechacancelacion = models.DateField(db_column='FechaCancelacion', blank=True, null=True)  # Field name made lowercase.
    horacancelacion = models.TimeField(db_column='HoraCancelacion', blank=True, null=True)  # Field name made lowercase.
    usuario = models.IntegerField(db_column='Usuario', blank=True, null=True)  # Field name made lowercase.
    motivo = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documentoscancelados'
        unique_together = ['empresano', 'nodocto']


class Enviomailsaproveedor(models.Model):
    empresa = models.SmallIntegerField(db_column='Empresa')  # Field name made lowercase.
    enviono_field = models.IntegerField(db_column='EnvioNo.')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    proveedor = models.IntegerField(db_column='Proveedor')  # Field name made lowercase.
    numalmacen = models.SmallIntegerField(db_column='NumAlmacen')  # Field name made lowercase.
    fecha = models.DateField(db_column='Fecha')  # Field name made lowercase.
    hora = models.TimeField(db_column='Hora')  # Field name made lowercase.
    buzondestinatarios = models.TextField(db_column='BuzonDestinatarios')  # Field name made lowercase.
    asunto = models.CharField(db_column='Asunto', max_length=50)  # Field name made lowercase.
    mensaj = models.TextField(db_column='Mensaj')  # Field name made lowercase.
    archivoanexo1 = models.TextField(db_column='ArchivoAnexo1')  # Field name made lowercase.
    archivoanexo2 = models.TextField(db_column='ArchivoAnexo2')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'enviomailsaproveedor'
        unique_together = ['empresa', 'enviono_field']


class Pedido(models.Model):

    class Meta:
        managed = False
        db_table = 'pedido'


class Pedidoconfirmacion(models.Model):
    empresano = models.ForeignKey('Pedidosheader',related_name="fk_pedhead_empresano", db_column='EmpresaNo')  # Field name made lowercase.
    pedido = models.ForeignKey('Pedidosheader',related_name="fk_pedhead_pedido", db_column='Pedido')  # Field name made lowercase.
    numalmacen = models.SmallIntegerField(db_column='NumAlmacen')  # Field name made lowercase.
    productono = models.ForeignKey(Articulo,related_name="fk_articulo_producto", db_column='ProductoNo')  # Field name made lowercase.
    fechasolicitud = models.DateField(db_column='FechaSolicitud')  # Field name made lowercase.
    fechatentativaconfirmacion = models.DateField(db_column='FechaTentativaConfirmacion')  # Field name made lowercase.
    status = models.CharField(max_length=15, blank=True, null=True)
    catalogo = models.ForeignKey(Articulo,related_name="fk_articulo_catalogo", db_column='catalogo')
    nolinea = models.IntegerField(db_column='NoLinea')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pedidoconfirmacion'
        unique_together = ['empresano', 'pedido', 'productono', 'numalmacen', 'fechasolicitud', 'catalogo', 'nolinea']


class PedidosStatusFechas(models.Model):
    empresano = models.ForeignKey('Pedidoslines',related_name="fk_pedlin_empno", db_column='EmpresaNo')  # Field name made lowercase.
    pedido = models.ForeignKey('Pedidoslines',related_name="fk_pedido", db_column='Pedido')  # Field name made lowercase.
    productono = models.ForeignKey('Pedidoslines',related_name="fk_producto", db_column='ProductoNo')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=15)  # Field name made lowercase.
    catalogo = models.ForeignKey('Pedidoslines',related_name="fk_pedlin_cat", db_column='catalogo')
    nolinea = models.ForeignKey('Pedidoslines',related_name="pedlino_no_nolinea", db_column='NoLinea')  # Field name made lowercase.
    fechamvto = models.DateField(db_column='FechaMvto', blank=True, null=True)  # Field name made lowercase.
    horamvto = models.TimeField(db_column='HoraMvto', blank=True, null=True)  # Field name made lowercase.
    usuario = models.IntegerField(db_column='Usuario', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pedidos_status_fechas'
        unique_together = ['empresano', 'pedido', 'productono', 'catalogo', 'nolinea', 'status']


class Pedidoscancelados(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    pedido = models.IntegerField(db_column='Pedido')  # Field name made lowercase.
    productono = models.CharField(db_column='productono', max_length=16)  # Field name made lowercase.
    catalogo = models.CharField(max_length=12)
    nolinea = models.IntegerField(db_column='NoLinea')  # Field name made lowercase.
    motivo = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'pedidoscancelados'
        unique_together = ['empresano', 'pedido', 'productono', 'catalogo', 'nolinea']


class Pedidosheader(models.Model):
    empresano = models.ForeignKey(Asociado,related_name="empresa_asociado_1", db_column='EmpresaNo')  # Field name made lowercase.
    pedidono = models.IntegerField(db_column='PedidoNo')  # Field name made lowercase.
    fechapedido = models.DateField(db_column='FechaPedido')  # Field name made lowercase.
    horapedido = models.TimeField(db_column='HoraPedido', blank=True, null=True)  # Field name made lowercase.
    saldototal = models.DecimalField(db_column='Saldototal', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    vtatotal = models.DecimalField(db_column='VtaTotal', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    usuariocrea = models.IntegerField(db_column='UsuarioCrea', blank=True, null=True)  # Field name made lowercase.
    fechaultimamodificacion = models.DateField(db_column='FechaUltimaModificacion')  # Field name made lowercase.
    fechacreacion = models.DateField(db_column='FechaCreacion')  # Field name made lowercase.
    horacreacion = models.TimeField(db_column='HoraCreacion', blank=True, null=True)  # Field name made lowercase.
    horamodicacion = models.TimeField(db_column='HoraModicacion', blank=True, null=True)  # Field name made lowercase.
    usuariomodifica = models.IntegerField(db_column='UsuarioModifica', blank=True, null=True)  # Field name made lowercase.
    idsucursal = models.IntegerField(db_column='idSucursal')  # Field name made lowercase.
    asociadono = models.ForeignKey(Asociado, related_name="empresa_asociado_2",db_column='AsociadoNo')  # Field name made lowercase.
    tiposervicio = models.CharField(max_length=20)
    viasolicitud = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pedidosheader'
        unique_together = ['empresano', 'pedidono']


class Pedidoslines(models.Model):
    empresano = models.ForeignKey(Pedidosheader,related_name="fk_pedhead_emp", db_column='EmpresaNo')  # Field name made lowercase.
    pedido = models.ForeignKey(Pedidosheader,related_name="fk_pedhead_ped", db_column='Pedido')  # Field name made lowercase.
    productono = models.ForeignKey(Articulo,related_name="fk_pedhead_art", db_column='ProductoNo')  # Field name made lowercase.
    cantidadsolicitada = models.IntegerField(db_column='CantidadSolicitada', blank=True, null=True)  # Field name made lowercase.
    precio = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    saldo = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=15, blank=True, null=True)  # Field name made lowercase.
    remisionno = models.IntegerField(db_column='RemisionNo')  # Field name made lowercase.
    nonotacreditoporpedido = models.IntegerField(db_column='NoNotaCreditoPorPedido')  # Field name made lowercase.
    nonotacreditopordevolucion = models.IntegerField(db_column='NoNotaCreditoPorDevolucion')  # Field name made lowercase.
    norequisicionaproveedor = models.IntegerField(db_column='NoRequisicionAProveedor')  # Field name made lowercase.
    nonotacreditopordiferencia = models.IntegerField(db_column='NoNotaCreditoPorDiferencia')  # Field name made lowercase.
    catalogo = models.ForeignKey(Articulo,related_name="fk_art_cat", db_column='catalogo')
    nolinea = models.IntegerField(db_column='NoLinea')  # Field name made lowercase.
    plazoentrega = models.IntegerField()
    opcioncompra = models.CharField(db_column='OpcionCompra', max_length=15)  # Field name made lowercase.
    fechamaximaentrega = models.DateField(db_column='FechaMaximaEntrega')  # Field name made lowercase.
    fechatentativallegada = models.DateField(db_column='FechaTentativaLLegada',null=False)
    fechamaximarecoger =models.DateField(db_column='FechaMaximaRecoger',null=False)
    
    class Meta:
        managed = False
        db_table = 'pedidoslines'
        unique_together = ['empresano', 'pedido', 'productono', 'catalogo', 'nolinea']
#
#class Pedidos_tem(models.Model):
#    idproducto = models.CharField(max_length=16)
#    idprovedor = models.ItegerField(db_column='idprovedor')
#    catalogo = models.CharField(max_length=12)
#    precio = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
#    nolinea = moodels.IntegerField()

#    class Meta:
#        managed = False
#        db_table = 'pedidos_tmp'

class Pedidoslinesdocumentos(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    pedido = models.IntegerField(db_column='Pedido')  # Field name made lowercase.
    productono = models.CharField(db_column='ProductoNo', max_length=16)  # Field name made lowercase.
    cantidadpendiente = models.IntegerField(db_column='CantidadPendiente')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pedidoslinesdocumentos'
        unique_together = ['empresano', 'pedido', 'productono', 'cantidadpendiente']


class Pedidoslinestemporada(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    pedido = models.IntegerField(db_column='Pedido')  # Field name made lowercase.
    productono = models.CharField(db_column='ProductoNo', max_length=16)  # Field name made lowercase.
    catalogo = models.CharField(max_length=12)
    nolinea = models.IntegerField(db_column='NoLinea')  # Field name made lowercase.
    temporada = models.IntegerField(db_column='Temporada')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pedidoslinestemporada'
        unique_together = ['empresano', 'pedido', 'productono', 'catalogo', 'nolinea']


class Periodosentrega(models.Model):
    id = models.IntegerField(primary_key=True)
    periodo = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'periodosentrega'


class Preciobase(models.Model):
    empresano = models.ForeignKey(Articulo,related_name="pk_empresa", db_column='EmpresaNo')  # Field name made lowercase.
    proveedorid = models.IntegerField(db_column='ProveedorId')  # Field name made lowercase.
    temporada = models.IntegerField(db_column='Temporada')  # Field name made lowercase.
    codigoarticulo = models.ForeignKey(Articulo, db_column='CodigoArticulo')  # Field name made lowercase.
    costo = models.DecimalField(db_column='Costo', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fechacreacion = models.DateField(db_column='FechaCreacion', blank=True, null=True)  # Field name made lowercase.
    fechamodificacion = models.DateField(db_column='FechaModificacion', blank=True, null=True)  # Field name made lowercase.
    horacreacion = models.TimeField(db_column='HoraCreacion', blank=True, null=True)  # Field name made lowercase.
    horamodificacion = models.TimeField(db_column='HoraModificacion', blank=True, null=True)  # Field name made lowercase.
    usuariocreo = models.IntegerField(db_column='UsuarioCreo', blank=True, null=True)  # Field name made lowercase.
    usuariomodifico = models.IntegerField(db_column='UsuarioModifico', blank=True, null=True)  # Field name made lowercase.
    pagina = models.CharField(db_column='Pagina', max_length=6, blank=True, null=True)  # Field name made lowercase.
    catalogo = models.ForeignKey(Articulo,related_name="pk_catalogo", db_column='Catalogo')  # Field name made lowercase.
    estilo = models.CharField(db_column='Estilo', max_length=40)  # Field name made lowercase.
    idmarca = models.CharField(max_length=40)
    idcolor = models.CharField(max_length=40)
    talla = models.CharField(max_length=12)

    class Meta:
        managed = False
        db_table = 'preciobase'
        unique_together = ['empresano', 'proveedorid', 'temporada', 'codigoarticulo', 'catalogo']


class Preciosopcionales(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    proveedor = models.IntegerField(db_column='Proveedor')  # Field name made lowercase.
    temporada = models.SmallIntegerField(db_column='Temporada')  # Field name made lowercase.
    articuloid = models.CharField(db_column='ArticuloId', max_length=16)  # Field name made lowercase.
    tipoprecio = models.CharField(db_column='TipoPrecio', max_length=15)  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fechacreacion = models.DateField(db_column='FechaCreacion')  # Field name made lowercase.
    horacreacion = models.TimeField(db_column='HoraCreacion', blank=True, null=True)  # Field name made lowercase.
    fechamodificacion = models.DateField(db_column='FechaModificacion')  # Field name made lowercase.
    horamodificacion = models.TimeField(db_column='HoraModificacion', blank=True, null=True)  # Field name made lowercase.
    catalogo = models.CharField(max_length=12)

    class Meta:
        managed = False
        db_table = 'preciosopcionales'
        unique_together = ['empresano', 'proveedor', 'temporada', 'articuloid', 'tipoprecio', 'catalogo']


class Proveedor(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    proveedorno = models.IntegerField(db_column='ProveedorNo')  # Field name made lowercase.
    razonsocial = models.CharField(db_column='RazonSocial', max_length=45, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=45, blank=True, null=True)  # Field name made lowercase.
    colonia = models.CharField(db_column='Colonia', max_length=45, blank=True, null=True)  # Field name made lowercase.
    ciudad = models.CharField(db_column='Ciudad', max_length=45, blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(db_column='Estado', max_length=45, blank=True, null=True)  # Field name made lowercase.
    pais = models.CharField(db_column='Pais', max_length=45, blank=True, null=True)  # Field name made lowercase.
    codigopostal = models.IntegerField(db_column='CodigoPostal', blank=True, null=True)  # Field name made lowercase.
    telefono1 = models.CharField(max_length=15, blank=True, null=True)
    telefono2 = models.CharField(max_length=15, blank=True, null=True)
    fax = models.CharField(max_length=15, blank=True, null=True)
    cel = models.CharField(max_length=15, blank=True, null=True)
    radio = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    fechaata = models.DateField(db_column='FechaAta')  # Field name made lowercase.
    fechabaja = models.DateField(db_column='FechaBaja')  # Field name made lowercase.
    usuarioquedioalta = models.SmallIntegerField(db_column='UsuarioQueDioAlta')  # Field name made lowercase.
    usuaroi = models.SmallIntegerField(db_column='Usuaroi')  # Field name made lowercase.
    manejar_desc = models.BooleanField(db_column='manejar_desc')
    class Meta:
        managed = False
        db_table = 'proveedor'
        unique_together = ['empresano', 'proveedorno']


class ProveedorCatalogo(models.Model):
    idproveedor = models.IntegerField(db_column='idProveedor')  # Field name made lowercase.
    clasecatalogo = models.CharField(db_column='ClaseCatalogo', max_length=12)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'proveedor_catalogo'
        unique_together = ['idproveedor', 'clasecatalogo']


class Remisonesacredito(models.Model):
    empresano = models.ForeignKey(Documentos,related_name="fk_docto_empresa", db_column='EmpresaNo')  # Field name made lowercase.
    nodocto = models.ForeignKey(Documentos,related_name="fk_docto_Nodocto", db_column='NoDocto')  # Field name made lowercase.
    periodopago = models.SmallIntegerField(db_column='PeriodoPago')  # Field name made lowercase.
    a_nombre_de = models.CharField(db_column='A_nombre_de', max_length=35)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'remisonesacredito'
        unique_together = ['empresano', 'nodocto']


class Requisicionheader(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    proveedor = models.IntegerField(db_column='Proveedor')  # Field name made lowercase.
    almacen = models.SmallIntegerField(db_column='Almacen')  # Field name made lowercase.
    requisicionno = models.IntegerField(db_column='RequisicionNO')  # Field name made lowercase.
    fechacreacion = models.DateField(db_column='FechaCreacion', blank=True, null=True)  # Field name made lowercase.
    fechauitimamodificacion = models.DateField(db_column='FechaUItimaModificacion', blank=True, null=True)  # Field name made lowercase.
    horacraacion = models.TimeField(db_column='HoraCraacion')  # Field name made lowercase.
    horaultimamodificacion = models.TimeField(db_column='HoraUltimaModificacion')  # Field name made lowercase.
    usuariocreo = models.SmallIntegerField(db_column='UsuarioCreo')  # Field name made lowercase.
    usuariomodifico = models.SmallIntegerField(db_column='UsuarioModifico')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'requisicionheader'
        unique_together = ['empresano', 'proveedor', 'almacen', 'requisicionno']


class Requisicionlines(models.Model):
    empresano = models.ForeignKey(Articulo,related_name="fk_articulo_empresa", db_column='EmpresaNo')  # Field name made lowercase.
    proveedorno = models.ForeignKey(Requisicionheader,related_name="fk_proveedor_reqheader", db_column='ProveedorNo')  # Field name made lowercase.
    numalmacen = models.ForeignKey(Requisicionheader,related_name="fk_numalmacen_reqheader", db_column='NumAlmacen')  # Field name made lowercase.
    requisicionno = models.ForeignKey(Requisicionheader,related_name="fk_requhead_reqno", db_column='RequisicionNo')  # Field name made lowercase.
    codigoarticulo = models.ForeignKey(Articulo,related_name="fk_reqart_codpro", db_column='CodigoArticulo')  # Field name made lowercase.
    cantidadsolicitada = models.IntegerField(db_column='CantidadSolicitada')  # Field name made lowercase.
    cantidadpendiente = models.IntegerField(db_column='CantidadPendiente')  # Field name made lowercase.
    requisicionquesustituye = models.IntegerField(db_column='RequisicionQueSustituye')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20)  # Field name made lowercase.
    catalogo = models.ForeignKey(Articulo,related_name="fk_art_catalogo", db_column='Catalogo')  # Field name made lowercase.
    nolinea = models.IntegerField(db_column='NoLinea')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'requisicionlines'
        unique_together = ['empresano', 'proveedorno', 'numalmacen', 'requisicionno', 'codigoarticulo', 'catalogo', 'nolinea']


class Sociocatalogo(models.Model):
    idsocio = models.IntegerField(db_column='idSocio')  # Field name made lowercase.
    idproveedor = models.IntegerField(db_column='idProveedor')  # Field name made lowercase.
    clasecatalogo = models.CharField(db_column='ClaseCatalogo', max_length=12)  # Field name made lowercase.
    activo = models.TextField(db_column='Activo')  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = False
        db_table = 'sociocatalogo'


class Sociocatalogostemporada(models.Model):
    proveedorno = models.ForeignKey(Catalogostemporada,related_name="pk_proveedor_id", db_column='ProveedorNo')  # Field name made lowercase.
    periodo = models.ForeignKey(Catalogostemporada,related_name="fk_cattemp_periodo", db_column='Periodo')  # Field name made lowercase.
    anio = models.ForeignKey(Catalogostemporada,related_name="pk_anio", db_column='Anio')  # Field name made lowercase.
    clasearticulo = models.ForeignKey(Catalogostemporada,related_name="pk_clasearticulo", db_column='ClaseArticulo')  # Field name made lowercase.
    asociadono = models.IntegerField(db_column='AsociadoNo')  # Field name made lowercase.
    activo = models.TextField(db_column='Activo')  # Field name made lowercase. This field type is a guess.
    nodocto = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sociocatalogostemporada'
        unique_together = ['proveedorno', 'periodo', 'anio', 'clasearticulo', 'asociadono']


class Sucursal(models.Model):
    empresano = models.SmallIntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    sucursalno = models.SmallIntegerField(db_column='SucursalNo')  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=45, blank=True, null=True)  # Field name made lowercase.
    colonia = models.CharField(db_column='Colonia', max_length=45, blank=True, null=True)  # Field name made lowercase.
    ciudad = models.CharField(db_column='Ciudad', max_length=45, blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(db_column='Estado', max_length=45, blank=True, null=True)  # Field name made lowercase.
    pais = models.CharField(db_column='Pais', max_length=45, blank=True, null=True)  # Field name made lowercase.
    codigopostal = models.IntegerField(db_column='CodigoPostal', blank=True, null=True)  # Field name made lowercase.
    telefono1 = models.IntegerField(db_column='Telefono1', blank=True, null=True)  # Field name made lowercase.
    telefono2 = models.IntegerField(blank=True, null=True)
    fax = models.IntegerField(db_column='Fax', blank=True, null=True)  # Field name made lowercase.
    celular = models.IntegerField(db_column='Celular', blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(max_length=100, blank=True, null=True)
    radio = models.CharField(max_length=15, blank=True, null=True)
    fechaalta = models.DateField(db_column='FechaAlta')  # Field name made lowercase.
    fehabaja = models.DateField(db_column='FehaBaja')  # Field name made lowercase.
    iva = models.FloatField(db_column='Iva')  # Field name made lowercase.
    nombre = models.CharField(db_column='nombre',max_length=30,null=True)

    class Meta:
        managed = False
        db_table = 'sucursal'
        unique_together = ['empresano', 'sucursalno']


class Tiendaabastece(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    proveedorno = models.IntegerField(db_column='ProveedorNo')  # Field name made lowercase.
    tienda_no_field = models.IntegerField(db_column='Tienda_No.')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    razonsocial = models.CharField(db_column='RazonSocial', max_length=45, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=45, blank=True, null=True)  # Field name made lowercase.
    colonia = models.CharField(db_column='Colonia', max_length=45, blank=True, null=True)  # Field name made lowercase.
    ciudad = models.CharField(db_column='Ciudad', max_length=45, blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(db_column='Estado', max_length=45, blank=True, null=True)  # Field name made lowercase.
    pais = models.CharField(db_column='Pais', max_length=45, blank=True, null=True)  # Field name made lowercase.
    codigopostal = models.IntegerField(db_column='CodigoPostal', blank=True, null=True)  # Field name made lowercase.
    telefono1 = models.IntegerField(db_column='Telefono1', blank=True, null=True)  # Field name made lowercase.
    telefono2 = models.IntegerField(db_column='Telefono2', blank=True, null=True)  # Field name made lowercase.
    fax = models.IntegerField(db_column='Fax', blank=True, null=True)  # Field name made lowercase.
    cel = models.IntegerField(blank=True, null=True)
    radio = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    fechaata = models.DateField(db_column='FechaAta')  # Field name made lowercase.
    fechabaja = models.DateField(db_column='FechaBaja')  # Field name made lowercase.
    usuarioquedioalta = models.SmallIntegerField(db_column='UsuarioQueDioAlta')  # Field name made lowercase.
    usuaroi = models.SmallIntegerField(db_column='Usuaroi')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tiendaabastece'
        unique_together = ['empresano', 'proveedorno', 'tienda_no_field']

class Tiposervicio(models.Model):
    tiposervicio = models.CharField(primary_key=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'tiposervicio'


class UsuarioDerechos(models.Model):
    derechono = models.IntegerField(db_column='DerechoNo')  # Field name made lowercase.
    usuariono = models.ForeignKey('Usuarios',related_name="fk_usu_usuano",db_column='UsuarioNo')  # Field name made lowercase.
    activo_field = models.TextField(db_column='Activo?')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'. This field type is a guess.
    empresano = models.ForeignKey('Usuarios',related_name="fk_usuemp", db_column='EmpresaNo')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuario_derechos'
        unique_together = ['empresano', 'usuariono', 'derechono']


class Usuarios(models.Model):
    empresano = models.IntegerField(db_column='EmpresaNo')  # Field name made lowercase.
    usuariono = models.IntegerField(db_column='UsuarioNo')  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=45)  # Field name made lowercase.
    password = models.TextField(blank=True, null=True)
    fechacreacion = models.DateField(db_column='FechaCreacion')  # Field name made lowercase.
    fechamodificacion = models.DateField(db_column='FechaModificacion')  # Field name made lowercase.
    activo = models.TextField(db_column='Activo')  # Field name made lowercase. This field type is a guess.
    nivel = models.IntegerField(db_column='Nivel')  # Field name made lowercase.
    usuario = models.CharField(db_column='Usuario', unique=True, max_length=15)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuarios'
        unique_together = ['empresano', 'usuariono']

class Viasolicitud(models.Model):
    id = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'viasolicitud'

class Pedidos_tmp(models.Model):
    session_key = models.CharField(max_length=50)
    idproveedor = models.IntegerField()
    idproducto = models.CharField(max_length=16)
    catalogo = models .CharField(max_length=12)
    precio = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
