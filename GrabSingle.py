#coding=UTF-8
import urllib
import sys
import os
import threading
import time
import pdb
import sys

class Downloader(threading.Thread):
	def __init__(self, url_file):
		threading.Thread.__init__(self)
		artist = os.path.basename(url_file)[:-4]
		dirname = 'Images/%s' % artist
		global mutex
		mutex.acquire()
		if not os.path.exists(dirname):
			os.makedirs(dirname)
		mutex.release()
		self._dirname = dirname

	def run(self):
		global mutex
		global logfile
		global count

		while True:
			mutex.acquire()
			if count < len(url_lists):
				self._url = url_lists[count]
				self._count = count
				count += 1
			else:
				self._url = ''
			mutex.release()
	
			if self._url:
				try:
					filename = self._url[self._url.rfind('/'):]
					self._path = (self._dirname + filename)
					mutex.acquire()
					exists = os.path.exists(self._path)
					mutex.release()
					if not exists:
						mutex.acquire()
						print "Downloading %s %d" % (self._dirname, self._count + 1)
						mutex.release()
						urllib.urlretrieve(self._url,self._path)
						mutex.acquire()
						print 'Finisth %s %d' % (self._dirname, self._count + 1)
						mutex.release()
				except:
					mutex.acquire()
					logfile.write(u'Download Failed at %s %d' % (self._dirname, self._count + 1))
					logfile.flush()
					os.fsync(logfile.fileno())
					mutex.release()
			else:
				break

def Download(url_path):
	global url_lists
	f = open(url_path)
	for l in f:
		l = l.strip()
		if not l:
			continue
		url_lists.append(l)

	threadsnum = 100
	threads = [Downloader(url_path) for i in range(threadsnum)]
	for i in range(threadsnum):
		threads[i].start()

	for i in range(threadsnum):
		threads[i].join()


if __name__ == '__main__':
	global mutex
	global count
	global url_lists	
	global logfile
	mutex = threading.Lock()
	url_lists = []
	count = 0

	logfile = open('log_downloader.txt','w')

	while True:
		path = raw_input("Input the artist list(for example: vittore-carpaccio.lst)\n")
		if os.path.exists('lists/' + path):
			Download('lists/' + path)
			print "Finish %s\n\n" % path
		else:
			print 'can not find lists/%s' % path
	logfile.close()