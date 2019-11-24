a="hey"
try:
	print a+3
except TypeError as e:
	print "paso por aqui"
	print "El error es: " + e
