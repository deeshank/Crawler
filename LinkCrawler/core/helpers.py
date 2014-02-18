import urllib2

__author__ = 'deepakss'


class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances.keys():
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class HeadRequest(urllib2.Request):
	def get_method(self):
		return "HEAD"