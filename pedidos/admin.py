from django.contrib import admin
from .models import Articulo,Asociado,Pedidosheader,Pedidoslines,PedidosStatusFechas,Preciobase,Usuarios

# Register your models here.
admin.site.register(Articulo)
admin.site.register(Asociado)
admin.site.register(Pedidosheader)
admin.site.register(Pedidoslines)
admin.site.register(PedidosStatusFechas)
admin.site.register(Preciobase)
admin.site.register(Usuarios)