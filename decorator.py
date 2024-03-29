##JA 23/10/2020 : debug class for wrapping any functions and permits to get all private variables and return values of functions wrapped with @debug decorator
## The class is devoted to the GUI debuger

import sys
import functools
import os
import json
import asyncio
#import websockets
import websocket

print = functools.partial(print,flush=True)
##On se sert de sys.setprofile pour définir une fonction de profilage du système : l'evenement "return" capture le fait que la méthode est sur le point de se terminer et la fonction de tracage est ainsi appellée
class HiddenPrints:
	def __enter__(self):
		self._original_stdout = sys.stdout
		sys.stdout = open(os.devnull, 'w')

	def __exit__(self, exc_type, exc_val, exc_tb):
		sys.stdout.close()
		sys.stdout = self._original_stdout

class debug(object):
	def __init__(self, func):
		functools.update_wrapper(self, func) ## equivalent of @functool.wraps(func) for a class 
		self._locals = {}
		self.func = func
		self.signature = None
		self.res = None
		self.ws = websocket.create_connection("ws://localhost:6171/")

	def __call__(self, *args, **kwargs): ##Defining a custom __call__() method in the meta-class allows the class's instance to be called as a function, not always modifying the instance itself.
		def tracer(frame, event, arg):
			if event=='return':
				if frame.f_code.co_name == self.__name__ : ## For avoiding to get local variables of other frames in stack 
					self._locals = frame.f_locals.copy()

        # tracer is activated on next call, return or exception, here we activate it on return signal
		args_repr = [repr(a) for a in args]                      
		kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  
		self.signature = ", ".join(args_repr + kwargs_repr)
		sys.setprofile(tracer)
		try:
		# trace the function call
			with HiddenPrints():         
				self.res = self.func(*args, **kwargs)
			msg = self.convert_to_serialized_string()
			self.ws.send(msg.encode())

		finally:
		# disable tracer and replace with old one
			sys.setprofile(None)
		return self.res
	def __exit__(self, exc_type, exc_value, traceback):
	 	print("heeeey")

	def convert_to_serialized_string(self):
		list_to_send = [self.__name__,self.signature,self._locals,self.res]
		data_string = json.dumps(list_to_send) #data serialized
		return data_string

	# def clean_printing(self):
	# 	print("-----------------------------------------")
	# 	print(f"Calling {self.__name__}({self.signature})")
	# 	print(self._locals)
	# 	#print("Intern variables ",json.dumps(self._locals))
	# 	print(f"{self.__name__!r} returned {self.res!r}")
	# 	print("-----------------------------------------")


