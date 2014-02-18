import argparse
import urlparse
import time
import logging
import threading

from bs4 import BeautifulSoup
import sys

from LinkCrawler.core.dataStore import DB
from LinkCrawler.core.helpers import *

global pool
pool = []

__author__ = 'deepakss'
logging.basicConfig()
log = logging.getLogger("Crawler")
log.setLevel(logging.INFO)


class HtmlParser(object):
	def __init__(self, url):
		self.url = url
		self.db = DB()
		self.html = ''

	def get_html(self):
		"""Gets HTML Source for the given url"""
		if not self.db.isFull():
			try:
				request = HeadRequest(self.url)
				response = urllib2.urlopen(request)
				response_headers = response.info()
				content_type = response_headers['content-type']
				if 'text/html' in str(content_type).lower().strip():    #Filters only text/html content-type urls
					raw_html = urllib2.urlopen(self.url, timeout=5).read()
					self.html = BeautifulSoup(raw_html)
					#log.info("Parsed : {0}".format(self.url))
				else:
					log.error("Content Type Restricted => {0}".format(content_type))
					self.html = ''
			except Exception, e:
				log.info("Unable to Parse the URL {0} => {1}".format(self.url, e))
				self.html=''
		else:
			pass

	def get_all_ids(self):
		"""Gets all ids of all the html tags if available,
		since some href tags might contain links to div elements in the same page"""
		ids = []
		if self.html:
			for tag in self.html.find_all('', id=True):
				ids.append(str(tag['id']).strip())
			return list(set(ids))
		else:
			return []

	def parse_links(self):
		if self.db.isFull():
			log.info("Return the threads!")
			return
		log.info("Thread running the parse link => {0}".format(self.url))
		self.get_html()
		tag_ids = self.get_all_ids()
		if not self.html:
			return
		else:
			for link in self.html.find_all('a', href=True):
				href = str(link['href']).strip()
				if href:
					href = href[1:] if href[0] == "#" else href
					if href not in tag_ids:
						if href.startswith("mailto:"):
							pass
						if not href.startswith('http://') and not href.startswith('www'):
							rtn = self.db.add(urlparse.urljoin(self.url, href))
						else:
							rtn = self.db.add(href)
						if rtn:
							continue
						else:
							log.info("Terminate Thread '{0}' as the Queue is full !".format(self.url))
							break
		return


#### WITHOUT THREADS
# def main():
# 	db=DB(1000)
# 	HtmlParser('http://docs.python.org/2/library/queue.html').parse_links()
# 	while not db.isFull():
# 		url=db.nextURL()
# 		HtmlParser(url).parse_links()
# 	log.info("Done.")
#   db.collectStats()



def runner(n=10):
	global pool
	db = DB()
	for x in range(n):
		next_url = db.nextURL()
		if next_url:
			parser = HtmlParser(next_url)
			th = threading.Thread(target=parser.parse_links, args=tuple())
			pool.append(th)
			th.start()
		else:
			log.info("No URL!")
			if db.isFull():
				log.info("DB IS FULL!")
				break
			continue
	#log.info("JOINING the threads...")
	[x.join() for x in pool]  # waits till all the threads are done
	pool = []
	return



def crawl(url, n=100, t=10):
	db = DB(n)
	HtmlParser(str(url).strip()).parse_links()
	if db.isEmpty():
		log.error("No Links Found!")
		sys.exit(1)
	while not db.isFull():  # spawn t threads in batches
		log.info("Starting {0} threads parallely".format(t))
		runner(t)
	db.collectStats()


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--threads", help="No. of threads to run", dest="th")
	parser.add_argument("-n", "--count", help="No. of Links to parse", dest="n")
	parser.add_argument("-u", "--url", help="URL to parse", dest="url", required=True)

	args = parser.parse_args()
	url = args.url
	th = 10 if not args.th else int(args.th)
	n = 100 if not args.n else int(args.n)
	start_time = time.time()
	crawl(url, n, th)
	log.info("Processed in {0} seconds".format(time.time() - start_time))
