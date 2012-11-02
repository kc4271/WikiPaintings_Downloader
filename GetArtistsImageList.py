#coding=UTF-8
from BeautifulSoup import BeautifulSoup
import urllib
import re
import os
import threading
import time
import pdb
import sys

class Artists(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):

		global mutex_artist
		global lines
		global artist_count
		
		#pdb.set_trace()
		while(True):
			suffix = ""
			mutex_artist.acquire()
			if artist_count < len(lines):
				suffix = lines[artist_count]
				artist_count += 1
			mutex_artist.release()
			if not suffix:
				break
			
			try:
				self.download_artist(suffix)
			except:
				pass
		
	def download_artist(self,suffix):
		global mutex_artist
		global logfile
		

		artist = suffix[suffix.rfind('/')+1:]
		queue = []
		record_path = u"lists/%s.lst" % artist
		if os.path.exists(record_path):
			f = open(record_path)
			for l in f:
				if not l.strip():
					continue
				queue.append(l.strip())
			f.close()
			return
	
		mutex_artist.acquire()
		print "Start Download %s list" % suffix
		mutex_artist.release()
		
		img_urls = []
		try:
			page = read_web(suffix, 1)
			soup = BeautifulSoup(page)
			bigenough = soup.findAll('div',{'class':'pager-total'})
			if not bigenough:
				img_urls.extend(parse_page(page))
			else:
				itemnumber = int(soup.findAll('div',{'class':'pager-total'})[0].string[7:])
				pagenumber = (itemnumber + 59) / 60
			
				for i in range(pagenumber):
					curNumber = i + 1
					page = read_web(suffix, curNumber)
					img_urls.extend(parse_page(page))

			f = open(record_path,'w')
			for l in img_urls:
				f.write(l.encode('UTF-8','ignore')+'\n')
			f.close()
		except:
			mutex_artist.acquire()
			logfile.write(u"Parse Error:%s\n" % suffix)
			mutex_artist.release()

		


def read_web(suffix, pagenumber):
	_url = 'http://www.wikipaintings.org/' + suffix + '/mode/all-paintings-by-alphabet/' + '%d' % (pagenumber)
	return  urllib.urlopen(_url).read().decode('utf-8','ignore')

def parse_page(page):
	book = []
	soup = BeautifulSoup(page)
	items = soup.findAll('ins',{'class':re.compile('search-item.*')})
	imgs = [i.findAll('img')[0]['src'] for i in items]
	for s in imgs:
		book.append(s[:s.find(u'.jpg')+4])
	return book

if __name__ == "__main__":
	global logfile
	global artist_count
	global mutex_artist
	global lines
	global mutex
	
	mutex = threading.Lock()
	mutex_artist = threading.Lock()
	artist_count = 0
	
	if not os.path.exists('lists'):
		os.mkdir('lists')

	lines = []
	logfile = open("log_downloadArtistsAll.txt",'w')
	f = open('artists.txt')
	for l in f:
		l = l.strip()
		if not l:
			continue
		lines.append(l)

	threadnum = 100
	threads = [Artists() for i in range(threadnum)]
	#pdb.set_trace()
	for i in range(threadnum):
		threads[i].start()

	for i in range(threadnum):
		threads[i].join()
	logfile.close()
	

