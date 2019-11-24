from django.db import models

class Cliente(models.Model):
	nombre =models.CharField(verbose_name='Nombre', max_length=100)
	domicilio = models.CharField(verbose_name='Domicilio',max_length=200)
	email = models.EmailField(verbose_name='email',max_length=200)

	def __str__(self):
		return self.nombre

class Reporte(models.Model):
	descripcion = models.CharField(max_length=5000)
	Solucion = models.CharField(max_length=5000)
	fecha_mod = models.DateField()
	id_cliente =models.ForeignKey(Cliente)

	def __str__(self):
		return self.descripcion

		# Create your models here.
