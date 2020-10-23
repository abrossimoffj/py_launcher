##JA 23/10/2020 : debug class for wrapping any functions and permits to get all private variables and return values of functions wrapped with @debug decorator
## The class is devoted to the GUI debuger

import sys
import functools

##On se sert de sys.setprofile pour définir une fonction de profilage du système : l'evenement "return" capture le fait que la méthode est sur le point de se terminer et la fonction de tracage est ainsi appellée

class debug(object):
	def __init__(self, func):
		functools.update_wrapper(self, func) ## equivalent of @functool.wraps(func) for a class 
		self._locals = {}
		self.func = func
		self.signature = None
		self.res = None

	def __call__(self, *args, **kwargs): ##Defining a custom __call__() method in the meta-class allows the class's instance to be called as a function, not always modifying the instance itself.
		def tracer(frame, event, arg):
			if event=='return':
				self._locals = frame.f_locals.copy()

        # tracer is activated on next call, return or exception, here we activate it on return signal
		sys.setprofile(tracer)
		try:
		# trace the function call
			args_repr = [repr(a) for a in args]                      
			kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  
			self.signature = ", ".join(args_repr + kwargs_repr)           
			self.res = self.func(*args, **kwargs)
		finally:
		# disable tracer and replace with old one
			sys.setprofile(None)
		return self.res

	def clear_locals(self):
		self._locals = {}

	@property
	def locals(self):
		return self._locals

	@property
	def get_signature(self):
		return self.signature
	@property
	def get_output(self):
		return self.res

@debug
def func():
    local1 = 1
    local2 = 2
    return '42'

@debug
def func2():
	pif = "paf"
	pouf = "7777"



def clean_printing(func):
	print("-----------------------------------------")
	print(f"Calling {func.__name__}({func.get_signature})")
	print(f"Intern variables {func.locals!r}")
	print(f"{func.__name__!r} returned {func.get_output!r}")
	print("-----------------------------------------")

a = func()
func2()
clean_printing(func)
clean_printing(func2)