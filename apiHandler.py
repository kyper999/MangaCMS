

import traceback
from pyramid.response import Response

import nameTools as nt
import logging
import json
import settings

class ApiInterface(object):

	log = logging.getLogger("Main.API")

	def __init__(self):
		pass



	def handleApiCall(self, request):

		print("API Call!", request.params)

		return Response(body="No API calls are available in the reader-only version.")
