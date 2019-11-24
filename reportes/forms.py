from django import forms
from reportes.models import Cliente

class ClienteForm(forms.ModelForm):
	class Meta:
		model = Cliente
		fields ='__all__'

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if not 'j' in email:
			raise forms.ValidationError('Por favor incluye una j en el email !')
		return email 
	def clean_nombre(self):
		nombre = self.cleaned_data.get('nombre')
		may_nombre = nombre.upper()
		return may_nombre

	def clean_domicilio(self):
		domicilio = self.cleaned_data.get('domicilio')
		may_domicilio = domicilio.upper()
		return may_domicilio


class FiltraclienteForm(forms.Form):
	
		opciones_busqueda = (('1','Codigo de cliente.',),('2','Un texto en el nombre o en la direccion.',))
		buscar_por = forms.ChoiceField(label='Buscar por',choices=opciones_busqueda)
		id_cliente = forms.IntegerField(label ='Codigo del cliente')
		token_to_search =forms.CharField(label ='Texto a buscar en el nombre o la direccion',max_length=50)
		
		def clean_token_to_search(self):
			token_to_search = self.cleaned_data.get('token_to_search')
			return token_to_search
		
	

