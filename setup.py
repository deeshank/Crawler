from setuptools import setup

setup(name='Crawler', version='1.0', packages=['LinkCrawler', 'LinkCrawler.core'], url='', license='',
	author='deepakss', author_email='deepakss@cisco.com', description='Link Parser Crawler',
	entry_points={'console_scripts': ['crawl = LinkCrawler.core.parser:main']})
