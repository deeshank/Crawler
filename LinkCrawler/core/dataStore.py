__author__ = 'deepakss'

from Queue import Queue
import logging
from LinkCrawler.core.helpers import Singleton


logging.basicConfig()
logger = logging.getLogger("DataStore")
logger.setLevel(logging.INFO)


class DB(object):
	__metaclass__ = Singleton

	def __init__(self, n=100):
		logger.info("Setting DB size to {0}".format(n))
		self.permanentQ = Queue(n)
		self.q = Queue()

	def isFull(self):
		return self.permanentQ.full()

	def nextURL(self):
		try:
			if not self.q.empty():
				data = self.q.get(timeout=2)
				self.q.task_done()
				return data
			else:
				return None
		except Exception, e:
			print e

	def isEmpty(self):
		return self.permanentQ.empty()

	def add(self, data):
		if not self.permanentQ.full():
			if data:
				data = str(data).strip()
				#print "Adding data =>",self.permanentQ.qsize()
				if data not in self.permanentQ.queue:
					self.q.put(data)
					self.permanentQ.put(data)
			return 1
		else:
			return 0

	def stats(self):
		logger.info(self.permanentQ.qsize())

