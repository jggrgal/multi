from django.shortcuts import render,redirect,render_to_response
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.template import RequestContext,loader
from django.core.urlresolvers import reverse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder # Permite decodificar fecha y hora con formato mysql obtenido con dictfetchall
from django.db import connection,DatabaseError,Error,transaction,IntegrityError,OperationalError,InternalError,ProgrammingError,NotSupportedError
from django.conf import settings
import pdb
import unicodedata
import json



