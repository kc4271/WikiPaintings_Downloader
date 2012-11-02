#coding=UTF-8
from BeautifulSoup import BeautifulSoup
import urllib
import re
import os

def read_web():
	_url = 'http://www.wikipaintings.org/en/alphabet'
	print 'Loading...'
	return  urllib.urlopen(_url).read()

if __name__ == "__main__":
	page = read_web()
	soup = BeautifulSoup(page)
	seg = soup.findAll('h6', {'class':'artist-grouped b0'})
	f = open('artists.txt','w')
	for s in seg:
		f.write(s.findAll('a')[0]['href'] + '\n')
	f.close()