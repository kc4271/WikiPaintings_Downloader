#coding=UTF-8
from BeautifulSoup import BeautifulSoup
import urllib
import re
import os

def read_web(alpha):
	_url = 'http://www.wikipaintings.org/en/alphabet/' + alpha
	return  urllib.urlopen(_url).read().decode('utf-8','ignore')

if __name__ == "__main__":
	#page = read_web()
	artists_list = []
	begin = ord('a')
	for i in range(26):
		print 'Loading Page ' + chr(begin + i)
		page = read_web(chr(begin + i))
		soup = BeautifulSoup(page)
		cates = soup.findAll('div',{'class':'search-item fLeft'})
		hrefs = [item.findAll('a',{'href':re.compile('/en/.*')})[0]['href'] for item in cates]
		artists_list.extend(hrefs)

	
	f = open('artists.txt','w')
	for artist in artists_list:
		f.write(u'%s\n' % artist)
	f.close()