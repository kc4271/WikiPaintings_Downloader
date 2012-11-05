#coding=UTF-8
import urllib
import sys
import os
import threading
import time
import pdb
import sys

class Downloader(threading.Thread):
	def __init__(self, url_file, time_count):
		threading.Thread.__init__(self)
		artist = os.path.basename(url_file)[:-4]
		dirname = 'Images/%s' % artist
		global mutex
		mutex.acquire()
		if not os.path.exists(dirname):
			os.makedirs(dirname)
		mutex.release()
		self._dirname = dirname
		self._time_count = time_count

	def run(self):
		global mutex
		global logfile
		global count
		
		self._time_count[0] = int(time.time())
		while True:
			mutex.acquire()
			
			if count < len(url_lists):
				self._url = url_lists[count]
				self._count = count
				count += 1
				self._time_count[0] = int(time.time())
			else:
				self._url = ''
			mutex.release()
	
			if self._url:
				filename = self._url[self._url.rfind('/'):]
				self._path = (self._dirname + filename)
				
				exists = os.path.exists(self._path)
				
				if not exists:
					mutex.acquire()
					print "Downloading %s %d" % (self._dirname, self._count + 1)
					mutex.release()
					try:
						urllib.urlretrieve(self._url,self._path)
					except:
						mutex.acquire()
						logfile.write('Exception: ')
						logfile.write(self._url)
						logfile.write('\n')
						logfile.flush()
						os.fsync(logfile.fileno())
						mutex.release()
					mutex.acquire()
					curtime = int(time.time())
					print 'Finisth %s %d, %ds' % (self._dirname, self._count + 1, curtime - self._time_count[0])
					mutex.release()
				
					
			else:
				break

class DownloadManager(threading.Thread):
	def __init__(self, url_file):
		threading.Thread.__init__(self)
		self._url_file = url_file
		self._time_count = [0]

	def run(self):
		global mutex

		worker = Downloader(self._url_file, self._time_count)
		worker.daemon = True
		worker.start()

		while True:
			worker.join(20)
			if worker.isAlive():
				timeout = False
				curtime = int(time.time())
				mutex.acquire()
				runtime = self._time_count[0]
				if curtime - runtime > 3 * 60:
					print '[Warning!!!] %s maybe timeout, it will be killed after 17 minutes' % (worker._path.encode('ascii','replace'))
				if curtime - runtime > 20 * 60:
					logfile.write('Timeout: ')
					logfile.write(worker._url)
					logfile.write('\n')
					logfile.flush()
					os.fsync(logfile.fileno())
					timeout = True
				mutex.release()

				if timeout:
					break
			else:
				break

def Download(url_path):
	global url_lists
	global count
	global mutex

	mutex = threading.Lock()

	f = open(url_path)
	url_lists = []
	count = 0
	for l in f:
		l = l.strip()
		if not l:
			continue
		url_lists.append(l)
	f.close()
	
	threadsnum = 100
	threads = [DownloadManager(url_path) for i in range(threadsnum)]
	for i in range(threadsnum):
		threads[i].start()

	while True:
		alive = False
		for i in range(threadsnum):
			if threads[i].isAlive():
				alive = True
				time.sleep(0.2)
		if not alive:
			break
		
if __name__ == '__main__':
	global count
	global url_lists	
	global logfile
	
	url_lists = []
	count = 0

	logfile = open('log_Single.txt','a')

	while True:
		path = raw_input("Input the artist list(for example: vittore-carpaccio.lst)\n")
		if os.path.exists('lists/' + path):
			Download('lists/' + path)
			print "Finish %s\n\n" % path
		else:
			print 'can not find lists/%s' % path
	logfile.close()