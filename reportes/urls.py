from django.conf.urls import url
from . import views
urlpatterns = [
	url(r'^$',views.listaclientes,name='listaclientes'),
    url(r'^creacliente/$',views.creacliente, name='creacliente'),
    url(r'^modificacliente/(?P<id_cliente>[0-9]+)/$',views.modificacliente, name='modificacliente'),
    url(r'^reportes/(?P<id_cliente>[0-9]+)/$',views.reportes_por_cliente, name='reportes_por_cliente'),
    url(r'^$',views.clienteactualizado,name='clienteactualizado'),
    url(r'^eliminaclientes/$',views.eliminaclientes,name='eliminaclientes'),
    url(r'^commitdelclientes/$',views.commitdelclientes,name='commitdelclientes'),
    url(r'^filtraclientes/$',views.filtraclientes, name='filtraclientes'),
    ]